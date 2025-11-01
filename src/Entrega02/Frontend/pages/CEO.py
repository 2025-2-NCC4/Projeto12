import streamlit as st
import plotly.express as px
from utils.styles import injetar_estilos_globais
from utils.database import carregar_dados_mysql

# --- Configuração da Página ---
st.set_page_config(
    page_title="PicMoney Dashboard | CEO",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide"
)

st.sidebar.image("assets/Logo_PicMoney_SemFundo.png", width=200)

# --- Injetar Estilos ---
# (Não precisamos das partículas aqui, só na Home, mas o CSS sim)
injetar_estilos_globais()

# --- Título ---
st.title("Painel Executivo: CEO (Chief Executive Officer)")
st.markdown("Visão de performance geral, público e parceiros.")

# --- Carregar Dados ---
# (Busque apenas os dados que o CEO precisa)
try:
    df_ceo = carregar_dados_mysql("SELECT * FROM sua_tabela_players LIMIT 100") # Query de exemplo
    if df_ceo.empty:
        st.error("Não foi possível carregar os dados do CEO.")
        st.stop()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()
    
# --- Filtros (Exemplo na Barra Lateral) ---
st.sidebar.header("Filtros CEO")
cidade_selecionada = st.sidebar.multiselect(
    "Selecione a Cidade",
    options=df_ceo["cidade_residencial"].unique(),
    default=df_ceo["cidade_residencial"].unique()
)

# Filtra o DataFrame
df_filtrado = df_ceo[df_ceo["cidade_residencial"].isin(cidade_selecionada)]

# --- Conteúdo da Página ---
st.header("Análise de Usuários (Players)")

# Gráfico de exemplo
fig_idade = px.histogram(
    df_filtrado,
    x="idade",
    title="Distribuição de Idade dos Usuários",
    color_discrete_sequence=['#6bbf30'], # Verde PicMoney
    template='plotly_dark'
)
fig_idade.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

st.plotly_chart(fig_idade, use_container_width=True)

st.dataframe(df_filtrado) # Mostra os dados filtrados