import streamlit as st
import plotly.express as px
import pandas as pd
from utils.styles import injetar_estilos_globais, injetar_particulas, PICMONEY_COLORS # [CORREÇÃO] Importei a paleta
from utils.database import carregar_dados_mysql
import base64
import os

# --- Função de carregar vídeo (sempre necessária) ---
def get_video_as_base64(path):
    if not os.path.exists(path):
        st.error(f"Arquivo de vídeo não encontrado em: {path}")
        return None
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Erro ao ler o arquivo de vídeo: {e}")
        return None

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="PicMoney Dashboard | Principal",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide"
)

st.sidebar.image("assets/Logo_PicMoney_SemFundo.png", width=200)

# --- 2. Injetar Estilos e Partículas ---
injetar_estilos_globais()
injetar_particulas()

# --- 3. Carregar os Dados ---
try:
    # [CORREÇÃO] Puxei também o ID do player e do cupom para calcularmos os KPIs
    df_transacoes = carregar_dados_mysql("SELECT valor_transacao, data_hora_transacao, id_player_fk, id_cupom_fk FROM transacao")
    
    if df_transacoes.empty:
        st.error("Não foi possível carregar os dados das transações. Verifique a conexão e a query.")
        st.stop()
        
except Exception as e:
    st.error(f"Erro fatal ao carregar dados: {e}")
    st.stop()

# --- 4. Vídeo Hero Full-Width (Sem Overlay) ---
VIDEO_PATH = "assets/video_formato2.mp4" 
video_base64 = get_video_as_base64(VIDEO_PATH)

if video_base64:
    video_html = f"""
    <style>
    .hero-video-container {{
        position: relative;
        width: 100%;
        height: 500px; /* <<< AJUSTE A ALTURA DO VÍDEO AQUI */
        overflow: hidden;
    }}
    
    .hero-video-container video {{
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100%;
        height: 100%;
        object-fit: cover; 
        transform: translate(-50%, -50%);
    }}
    </style>
    
    <div class="hero-video-container">
        <video autoplay loop muted playsinline>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
    </div>
    """
    st.components.v1.html(video_html, height=500)
else:
    st.warning("O vídeo de cabeçalho não pôde ser carregado.")


# --- 5. Wrapper de Conteúdo ---
st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)

# --- 6. Título ---
st.title("Dashboard Estratégico PicMoney")
st.markdown("Visão consolidada dos principais indicadores (CEO e CFO)")
st.markdown("---")

# --- 5. KPIs Principais (AGORA COM DADOS REAIS) ---
st.header("⚡ Resumo Executivo")

# [CORREÇÃO] Cálculos reais usando os dados do banco
total_receita = df_transacoes['valor_transacao'].sum()
total_cupons = df_transacoes['id_cupom_fk'].count() # Conta o número de transações/cupons
usuarios_ativos = df_transacoes['id_player_fk'].nunique() # Conta o número de players únicos

if total_cupons > 0:
    ticket_medio = total_receita / total_cupons
else:
    ticket_medio = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Receita Total (GMV)</div>
            <div class="kpi-value">R$ {total_receita:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Cupons Capturados</div>
            <div class="kpi-value">{total_cupons:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Ticket Médio</div>
            <div class="kpi-value">R$ {ticket_medio:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Usuários Ativos</div>
            <div class="kpi-value">{usuarios_ativos:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True) # Adiciona um espaço

# --- 6. Gráficos Principais ---
st.header("📈 Gráficos Resumidos")

try:
    # Garante que a coluna de data é do tipo datetime
    df_transacoes['data_hora_transacao'] = pd.to_datetime(df_transacoes['data_hora_transacao'])
    
    # Agrupa a receita por dia
    receita_diaria = df_transacoes.groupby(
        df_transacoes['data_hora_transacao'].dt.date
    )['valor_transacao'].sum().reset_index()

    # [CORREÇÃO] Corrigi os nomes das colunas 'x' e 'y' e as 'labels'
    fig_receita = px.line(
        receita_diaria,
        x='data_hora_transacao',  # [CORREÇÃO] Estava 'data_transacao'
        y='valor_transacao',    # [CORREÇÃO] Estava 'valor_cupom'
        title='Receita Total (GMV) ao Longo do Tempo',
        labels={'data_hora_transacao': 'Data', 'valor_transacao': 'Receita (R$)'}, # [CORREÇÃO]
        template='plotly_dark' 
    )    # Customiza o gráfico com as cores da PicMoney
    fig_receita.update_traces(
        line=dict(color=PICMONEY_COLORS['verde'], width=3)
    )
    fig_receita.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        title_font_color=PICMONEY_COLORS['verde'],
        font_color=PICMONEY_COLORS['branco']
    )

    st.plotly_chart(fig_receita, use_container_width=True)

except KeyError as e: # [CORREÇÃO] Mudei a captura do erro
    st.warning(f"Erro ao gerar gráfico. A coluna {e} não foi encontrada. Verifique sua query SQL.")
except Exception as e:
    st.error(f"Erro inesperado ao gerar gráfico: {e}")

# --- 9. Fechamento do Wrapper ---
st.markdown('</div>', unsafe_allow_html=True)