from abc import ABC, abstractmethod
import streamlit as st
from typing import Any, Dict, Optional

class BaseComponent(ABC):
    """Base class for all reusable components"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    @abstractmethod
    def render(self) -> Any:
        """Render the component and optionally return a value"""
        pass
    
    def _get_config(self, key: str, default: Any = None) -> Any:
        """Safely get config value"""
        return self.config.get(key, default)