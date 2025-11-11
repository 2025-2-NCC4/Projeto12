from components.base import BaseComponent
import streamlit as st
from utils.styles import PICMONEY_COLORS

class InfoCard(BaseComponent):
    """Info card using custom-info-box CSS"""
    
    def __init__(self, content: str):
        super().__init__(content=content)
    
    def render(self):
        content = self._get_config('content')
        st.markdown(f"""
        <div class="custom-info-box">
            {content}
        </div>
        """, unsafe_allow_html=True)