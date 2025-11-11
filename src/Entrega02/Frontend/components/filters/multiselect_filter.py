from components.base import BaseComponent
import streamlit as st
from typing import List

class MultiSelectWithAllFilter(BaseComponent):
    """Multi-select filter with 'Select All' checkbox that actually works"""
    
    def __init__(self, label: str, options: List, key: str, icon: str = "🔍"):
        super().__init__(
            label=label,
            options=options,
            key=key,
            icon=icon
        )
    
    def render(self) -> List:
        """Render multiselect with select all checkbox"""
        st.sidebar.markdown("---")
        
        options = self._get_config('options')
        key = self._get_config('key')
        select_all_key = f"{key}_select_all"
        multiselect_key = f"{key}_multiselect"
        
        # Initialize session state
        if multiselect_key not in st.session_state:
            st.session_state[multiselect_key] = []
        
        # Select all checkbox
        select_all = st.sidebar.checkbox(
            f"Selecionar Todas as {self._get_config('label')}",
            key=select_all_key
        )
        
        # Update multiselect based on checkbox
        if select_all:
            current_selection = options
        else:
            current_selection = st.session_state[multiselect_key]
        
        # Multiselect
        selected = st.sidebar.multiselect(
            f"{self._get_config('icon')} {self._get_config('label')}",
            options=options,
            default=current_selection,
            key=multiselect_key,
            disabled=select_all  # Disable when "select all" is checked
        )
        
        # If select_all is checked, return all options
        if select_all:
            return options
        
        return selected