from components.base import BaseComponent
import streamlit as st
from typing import List

class CityMultiSelectFilter(BaseComponent):
    """City multiselect filter with all cities selected by default"""
    
    def __init__(self, cities: List[str], key: str = "city_filter", label: str = "Selecione a Cidade", icon: str = "🏙️"):
        super().__init__(
            cities=sorted(cities),
            key=key,
            label=label,
            icon=icon
        )
    
    def render(self) -> List[str]:
        """Render city multiselect filter"""
        cities = self._get_config('cities')
        
        selected = st.sidebar.multiselect(
            f"{self._get_config('icon')} {self._get_config('label')}",
            options=cities,
            default=cities,  # All cities selected by default
            key=self._get_config('key')
        )
        
        return selected