import base64
from pathlib import Path
import streamlit as st
from .backend_client import BackendAPI
from utils.styles import PICMONEY_COLORS, injetar_estilos_globais
from streamlit_cookies_controller import CookieController

FIELD_WIDTH_PX = 300   # largura dos inputs/botão
CENTER_COL = 5         # largura relativa da coluna central
SIDE_COL = 5           # larguras das colunas laterais
LOGO_HEIGHT = 150      # altura do logo
SHIFT_UP_PX = 120      # quanto o bloco do login sobe


def _force_logout(base_url: str | None = None):
    try:
        api = BackendAPI(base_url)
        api.logout()
    except Exception:
        pass
    st.session_state.pop("usuario_logado", None)
    controller = CookieController()
    controller.remove('usuario_logado')


def go_to_login(base_url: str | None = None, reason: str | None = None, after: str | None = None):
    if reason:
        st.session_state["login_warning"] = reason
    if after:
        st.session_state["after_login_redirect"] = after
    try:
        st.switch_page("pages/Login.py")
    except Exception:
        st.rerun()


def _load_logo_base64() -> str:
    candidates = [
        Path(__file__).resolve().parents[1] / "assets" / "Logo_PicMoney_SemFundo.png",
        Path("assets/Logo_PicMoney_SemFundo.png"),
    ]
    for p in candidates:
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""


def render_login_ui(base_url: str | None = None):
    injetar_estilos_globais()

    st.set_page_config(
        page_title="PicMoney Dashboard | Principal",
        page_icon="assets/Logo_PicMoney_SemFundo.png",
        layout="wide"
    )

    logo_b64 = _load_logo_base64()
    logo_html = (
        f"<img src='data:image/png;base64,{logo_b64}' alt='Logo PicMoney' height='{LOGO_HEIGHT}'>"
        if logo_b64
        else f"<img src='assets/Logo_PicMoney_SemFundo.png' alt='Logo PicMoney' height='{LOGO_HEIGHT}'>"
    )

    st.markdown(f"""
    <style>

        /* Remove padding/margens globais */
        html, body, [data-testid="stAppViewContainer"] {{
            padding: 0 !important;
            margin: 0 !important;
        }}

        /* Some o header nativo do Streamlit */
        [data-testid="stHeader"] {{
            height: 0 !important;
            min-height: 0 !important;
            background: transparent !important;
        }}

        /* ZERA TOTALMENTE padding do bloco principal */
        [data-testid="stMainBlockContainer"],
        .stMainBlockContainer,
        .main .block-container,
        section[data-testid="stMain"] > div.block-container,
        div.stMainBlockContainer.block-container {{
            padding-top: 0 !important;
            padding-right: 0 !important;
            padding-bottom: 0 !important;
            padding-left: 0 !important;
        }}

        @media (min-width: 0px) {{
            [data-testid="stMainBlockContainer"],
            .stMainBlockContainer,
            .main .block-container,
            section[data-testid="stMain"] > div.block-container,
            div.stMainBlockContainer.block-container {{
                padding: 0 !important;
            }}
        }}

        /* Wrapper do login — puxar para cima */
        .login-wrapper {{
            transform: translateY(-{SHIFT_UP_PX}px);
        }}

        .login-logo {{
            display:flex; 
            justify-content:center; 
            margin-bottom: 6px !important;
        }}

        .login-title {{
            font-weight: 800;
            color: {PICMONEY_COLORS['branco']};
            display: flex; 
            align-items: center; 
            justify-content: center;
            gap: 8px; 
            margin-bottom: 10px; 
            font-size: 18px;
        }}

        /* Inputs */
        .login-fields [data-testid="stTextInput"],
        .login-fields [data-testid="stPassword"],
        .login-fields .stTextInput, 
        .login-fields .stPasswordInput {{
            max-width: {FIELD_WIDTH_PX}px;
            margin: 0 auto 12px;
            width: 100%;
        }}

        .login-fields input[type="text"],
        .login-fields input[type="email"],
        .login-fields input[type="password"] {{
            max-width: {FIELD_WIDTH_PX}px;
            width: 100%;
            margin: 0 auto;
        }}

        .login-fields label p, 
        .login-fields label {{
            color: {PICMONEY_COLORS['branco']} !important;
            font-weight: 600 !important;
        }}

        /* Botão */
        .login-submit {{
            width: {FIELD_WIDTH_PX}px !important;
            display: block !important;
            margin: 8px auto 0 !important;
            height: 40px !important;
            font-weight: 800 !important;
            background: {PICMONEY_COLORS['verde']} !important;
            color: {PICMONEY_COLORS['preto']} !important;
            border: none !important;
            border-radius: 10px !important;
        }}

    </style>
    """, unsafe_allow_html=True)

    # ===== Render =====
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="login-logo">{logo_html}</div>', unsafe_allow_html=True)

    left, center, right = st.columns([SIDE_COL, CENTER_COL, SIDE_COL])

    with center:
        warn = st.session_state.pop("login_warning", None)
        if warn:
            st.warning(warn)

        with st.form("form_login", clear_on_submit=False):
            st.markdown('<div class="login-title">🔒 Login</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-fields">', unsafe_allow_html=True)

            email = st.text_input("E-mail", value="", placeholder="seuemail@empresa.com")
            senha = st.text_input("Senha", value="", type="password", placeholder="••••••••")

            st.markdown('</div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("Entrar")

        st.markdown(
            """
            <script>
                const btns = window.parent.document.querySelectorAll('button[kind="primary"]');
                if (btns && btns.length) btns[btns.length-1].classList.add('login-submit');
            </script>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)  # fecha wrapper

    if submitted:
        try:
            api = BackendAPI(base_url)
            data = api.login(email, senha)

            controller = CookieController()
            controller.set('usuario_logado', data)

            st.session_state["usuario_logado"] = data
            st.success(f"Bem-vindo, {data.get('nome', 'usuário')}!")

            try:
                st.switch_page("Main.py")
            except Exception:
                st.rerun()

        except Exception as e:
            msg = str(e)
            if "credenciais_invalidas" in msg or "401" in msg:
                st.error("Usuário não existente ou credenciais inválidas.")
            else:
                st.error(msg)
            st.stop()

    st.stop()


def require_login(base_url: str = None, perfil_obrigatorio: str | None = None, redirect_to: str | None = "pages/Login.py"):
    controller = CookieController()
    usuario = controller.get('usuario_logado')
    if not usuario:
        try:
            current_page = st.context.page_name
        except Exception:
            current_page = None
        go_to_login(base_url, after=current_page)
        st.stop()

    if perfil_obrigatorio and usuario.get("perfil") != perfil_obrigatorio:
        reason = (
            f"Acesso não autorizado. Perfil requerido: {perfil_obrigatorio}. "
            f"Seu perfil: {usuario.get('perfil')}."
        )
        try:
            current_page = st.context.page_name
        except Exception:
            current_page = None

        if redirect_to:
            go_to_login(base_url, reason=reason, after=current_page)
        else:
            _force_logout(base_url)
            render_login_ui(base_url)
        st.stop()

    return usuario


def logout(base_url: str = None):
    _force_logout(base_url)
    try:
        st.switch_page("pages/Login.py")
    except Exception:
        st.rerun()
