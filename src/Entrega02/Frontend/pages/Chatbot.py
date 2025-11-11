import streamlit as st
from utils.styles import injetar_estilos_globais, PICMONEY_COLORS
from utils.chatbot import configurar_gemini, processar_pergunta_com_sql
from utils.auth_ui import require_login, logout

st.set_page_config(
    page_title="PicMoney Dashboard | Chatbot AI",
    page_icon="🤖",
    layout="wide"
)


st.markdown("""
<style>
/* Oculta o container de navegação automática de páginas do Streamlit */
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)



usuario = require_login(perfil_obrigatorio=None, redirect_to="pages/Login.py")
perfil = (usuario or {}).get("perfil", "").upper() 
nome   = (usuario or {}).get("nome", "")

st.sidebar.image("assets/Logo_PicMoney_SemFundo.png", width=200)
st.sidebar.markdown("---")

st.sidebar.page_link("Main.py", label="Início", icon="🏠")

if perfil == "CEO":
    st.sidebar.page_link("pages/CEO.py", label="CEO", icon="👑")
elif perfil == "CFO":
    st.sidebar.page_link("pages/CFO.py", label="CFO", icon="💰")
    
st.sidebar.page_link("pages/Chatbot.py", label="Chatbot", icon="🤖")  

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair da Conta", width='stretch'):
    logout()  

injetar_estilos_globais()


if "historico_chat" not in st.session_state:

    st.session_state.historico_chat = []


st.markdown(f"""
<style>
.user-message {{
    background: linear-gradient(135deg, {PICMONEY_COLORS['verde']} 0%, #7FFF00 100%);
    color: #000;
    padding: 15px 20px;
    border-radius: 15px;
    margin: 12px 0;
    font-weight: 500;
    box-shadow: 0 3px 10px rgba(107, 191, 48, 0.3);
}}
.bot-message {{
    background: #2d2d2d;
    color: #fff;
    padding: 15px 20px;
    border-radius: 15px;
    margin: 12px 0;
    border: 2px solid {PICMONEY_COLORS['verde']};
    box-shadow: 0 3px 10px rgba(107, 191, 48, 0.2);
}}
</style>
""", unsafe_allow_html=True)


titulo = "🤖 PicMoney AI Assistant"
if nome:
    titulo += f" — Olá, {nome}!"
st.title(titulo)
st.markdown("Faça perguntas sobre os dados financeiros e obtenha respostas inteligentes com SQL!")
st.markdown("---")


messages_container = st.container()
with messages_container:
    if not st.session_state.historico_chat:
        st.info("👋 **Olá!** Sou o assistente AI da PicMoney. Pergunte-me qualquer coisa sobre os dados!")
        st.markdown("""
        **Exemplos de perguntas:**
        - Qual foi a receita total?
        - Quais os 10 parceiros com mais transações?
        - Quantos players temos por cidade?
        - Qual o ticket médio por categoria de parceiro?
        - Mostre a receita por mês
        """)
    else:
        for msg in st.session_state.historico_chat:
            if msg["tipo"] == "user":
                st.markdown(
                    f'<div class="user-message">💬 <strong>Você:</strong><br>{msg["texto"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="bot-message">🤖 <strong>Bot:</strong><br>{msg["texto"]}</div>',
                    unsafe_allow_html=True
                )
                if msg.get("dataframe") is not None and not msg["dataframe"].empty:
                    st.dataframe(msg["dataframe"], width='stretch')
                if msg.get("sql"):
                    with st.expander("📝 Ver SQL executada"):
                        st.code(msg["sql"], language="sql")

st.markdown("---")


col1, col2 = st.columns([7, 3])

with col1:
    with st.form(key="chat_form", clear_on_submit=True):
        pergunta = st.text_area(
            "Digite sua pergunta:",
            placeholder="Ex: Qual foi a receita total de julho?",
            height=100,
            key="input_chat"
        )
        c1_btn, c2_btn = st.columns([1, 1])
        with c1_btn:
            enviar = st.form_submit_button("📤 Enviar Pergunta", width='stretch')
        with c2_btn:
            limpar = st.form_submit_button("🗑️ Limpar Conversa", width='stretch')

        if limpar:
            st.session_state.historico_chat = []
            st.rerun()

        if enviar and pergunta.strip():
            if configurar_gemini():
                st.session_state.historico_chat.append({"tipo": "user", "texto": pergunta})
                with st.spinner("🤔 Processando sua pergunta..."):
                    resposta, df, sql = processar_pergunta_com_sql(pergunta)
                st.session_state.historico_chat.append({
                    "tipo": "bot",
                    "texto": resposta,
                    "dataframe": df,
                    "sql": sql
                })
                st.rerun()
            else:
                st.error("❌ Erro ao configurar Gemini. Verifique sua API key.")

with col2:
    st.markdown("### 💡 Dicas")
    st.markdown("""
    - Seja específico
    - Use nomes de tabelas: player, parceiro, transacao
    - Pergunte sobre períodos, categorias, regiões
    """)