import streamlit as st
import plotly.express as px
import pandas as pd
from utils.styles import injetar_estilos_globais, injetar_particulas
from utils.database import carregar_dados_mysql
from utils.auth_ui import require_login, logout

COLUNAS_ORDEM = [
    "id_player",
    "celular",
    "idade",
    "genero",
    "dataNascimento",
    "cidade",
    "bairro",
    "nome",
    "email"
]

def chamar_api_backend(endpoint, params=None):
    """
    ⚠️ SUBSTITUA PELA SUA FUNÇÃO REAL DE CHAMADA AO FLASK/BACKEND.
    Esta função deve fazer a requisição HTTP (GET) para o endereço da sua API Flask,
    lidando com autenticação e retornando um dicionário JSON.
    """
    if "hist_idade" in endpoint:
        df_temp = carregar_dados_mysql("SELECT idade, cidade FROM player WHERE idade IS NOT NULL") 
        
        cidades_list = [c.strip() for c in params.get("cidades", "").split(",") if c.strip()]
        if cidades_list:
            df_temp = df_temp[df_temp["cidade"].isin(cidades_list)]
        
        hist_data = df_temp["idade"].value_counts().reset_index()
        hist_data.columns = ['idade', 'quantidade']
        return {"ok": True, "histograma": hist_data.to_dict('records')}
    
    return {"ok": False}

require_login(perfil_obrigatorio="CEO", redirect_to="pages/Login.py")

st.set_page_config(
    page_title="PicMoney Dashboard | Principal",
    page_icon="assets/Logo_PicMoney_SemFundo.png",
    layout="wide"
)

st.markdown("""
<style>
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
st.sidebar.page_link("pages/CEO.py", label="CEO", icon="👑")
st.sidebar.page_link("pages/Chatbot.py", label="Chatbot", icon="🤖")
st.sidebar.markdown("---")

if st.sidebar.button("🚪 Sair da Conta", use_container_width=True):
    logout()

st.title("Painel Executivo: CEO (Chief Executive Officer)")
st.markdown("Visão de performance geral, público e parceiros.")

try:
    df_ceo = carregar_dados_mysql("""
        SELECT id_player, celular, idade, genero, dataNascimento, cidade, bairro, nome, email 
        FROM player
    """)
    if df_ceo.empty:
        st.error("Não foi possível carregar os dados do CEO.")
        st.stop()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

st.sidebar.header("Filtros CEO")
cidades_disponiveis = sorted([c for c in df_ceo["cidade"].dropna().unique()])
cidade_selecionada = st.sidebar.multiselect(
    "Selecione a Cidade",
    options=cidades_disponiveis,
    default=cidades_disponiveis
)

df_filtrado = df_ceo[df_ceo["cidade"].isin(cidade_selecionada)] if cidade_selecionada else df_ceo.copy()
if df_filtrado.empty:
    st.warning("Sem dados para os filtros selecionados.")
    st.stop()

st.header("Análise de Usuários (Players)")

try:
    cidades_param = ",".join(cidade_selecionada)
    params = {"cidades": cidades_param}
    dados_hist_api = chamar_api_backend("/ceo/players/hist_idade", params=params)

    if not dados_hist_api.get("ok") or not dados_hist_api.get("histograma"):
        st.error("Erro ao carregar dados do histograma do Backend.")
        st.stop()

    df_hist = pd.DataFrame(dados_hist_api["histograma"])
    fig_idade = px.bar(
        df_hist,
        x="idade",
        y="quantidade", 
        title="Distribuição de Idade dos Usuários (Calculado no Backend)",
        color_discrete_sequence=['#6bbf30'], 
        template='plotly_dark'
    )
    fig_idade.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_idade, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao consultar o backend ou gerar gráfico: {e}")
    st.warning("Verifique se o servidor Flask está rodando e se a função 'chamar_api_backend' está correta.")
    st.stop()

st.dataframe(df_filtrado[COLUNAS_ORDEM], use_container_width=True)
