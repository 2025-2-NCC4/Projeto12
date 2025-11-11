from abc import ABC, abstractmethod
import streamlit as st
import pandas as pd
from typing import Optional

class BasePage(ABC):
    """Base class for all pages with tab navigation"""
    
    def __init__(self, title: str, icon: str = "📊"):
        self.title = title
        self.icon = icon
        self.filters = {}
    
    @abstractmethod
    def render_filters(self):
        """Render sidebar filters specific to this page"""
        pass
    
    @abstractmethod
    def render_content(self):
        """Render main page content"""
        pass
    
    def render(self):
        """Main render method called from Main.py"""
        self.render_content()
    
    def apply_filters(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to dataframe - override in subclass if needed"""
        return data
    
    def _render_section_header(self, title: str, icon: str = ""):
        """Helper to render consistent section headers"""
        st.header(f"{icon} {title}" if icon else title)
        st.markdown("---")