from components.base import BaseComponent
import streamlit as st
import plotly.express as px
from utils.styles import PICMONEY_COLORS

# components/charts/pie_chart.py
class PieChart(BaseComponent):
    """Reusable pie chart with PicMoney styling"""
    
    def __init__(self, data, names: str, values: str, title: str):
        super().__init__(data=data, names=names, values=values, title=title)
    
    def render(self):
        fig = px.pie(
            self._get_config('data'),
            names=self._get_config('names'),
            values=self._get_config('values'),
            title=self._get_config('title'),
            color_discrete_sequence=[
                PICMONEY_COLORS['verde'],
                PICMONEY_COLORS['amarelo'],
                PICMONEY_COLORS['azul'],
                PICMONEY_COLORS['branco']
            ],
            template='plotly_dark'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=PICMONEY_COLORS['branco']
        )
        st.plotly_chart(fig, use_container_width=True)