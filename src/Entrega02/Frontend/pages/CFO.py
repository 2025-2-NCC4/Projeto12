import streamlit as st
import pandas as pd
import plotly.express as px
import json, re
from unidecode import unidecode
from utils.styles import injetar_estilos_globais, PICMONEY_COLORS, injetar_particulas
from utils.auth_ui import require_login, logout
from utils.backend_client import BackendAPI


def brl(v):
    try:
        s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {s}"
    except Exception:
        return "R$ 0,00"

def limpar_nome_bairro(nome):
    if not isinstance(nome, str):
        return ""

    nome_maiusculo = nome.upper()
    
    if nome_maiusculo == "HIGIENOPOLIS":
        nome_maiusculo = "CONSOLACAO"
        
    nome_sem_acento = unidecode(nome_maiusculo)
    nome_limpo = re.sub(r'[^A-Z0-9\s]', '', nome_sem_acento)
    nome_limpo = re.sub(r'\s+', ' ', nome_limpo)
    nome_final = nome_limpo.strip()
    return nome_final



require_login(perfil_obrigatorio="CFO", redirect_to="pages/Login.py")

st.set_page_config(
    page_title="PicMoney Dashboard | CFO",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide"
)

st.markdown("""
<style>
/* Oculta o container de navegação automática de páginas do Streamlit */
[data-testid="stSidebarNav"] {
    display: none
}
</style>
""", unsafe_allow_html=True)

injetar_estilos_globais()
injetar_particulas()

st.sidebar.image("assets/Logo_PicMoney_SemFundo.png", width=200)

st.sidebar.markdown("---")
st.sidebar.page_link("Main.py", label="Início", icon="🏠")
st.sidebar.page_link("pages/CFO.py", label="CFO", icon="💰")
st.sidebar.page_link("pages/Chatbot.py", label="Chatbot", icon="🤖")

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair da Conta", use_container_width=True):
    logout()
    

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
        video_base64 = __import__('base64').b64encode(video_file.read()).decode()
        st.markdown(f"""
            <div class="video-container">
                <video width="100%" height="auto" autoplay muted 
                       onended="this.pause(); this.currentTime=this.duration;">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Seu navegador não suporta vídeo HTML5.
                </video>
            </div>
        """, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning(f"Vídeo não encontrado em: {video_path}")

st.markdown("<br>", unsafe_allow_html=True)

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



api = BackendAPI()
with st.spinner("Carregando filtros..."):
    r = api.get("/api/cfo/filters", timeout=60)
    fdata = r.json() if r.ok else {}
    if not fdata.get("ok"):
        st.error("Não foi possível carregar filtros do CFO.")
        st.stop()
        
min_dt = fdata["min_date"]; max_dt = fdata["max_date"]
categorias = fdata["categorias"]; bairros = fdata["bairros"]

min_date_obj = pd.to_datetime(min_dt).date() if min_dt else None
max_date_obj = pd.to_datetime(max_dt).date() if max_dt else None

st.sidebar.header("Filtros Financeiros")

data_inicio = st.sidebar.date_input(
    "Data Início", value=None,
    min_value=min_date_obj,
    max_value=max_date_obj,
    format="DD/MM/YYYY"
)
data_fim = st.sidebar.date_input(
    "Data Fim", value=None,
    min_value=data_inicio if data_inicio else min_date_obj,
    max_value=max_date_obj,
    format="DD/MM/YYYY"
)

st.sidebar.markdown("---")
sel_all_cat = st.sidebar.checkbox("Selecionar Todas as Categorias")
categorias_sel = st.sidebar.multiselect(
    "Categoria do Parceiro (Tipo de Loja)",
    options=categorias,
    default=(categorias if sel_all_cat else [])
)

st.sidebar.markdown("---")
sel_all_brr = st.sidebar.checkbox("Selecionar Todos os Bairros")
bairros_sel = st.sidebar.multiselect(
    "Bairro",
    options=bairros,
    default=(bairros if sel_all_brr else [])
)

if not data_inicio or not data_fim or not categorias_sel or not bairros_sel:
    st.markdown("""
        <div class="custom-info-box">
            ⬅️ Por favor, selecione o período, categoria e bairro no filtro lateral para começar.
        </div>
    """, unsafe_allow_html=True)
    st.stop()


payload = {
    "from": str(data_inicio),
    "to": str(data_fim),
    "categorias": categorias_sel,
    "bairros": bairros_sel
}

with st.spinner("Calculando indicadores financeiros..."):
    r = api.post("/api/cfo/data", json=payload, timeout=1000)
    data = r.json() if r.ok else {}
    if not data.get("ok"):
        st.error("Não foi possível carregar os dados financeiros.")
        st.stop()


k = data["kpis"]
st.header("Indicadores Chave de Performance")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Receita Líquida</div><div class="kpi-value">{brl(k["receita_liquida"])}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Margem Operacional</div><div class="kpi-value">{k["margem_operacional"]:,.2f} %</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Ticket Médio</div><div class="kpi-value">{brl(k["ticket_medio"])}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col4, col5 = st.columns(2)
with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Valor Médio do Repasse (R$)</div><div class="kpi-value">{brl(k["valor_medio_repasse"])}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Receita Bruta (GMV)</div><div class="kpi-value">{brl(k["gmv"])}</div></div>', unsafe_allow_html=True)

st.markdown("---")


st.header("Receita Líquida por Período")
df_receita_dia = pd.DataFrame(data["receita_diaria"])

if not df_receita_dia.empty:
    df_receita_dia['data'] = pd.to_datetime(df_receita_dia['data']) 
    fig_linha = px.line(df_receita_dia, x='data', y='valor_repasse',
                        labels={'data': 'Data', 'valor_repasse': 'Receita (R$) P/ Dia'},
                        template='plotly_dark')
    fig_linha.update_traces(line=dict(color=PICMONEY_COLORS['verde'], width=3))
    fig_linha.update_xaxes(tickformat="%d/%m/%Y") 
    fig_linha.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_linha, use_container_width=True)
else:
    st.info("Sem dados para o período selecionado.")

st.markdown("---")
st.header("Análise de Rentabilidade (Cupom e Categoria)")
c1, c2 = st.columns(2)


with c1:
    st.subheader("Receita Líquida por Tipo de Cupom")
    df_cupom = pd.DataFrame(data["receita_por_cupom"])
    if not df_cupom.empty:
        fig_barra = px.bar(
            df_cupom, x='tipo_cupom', y='valor_repasse',
            labels={'tipo_cupom': 'Tipo de Cupom', 'valor_repasse': 'Receita (R$) Acumulada'},
            template='plotly_dark', color='tipo_cupom',
            color_discrete_map={'Desconto': PICMONEY_COLORS['verde'],
                                'Cashback': PICMONEY_COLORS['amarelo'],
                                'Produto': PICMONEY_COLORS['branco']}
        )
        fig_barra.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_barra, use_container_width=True)
    else:
        st.info("Sem dados por tipo de cupom.")

with c2:
    st.subheader("Receita Líquida vs. GMV por Categoria")
    df_cat = pd.DataFrame(data["por_categoria"])
    if not df_cat.empty:
        fig_scatter = px.scatter(
            df_cat, x='gmv', y='receita_liquida',
            color='margem', size='num_transacoes',
            hover_name='categoria_parceiro',
            hover_data={'num_transacoes': True, 'margem': ':.2f'},
            labels={'receita_liquida': 'Receita Líquida (R$)', 'gmv': 'GMV (R$)', 'margem': 'Margem (%)', 'num_transacoes': 'Transações'},
            template='plotly_dark', color_continuous_scale=px.colors.sequential.YlGn, size_max=50
        )
        fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hovermode='closest')
        fig_scatter.update_xaxes(title_text='GMV Total da Categoria (R$)')
        fig_scatter.update_yaxes(title_text='Receita PicMoney (R$)')
        
        fig_scatter.add_scatter(x=df_cat['gmv'], y=df_cat['receita_liquida'],
                                mode='lines', name='Tendência',
                                line=dict(color=PICMONEY_COLORS['verde'], width=2, dash='dash'), opacity=0.5)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Sem dados por categoria.")

st.markdown("---")
st.header("Análise de Risco e Eficiência")


st.subheader("Risco de Concentração (Top 5 Parceiros)")
df_parc = pd.DataFrame(data["top_parceiros"])
if not df_parc.empty:
    fig_parc = px.bar(
        df_parc.sort_values(by='valor_repasse', ascending=True),
        x='valor_repasse', y='nome_parceiro', orientation='h',
        labels={'nome_parceiro': 'Parceiro', 'valor_repasse': 'Receita Líquida'},
        template='plotly_dark', color='valor_repasse',
        color_continuous_scale=px.colors.sequential.YlGn
    )
    fig_parc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           coloraxis_showscale=False, margin=dict(t=30, l=10, r=10, b=10))
    fig_parc.update_yaxes(title_text="")
    st.plotly_chart(fig_parc, use_container_width=True)
else:
    st.info("Sem dados de parceiros.")


st.markdown("---")
st.subheader("Receita Líquida por Bairro")
df_bairro = pd.DataFrame(data["por_bairro"])
stats = data["stats_bairro"] 
if not df_bairro.empty:
    GEOJSON_PATH = "assets/sp_bairros.geojson"
    try:
        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            geojson_sp = json.load(f)
    except FileNotFoundError:
        st.error("Arquivo GeoJSON não encontrado!")
        st.stop()

    for feat in geojson_sp["features"]:
        nome_original = feat["properties"]["ds_nome"]
        feat["properties"]["id_limpo"] = limpar_nome_bairro(nome_original)

    st.markdown("**Estatísticas dos Valores:**")
    col_debug1, col_debug2, col_debug3 = st.columns(3)
    with col_debug1:
        st.metric("Valor Mínimo", brl(stats['min']))
    with col_debug2:
        st.metric("Valor Médio", brl(stats['mean']))
    with col_debug3:
        st.metric("Valor Máximo", brl(stats['max']))

    color_scale = [
        [0.0, "#0A3D3D"], [0.25, "#1A5D5D"],
        [0.5, "#FFD700"], [0.75, "#E8DC3C"], [1.0, "#C8D962"]
    ]

    fig_mapa = px.choropleth_mapbox(
        df_bairro,
        geojson=geojson_sp,
        featureidkey="properties.id_limpo",
        locations="id_limpo",
        color="valor_repasse",
        color_continuous_scale=color_scale,
        range_color=[stats["min"], stats["max"]],
        mapbox_style="carto-darkmatter",
        zoom=9.5, center={"lat": -23.5505, "lon": -46.6333},
        opacity=0.8, hover_name="bairro",
        hover_data={'valor_repasse': ':,.2f', 'id_limpo': False}
    )
    fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                           plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_mapa, use_container_width=True)
else:
    st.info("Sem dados por bairro para os filtros selecionados.")