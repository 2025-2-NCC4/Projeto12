import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from utils.styles import injetar_estilos_globais, PICMONEY_COLORS, injetar_particulas
from utils.database import carregar_dados_mysql

# --- [NOVO] Função para formatar moeda em Padrão Brasileiro ---
def formatar_brl(valor):
    """
    Formata um número para o padrão R$ 1.234.567,89
    """
    try:
        texto_padrao = f"{valor:,.2f}"
        texto_temp = texto_padrao.replace(",", "X")
        texto_br = texto_temp.replace(".", ",")
        texto_final = texto_br.replace("X", ".")
        return f"R$ {texto_final}"
    except Exception:
        return "R$ 0,00"
# --- Fim da nova função ---

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="PicMoney Dashboard | CFO",
    page_icon="💰",
    layout="wide"
)

# --- 2. Logo na Barra Lateral ---
st.sidebar.image("assets/Logo_PicMoney_SemFundo.png", width=200)

# --- 3. Injetar Estilos e Partículas ---
injetar_estilos_globais()
injetar_particulas() # Adicionando as partículas nesta página

# --- 4. Título ---
st.title("Painel Financeiro: CFO (Chief Financial Officer)")
st.markdown("Visão detalhada da saúde financeira, receitas e margens.")
st.markdown("---")

# --- 5. Carregar os Dados ---
# [MUDANÇA] Query SQL agora junta TODAS as tabelas para os novos gráficos
sql_query = """
SELECT
    t.valor_transacao,
    t.valor_repasse,
    t.data_hora_transacao,
    t.id_transacao,
    c.tipo_cupom,
    c.valor_cupom,
    p.categoria_parceiro,
    p.nome_parceiro,
    r.cidade,
    r.bairro,
    camp.nome AS nome_campanha
FROM
    transacao AS t
JOIN
    cupom AS c ON t.id_cupom_fk = c.id_cupom
JOIN
    parceiro AS p ON t.id_parceiros_fk = p.id_parceiros
JOIN
    regiao AS r ON p.id_regiao_fk = r.id_regiao
JOIN
    campanha AS camp ON c.id_campanha_fk = camp.id_campanha
"""

try:
    df_full = carregar_dados_mysql(sql_query)
    
    if df_full.empty:
        st.error("Não foi possível carregar os dados financeiros. Verifique a conexão e as tabelas.")
        st.stop() 

    df_full['data_hora_transacao'] = pd.to_datetime(df_full['data_hora_transacao'])

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.stop()


# --- 6. Filtros Interativos na Barra Lateral ---
st.sidebar.header("Filtros Financeiros")

min_data = df_full['data_hora_transacao'].min().date()
max_data = df_full['data_hora_transacao'].max().date()

data_inicio = st.sidebar.date_input(
    "Data Início", value=None, min_value=min_data, max_value=max_data, format="DD/MM/YYYY"
)
data_fim = st.sidebar.date_input(
    "Data Fim", value=None, min_value=data_inicio if data_inicio else min_data, max_value=max_data, format="DD/MM/YYYY"
)

categorias_unicas = df_full['categoria_parceiro'].unique()
categorias_selecionadas = st.sidebar.multiselect(
    "Categoria do Parceiro (Tipo de Loja)", options=categorias_unicas, default=[]
)

# [NOVO FILTRO] Filtro de Cidade para o Treemap
cidades_unicas = df_full['cidade'].unique()
cidades_selecionadas = st.sidebar.multiselect(
    "Cidade", options=cidades_unicas, default=[]
)


# --- 7. Lógica de Carregamento ---
if not data_inicio or not data_fim or not categorias_selecionadas or not cidades_selecionadas:
    st.info("⬅️ Por favor, selecione o período, categoria e cidade no filtro lateral para começar.")
    st.stop()

# [MUDANÇA] Filtro agora inclui as cidades
df_filtrado = df_full[
    (df_full['data_hora_transacao'].dt.date >= data_inicio) &
    (df_full['data_hora_transacao'].dt.date <= data_fim) &
    (df_full['categoria_parceiro'].isin(categorias_selecionadas)) &
    (df_full['cidade'].isin(cidades_selecionadas))
]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()


# --- 8. KPIs Principais (Cartões) ---
# (Esta seção não muda, mas usa o df_filtrado)
st.header("📈 Indicadores Chave de Performance")

receita_total_gmv = df_filtrado['valor_transacao'].sum()
receita_liquida_picmoney = df_filtrado['valor_repasse'].sum()
num_transacoes = len(df_filtrado)
margem_operacional = (receita_liquida_picmoney / receita_total_gmv) * 100 if receita_total_gmv > 0 else 0
ticket_medio = receita_total_gmv / num_transacoes if num_transacoes > 0 else 0
valor_medio_repasse = receita_liquida_picmoney / num_transacoes if num_transacoes > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Receita Líquida (Repasse)</div><div class="kpi-value">{formatar_brl(receita_liquida_picmoney)}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Margem Operacional Média</div><div class="kpi-value">{margem_operacional:,.2f} %</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Ticket Médio (GMV)</div><div class="kpi-value">{formatar_brl(ticket_medio)}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) 
col4, col5 = st.columns(2)
with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Valor Médio do Repasse (R$)</div><div class="kpi-value">{formatar_brl(valor_medio_repasse)}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Receita Total Transacionada (GMV)</div><div class="kpi-value">{formatar_brl(receita_total_gmv)}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 9. Gráficos (Linha 1) ---
st.header("📊 Análises Visuais")
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Receita (Repasse) por Período")
    df_receita_dia = df_filtrado.set_index('data_hora_transacao').resample('D')['valor_repasse'].sum().reset_index()
    fig_linha = px.line(df_receita_dia, x='data_hora_transacao', y='valor_repasse', labels={'data_hora_transacao': 'Data', 'valor_repasse': 'Receita (R$) P/ Dia'}, template='plotly_dark')
    fig_linha.update_traces(line=dict(color=PICMONEY_COLORS['verde'], width=3))
    fig_linha.update_xaxes(tickformat="%d/%m/%Y") 
    fig_linha.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_linha, use_container_width=True)

with col_graf2:
    st.subheader("Receita (Repasse) por Tipo de Cupom")
    df_receita_cupom = df_filtrado.groupby('tipo_cupom')['valor_repasse'].sum().reset_index()
    fig_barra = px.bar(df_receita_cupom, x='tipo_cupom', y='valor_repasse', labels={'tipo_cupom': 'Tipo de Cupom', 'valor_repasse': 'Receita (R$) Acumulada'}, template='plotly_dark', color='tipo_cupom',
                       color_discrete_map={'Desconto': PICMONEY_COLORS['verde'], 'Cashback': PICMONEY_COLORS['amarelo'], 'Produto': PICMONEY_COLORS['branco']})
    fig_barra.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_barra, use_container_width=True)

# --- [NOVO] 10. Gráfico (Linha 2) - KPI 1: Custo vs. Receita ---
st.markdown("---")
st.header("💸 Análise de Custo e Rentabilidade")
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.subheader("KPI 1: Custo (Cupom) vs. Receita (Repasse)")
    
    # Agrupa por tipo de cupom e soma Custo (valor_cupom) e Receita (valor_repasse)
    df_custo_receita = df_filtrado.groupby('tipo_cupom')[['valor_cupom', 'valor_repasse']].sum().reset_index()
    
    # Reorganiza (derrete) o dataframe para o Plotly agrupar
    df_melted = df_custo_receita.melt(id_vars='tipo_cupom', var_name='Metrica', value_name='Valor')
    
    # Mapeia os nomes para algo mais amigável
    df_melted['Metrica'] = df_melted['Metrica'].map({'valor_cupom': 'Custo (Valor Cupom)', 'valor_repasse': 'Receita (Repasse)'})
    
    fig_custo = px.bar(
        df_melted,
        x='tipo_cupom',
        y='Valor',
        color='Metrica', # Cria as duas barras (Custo e Receita)
        barmode='group', # Coloca as barras lado a lado
        labels={'tipo_cupom': 'Tipo de Cupom', 'Valor': 'Valor (R$)'},
        template='plotly_dark',
        color_discrete_map={
            'Custo (Valor Cupom)': PICMONEY_COLORS['amarelo'],
            'Receita (Repasse)': PICMONEY_COLORS['verde']
        }
    )
    fig_custo.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_custo, use_container_width=True)

# --- [NOVO] 11. Gráfico (Linha 2) - KPI 2: Rentabilidade por Região ---
with col_graf4:
    st.subheader("KPI 2: Rentabilidade por Cidade")
    
    # Agrupa por cidade e calcula receita, gmv e margem
    df_cidade = df_filtrado.groupby('cidade').agg(
        valor_repasse=('valor_repasse', 'sum'),
        valor_transacao=('valor_transacao', 'sum')
    ).reset_index()
    
    df_cidade['margem'] = (df_cidade['valor_repasse'] / df_cidade['valor_transacao']) * 100
    df_cidade = df_cidade.dropna() # Remove cidades sem transação
    
    fig_treemap = px.treemap(
        df_cidade,
        path=[px.Constant("Todas as Cidades"), 'cidade'], # Cria a hierarquia
        values='valor_repasse', # Tamanho do retângulo
        color='margem', # Cor do retângulo
        labels={'cidade': 'Cidade', 'valor_repasse': 'Receita (Repasse)', 'margem': 'Margem (%)'},
        template='plotly_dark',
        color_continuous_scale=['#FFFF00', '#7FFF00'] # Escala de Amarelo (ruim) para Verde (bom)
    )
    fig_treemap.update_layout(margin = dict(t=30, l=10, r=10, b=10))
    st.plotly_chart(fig_treemap, use_container_width=True)

# --- [NOVO] 12. Gráfico (Linha 3) - KPI 3: Concentração de Receita ---
st.markdown("---")
st.header("🎯 Análise de Risco e Eficiência")
col_graf5, col_graf6 = st.columns(2)

with col_graf5:
    st.subheader("KPI 3: Risco de Concentração (Top 10 Parceiros)")
    
    # Agrupa receita por parceiro
    df_parceiros = df_filtrado.groupby('nome_parceiro')['valor_repasse'].sum().reset_index()
    df_parceiros = df_parceiros.sort_values(by='valor_repasse', ascending=False)
    
    # Lógica para "Top 10 + Outros"
    if len(df_parceiros) > 10:
        df_top10 = df_parceiros.head(10)
        outros_sum = df_parceiros.iloc[10:]['valor_repasse'].sum()
        df_outros = pd.DataFrame([{'nome_parceiro': 'Outros', 'valor_repasse': outros_sum}])
        df_parceiros_donut = pd.concat([df_top10, df_outros], ignore_index=True)
    else:
        df_parceiros_donut = df_parceiros
        
    fig_donut = px.pie(
        df_parceiros_donut,
        names='nome_parceiro',
        values='valor_repasse',
        hole=0.5, # Transforma em "Donut"
        template='plotly_dark',
        color_discrete_sequence=px.colors.sequential.YlGn_r # Paleta de Amarelo->Verde
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(showlegend=False, margin = dict(t=30, l=10, r=10, b=10))
    st.plotly_chart(fig_donut, use_container_width=True)
    
# --- [NOVO] 13. Gráfico (Linha 3) - KPI 4: Eficiência de Campanha ---
with col_graf6:
    st.subheader("KPI 4: Eficiência de Campanha (Custo vs. Receita)")
    
    # Agrupa por campanha e calcula Custo, Receita e # de Transações
    df_campanha = df_filtrado.groupby('nome_campanha').agg(
        custo=('valor_cupom', 'sum'),
        receita=('valor_repasse', 'sum'),
        transacoes=('id_transacao', 'count')
    ).reset_index()
    
    fig_bolhas = px.scatter(
        df_campanha,
        x='custo',
        y='receita',
        size='transacoes', # Tamanho da bolha
        color='receita', # Cor da bolha
        hover_name='nome_campanha',
        labels={'custo': 'Custo Total (R$)', 'receita': 'Receita Total (R$)', 'transacoes': 'Nº de Transações'},
        template='plotly_dark',
        color_continuous_scale=px.colors.sequential.YlGn # Escala de Amarelo->Verde
    )
    fig_bolhas.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig_bolhas.update_xaxes(title_text='CUSTO (Pior)')
    fig_bolhas.update_yaxes(title_text='RECEITA (Melhor)')
    st.plotly_chart(fig_bolhas, use_container_width=True)