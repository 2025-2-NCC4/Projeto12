import streamlit as st
import google.generativeai as genai
from utils.database import carregar_dados_mysql
import pandas as pd

def configurar_gemini():
    """Configura a API do Google Gemini"""
    try:
        api_key = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Erro ao configurar Gemini: {e}")
        return False

def obter_contexto_dados():
    """Busca dados resumidos do banco para dar contexto ao chatbot"""
    try:
        query_resumo = """
        SELECT 
            COUNT(DISTINCT t.id_player_fk) as total_players,
            COUNT(DISTINCT t.id_parceiros_fk) as total_parceiros,
            COUNT(t.id_transacao) as total_transacoes,
            SUM(t.valor_transacao) as receita_total_gmv,
            SUM(t.valor_repasse) as receita_liquida,
            AVG(t.valor_transacao) as ticket_medio,
            MIN(t.data_hora_transacao) as data_primeira_transacao,
            MAX(t.data_hora_transacao) as data_ultima_transacao
        FROM transacao t
        """
        
        df_resumo = carregar_dados_mysql(query_resumo)
        if df_resumo.empty:
            return "Não foi possível carregar dados do banco."
        
        resumo = df_resumo.iloc[0]
        
        # Estrutura REAL do banco conforme CSV fornecido pelo usuário
        contexto = f"""
        CONTEXTO DO BANCO DE DADOS PICMONEY:
        
        **Resumo Geral:**
        - Total de Usuários (Players): {resumo['total_players']:,.0f}
        - Total de Parceiros (Lojas): {resumo['total_parceiros']:,.0f}
        - Total de Transações: {resumo['total_transacoes']:,.0f}
        - Receita Total (GMV): R$ {resumo['receita_total_gmv']:,.2f}
        - Receita Líquida (Repasse): R$ {resumo['receita_liquida']:,.2f}
        - Ticket Médio: R$ {resumo['ticket_medio']:,.2f}
        - Período dos dados: {resumo['data_primeira_transacao']} até {resumo['data_ultima_transacao']}
        
        **Estrutura EXATA do Banco (baseada no schema MySQL real):**
        
        Tabela 'transacao':
        - id_transacao (bigint, PRIMARY KEY)
        - valor_transacao (double)
        - valor_repasse (double)
        - data_hora_transacao (datetime)
        - id_player_fk (bigint, FOREIGN KEY)
        - id_parceiros_fk (bigint, FOREIGN KEY) ⚠️ PLURAL "parceiros"
        - id_cupom_fk (bigint, FOREIGN KEY)
        
        Tabela 'player':
        - id_player (bigint, PRIMARY KEY)
        - celular (text)
        - idade (bigint)
        - genero (text)
        - dataNascimento (datetime)
        - cidade (text)
        - bairro (text)
        - nome (text)
        - email (text)
        
        Tabela 'parceiro':
        - id_parceiros (bigint, PRIMARY KEY) ⚠️ PLURAL "parceiros"
        - nome_parceiro (text)
        - categoria_parceiro (text)
        - id_regiao_fk (bigint, FOREIGN KEY)
        
        Tabela 'cupom':
        - id_cupom (bigint, PRIMARY KEY)
        - codigo_cupom (text)
        - valor_cupom (double)
        - tipo_cupom (text)
        - id_campanha_fk (bigint, FOREIGN KEY)
        
        Tabela 'campanha':
        - id_campanha (bigint, PRIMARY KEY)
        - nome (text)
        - id_regiao_fk (bigint, FOREIGN KEY)
        
        Tabela 'regiao':
        - id_regiao (bigint, PRIMARY KEY)
        - bairro (text)
        - cidade (text)
        
        **⚠️ ATENÇÃO - INCONSISTÊNCIAS NO SCHEMA:**
        - Na tabela 'parceiro': a PK é "id_parceiros" (PLURAL, não "id_parceiro")
        - Na tabela 'transacao': a FK é "id_parceiros_fk" (PLURAL, não "id_parceiro_fk")
        - Use EXATAMENTE "id_parceiros" e "id_parceiros_fk" - não tente "corrigir" para singular
        """
        
        return contexto
        
    except Exception as e:
        return f"Erro ao obter contexto: {e}"

def processar_pergunta_com_sql(pergunta):
    """Usa o Gemini para gerar uma query SQL e executá-la no banco"""
    try:
        contexto = obter_contexto_dados()
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # ETAPA 1: Identificar valores/termos que precisam ser verificados no banco
        prompt_extracao = f"""
        Analise a pergunta do usuário e identifique se há menção a:
        - Nomes de categorias, parceiros, cidades, bairros, tipos, campanhas
        - Valores específicos que podem variar em escrita (plural/singular, acentos, maiúsculas)
        
        Pergunta: "{pergunta}"
        
        Se houver termos específicos que precisam ser verificados no banco, retorne uma query SQL simples 
        usando LIKE para encontrar os valores corretos. Se não houver, retorne "NENHUM".
        
        Exemplo: Se mencionar "Academia", gere: SELECT DISTINCT categoria_parceiro FROM parceiro WHERE categoria_parceiro LIKE '%academi%'
        """
        
        response_extracao = model.generate_content(prompt_extracao)
        query_verificacao = response_extracao.text.strip().replace("```sql", "").replace("```", "").strip()
        
        # Executar verificação se necessário
        contexto_adicional = ""
        if query_verificacao != "NENHUM" and "SELECT" in query_verificacao.upper():
            try:
                df_verificacao = carregar_dados_mysql(query_verificacao)
                if not df_verificacao.empty:
                    valores_encontrados = df_verificacao.iloc[:, 0].unique().tolist()
                    contexto_adicional = f"\n\n**VALORES REAIS ENCONTRADOS NO BANCO:** {valores_encontrados}\nUSE EXATAMENTE estes valores na query final."
            except:
                pass  # Se falhar, continua sem contexto adicional
        
        # ETAPA 2: Gerar query final com contexto completo
        prompt_sql = f"""
        {contexto}{contexto_adicional}
        
        O usuário fez a seguinte pergunta sobre os dados:
        "{pergunta}"
        
        **INSTRUÇÕES CRÍTICAS - LIMITAÇÕES DO MYSQL:**
        1. Gere APENAS uma query SQL válida para MySQL 8.0 que responda essa pergunta.
        2. Use as tabelas disponíveis: transacao, player, parceiro, cupom, campanha, regiao
        3. Retorne SOMENTE o código SQL, sem explicações, comentários ou markdown.
        
        **CRÍTICO - NOMES EXATOS DE COLUNAS:**
        - Use EXATAMENTE os nomes de colunas fornecidos no contexto acima
        - ATENÇÃO ESPECIAL: id_parceiro_fk (SINGULAR, não id_parceiros_fk)
        - ATENÇÃO ESPECIAL: id_parceiro (SINGULAR, não id_parceiros)
        - Se tiver dúvida sobre nome de coluna, consulte a estrutura completa fornecida
        - NÃO invente ou assuma nomes de colunas, use apenas os listados
        
        **IMPORTANTE - CORRESPONDÊNCIA DE VALORES:**
        - SEMPRE use LIKE '%termo%' para buscas de texto, NUNCA use igualdade exata (=) com strings literais
        - Ignore diferenças de plural/singular, maiúsculas/minúsculas, acentuação
        - Se valores reais foram fornecidos acima, USE EXATAMENTE como estão no banco
        - Para colunas de texto, prefira: WHERE coluna LIKE '%termo%' em vez de WHERE coluna = 'termo'
        
        **IMPORTANTE - FUNÇÕES ESTATÍSTICAS:**
        MySQL NÃO possui muitas funções estatísticas avançadas como CORR(), COVAR(), MEDIAN(), MODE(), PERCENTILE(), etc.
        Se a pergunta exigir cálculos estatísticos, você DEVE:
        - Usar APENAS funções nativas do MySQL: SUM(), AVG(), COUNT(), MIN(), MAX(), STDDEV(), VARIANCE(), POW(), SQRT()
        - Implementar fórmulas matemáticas manualmente usando essas funções básicas
        - Exemplo de correlação de Pearson: (SUM(x*y) - SUM(x)*SUM(y)/COUNT(*)) / SQRT((SUM(x*x) - POW(SUM(x),2)/COUNT(*)) * (SUM(y*y) - POW(SUM(y),2)/COUNT(*)))
        - Exemplo de mediana: usar subqueries com ORDER BY e LIMIT para encontrar o valor central
        - Se não conseguir implementar com funções nativas, simplifique a análise para algo possível no MySQL
        
        **DATAS E TEMPO:**
        - Para datas, use 'data_hora_transacao' da tabela transacao
        - Funções disponíveis: MONTH(), YEAR(), DAY(), DATE(), DATEDIFF(), DATE_FORMAT()
        - Para filtros de período: WHERE MONTH(data_hora_transacao) = X AND YEAR(data_hora_transacao) = Y
        
        **BOAS PRÁTICAS:**
        - Use JOINs explícitos (INNER JOIN, LEFT JOIN) com condições ON claras
        - Sempre que usar agregações (SUM, COUNT, AVG), considere se precisa de GROUP BY
        - Limite resultados com LIMIT quando apropriado (ex: TOP 10)
        - Use aliases descritivos para colunas calculadas
        
        QUERY SQL:
        """
        
        response_sql = model.generate_content(prompt_sql)
        sql_query = response_sql.text.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        df_resultado = carregar_dados_mysql(sql_query)
        
        if df_resultado.empty:
            return "Não encontrei resultados para essa consulta.", None, sql_query
        
        prompt_resposta = f"""
        O usuário perguntou: "{pergunta}"
        
        Executei a seguinte query SQL:
        {sql_query}
        
        Resultado:
        {df_resultado.to_string()}
        
        **INSTRUÇÕES:**
        Responda a pergunta do usuário de forma clara, objetiva e em português brasileiro.
        Use os dados do resultado acima para formular sua resposta.
        Formate valores monetários como R$ X.XXX,XX
        Seja conciso mas completo.
        """
        
        response_final = model.generate_content(prompt_resposta)
        return response_final.text, df_resultado, sql_query
        
    except Exception as e:
        return f"Erro ao processar pergunta: {e}", None, None

def renderizar_chatbot():
    """Renderiza chatbot em coluna direita"""
    if 'historico_chat' not in st.session_state:
        st.session_state.historico_chat = []
    
    st.markdown("""
    <style>
    .user-message {
        background: linear-gradient(135deg, #6bbf30 0%, #7FFF00 100%);
        color: #000;
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
        font-weight: 500;
    }
    .bot-message {
        background: #2d2d2d;
        color: #fff;
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
        border: 2px solid #6bbf30;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🤖 PicMoney AI")
    st.markdown("---")
    
    messages_container = st.container(height=400)
    with messages_container:
        if not st.session_state.historico_chat:
            st.info("👋 Pergunte sobre os dados!")
        else:
            for msg in st.session_state.historico_chat:
                if msg['tipo'] == 'user':
                    st.markdown(f'<div class="user-message">💬 {msg["texto"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">🤖 {msg["texto"]}</div>', unsafe_allow_html=True)
                    if msg.get('dataframe') is not None and not msg['dataframe'].empty:
                        st.dataframe(msg['dataframe'], use_container_width=True)
                    if msg.get('sql'):
                        with st.expander("📝 SQL"):
                            st.code(msg['sql'], language='sql')
    
    with st.form(key='chat_form', clear_on_submit=True):
        pergunta = st.text_area("Pergunte:", placeholder="Ex: Receita total?", height=80)
        col1, col2 = st.columns(2)
        with col1:
            enviar = st.form_submit_button("📤 Enviar")
        with col2:
            limpar = st.form_submit_button("🗑️ Limpar")
        
        if limpar:
            st.session_state.historico_chat = []
            st.rerun()
        
        if enviar and pergunta.strip():
            if configurar_gemini():
                st.session_state.historico_chat.append({'tipo': 'user', 'texto': pergunta})
                with st.spinner("🤔 Pensando..."):
                    resposta, df, sql = processar_pergunta_com_sql(pergunta)
                st.session_state.historico_chat.append({'tipo': 'bot', 'texto': resposta, 'dataframe': df, 'sql': sql})
                st.rerun()
