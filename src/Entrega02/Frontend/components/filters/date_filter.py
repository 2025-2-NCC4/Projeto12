from components.base import BaseComponent
import streamlit as st
import pandas as pd
from typing import Tuple, Optional
from datetime import date

class DateRangeFilter(BaseComponent):
    """Date range filter for sidebar with min/max constraints"""
    
    def __init__(self, key: str, min_date: str = None, max_date: str = None, label: str = "📅 Período"):
        # Convert string dates to date objects
        min_date_obj = pd.to_datetime(min_date).date() if min_date else None
        max_date_obj = pd.to_datetime(max_date).date() if max_date else None
        
        super().__init__(
            key=key,
            min_date=min_date_obj,
            max_date=max_date_obj,
            label=label
        )
    
    def render(self) -> Tuple[Optional[date], Optional[date]]:
        """Render date range inputs and return selected dates"""
        st.sidebar.subheader(self._get_config('label'))
        
        min_date = self._get_config('min_date')
        max_date = self._get_config('max_date')
        
        # Start date
        data_inicio = st.sidebar.date_input(
            "Data Início",
            value=None,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            key=f"{self._get_config('key')}_start"
        )
        
        # End date
        data_fim = st.sidebar.date_input(
            "Data Fim",
            value=None,
            min_value=data_inicio if data_inicio else min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            key=f"{self._get_config('key')}_end"
        )
        
        return data_inicio, data_fim