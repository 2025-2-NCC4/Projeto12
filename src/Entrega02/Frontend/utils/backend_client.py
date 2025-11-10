import requests
import streamlit as st

DEFAULT_BASE_URL = "http://localhost:5000"  

class BackendAPI:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        if "backend_session" not in st.session_state:
            st.session_state.backend_session = requests.Session()
        self.s = st.session_state.backend_session

    def login(self, email: str, senha: str):
        r = self.s.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "senha": senha},
            timeout=15
        )
        if not r.ok or not r.json().get("ok"):
            raise RuntimeError(f"Falha no login: {r.status_code}  {r.text}")
        return r.json()

    def logout(self):
        try:
            self.s.post(f"{self.base_url}/api/auth/logout", timeout=10)
        finally:
            st.session_state.pop("backend_session", None)
            st.session_state.pop("usuario_logado", None)

    def get(self, path: str, **kwargs):
        """GET com timeout opcional (padrão 60s)."""
 
        return self.s.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path: str, json=None, **kwargs):
        """POST com timeout opcional (padrão 60s)."""
        
        return self.s.post(f"{self.base_url}{path}", json=json, **kwargs)
