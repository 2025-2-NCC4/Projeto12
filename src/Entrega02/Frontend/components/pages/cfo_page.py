import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from unidecode import unidecode

from components.pages.base_page import BasePage
from components.cards.kpi_card import KPICard
from components.charts.line_chart import LineChart
from components.filters.date_filter import DateRangeFilter
from components.filters.multiselect_filter import MultiSelectWithAllFilter
from utils.styles import PICMONEY_COLORS
from utils.backend_client import BackendAPI


class CFOPage(BasePage):
    """CFO Dashboard - Financial metrics and analysis"""
    
    def __init__(self):
        super().__init__("Dashboard CFO", "💼")
        self.api = BackendAPI()
        
        # Filter components (will be initialized after loading filter data)
        self.date_filter = None
        self.category_filter = None
        self.bairro_filter = None
        
        # Filter data from backend
        self.filter_data = {}
        self.data = {}
        
    def _load_filter_options(self):
        """Load filter options from backend"""
        with st.spinner("Carregando filtros..."):
            r = self.api.get("/api/cfo/filters", timeout=60)
            fdata = r.json() if r.ok else {}
            
            if not fdata.get("ok"):
                st.error("Não foi possível carregar filtros do CFO.")
                st.stop()
            
            self.filter_data = fdata
            
            # Initialize filter components
            self.date_filter = DateRangeFilter(
                key="cfo_dates",
                min_date=fdata.get("min_date"),
                max_date=fdata.get("max_date"),
                label="📅 Período Financeiro"
            )
            
            self.category_filter = MultiSelectWithAllFilter(
                label="Categorias",
                options=fdata.get("categorias", []),
                key="cfo_categories",
                icon="🏪"
            )
            
            self.bairro_filter = MultiSelectWithAllFilter(
                label="Bairros",
                options=fdata.get("bairros", []),
                key="cfo_bairros",
                icon="📍"
            )
    
    def render_filters(self):
        """Render CFO-specific filters in sidebar"""
        # Load filter options first
        if not self.filter_data:
            self._load_filter_options()
        
        st.sidebar.markdown("## 💰 Filtros Financeiros")
        
        # Date range filter
        data_inicio, data_fim = self.date_filter.render()
        self.filters['date_start'] = data_inicio
        self.filters['date_end'] = data_fim
        
        # Category filter
        categorias_sel = self.category_filter.render()
        self.filters['categorias'] = categorias_sel
        
        # Bairro filter
        bairros_sel = self.bairro_filter.render()
        self.filters['bairros'] = bairros_sel
        
        st.sidebar.markdown("---")
    
    def _validate_filters(self) -> bool:
        """Check if all required filters are selected"""
        return (
            self.filters.get('date_start') and
            self.filters.get('date_end') and
            self.filters.get('categorias') and
            self.filters.get('bairros')
        )
    
    def _load_data(self):
        """Load CFO data from backend with current filters"""
        payload = {
            "from": str(self.filters['date_start']),
            "to": str(self.filters['date_end']),
            "categorias": self.filters['categorias'],
            "bairros": self.filters['bairros']
        }
        
        with st.spinner("Calculando indicadores financeiros..."):
            r = self.api.post("/api/cfo/data", json=payload, timeout=1000)
            data = r.json() if r.ok else {}
            
            if not data.get("ok"):
                st.error("Não foi possível carregar os dados financeiros.")
                st.stop()
            
            self.data = data
    
    def render_content(self):
        """Render CFO dashboard content"""
        self._render_section_header("Painel Financeiro: CFO", "💼")
        st.markdown(f"""
            <p style='color: {PICMONEY_COLORS["branco"]};'>
                Visão detalhada da saúde financeira, receitas e margens. 
            </p>
        """, unsafe_allow_html=True)
        
        # Validate filters
        if not self._validate_filters():
            st.markdown("""
                <div class="custom-info-box">
                    ⬅️ Por favor, selecione o período, categoria e bairro no filtro lateral para começar.
                </div>
            """, unsafe_allow_html=True)
            return
        
        # Load data with filters
        self._load_data()
        
        # Render sections
        self._render_kpis()
        st.markdown("<br>", unsafe_allow_html=True)
        self._render_receita_timeline()
        st.markdown("---")
        self._render_rentabilidade_analysis()
        st.markdown("---")
        self._render_risk_analysis()
        st.markdown("---")
        self._render_bairro_map()
    
    def _render_kpis(self):
        """Render financial KPI cards"""
        st.header("Indicadores Chave de Performance")
        
        k = self.data.get("kpis", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            KPICard(
                "Receita Líquida",
                self._brl(k.get("receita_liquida", 0))
            ).render()
        
        with col2:
            KPICard(
                "Margem Operacional",
                f"{k.get('margem_operacional', 0):,.2f} %"
            ).render()
        
        with col3:
            KPICard(
                "Ticket Médio",
                self._brl(k.get("ticket_medio", 0))
            ).render()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col4, col5 = st.columns(2)
        with col4:
            KPICard(
                "Valor Médio do Repasse (R$)",
                self._brl(k.get("valor_medio_repasse", 0))
            ).render()
        
        with col5:
            KPICard(
                "Receita Bruta (GMV)",
                self._brl(k.get("gmv", 0))
            ).render()
    
    def _render_receita_timeline(self):
        """Render revenue over time chart"""
        st.header("Receita Líquida por Período")
        
        df_receita_dia = pd.DataFrame(self.data.get("receita_diaria", []))
        
        if not df_receita_dia.empty:
            df_receita_dia['data'] = pd.to_datetime(df_receita_dia['data'])
            
            fig_linha = px.line(
                df_receita_dia,
                x='data',
                y='valor_repasse',
                labels={'data': 'Data', 'valor_repasse': 'Receita (R$) P/ Dia'},
                template='plotly_dark'
            )
            fig_linha.update_traces(line=dict(color=PICMONEY_COLORS['verde'], width=3))
            fig_linha.update_xaxes(tickformat="%d/%m/%Y")
            fig_linha.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.info("Sem dados para o período selecionado.")
    
    def _render_rentabilidade_analysis(self):
        """Render profitability analysis charts"""
        st.header("Análise de Rentabilidade (Cupom e Categoria)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Receita Líquida por Tipo de Cupom")
            df_cupom = pd.DataFrame(self.data.get("receita_por_cupom", []))
            
            if not df_cupom.empty:
                fig_barra = px.bar(
                    df_cupom,
                    x='tipo_cupom',
                    y='valor_repasse',
                    labels={'tipo_cupom': 'Tipo de Cupom', 'valor_repasse': 'Receita (R$) Acumulada'},
                    template='plotly_dark',
                    color='tipo_cupom',
                    color_discrete_map={
                        'Desconto': PICMONEY_COLORS['verde'],
                        'Cashback': PICMONEY_COLORS['amarelo'],
                        'Produto': PICMONEY_COLORS['branco']
                    }
                )
                fig_barra.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(fig_barra, use_container_width=True)
            else:
                st.info("Sem dados por tipo de cupom.")
        
        with col2:
            st.subheader("Receita Líquida vs. GMV por Categoria")
            df_cat = pd.DataFrame(self.data.get("por_categoria", []))
            
            if not df_cat.empty:
                fig_scatter = px.scatter(
                    df_cat,
                    x='gmv',
                    y='receita_liquida',
                    color='margem',
                    size='num_transacoes',
                    hover_name='categoria_parceiro',
                    hover_data={'num_transacoes': True, 'margem': ':.2f'},
                    labels={
                        'receita_liquida': 'Receita Líquida (R$)',
                        'gmv': 'GMV (R$)',
                        'margem': 'Margem (%)',
                        'num_transacoes': 'Transações'
                    },
                    template='plotly_dark',
                    color_continuous_scale=px.colors.sequential.YlGn,
                    size_max=50
                )
                fig_scatter.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    hovermode='closest'
                )
                fig_scatter.update_xaxes(title_text='GMV Total da Categoria (R$)')
                fig_scatter.update_yaxes(title_text='Receita PicMoney (R$)')
                
                # Trend line
                fig_scatter.add_scatter(
                    x=df_cat['gmv'],
                    y=df_cat['receita_liquida'],
                    mode='lines',
                    name='Tendência',
                    line=dict(color=PICMONEY_COLORS['verde'], width=2, dash='dash'),
                    opacity=0.5
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Sem dados por categoria.")
    
    def _render_risk_analysis(self):
        """Render risk and efficiency analysis"""
        st.header("Análise de Risco e Eficiência")
        st.subheader("Risco de Concentração (Top 5 Parceiros)")
        
        df_parc = pd.DataFrame(self.data.get("top_parceiros", []))
        
        if not df_parc.empty:
            fig_parc = px.bar(
                df_parc.sort_values(by='valor_repasse', ascending=True),
                x='valor_repasse',
                y='nome_parceiro',
                orientation='h',
                labels={'nome_parceiro': 'Parceiro', 'valor_repasse': 'Receita Líquida'},
                template='plotly_dark',
                color='valor_repasse',
                color_continuous_scale=px.colors.sequential.YlGn
            )
            fig_parc.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False,
                margin=dict(t=30, l=10, r=10, b=10)
            )
            fig_parc.update_yaxes(title_text="")
            st.plotly_chart(fig_parc, use_container_width=True)
        else:
            st.info("Sem dados de parceiros.")
    
    def _render_bairro_map(self):
        """Render neighborhood revenue map"""
        st.subheader("Receita Líquida por Bairro")
        
        df_bairro = pd.DataFrame(self.data.get("por_bairro", []))
        stats = self.data.get("stats_bairro", {})
        
        if not df_bairro.empty:
            GEOJSON_PATH = "assets/sp_bairros.geojson"
            
            try:
                with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
                    geojson_sp = json.load(f)
            except FileNotFoundError:
                st.error("Arquivo GeoJSON não encontrado!")
                return
            
            # Clean neighborhood names
            for feat in geojson_sp["features"]:
                nome_original = feat["properties"]["ds_nome"]
                feat["properties"]["id_limpo"] = self._limpar_nome_bairro(nome_original)
            
            # Display statistics
            st.markdown("**Estatísticas dos Valores:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Valor Mínimo", self._brl(stats.get('min', 0)))
            with col2:
                st.metric("Valor Médio", self._brl(stats.get('mean', 0)))
            with col3:
                st.metric("Valor Máximo", self._brl(stats.get('max', 0)))
            
            # Color scale
            color_scale = [
                [0.0, "#0A3D3D"], [0.25, "#1A5D5D"],
                [0.5, "#FFD700"], [0.75, "#E8DC3C"], [1.0, "#C8D962"]
            ]
            
            # Create map
            fig_mapa = px.choropleth_mapbox(
                df_bairro,
                geojson=geojson_sp,
                featureidkey="properties.id_limpo",
                locations="id_limpo",
                color="valor_repasse",
                color_continuous_scale=color_scale,
                range_color=[stats.get("min", 0), stats.get("max", 1)],
                mapbox_style="carto-darkmatter",
                zoom=9.5,
                center={"lat": -23.5505, "lon": -46.6333},
                opacity=0.8,
                hover_name="bairro",
                hover_data={'valor_repasse': ':,.2f', 'id_limpo': False}
            )
            fig_mapa.update_layout(
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_mapa, use_container_width=True)
        else:
            st.info("Sem dados por bairro para os filtros selecionados.")
    
    @staticmethod
    def _brl(v) -> str:
        """Format value as Brazilian currency"""
        try:
            s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {s}"
        except Exception:
            return "R$ 0,00"
    
    @staticmethod
    def _limpar_nome_bairro(nome: str) -> str:
        """Clean neighborhood name for matching"""
        if not isinstance(nome, str):
            return ""
        
        nome_maiusculo = nome.upper()
        
        if nome_maiusculo == "HIGIENOPOLIS":
            nome_maiusculo = "CONSOLACAO"
        
        nome_sem_acento = unidecode(nome_maiusculo)
        nome_limpo = re.sub(r'[^A-Z0-9\s]', '', nome_sem_acento)
        nome_limpo = re.sub(r'\s+', ' ', nome_limpo)
        nome_final = nome_limpo.strip()
        
        return nome_final