import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from utils.styles import injetar_estilos_globais, PICMONEY_COLORS, injetar_particulas
from utils.database import carregar_dados_mysql
import json
import re
from unidecode import unidecode

#Formatação R$
def formatar_brl(valor):
    try:
        texto_padrao = f"{valor:,.2f}"
        texto_temp = texto_padrao.replace(",", "X")
        texto_br = texto_temp.replace(".", ",")
        texto_final = texto_br.replace("X", ".")
        return f"R$ {texto_final}"
    except Exception:
        return "R$ 0,00"

#limpeza dos nomes dos bairros
def limpar_nome_bairro(nome):
    """
    Remove acentos, caracteres especiais, converte para maiúsculas e limpa espaços.
    """
    if not isinstance(nome, str):
        return ""

    nome_maiusculo = nome.upper()
    
    mapa_bairros = {
        "HIGIENOPOLIS": "CONSOLACAO"
    }

    if nome_maiusculo in mapa_bairros:
        nome_maiusculo = mapa_bairros[nome_maiusculo]
    
    nome_sem_acento = unidecode(nome_maiusculo)
    nome_limpo = re.sub(r'[^A-Z0-9\s]', '', nome_sem_acento)
    nome_limpo = re.sub(r'\s+', ' ', nome_limpo)
    nome_final = nome_limpo.strip()
    return nome_final

injetar_estilos_globais()
injetar_particulas()

st.set_page_config(
    page_title="PicMoney Dashboard | CFO",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide"
)

video_path = "assets/video_picmoney.mp4"

st.markdown("""
    <style>
        .video-container {
            width: 100%;
            max-width: 100%;
            margin: 0;
            padding: 0;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
        .video-container video {
            width: 100%;
            height: auto;
            object-fit: cover;
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

try:
    with open(video_path, "rb") as video_file:
        st.markdown(f"""
            <div class="video-container">
                <video width="100%" height="auto" autoplay muted loop>
                    <source src="data:video/mp4;base64,{__import__('base64').b64encode(video_file.read()).decode()}" type="video/mp4">
                    Seu navegador não suporta vídeo HTML5.
                </video>
            </div>
        """, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning(f"Vídeo não encontrado em: {video_path}")

st.markdown("<br>", unsafe_allow_html=True)

st.sidebar.image("assets/Logo_PicMoney_SemFundo.png", width=200)

st.markdown(f"""
    <h1 style='color: {PICMONEY_COLORS['branco']};'>
        Painel Financeiro: 
        <span style='color: {PICMONEY_COLORS['amarelo']};'>
            CFO (Chief Financial Officer)
        </span>
    </h1>
""", unsafe_allow_html=True)
st.markdown(f"""
    <p style='color: {PICMONEY_COLORS['branco']};'>
        Visão detalhada da saúde financeira, receitas e margens. 
    </p>
""", unsafe_allow_html=True)

#selecionando os dados
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


#filtros
st.sidebar.header("Filtros Financeiros")

min_data = df_full['data_hora_transacao'].min().date()
max_data = df_full['data_hora_transacao'].max().date()

data_inicio = st.sidebar.date_input(
    "Data Início", value=None, min_value=min_data, max_value=max_data, format="DD/MM/YYYY"
)
data_fim = st.sidebar.date_input(
    "Data Fim", value=None, min_value=data_inicio if data_inicio else min_data, max_value=max_data, format="DD/MM/YYYY"
)

st.sidebar.markdown("---")
categorias_unicas = df_full['categoria_parceiro'].unique()

selecionar_todas_categorias = st.sidebar.checkbox("Selecionar Todas as Categorias")

if selecionar_todas_categorias:
    default_categorias = categorias_unicas
else:
    default_categorias = []

categorias_selecionadas = st.sidebar.multiselect(
    "Categoria do Parceiro (Tipo de Loja)",
    options=categorias_unicas,
    default=default_categorias
)

st.sidebar.markdown("---")
bairros_unicos = df_full['bairro'].unique()

selecionar_todos_bairros = st.sidebar.checkbox("Selecionar Todos os Bairros")
if selecionar_todos_bairros:
    default_bairros = bairros_unicos
else:
    default_bairros = []

bairros_selecionados = st.sidebar.multiselect(
    "Bairro", 
    options=bairros_unicos, 
    default=default_bairros
)

#aviso de seleção de filtro
if not data_inicio or not data_fim or not categorias_selecionadas or not bairros_selecionados:
    st.markdown("""
        <div class="custom-info-box">
        ⬅️ Por favor, selecione o período, categoria e bairro no filtro lateral para começar.
        </div>
    """, unsafe_allow_html=True)
    st.stop()

df_filtrado = df_full[
    (df_full['data_hora_transacao'].dt.date >= data_inicio) &
    (df_full['data_hora_transacao'].dt.date <= data_fim) &
    (df_full['categoria_parceiro'].isin(categorias_selecionadas)) &
    (df_full['bairro'].isin(bairros_selecionados))
]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()


#KPIs principais
st.header("Indicadores Chave de Performance")

receita_total_gmv = df_filtrado['valor_transacao'].sum()
receita_liquida_picmoney = df_filtrado['valor_repasse'].sum()
num_transacoes = len(df_filtrado)
margem_operacional = (receita_liquida_picmoney / receita_total_gmv) * 100 if receita_total_gmv > 0 else 0
ticket_medio = receita_total_gmv / num_transacoes if num_transacoes > 0 else 0
valor_medio_repasse = receita_liquida_picmoney / num_transacoes if num_transacoes > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Receita Líquida</div><div class="kpi-value">{formatar_brl(receita_liquida_picmoney)}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Margem Operacional</div><div class="kpi-value">{margem_operacional:,.2f} %</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Ticket Médio</div><div class="kpi-value">{formatar_brl(ticket_medio)}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) 
col4, col5 = st.columns(2)
with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Valor Médio do Repasse (R$)</div><div class="kpi-value">{formatar_brl(valor_medio_repasse)}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Receita Bruta (GMV)</div><div class="kpi-value">{formatar_brl(receita_total_gmv)}</div></div>', unsafe_allow_html=True)

st.markdown("---")

#gráfico de receita por periodo
st.header("Receita Liquída por Período")

df_receita_dia = df_filtrado.set_index('data_hora_transacao').resample('D')['valor_repasse'].sum().reset_index()
fig_linha = px.line(df_receita_dia, x='data_hora_transacao', y='valor_repasse', labels={'data_hora_transacao': 'Data', 'valor_repasse': 'Receita (R$) P/ Dia'}, template='plotly_dark')
fig_linha.update_traces(line=dict(color=PICMONEY_COLORS['verde'], width=3))
fig_linha.update_xaxes(tickformat="%d/%m/%Y") 
fig_linha.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_linha, use_container_width=True)


st.markdown("---")
st.header("Análise de Rentabilidade (Cupom e Categoria)")   
col_graf_a, col_graf_b = st.columns(2)

with col_graf_a:
    st.subheader("Receita Liquída por Tipo de Cupom")
    df_receita_cupom = df_filtrado.groupby('tipo_cupom')['valor_repasse'].sum().reset_index()
    fig_barra = px.bar(
        df_receita_cupom, 
        x='tipo_cupom', 
        y='valor_repasse', 
        labels={'tipo_cupom': 'Tipo de Cupom', 'valor_repasse': 'Receita (R$) Acumulada'}, 
        template='plotly_dark', 
        color='tipo_cupom',
        color_discrete_map={'Desconto': PICMONEY_COLORS['verde'], 'Cashback': PICMONEY_COLORS['amarelo'], 'Produto': PICMONEY_COLORS['branco']}
    )
    fig_barra.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_barra, use_container_width=True)

with col_graf_b:
    st.subheader("Receita Líquida vs. GMV por Categoria")
    
    df_categoria = df_filtrado.groupby('categoria_parceiro').agg(
        receita_liquida=('valor_repasse', 'sum'),
        gmv=('valor_transacao', 'sum'),
        num_transacoes=('id_transacao', 'count')  # 🔥 Adicionei isso
    ).reset_index()
    
    df_categoria['margem'] = (df_categoria['receita_liquida'] / df_categoria['gmv']) * 100
    df_categoria = df_categoria.dropna()
    
    fig_scatter_cat = px.scatter(
        df_categoria,
        x='gmv',
        y='receita_liquida',
        color='margem', 
        size='num_transacoes',
        hover_name='categoria_parceiro',
        hover_data={'num_transacoes': True, 'margem': ':.2f'},
        labels={
            'receita_liquida': 'Receita Líquida (R$)',
            'gmv': 'GMV (R$)',
            'margem': 'Margem (%)',
            'num_transacoes': 'Transações'
        },
        template='plotly_dark',
        color_continuous_scale=px.colors.sequential.YlGn,
        size_max=50
    )
    
    fig_scatter_cat.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    
    fig_scatter_cat.update_xaxes(title_text='GMV Total da Categoria (R$)')
    fig_scatter_cat.update_yaxes(title_text='Receita PicMoney (R$)')

    fig_scatter_cat.add_scatter(
        x=df_categoria['gmv'],
        y=df_categoria['receita_liquida'],
        mode='lines',
        name='Tendência',
        line=dict(color=PICMONEY_COLORS['verde'], width=2, dash='dash'),
        opacity=0.5
    )
    
    st.plotly_chart(fig_scatter_cat, use_container_width=True)

st.markdown("---")
st.header("Análise de Risco e Eficiência")

st.subheader("Risco de Concentração (Top 5 Parceiros)")

df_parceiros = df_filtrado.groupby('nome_parceiro')['valor_repasse'].sum().reset_index()
df_parceiros = df_parceiros.sort_values(by='valor_repasse', ascending=False)

df_parceiros_grafico = df_parceiros.head(5)
    
fig_bar_parceiros = px.bar(
    df_parceiros_grafico.sort_values(by='valor_repasse', ascending=True),
    x='valor_repasse',
    y='nome_parceiro',
    orientation='h',
    labels={'nome_parceiro': 'Parceiro', 'valor_repasse': 'Receita Liquída'},
    template='plotly_dark',
    color='valor_repasse',
    color_continuous_scale=px.colors.sequential.YlGn
)

fig_bar_parceiros.update_layout(
    plot_bgcolor='rgba(0,0,0,0)', 
    paper_bgcolor='rgba(0,0,0,0)',
    coloraxis_showscale=False, 
    margin=dict(t=30, l=10, r=10, b=10)
)

fig_bar_parceiros.update_yaxes(title_text="") 
st.plotly_chart(fig_bar_parceiros, use_container_width=True)


#grafico de mapa de calor
st.markdown("---")
st.subheader("Receita Líquida por Bairro")

df_filtrado['id_limpo'] = df_filtrado['bairro'].apply(limpar_nome_bairro)

df_bairro = df_filtrado.groupby('id_limpo').agg(
    bairro=('bairro', 'first'),
    valor_repasse=('valor_repasse', 'sum')
).reset_index()

#Carregando GeoJSON
GEOJSON_PATH = "assets/sp_bairros.geojson"
try:
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson_sp = json.load(f)
except FileNotFoundError:
    st.error(f"Arquivo GeoJSON não encontrado!")
    st.stop()

for feature in geojson_sp['features']:
    nome_original = feature['properties']['ds_nome']
    feature['properties']['id_limpo'] = limpar_nome_bairro(nome_original)

st.markdown("**Estatísticas dos Valores:**")
col_debug1, col_debug2, col_debug3 = st.columns(3)
with col_debug1:
    st.metric("Valor Mínimo", f"R$ {df_bairro['valor_repasse'].min():,.2f}")
with col_debug2:
    st.metric("Valor Médio", f"R$ {df_bairro['valor_repasse'].mean():,.2f}")
with col_debug3:
    st.metric("Valor Máximo", f"R$ {df_bairro['valor_repasse'].max():,.2f}")

valor_min = df_bairro['valor_repasse'].min()
valor_max = df_bairro['valor_repasse'].max()

color_scale = [
    [0.0, "#0A3D3D"],
    [0.25, "#1A5D5D"],
    [0.5, "#FFD700"],
    [0.75, "#E8DC3C"],
    [1.0, "#C8D962"]
]

fig_mapa = px.choropleth_mapbox(
    df_bairro,
    geojson=geojson_sp,
    featureidkey="properties.id_limpo",
    locations="id_limpo",
    color="valor_repasse",
    color_continuous_scale=color_scale,
    range_color=[valor_min, valor_max],
    mapbox_style="carto-darkmatter",
    zoom=9.5,
    center={"lat": -23.5505, "lon": -46.6333},
    opacity=0.8,
    hover_name="bairro",
    hover_data={'valor_repasse': ':,.2f', 'id_limpo': False}
)

fig_mapa.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig_mapa, use_container_width=True)