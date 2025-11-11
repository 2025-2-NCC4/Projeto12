import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.pages.base_page import BasePage
from components.cards.kpi_card import KPICard
from components.filters.city_filter import CityMultiSelectFilter
from components.filters.date_filter import DateRangeFilter
from utils.styles import PICMONEY_COLORS
from utils.database import carregar_dados_mysql
from utils.backend_client import BackendAPI


class CEOPage(BasePage):
    """CEO Dashboard - User analytics and business metrics"""

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
        self.date_filter = None
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

            cidades_disponiveis = [
                c for c in self.df_ceo["cidade"].dropna().unique()
            ]

            self.city_filter = CityMultiSelectFilter(
                cities=cidades_disponiveis,
                key="ceo_city_filter",
                label="Selecione a Cidade",
                icon="🏙️"
            )

            transacoes_data = carregar_dados_mysql("""
                SELECT MIN(data_hora_transacao) as min_date,
                       MAX(data_hora_transacao) as max_date
                FROM transacao
            """)

            if not transacoes_data.empty:
                min_dt = transacoes_data['min_date'].iloc[0]
                max_dt = transacoes_data['max_date'].iloc[0]
                if pd.notna(min_dt) and pd.notna(max_dt):
                    self.date_filter = DateRangeFilter(
                        key="ceo_dates",
                        min_date=min_dt,
                        max_date=max_dt,
                        label="📅 Período de Análise"
                    )

        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            st.stop()

    def render_filters(self):
        """Render CEO-specific filters in sidebar"""
        st.sidebar.markdown("## 🎯 Filtros CEO")

        if self.date_filter:
            data_inicio, data_fim = self.date_filter.render()
            self.filters['date_start'] = data_inicio
            self.filters['date_end'] = data_fim

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

        df_filtrado = self.apply_filters(self.df_ceo)

        if df_filtrado.empty:
            st.warning("Sem dados para os filtros selecionados.")
            return

        self._render_user_analysis(df_filtrado)
        st.markdown("---")
        self._render_coupon_metrics()
        st.markdown("---")
        # self._render_geographic_analysis()
        # st.markdown("---")
        self._render_retention_analysis()
        st.markdown("---")
        self._render_demographic_analysis()
        st.markdown("---")
        self._render_player_table(df_filtrado)

    def _render_user_analysis(self, df_filtrado: pd.DataFrame):
        """Render user analysis section with age distribution"""
        st.header("Análise de Usuários (Players)")

        try:
            cidades = self.filters.get('cidades', [])
            body = {"cidades": cidades}

            response = self.api.post("/api/ceo/players/hist_idade", json=body)
            dados_hist_api = response.json() if response.ok else {}

            if not dados_hist_api.get("ok") or not dados_hist_api.get("histograma"):
                st.error("Erro ao carregar dados do histograma do Backend.")
                self._render_age_histogram_local(df_filtrado)
                return

            df_hist = pd.DataFrame(dados_hist_api["histograma"])
            self._render_age_histogram(df_hist)

        except Exception as e:
            st.error(f"Erro ao consultar o backend: {e}")
            st.warning("Calculando histograma localmente...")
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
        st.plotly_chart(fig_idade, width='stretch')

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
        st.plotly_chart(fig_idade, width='stretch')

    def _render_player_table(self, df_filtrado: pd.DataFrame):
        """Render player data table"""
        st.header("📋 Dados dos Usuários")

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

        available_columns = [col for col in self.COLUNAS_ORDEM if col in df_filtrado.columns]
        st.dataframe(
            df_filtrado[available_columns],
            width='stretch',
            height=400
        )

    def _render_coupon_metrics(self):
        """Render coupon consumption metrics"""
        st.header("📊 Métricas de Cupons")

        date_filter = ""
        if self.filters.get('date_start') and self.filters.get('date_end'):
            date_filter = f"""
                AND t.data_hora_transacao BETWEEN '{self.filters['date_start']}'
                AND '{self.filters['date_end']}'
            """

        city_filter = ""
        if self.filters.get('cidades'):
            cidades_str = "','".join(self.filters['cidades'])
            city_filter = f"AND p.cidade IN ('{cidades_str}')"

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 5 Categorias Mais Consumidas")
            
            df_categorias = carregar_dados_mysql(f"""
                SELECT
                    pa.categoria_parceiro,
                    COUNT(t.id_transacao) as total_cupons,
                    SUM(t.valor_transacao) as valor_total
                FROM transacao t
                JOIN parceiro pa ON t.id_parceiros_fk = pa.id_parceiros
                JOIN player p ON t.id_player_fk = p.id_player
                WHERE 1=1 {date_filter} {city_filter}
                GROUP BY pa.categoria_parceiro
                ORDER BY total_cupons DESC
                LIMIT 5
            """)

            if not df_categorias.empty:
                fig_cat = px.bar(
                    df_categorias,
                    x='total_cupons',
                    y='categoria_parceiro',
                    orientation='h',
                    labels={'total_cupons': 'Total de Cupons', 'categoria_parceiro': 'Categoria'},
                    template='plotly_dark',
                    color='total_cupons',
                    color_continuous_scale=[[0, PICMONEY_COLORS['verde']], [1, PICMONEY_COLORS['amarelo']]]
                )
                fig_cat.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig_cat, width='stretch')
            else:
                st.info("Sem dados de categorias.")

        with col2:
            st.subheader("Cupons Capturados por Hora")
            df_hora = carregar_dados_mysql(f"""
                SELECT
                    HOUR(t.data_hora_transacao) as hora,
                    COUNT(t.id_transacao) as total_cupons
                FROM transacao t
                JOIN player p ON t.id_player_fk = p.id_player
                WHERE 1=1 {date_filter} {city_filter}
                GROUP BY HOUR(t.data_hora_transacao)
                ORDER BY hora
            """)

            if not df_hora.empty:
                fig_hora = px.line(
                    df_hora,
                    x='hora',
                    y='total_cupons',
                    labels={'hora': 'Hora do Dia', 'total_cupons': 'Cupons Capturados'},
                    template='plotly_dark',
                    markers=True
                )
                fig_hora.update_traces(line=dict(color=PICMONEY_COLORS['verde'], width=3))
                fig_hora.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                fig_hora.update_xaxes(dtick=1)
                st.plotly_chart(fig_hora, width='stretch')
            else:
                st.info("Sem dados por hora.")

    def _render_geographic_analysis(self):
        """Render geographic distribution analysis"""
        st.header("🗺️ Análise Geográfica")

        date_filter = ""
        if self.filters.get('date_start') and self.filters.get('date_end'):
            date_filter = f"""
                AND t.data_hora_transacao BETWEEN '{self.filters['date_start']}'
                AND '{self.filters['date_end']}'
            """

        st.subheader("Cupons Capturados por Região")
        df_regiao = carregar_dados_mysql(f"""
            SELECT
                p.cidade,
                p.bairro,
                COUNT(t.id_transacao) as total_cupons,
                COUNT(DISTINCT p.id_player) as total_usuarios
            FROM transacao t
            JOIN player p ON t.id_player_fk = p.id_player
            WHERE 1=1 {date_filter}
            GROUP BY p.cidade, p.bairro
            ORDER BY total_cupons DESC
        """)

        if not df_regiao.empty:
            df_cidade_agg = df_regiao.groupby('cidade').agg({
                'total_cupons': 'sum',
                'total_usuarios': 'sum',
                'bairro': 'count'
            }).reset_index()
            df_cidade_agg.rename(columns={'bairro': 'total_bairros'}, inplace=True)

            city_coords = {
                'São Paulo': {'lat': -23.5505, 'lon': -46.6333},
                'Rio de Janeiro': {'lat': -22.9068, 'lon': -43.1729},
                'Belo Horizonte': {'lat': -19.9167, 'lon': -43.9345},
                'Brasília': {'lat': -15.7939, 'lon': -47.8828},
                'Salvador': {'lat': -12.9714, 'lon': -38.5014},
                'Fortaleza': {'lat': -3.7172, 'lon': -38.5433},
                'Curitiba': {'lat': -25.4284, 'lon': -49.2733},
                'Recife': {'lat': -8.0476, 'lon': -34.8770},
                'Porto Alegre': {'lat': -30.0346, 'lon': -51.2177},
                'Manaus': {'lat': -3.1190, 'lon': -60.0217},
                'Belém': {'lat': -1.4558, 'lon': -48.5039},
                'Goiânia': {'lat': -16.6869, 'lon': -49.2648},
                'Campinas': {'lat': -22.9099, 'lon': -47.0626},
                'São Luís': {'lat': -2.5387, 'lon': -44.2825},
                'São Gonçalo': {'lat': -22.8268, 'lon': -43.0534},
                'Maceió': {'lat': -9.6658, 'lon': -35.7353},
                'Duque de Caxias': {'lat': -22.7858, 'lon': -43.3054},
                'Natal': {'lat': -5.7945, 'lon': -35.2110},
                'Teresina': {'lat': -5.0892, 'lon': -42.8019},
                'Campo Grande': {'lat': -20.4697, 'lon': -54.6201}
            }

            df_cidade_agg['lat'] = df_cidade_agg['cidade'].map(lambda x: city_coords.get(x, {}).get('lat'))
            df_cidade_agg['lon'] = df_cidade_agg['cidade'].map(lambda x: city_coords.get(x, {}).get('lon'))

            df_cidade_agg = df_cidade_agg.dropna(subset=['lat', 'lon'])

            if not df_cidade_agg.empty:
                fig_regiao = px.scatter_geo(
                    df_cidade_agg,
                    lat='lat',
                    lon='lon',
                    size='total_cupons',
                    hover_name='cidade',
                    hover_data={
                        'total_cupons': ':,',
                        'total_usuarios': ':,',
                        'total_bairros': True,
                        'lat': False,
                        'lon': False
                    },
                    color='total_cupons',
                    color_continuous_scale=[[0, PICMONEY_COLORS['verde']], [0.5, PICMONEY_COLORS['amarelo']], [1, '#FF6B6B']],
                    template='plotly_dark',
                    labels={
                        'total_cupons': 'Total de Cupons',
                        'total_usuarios': 'Total de Usuários',
                        'total_bairros': 'Bairros'
                    },
                    size_max=60
                )

                fig_regiao.update_geos(
                    center=dict(lat=-14.2350, lon=-51.9253),
                    projection_scale=2.5,
                    visible=True,
                    resolution=50,
                    showcountries=True,
                    countrycolor="rgba(255,255,255,0.3)",
                    showcoastlines=True,
                    coastlinecolor="rgba(255,255,255,0.3)",
                    showland=True,
                    landcolor='rgba(40,40,40,0.9)',
                    showlakes=True,
                    lakecolor='rgba(20,20,50,0.8)',
                    bgcolor='rgba(0,0,0,0)'
                )

                fig_regiao.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    geo=dict(bgcolor='rgba(0,0,0,0)'),
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=600
                )
                st.plotly_chart(fig_regiao, width='stretch')

                st.markdown("<br>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    KPICard(
                        "Total de Cidades",
                        f"{len(df_cidade_agg)}"
                    ).render()
                with col2:
                    KPICard(
                        "Total de Cupons",
                        f"{df_cidade_agg['total_cupons'].sum():,}"
                    ).render()
                with col3:
                    KPICard(
                        "Total de Usuários",
                        f"{df_cidade_agg['total_usuarios'].sum():,}"
                    ).render()
            else:
                st.warning("Nenhuma cidade encontrada com coordenadas válidas.")
        else:
            st.info("Sem dados geográficos.")

    def _render_retention_analysis(self):
        """Render retention rate analysis"""
        st.header("🔄 Análise de Retenção")

        date_filter = ""
        if self.filters.get('date_start') and self.filters.get('date_end'):
            date_filter = f"""
                AND t.data_hora_transacao BETWEEN '{self.filters['date_start']}'
                AND '{self.filters['date_end']}'
            """

        city_filter = ""
        if self.filters.get('cidades'):
            cidades_str = "','".join(self.filters['cidades'])
            city_filter = f"AND p.cidade IN ('{cidades_str}')"

        df_retencao = carregar_dados_mysql(f"""
            SELECT
                p.id_player,
                COUNT(t.id_transacao) as total_transacoes,
                MIN(DATE(t.data_hora_transacao)) as primeira_transacao,
                MAX(DATE(t.data_hora_transacao)) as ultima_transacao,
                DATEDIFF(MAX(t.data_hora_transacao), MIN(t.data_hora_transacao)) as dias_ativo
            FROM transacao t
            JOIN player p ON t.id_player_fk = p.id_player
            WHERE 1=1 {date_filter} {city_filter}
            GROUP BY p.id_player
        """)

        if not df_retencao.empty:
            total_usuarios = len(df_retencao)
            usuarios_retornaram = len(df_retencao[df_retencao['total_transacoes'] > 1])
            taxa_retencao = (usuarios_retornaram / total_usuarios * 100) if total_usuarios > 0 else 0

            col1, col2, col3 = st.columns(3)

            with col1:
                KPICard(
                    "Taxa de Retenção",
                    f"{taxa_retencao:.1f}%"
                ).render()

            with col2:
                KPICard(
                    "Usuários Recorrentes",
                    f"{usuarios_retornaram:,}"
                ).render()

            with col3:
                media_dias_ativo = df_retencao['dias_ativo'].mean()
                KPICard(
                    "Média de Dias Ativo",
                    f"{media_dias_ativo:.0f} dias"
                ).render()

            st.markdown("<br>", unsafe_allow_html=True)

            st.subheader("Dias Ativos no Sistema")
            fig_dias = px.line(
                df_retencao.groupby('dias_ativo').size().reset_index(name='count'),
                x='dias_ativo',
                y='count',
                labels={'dias_ativo': 'Dias Ativo', 'count': 'Número de Usuários'},
                template='plotly_dark',
                color_discrete_sequence=[PICMONEY_COLORS['verde']]
            )
            fig_dias.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_dias, width='stretch')
        else:
            st.info("Sem dados de retenção.")

    def _render_demographic_analysis(self):
        """Render demographic analysis with coupon correlation"""
        st.header("👥 Análise Demográfica e Preferências")

        date_filter = ""
        if self.filters.get('date_start') and self.filters.get('date_end'):
            date_filter = f"""
                AND t.data_hora_transacao BETWEEN '{self.filters['date_start']}'
                AND '{self.filters['date_end']}'
            """

        city_filter = ""
        if self.filters.get('cidades'):
            cidades_str = "','".join(self.filters['cidades'])
            city_filter = f"AND p.cidade IN ('{cidades_str}')"

        df_demografico = carregar_dados_mysql(f"""
            SELECT
                p.idade,
                p.genero,
                c.tipo_cupom,
                pa.categoria_parceiro,
                COUNT(t.id_transacao) as total_cupons,
                SUM(t.valor_transacao) as valor_total
            FROM transacao t
            JOIN player p ON t.id_player_fk = p.id_player
            JOIN cupom c ON t.id_cupom_fk = c.id_cupom
            JOIN parceiro pa ON t.id_parceiros_fk = pa.id_parceiros
            WHERE p.idade IS NOT NULL
                AND p.genero IS NOT NULL
                {date_filter} {city_filter}
            GROUP BY p.idade, p.genero, c.tipo_cupom, pa.categoria_parceiro
        """)

        if not df_demografico.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Preferência de Cupom por Gênero")
                df_genero_cupom = df_demografico.groupby(['genero', 'tipo_cupom'])['total_cupons'].sum().reset_index()

                fig_genero = px.bar(
                    df_genero_cupom,
                    x='genero',
                    y='total_cupons',
                    color='tipo_cupom',
                    barmode='group',
                    labels={'genero': 'Gênero', 'total_cupons': 'Total de Cupons', 'tipo_cupom': 'Tipo de Cupom'},
                    template='plotly_dark',
                    color_discrete_map={
                        'Desconto': PICMONEY_COLORS['verde'],
                        'Cashback': PICMONEY_COLORS['amarelo'],
                        'Produto': PICMONEY_COLORS['branco']
                    }
                )
                fig_genero.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_genero, width='stretch')

            with col2:
                st.subheader("Preferência de Cupom por Faixa Etária")
                df_demografico['faixa_etaria'] = pd.cut(
                    df_demografico['idade'],
                    bins=[0, 18, 25, 35, 45, 55, 100],
                    labels=['<18', '18-25', '26-35', '36-45', '46-55', '55+']
                )
                df_idade_cupom = df_demografico.groupby(['faixa_etaria', 'tipo_cupom'])['total_cupons'].sum().reset_index()

                fig_idade = px.bar(
                    df_idade_cupom,
                    x='faixa_etaria',
                    y='total_cupons',
                    color='tipo_cupom',
                    barmode='stack',
                    labels={'faixa_etaria': 'Faixa Etária', 'total_cupons': 'Total de Cupons', 'tipo_cupom': 'Tipo de Cupom'},
                    template='plotly_dark',
                    color_discrete_map={
                        'Desconto': PICMONEY_COLORS['verde'],
                        'Cashback': PICMONEY_COLORS['amarelo'],
                        'Produto': PICMONEY_COLORS['branco']
                    }
                )
                fig_idade.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_idade, width='stretch')

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Categoria Preferida por Idade e Gênero")

            df_cat_demo = df_demografico.groupby(['idade', 'genero', 'categoria_parceiro'])['total_cupons'].sum().reset_index()
            df_cat_demo = df_cat_demo.sort_values('total_cupons', ascending=False).groupby(['idade', 'genero']).first().reset_index()

            fig_bar = px.bar(
                df_cat_demo,
                x='idade',
                y='total_cupons',
                color='genero',
                barmode='group',
                facet_col='categoria_parceiro',
                labels={'idade': 'Idade', 'total_cupons': 'Total de Cupons', 'genero': 'Gênero'},
                template='plotly_dark',
                color_discrete_map={'Masculino': PICMONEY_COLORS['verde'], 'Feminino': PICMONEY_COLORS['amarelo']}
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, width='stretch')
        else:
            st.info("Sem dados demográficos.")
