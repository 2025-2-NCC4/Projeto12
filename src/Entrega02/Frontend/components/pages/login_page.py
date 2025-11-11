import streamlit as st
from utils.auth_ui import render_login_ui

st.set_page_config(
    page_title="Entrar | PicMoney",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
    <style>
        /* Esconde a navegação multipage (lista de páginas) */
        section[data-testid="stSidebarNav"] { display: none !important; }
        /* Esconde a sidebar inteira */
        [data-testid="stSidebar"] { display: none !important; }
        /* Ajusta o padding do conteúdo quando a sidebar some */
        .main .block-container { padding-left: 1.5rem; padding-right: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

render_login_ui()
