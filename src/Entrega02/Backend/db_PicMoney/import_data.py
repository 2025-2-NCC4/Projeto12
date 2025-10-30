import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
usuario = os.getenv('DB_USUARIO')
senha = os.getenv('DB_SENHA')
banco = os.getenv('DB_BANCO')
host = os.getenv('DB_HOST')
engine  = create_engine(
    f"mysql+pymysql://{usuario}@{host}/{banco}",
    connect_args={"password": senha}
)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')

with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
    for tbl in ['transacao','cupom','parceiro','campanha','player','regiao']:
        conn.execute(text(f"DROP TABLE IF EXISTS {tbl};"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

df_transacao = pd.read_excel(os.path.join(DATA_DIR, 'PicMoney_Base_Transacoes.xlsx'))
df_lojas     = pd.read_excel(os.path.join(DATA_DIR, 'PicMoney_Base_Lojas_e_Valores.xlsx'))
df_pedestres = pd.read_excel(os.path.join(DATA_DIR, 'PicMoney_Base_Pedestres_Av_Paulista.xlsx'))
df_players   = pd.read_excel(os.path.join(DATA_DIR, 'PicMoney_Base_Cadastral_Players.xlsx'))

#Tabela Região
bairros = df_transacao['bairro_estabelecimento'].unique()
df_regiao = pd.DataFrame({
    'id_regiao': range(1, len(bairros)+1),
    'bairro': bairros,
    'cidade': 'SP'
})

#Tabela Campanha
campanhas_unicas = df_transacao['id_campanha'].unique()
campanha_map = {camp: idx for idx, camp in enumerate(campanhas_unicas, start=1)}
camp_bairro = df_transacao[['id_campanha','bairro_estabelecimento']].drop_duplicates(subset='id_campanha', keep='first')
df_campanha = (
    camp_bairro
    .merge(df_regiao, left_on='bairro_estabelecimento', right_on='bairro', how='left')
    .rename(columns={'id_regiao':'id_regiao_fk'})
)
df_campanha['id_campanha_int'] = df_campanha['id_campanha'].map(campanha_map)
df_campanha['nome'] = 'Campanha ' + df_campanha['id_campanha'].astype(str)
df_campanha = df_campanha[['id_campanha_int','nome','id_regiao_fk']].rename(columns={'id_campanha_int':'id_campanha'})

#Tabela Player
cols_p = {
    'celular':'celular','idade':'idade','sexo':'genero',
    'data_nascimento':'dataNascimento','cidade_residencial':'cidade',
    'bairro_residencial':'bairro'
}
df_player = df_players[list(cols_p)].rename(columns=cols_p)
df_player['nome'] = 'Player ' + df_player['celular'].astype(str)
df_player['email'] = df_player['celular'].astype(str) + '@email.placeholder.com'
df_player['dataNascimento'] = pd.to_datetime(
    df_player['dataNascimento'],
    format='%d/%m/%Y',
    errors='coerce'
)
df_player.insert(0,'id_player',range(1,len(df_player)+1))

#Tabela Parceiro
df_parceiro = (
    df_transacao[['nome_estabelecimento','categoria_estabelecimento','bairro_estabelecimento']]
    .drop_duplicates()
    .rename(columns={
        'nome_estabelecimento':'nome_parceiro',
        'categoria_estabelecimento':'categoria_parceiro'
    })
    .merge(df_regiao, left_on='bairro_estabelecimento', right_on='bairro', how='left')
    .rename(columns={'id_regiao':'id_regiao_fk'})
    .drop(columns=['bairro_estabelecimento','bairro','cidade'])
)
df_parceiro.insert(0,'id_parceiros',range(1,len(df_parceiro)+1))

#Tabela Cupom
cupons_unicos = df_transacao['id_cupom'].unique()
cupom_map = {cup: idx for idx, cup in enumerate(cupons_unicos, start=1)}

df_cupom = (
    df_transacao[['id_cupom', 'valor_cupom', 'tipo_cupom', 'id_campanha']]
    .drop_duplicates(subset=['id_cupom'], keep='first')
)
df_cupom['id_cupom_int'] = df_cupom['id_cupom'].map(cupom_map)
df_cupom['codigo_cupom'] = df_cupom['id_cupom']  # mantém código original CUP...
df_cupom['id_campanha_int'] = df_cupom['id_campanha'].map(campanha_map)

df_cupom = df_cupom[['id_cupom_int', 'codigo_cupom', 'valor_cupom', 'tipo_cupom', 'id_campanha_int']].rename(columns={
    'id_cupom_int': 'id_cupom',
    'id_campanha_int': 'id_campanha_fk'
})

#Tabela Transação
df_transacao_final = df_transacao.copy()

df_transacao_final = pd.merge(
    df_transacao_final,
    df_player[['id_player', 'celular']],
    on='celular',
    how='left'
)

df_transacao_final = pd.merge(
    df_transacao_final,
    df_parceiro[['id_parceiros', 'nome_parceiro']],
    left_on='nome_estabelecimento',
    right_on='nome_parceiro',
    how='left'
)

df_transacao_final = pd.merge(
    df_transacao_final,
    df_cupom[['id_cupom', 'codigo_cupom']],
    left_on='id_cupom',
    right_on='codigo_cupom',
    how='left'
)

df_transacao_final['data_hora_transacao'] = pd.to_datetime(
    df_transacao_final['data'].astype(str) + ' ' + df_transacao_final['hora'].astype(str)
)

df_transacao_final.rename(columns={
    'valor_cupom': 'valor_transacao',
    'repasse_picmoney': 'valor_repasse',
    'id_player': 'id_player_fk',
    'id_parceiros': 'id_parceiros_fk',
    'id_cupom_y': 'id_cupom_fk'
}, inplace=True)
df_transacao_final.insert(0, 'id_transacao', range(1, 1 + len(df_transacao_final)))

colunas_finais_transacao = [
    'id_transacao', 'valor_transacao', 'valor_repasse',
    'data_hora_transacao', 'id_player_fk', 'id_parceiros_fk', 'id_cupom_fk'
]
df_transacao_final = df_transacao_final[colunas_finais_transacao]

#Tabelas
df_regiao.to_sql('regiao',    con=engine, if_exists='replace', index=False)
df_campanha.to_sql('campanha', con=engine, if_exists='replace', index=False)
df_player.to_sql('player',    con=engine, if_exists='replace', index=False)
df_parceiro.to_sql('parceiro', con=engine, if_exists='replace', index=False)
df_cupom.to_sql('cupom',      con=engine, if_exists='replace', index=False)
df_transacao_final.to_sql('transacao', con=engine, if_exists='replace', index=False)

#FK
print("Adicionando Chaves Primárias e Estrangeiras...")
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE regiao ADD PRIMARY KEY (id_regiao);"))
    conn.execute(text("ALTER TABLE campanha ADD PRIMARY KEY (id_campanha);"))
    conn.execute(text("ALTER TABLE player ADD PRIMARY KEY (id_player);"))
    conn.execute(text("ALTER TABLE parceiro ADD PRIMARY KEY (id_parceiros);"))
    conn.execute(text("ALTER TABLE cupom ADD PRIMARY KEY (id_cupom);"))
    conn.execute(text("ALTER TABLE transacao ADD PRIMARY KEY (id_transacao);"))
    conn.execute(text("""
        ALTER TABLE campanha
        ADD CONSTRAINT campanha_ibfk_1
        FOREIGN KEY (id_regiao_fk) REFERENCES regiao(id_regiao);
    """))
    conn.execute(text("""
        ALTER TABLE parceiro
        ADD CONSTRAINT parceiro_ibfk_1
        FOREIGN KEY (id_regiao_fk) REFERENCES regiao(id_regiao);
    """))
    conn.execute(text("""
        ALTER TABLE cupom
        ADD CONSTRAINT cupom_ibfk_1
        FOREIGN KEY (id_campanha_fk) REFERENCES campanha(id_campanha);
    """))
    conn.execute(text("""
        ALTER TABLE transacao
        ADD CONSTRAINT transacao_ibfk_1
        FOREIGN KEY (id_player_fk) REFERENCES player(id_player);
    """))
    conn.execute(text("""
        ALTER TABLE transacao
        ADD CONSTRAINT transacao_ibfk_2
        FOREIGN KEY (id_parceiros_fk) REFERENCES parceiro(id_parceiros);
    """))
    conn.execute(text("""
        ALTER TABLE transacao
        ADD CONSTRAINT transacao_ibfk_3
        FOREIGN KEY (id_cupom_fk) REFERENCES cupom(id_cupom);
    """))