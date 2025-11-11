from components.base import BaseComponent
import streamlit as st
import plotly.express as px
from utils.styles import PICMONEY_COLORS

class BarChart(BaseComponent):
    """Reusable bar chart with PicMoney styling"""
    
    def __init__(self, data, x: str, y: str, title: str, color: str = None):
        super().__init__(data=data, x=x, y=y, title=title, color=color or PICMONEY_COLORS['verde'])
    
    def render(self):
        fig = px.bar(
            self._get_config('data'),
            x=self._get_config('x'),
            y=self._get_config('y'),
            title=self._get_config('title'),
            color_discrete_sequence=[self._get_config('color')],
            template='plotly_dark'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font_color=self._get_config('color'),
            font_color=PICMONEY_COLORS['branco']
        )
        st.plotly_chart(fig, width='stretch')
