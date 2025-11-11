from components.base import BaseComponent
import streamlit as st
from utils.styles import PICMONEY_COLORS

class KPICard(BaseComponent):
    """KPI Card matching your existing CSS styles"""
    
    def __init__(self, title: str, value: str, delta: str = None, delta_positive: bool = True):
        super().__init__(title=title, value=value, delta=delta, delta_positive=delta_positive)
    
    def render(self):
        """Render KPI card using your existing .kpi-card CSS"""
        title = self._get_config('title')
        value = self._get_config('value')
        delta = self._get_config('delta')
        delta_positive = self._get_config('delta_positive', True)
        
        delta_html = ""
        if delta:
            delta_class = "kpi-delta-pos" if delta_positive else "kpi-delta-neg"
            delta_html = f'<div class="{delta_class}">{delta}</div>'
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)