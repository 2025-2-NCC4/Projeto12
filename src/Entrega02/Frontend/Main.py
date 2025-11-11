import os
import streamlit as st
import pandas as pd
from utils.styles import (
    injetar_estilos_globais, 
    injetar_particulas,
    remover_padding_completo
)
from utils.database import carregar_dados_mysql
from utils.auth_ui import require_login, logout
from components.video import HeroVideo
from components.pages.ceo_page import CEOPage
from components.pages.cfo_page import CFOPage
from components.pages.chatbot_page import ChatbotPage

st.set_page_config(
    page_title="PicMoney Dashboard",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide"
)

try:
    st.navigation(position="sidebar")
except Exception:
    st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)

usuario = require_login(perfil_obrigatorio=None, redirect_to="pages/Login.py")
PERFIL_DO_USUARIO = (usuario or {}).get("perfil", "N/A")
NOME_USUARIO = (usuario or {}).get("nome", "")

injetar_estilos_globais()
injetar_particulas()
remover_padding_completo()

@st.cache_data(ttl=600)
def load_data():
    return carregar_dados_mysql(
        "SELECT valor_transacao, data_hora_transacao, id_player_fk, id_cupom_fk FROM transacao"
    )

# Build available pages based on role
perfil_upper = str(PERFIL_DO_USUARIO).upper()
pages = {}

# CEO Page
if perfil_upper == "CEO":
    pages['ceo'] = {
        'label': '👔 CEO',
        'instance': CEOPage(),
        'filter_icon': '🎯'
    }

# CFO Page
if perfil_upper == "CFO":
    pages['cfo'] = {
        'label': '💼 CFO',
        'instance': CFOPage(),
        'filter_icon': '💰'
    }

# Chatbot (always available)
pages['chatbot'] = {
    'label': '🤖 Chatbot',
    'instance': ChatbotPage()
}

page_list = list(pages.items())

# Sidebar
image_path = os.path.join(os.path.dirname(__file__), "assets", "Logo_PicMoney_SemFundo.png")
st.sidebar.image(image_path, width=200)

# Render filters for ALL pages in sidebar (they'll only apply when tab is active)
st.sidebar.markdown("---")

# Show filters only for the first page (role-specific) with expanded=True
for idx, (key, page_info) in enumerate(page_list):
    # Only expand the first filter (role-specific page)
    is_expanded = (idx == 0)
    page_info['instance'].render_filters()
        
if st.sidebar.button("Sair", use_container_width=True):
    logout()

# Hero Video
# HeroVideo.render("assets/video_formato2.mp4")

st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)

# Initialize active tab in session state
if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0

# Render tabs or single page
if len(pages) == 1:
    # Single page, no tabs
    list(pages.values())[0]['instance'].render()
else:
    # Multiple pages with tabs
    tab_labels = [p['label'] for p in pages.values()]
    tabs = st.tabs(tab_labels)
    
    for idx, (tab, (key, page_info)) in enumerate(zip(tabs, page_list)):
        with tab:
            page_info['instance'].render()

st.markdown('</div>', unsafe_allow_html=True)

# titulo = "Dashboard Estratégico PicMoney"
# if NOME_USUARIO:
#     titulo += f" — Bem-vindo, {NOME_USUARIO}!"
# st.title(titulo)
# st.markdown("---")


st.markdown("---")
st.markdown("© 2025 PicMoney - Dashboard Estratégico")
