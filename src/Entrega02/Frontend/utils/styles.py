import streamlit as st

# Paleta de Cores da PicMoney (baseada no logo)
PICMONEY_COLORS = {
    "preto": "#000000",
    "azul": "#00333a",
    "verde": "#7FFF00",
    "amarelo": "#FFFF00",
    "branco": "#FFFFFF"
}

def injetar_estilos_globais():
    """
    Injeta o CSS customizado para o app.
    Isso muda a aparência de fontes, remove o "Made with Streamlit", etc.
    """
    # Esta linha (18) deve ter 4 espaços no começo.
    css = """
    <style>
        /* --- Fonte 'Raleway' --- */
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;700;800&display=swap');
        
        html, body, [class*="st-"], .stApp {
            font-family: 'Raleway', sans-serif; /* Fonte aplicada */
        }
        /* --- Fim da Mudança de Fonte --- */


        /* --- Títulos --- */
        h1, h2, h3 { font-weight: 800; }
        h1 { color: %(verde)s; }
        h2 { color: %(amarelo)s; }

        /* --- Remover o "Made with Streamlit" do rodapé --- */
        footer, .stApp footer { visibility: hidden; }
        
        /* --- Barra Lateral (Sidebar) --- */
        [data-testid="stSidebar"] {
            background-color: %(preto)s;
            border-right: 1px solid %(azul)s;
        }
        
        /* --- Botões e Widgets --- */
        [data-testid="stButton"] button {
            background-color: %(verde)s;
            color: %(preto)s;
            font-weight: 700;
            border-radius: 8px;
            border: none;
        }
        [data-testid="stButton"] button:hover {
            background-color: %(amarelo)s;
            color: %(preto)s;
        }

        /* --- Cartões de KPI --- */
        .kpi-card {
            background-color: %(azul)s;
            border: 1px solid #2a4a55;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        .kpi-title {
            font-size: 16px;
            color: %(branco)s;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 32px;
            color: %(verde)s;
            font-weight: 800;
        }
        .kpi-delta-pos { color: #4CAF50; font-size: 14px; font-weight: 600; }
        .kpi-delta-neg { color: #F44336; font-size: 14px; font-weight: 600; }


        /* --- Hack para Forçar a Logo Acima da Navegação --- */
        [data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
        }
        [data-testid="stSidebarUserContent"] { order: 1; }
        [data-testid="stSidebarNav"] { order: 2; }
        [data-testid="stSidebarUserContent"] img { border-radius: 10px; }


        /* --- CSS "Hero Video" --- */
        [data-testid="stHeader"] {
            display: none;
            visibility: hidden;
        }
        .stApp > div {
            padding-top: 0 !important;
        }
        [data-testid="block-container"] {
            padding: 0 !important;
            margin: 0 !important;
            width: 100%% !important; /* <<< [A CORREÇÃO ESTÁ AQUI] */
            max-width: none !important;
        }
        .main-content-wrapper {
            padding: 2rem 5rem 5rem 5rem;
        }
        
    </style> 
    """ % PICMONEY_COLORS  # Formata o CSS com as cores
    
    st.markdown(css, unsafe_allow_html=True)

def injetar_particulas():
    """
    Injeta o script do particles.js para o efeito de "movimento" no fundo.
    """
    # URL do script particles.js
    particles_js_url = "https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"
    
    # Configuração do JSON para as partículas
    particles_json_config = """
    {
      "particles": {
        "number": { "value": 80, "density": { "enable": true, "value_area": 800 } },
        "color": { "value": ["%(verde)s", "%(amarelo)s"] },
        "shape": { "type": "circle" },
        "opacity": { "value": 0.6, "random": true, "anim": { "enable": true, "speed": 1, "opacity_min": 0.1, "sync": false } },
        "size": { "value": 3, "random": true, "anim": { "enable": false } },
        "line_linked": { "enable": false },
        "move": { "enable": true, "speed": 1, "direction": "none", "random": true, "straight": false, "out_mode": "out", "bounce": false }
      },
      "interactivity": { "detect_on": "canvas", "events": { "onhover": { "enable": false }, "onclick": { "enable": false } } },
      "retina_detect": true
    }
    """ % PICMONEY_COLORS # Injeta as cores da paleta no JSON
    
    # O HTML que será injetado
    particles_html = f"""
    <div id="particles-js" style="position: fixed; width: 100%; height: 100%; top: 0; left: 0; z-index: -1;"></div>
    <script src="{particles_js_url}"></script>
    <script type"text/javascript">
        document.addEventListener('DOMContentLoaded', (event) => {{
            particlesJS('particles-js', {particles_json_config});
        }});
    </script>
    """
    
    st.components.v1.html(particles_html, height=0)