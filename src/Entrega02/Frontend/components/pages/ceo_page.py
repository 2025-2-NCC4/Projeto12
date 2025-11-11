import streamlit as st
import pandas as pd
import plotly.express as px

from components.pages.base_page import BasePage
from components.cards.kpi_card import KPICard
from components.filters.city_filter import CityMultiSelectFilter
from utils.styles import PICMONEY_COLORS
from utils.database import carregar_dados_mysql
from utils.backend_client import BackendAPI


class CEOPage(BasePage):
    """CEO Dashboard - User analytics and business metrics"""
    
    # Column order for player data table
    COLUNAS_ORDEM = [
        "id_player",
        "celular",
        "idade",
        "genero",
        "dataNascimento",
        "cidade",
        "bairro",
        "nome",
        "email"
    ]
    
    def __init__(self):
        super().__init__("Dashboard CEO", "👔")
        self.api = BackendAPI()
        self.df_ceo = None
        self.city_filter = None
        self._load_data()
    
    def _load_data(self):
        """Load CEO data from database"""
        try:
            self.df_ceo = carregar_dados_mysql("""
                SELECT id_player, celular, idade, genero, dataNascimento, 
                       cidade, bairro, nome, email 
                FROM player
            """)
            
            if self.df_ceo.empty:
                st.error("Não foi possível carregar os dados do CEO.")
                st.stop()
            
            # Initialize city filter with available cities
            cidades_disponiveis = [
                c for c in self.df_ceo["cidade"].dropna().unique()
            ]
            
            self.city_filter = CityMultiSelectFilter(
                cities=cidades_disponiveis,
                key="ceo_city_filter",
                label="Selecione a Cidade",
                icon="🏙️"
            )
            
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            st.stop()
    
    def render_filters(self):
        """Render CEO-specific filters in sidebar"""
        st.sidebar.markdown("## 🎯 Filtros CEO")
        
        if self.city_filter:
            cidade_selecionada = self.city_filter.render()
            self.filters['cidades'] = cidade_selecionada
        
        st.sidebar.markdown("---")
    
    def apply_filters(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply CEO filters to dataframe"""
        filtered = data.copy()
        
        if 'cidades' in self.filters and self.filters['cidades']:
            filtered = filtered[filtered['cidade'].isin(self.filters['cidades'])]
        
        return filtered
    
    def render_content(self):
        """Render CEO dashboard content"""
        self._render_section_header("Painel Executivo: CEO", "👔")
        st.markdown("Visão de performance geral, público e parceiros.")
        st.markdown("---")
        
        # Apply filters
        df_filtrado = self.apply_filters(self.df_ceo)
        
        if df_filtrado.empty:
            st.warning("Sem dados para os filtros selecionados.")
            return
        
        # Render sections
        self._render_user_analysis(df_filtrado)
        st.markdown("---")
        self._render_player_table(df_filtrado)
    
    def _render_user_analysis(self, df_filtrado: pd.DataFrame):
        """Render user analysis section with age distribution"""
        st.header("Análise de Usuários (Players)")
        
        try:
            # Get selected cities for API call
            cidades_param = ",".join(self.filters.get('cidades', []))
            params = {"cidades": cidades_param}
            
            # Call backend API for age histogram
            response = self.api.get("/ceo/players/hist_idade", params=params, timeout=30)
            dados_hist_api = response.json() if response.ok else {}
            
            if not dados_hist_api.get("ok") or not dados_hist_api.get("histograma"):
                st.error("Erro ao carregar dados do histograma do Backend.")
                # Fallback: calculate locally
                self._render_age_histogram_local(df_filtrado)
                return
            
            # Render histogram from backend data
            df_hist = pd.DataFrame(dados_hist_api["histograma"])
            self._render_age_histogram(df_hist)
            
        except Exception as e:
            st.error(f"Erro ao consultar o backend: {e}")
            st.warning("Calculando histograma localmente...")
            # Fallback: calculate locally
            self._render_age_histogram_local(df_filtrado)
    
    def _render_age_histogram(self, df_hist: pd.DataFrame):
        """Render age histogram chart from backend data"""
        fig_idade = px.bar(
            df_hist,
            x="idade",
            y="quantidade",
            title="Distribuição de Idade dos Usuários (Calculado no Backend)",
            color_discrete_sequence=[PICMONEY_COLORS['verde']],
            template='plotly_dark',
            labels={'idade': 'Idade', 'quantidade': 'Quantidade de Usuários'}
        )
        fig_idade.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font_color=PICMONEY_COLORS['verde'],
            font_color=PICMONEY_COLORS['branco']
        )
        st.plotly_chart(fig_idade, use_container_width=True)
    
    def _render_age_histogram_local(self, df_filtrado: pd.DataFrame):
        """Fallback: Render age histogram from local data"""
        df_idade = df_filtrado[df_filtrado['idade'].notna()]
        
        if df_idade.empty:
            st.info("Sem dados de idade disponíveis.")
            return
        
        hist_data = df_idade['idade'].value_counts().reset_index()
        hist_data.columns = ['idade', 'quantidade']
        hist_data = hist_data.sort_values('idade')
        
        fig_idade = px.bar(
            hist_data,
            x="idade",
            y="quantidade",
            title="Distribuição de Idade dos Usuários",
            color_discrete_sequence=[PICMONEY_COLORS['verde']],
            template='plotly_dark',
            labels={'idade': 'Idade', 'quantidade': 'Quantidade de Usuários'}
        )
        fig_idade.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font_color=PICMONEY_COLORS['verde'],
            font_color=PICMONEY_COLORS['branco']
        )
        st.plotly_chart(fig_idade, use_container_width=True)
    
    def _render_player_table(self, df_filtrado: pd.DataFrame):
        """Render player data table"""
        st.header("📋 Dados dos Usuários")
        
        # Show summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            KPICard(
                "Total de Usuários",
                f"{len(df_filtrado):,}"
            ).render()
        
        with col2:
            idade_media = df_filtrado['idade'].mean() if 'idade' in df_filtrado.columns else 0
            KPICard(
                "Idade Média",
                f"{idade_media:.1f} anos"
            ).render()
        
        with col3:
            cidades_unicas = df_filtrado['cidade'].nunique() if 'cidade' in df_filtrado.columns else 0
            KPICard(
                "Cidades",
                f"{cidades_unicas}"
            ).render()
        
        with col4:
            bairros_unicos = df_filtrado['bairro'].nunique() if 'bairro' in df_filtrado.columns else 0
            KPICard(
                "Bairros",
                f"{bairros_unicos}"
            ).render()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display table with ordered columns
        available_columns = [col for col in self.COLUNAS_ORDEM if col in df_filtrado.columns]
        st.dataframe(
            df_filtrado[available_columns],
            use_container_width=True,
            height=400
        )