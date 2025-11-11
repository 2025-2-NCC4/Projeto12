from components.base import BaseComponent
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple

class SliderFilter(BaseComponent):
    """Slider filter for sidebar"""
    
    def __init__(self, label: str, min_val: float, max_val: float, key: str, 
                 default: tuple = None, icon: str = "📊", step: float = None):
        super().__init__(
            label=label, min_val=min_val, max_val=max_val, 
            key=key, default=default, icon=icon, step=step
        )
    
    def render(self) -> tuple:
        st.sidebar.subheader(f"{self._get_config('icon')} {self._get_config('label')}")
        default = self._get_config('default') or (self._get_config('min_val'), self._get_config('max_val'))
        
        value = st.sidebar.slider(
            "Faixa:",
            min_value=self._get_config('min_val'),
            max_value=self._get_config('max_val'),
            value=default,
            step=self._get_config('step'),
            key=self._get_config('key')
        )
        return value