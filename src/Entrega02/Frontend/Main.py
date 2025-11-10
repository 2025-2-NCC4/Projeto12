import os, base64
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.styles import injetar_estilos_globais, injetar_particulas, PICMONEY_COLORS
from utils.database import carregar_dados_mysql
from utils.auth_ui import require_login, logout   

st.set_page_config(
    page_title="PicMoney Dashboard | Principal",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide"
)

try:
    st.navigation(position="hidden")
except Exception:
    st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)

usuario = require_login(perfil_obrigatorio=None, redirect_to="pages/Login.py")
PERFIL_DO_USUARIO = (usuario or {}).get("perfil", "N/A")
NOME_USUARIO = (usuario or {}).get("nome", "")

injetar_estilos_globais()
injetar_particulas()

st.sidebar.image("assets/Logo_PicMoney_SemFundo.png", width=200)
st.sidebar.markdown("---")

st.sidebar.page_link("Main.py", label="Início", icon="🏠")
if str(PERFIL_DO_USUARIO).upper() == "CEO":
    st.sidebar.page_link("pages/CEO.py", label="CEO", icon="👑")
elif str(PERFIL_DO_USUARIO).upper() == "CFO":
    st.sidebar.page_link("pages/CFO.py", label="CFO", icon="💰")

st.sidebar.page_link("pages/Chatbot.py", label="Chatbot", icon="🤖")

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair da Conta", use_container_width=True):
    logout()  

def get_video_as_base64(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

VIDEO_PATH = "assets/video_formato2.mp4"
video_base64 = get_video_as_base64(VIDEO_PATH)

if video_base64:
    st.components.v1.html(f"""
        <style>
        .hero-video-container {{
            position: relative;
            width: 100%;
            height: 500px;
            overflow: hidden;
            border-radius: 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,.35);
        }}
        .hero-video-container video {{
            position: absolute; top:50%; left:50%;
            width:100%; height:100%; object-fit:cover;
            transform: translate(-50%, -50%);
        }}
        </style>
        <div class="hero-video-container">
            <video autoplay loop muted playsinline>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
        </div>
    """, height=500)
else:
    st.warning("O vídeo de cabeçalho não pôde ser carregado.")

st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)

titulo = "Dashboard Estratégico PicMoney"
if NOME_USUARIO:
    titulo += f" — Bem-vindo, {NOME_USUARIO}!"
st.title(titulo)
st.markdown("Visão consolidada dos principais indicadores (CEO e CFO)")
st.markdown("---")

try:
    df_transacoes = carregar_dados_mysql(
        "SELECT valor_transacao, data_hora_transacao, id_player_fk, id_cupom_fk FROM transacao"
    )
    if df_transacoes.empty:
        st.error("Não foi possível carregar os dados das transações. Verifique a conexão e a query.")
        st.stop()
except Exception as e:
    st.error(f"Erro fatal ao carregar dados: {e}")
    st.stop()

total_receita = df_transacoes['valor_transacao'].sum()
total_cupons  = df_transacoes['id_cupom_fk'].count()
usuarios_ativos = df_transacoes['id_player_fk'].nunique()
ticket_medio = (total_receita / total_cupons) if total_cupons > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Receita Total (GMV)</div>
            <div class="kpi-value">R$ {total_receita:,.2f}</div>
        </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Cupons Capturados</div>
            <div class="kpi-value">{total_cupons:,}</div>
        </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Ticket Médio</div>
            <div class="kpi-value">R$ {ticket_medio:,.2f}</div>
        </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Usuários Ativos</div>
            <div class="kpi-value">{usuarios_ativos:,}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.header("📈 Gráficos Resumidos")
try:
    df_transacoes['data_hora_transacao'] = pd.to_datetime(df_transacoes['data_hora_transacao'])
    receita_diaria = df_transacoes.groupby(df_transacoes['data_hora_transacao'].dt.date)['valor_transacao'].sum().reset_index()

    fig_receita = px.line(
        receita_diaria, x='data_hora_transacao', y='valor_transacao',
        title='Receita Total (GMV) ao Longo do Tempo',
        labels={'data_hora_transacao': 'Data', 'valor_transacao': 'Receita (R$)'},
        template='plotly_dark'
    )
    fig_receita.update_traces(line=dict(color=PICMONEY_COLORS['verde'], width=3))
    fig_receita.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        title_font_color=PICMONEY_COLORS['verde'], font_color=PICMONEY_COLORS['branco']
    )
    st.plotly_chart(fig_receita, use_container_width=True)
except KeyError as e:
    st.warning(f"Erro ao gerar gráfico. A coluna {e} não foi encontrada. Verifique sua query SQL.")
except Exception as e:
    st.error(f"Erro inesperado ao gerar gráfico: {e}")

st.markdown('</div>', unsafe_allow_html=True)
