import streamlit as st
import pandas as pd
import mysql.connector

# Esta função usa o cache do Streamlit para não buscar os dados do banco
# toda vez que o usuário interagir com um filtro.
@st.cache_data(ttl=600)  # ttl=600 significa que os dados ficam em cache por 10 minutos
def carregar_dados_mysql(query):
    """
    Função para conectar ao MySQL (usando as credenciais do secrets.toml)
    e retornar um DataFrame pandas.
    """
    try:
        # Pega as credenciais do arquivo secrets.toml
        creds = st.secrets["mysql"]
        
        # Cria a conexão
        conexao = mysql.connector.connect(
            host=creds["host"],
            database=creds["database"],
            port=creds["port"],
            user=creds["user"],
            password=creds["password"]
        )
        
        # Executa a query e carrega em um DataFrame
        df = pd.read_sql(query, conexao)
        
        # Fecha a conexão
        conexao.close()
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao conectar ou buscar dados do MySQL: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

# Exemplo de como você vai chamar essa função nas suas páginas:
#
# from utils.database import carregar_dados_mysql
#
# df_transacoes = carregar_dados_mysql("SELECT * FROM sua_tabela_transacoes")
# df_players = carregar_dados_mysql("SELECT * FROM sua_tabela_players")
#