# utils/database.py
import streamlit as st
import pandas as pd
from .backend_client import BackendAPI

@st.cache_data(ttl=600)
def carregar_dados_mysql(query: str) -> pd.DataFrame:
    """
    Encaminha a query para o backend Flask (/api/query),
    usando a sessão autenticada (cookies do Flask-Login).
    """
    try:
        api = BackendAPI()  
        resp = api.post("/api/query", json={"sql": query})
        data = resp.json() if resp.ok else {}
        if not data or not data.get("ok"):
            msg = data.get("error", f"http_{resp.status_code}")
            st.error(f"Falha ao consultar o backend: {msg}")
            return pd.DataFrame()
        return pd.DataFrame(data.get("rows", []))
    except Exception as e:
        st.error(f"Erro ao consultar o backend: {e}")
        return pd.DataFrame()
