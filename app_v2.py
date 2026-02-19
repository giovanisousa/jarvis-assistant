import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Importa a versão V2 do cérebro
try:
    from brain_v2 import ApexBrain
    VERSAO_BRAIN = "V2"
except ImportError:
    from brain import ApexBrain
    VERSAO_BRAIN = "V1"

from voz import ApexVoz

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Apex Dashboard V2 - Animati",
    page_icon="🤖",
    layout="wide",
)

# --- ESTILO CSS FUTURISTA MELHORADO ---
st.markdown("""
<style>
    .stApp, .stSidebar { background-color: #0E1117; color: #FAFAFA; }
    h1, h2, h3 { color: #00ADB5; text-shadow: 0px 0px 10px rgba(0, 173, 181, 0.5); }
    .stMetricValue { color: #00FFF5 !important; font-weight: bold; }
    hr { border-color: #00ADB5; opacity: 0.2; }
    
    /* Botão com efeito neon */
    .stButton > button {
        background-color: transparent;
        color: #00FFF5;
        border: 2px solid #00ADB5;
        box-shadow: 0px 0px 10px #00ADB5;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #00ADB5;
        color: #0E1117;
        box-shadow: 0px 0px 20px #00FFF5;
        transform: scale(1.05);
    }
    
    /* Badge de versão */
    .version-badge {
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, #00ADB5 0%, #00FFF5 100%);
        color: #0E1117;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        z-index: 999;
        box-shadow: 0px 0px 15px rgba(0, 173, 181, 0.5);
    }
    
    /* Histórico de conversa */
    .chat-message {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        border-left: 3px solid #00ADB5;
    }
    
    .user-message {
        background-color: rgba(0, 173, 181, 0.1);
    }
    
    .assistant-message {
        background-color: rgba(0, 255, 245, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Badge de versão
st.markdown(f'<div class="version-badge">BRAIN {VERSAO_BRAIN}</div>', unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO SESSION STATE ---
if 'brain' not in st.session_state:
    st.session_state['brain'] = ApexBrain()
    st.session_state['historico_chat'] = []
    st.session_state['modo_voz'] = False

# --- CONEXÃO REAL COM OS DADOS ---
@st.cache_data(ttl=60)
def carregar_dados_reais():
    caminho = "db_projetos.json"
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

@st.cache_data(ttl=300)
def carregar_memoria():
    """Carrega anotações do gestor"""
    caminho = "db_memoria.json"
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# --- FUNÇÕES DE INTERAÇÃO ---
def processar_comando_texto(comando):
    """Processa comando digitado"""
    if not comando.strip():
        return
    
    brain = st.session_state['brain']
    
    # Adiciona ao histórico
    st.session_state['historico_chat'].append({
        'role': 'user',
        'content': comando,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })
    
    # Processa
    with st.spinner('🧠 Pensando...'):
        resposta = brain.analisar(comando)
    
    # Adiciona resposta ao histórico
    st.session_state['historico_chat'].append({
        'role': 'assistant',
        'content': resposta,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

def processar_comando_voz():
    """Processa comando por voz"""
    voz = ApexVoz()
    brain = st.session_state['brain']
    
    with st.spinner('🎤 Ouvindo...'):
        comando = voz.ouvir()
    
    if comando:
        # Adiciona ao histórico
        st.session_state['historico_chat'].append({
            'role': 'user',
            'content': comando,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        # Processa
        with st.spinner('🧠 Analisando...'):
            resposta = brain.analisar(comando)
        
        # Adiciona resposta
        st.session_state['historico_chat'].append({
            'role': 'assistant',
            'content': resposta,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        # Fala resposta
        texto_limpo = resposta.replace("*", "").replace("<b>", "").replace("</b>", "").replace("<br>", " ")
        voz.falar(texto_limpo[:500])  # Limita para não falar demais
        
        del voz

# --- CARREGAMENTO DE DADOS ---
dados = carregar_dados_reais()
df = pd.DataFrame(dados)
memoria = carregar_memoria()

# --- LAYOUT PRINCIPAL ---
st.title("🤖 APEX DASHBOARD V2 - CENTRAL DE PROJETOS")

# --- TABS PRINCIPAIS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💬 Conversa", "📝 Memórias", "⚙️ Configurações"])

# ========== TAB 1: DASHBOARD ==========
with tab1:
    if not df.empty:
        # Cálculos
        df['percent_complete'] = pd.to_numeric(df['percent_complete'], errors='coerce').fillna(0)
        total = len(df)
        concluidos = len(df[df['percent_complete'] == 100])
        em_andamento = len(df[(df['percent_complete'] > 0) & (df['percent_complete'] < 100)])
        nao_iniciados = len(df[df['percent_complete'] == 0])
        media = df['percent_complete'].mean()
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📋 Total de Projetos", total)
        col2.metric("✅ Concluídos", concluidos)
        col3.metric("⚡ Em Andamento", em_andamento)
        col4.metric("📊 Média Geral", f"{media:.1f}%")
        
        st.markdown("---")
        
        # Gráficos lado a lado
        graf_col1, graf_col2 = st.columns(2)
        
        with graf_col1:
            st.subheader("📈 Top 10 Projetos Avançados")
            top_df = df.nlargest(10, 'percent_complete').sort_values('percent_complete')
            
            fig1 = px.bar(
                top_df, 
                x='percent_complete', 
                y='name', 
                orientation='h',
                color='percent_complete',
                color_continuous_scale=[(0, '#0E1117'), (0.5, '#00ADB5'), (1, '#00FFF5')],
                text_auto=True,
                height=400
            )
            fig1.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color="#FFF", 
                showlegend=False,
                xaxis_title="Conclusão (%)",
                yaxis_title=""
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with graf_col2:
            st.subheader("🎯 Distribuição por Status")
            
            # Cria dados de distribuição
            status_data = pd.DataFrame({
                'Status': ['Concluídos', 'Em Andamento', 'Não Iniciados'],
                'Quantidade': [concluidos, em_andamento, nao_iniciados],
                'Cor': ['#00FFF5', '#00ADB5', '#FF6B6B']
            })
            
            fig2 = go.Figure(data=[go.Pie(
                labels=status_data['Status'],
                values=status_data['Quantidade'],
                marker=dict(colors=status_data['Cor']),
                hole=0.4,
                textinfo='label+percent',
                textfont=dict(color='white')
            )])
            
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#FFF",
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Tabela de projetos críticos
        st.markdown("---")
        st.subheader("⚠️ Projetos Críticos (< 30%)")
        criticos = df[df['percent_complete'] < 30].sort_values('percent_complete')
        
        if not criticos.empty:
            criticos_display = criticos[['name', 'percent_complete', 'status']].copy()
            criticos_display.columns = ['Projeto', 'Conclusão (%)', 'Status']
            st.dataframe(criticos_display, use_container_width=True, height=300)
        else:
            st.success("✅ Nenhum projeto crítico! Todos acima de 30%")
            
    else:
        st.error("⚠️ Nenhum dado de projeto encontrado. Execute `python zoho_sync.py` primeiro.")

# ========== TAB 2: CONVERSA ==========
with tab2:
    st.subheader("💬 Conversa com o Apex")
    
    # Modo de entrada
    modo_col1, modo_col2 = st.columns([1, 4])
    with modo_col1:
        modo = st.radio("Modo:", ["📝 Texto", "🎤 Voz"], horizontal=True)
    
    # Histórico de conversa
    if st.session_state['historico_chat']:
        st.markdown("### 📜 Histórico da Conversa")
        
        # Mostra últimas 10 mensagens
        for msg in st.session_state['historico_chat'][-10:]:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>🗣️ VOCÊ [{msg['timestamp']}]:</strong><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 APEX [{msg['timestamp']}]:</strong><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🗑️ Limpar Histórico"):
            st.session_state['historico_chat'] = []
            if VERSAO_BRAIN == "V2":
                st.session_state['brain'].limpar_historico()
            st.rerun()
    
    st.markdown("---")
    
    # Interface de entrada
    if modo == "📝 Texto":
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            comando_texto = st.text_input("Digite seu comando:", key="cmd_input", placeholder="Ex: Qual a situação do projeto Rivelare?")
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)  # Alinha botão
            if st.button("➡️ Enviar", use_container_width=True):
                if comando_texto:
                    processar_comando_texto(comando_texto)
                    st.rerun()
    
    else:  # Modo voz
        if st.button("🎙️ INICIAR GRAVAÇÃO", use_container_width=True, type="primary"):
            processar_comando_voz()
            st.rerun()
        
        st.info("💡 Clique no botão e fale seu comando quando aparecer 'Ouvindo...'")

# ========== TAB 3: MEMÓRIAS ==========
with tab3:
    st.subheader("📝 Anotações do Gestor")
    
    if memoria:
        # Busca
        busca = st.text_input("🔍 Buscar anotação:", placeholder="Digite parte do projeto ou anotação...")
        
        for proj_id, notas in memoria.items():
            # Busca projeto correspondente
            proj_nome = next((p['name'] for p in dados if str(p['id']) == proj_id), f"Projeto {proj_id}")
            
            # Filtro de busca
            if busca and busca.lower() not in proj_nome.lower():
                continue
            
            with st.expander(f"📌 {proj_nome}", expanded=False):
                for nota in notas:
                    st.markdown(f"- {nota}")
    else:
        st.info("📭 Nenhuma anotação registrada ainda. Use comandos como 'Anote que...' na conversa.")

# ========== TAB 4: CONFIGURAÇÕES ==========
with tab4:
    st.subheader("⚙️ Configurações do Sistema")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"""
        ### 🧠 Informações do Cérebro
        - **Versão:** {VERSAO_BRAIN}
        - **Projetos Carregados:** {len(dados)}
        - **Anotações:** {sum(len(notas) for notas in memoria.values())}
        - **Histórico Chat:** {len(st.session_state['historico_chat'])} mensagens
        """)
        
        if VERSAO_BRAIN == "V2":
            st.success("✅ Brain V2 ativo - Memória conversacional habilitada!")
        else:
            st.warning("⚠️ Brain V1 - Considere atualizar para V2")
    
    with info_col2:
        st.markdown("### 🔄 Ações do Sistema")
        
        if st.button("🔄 Recarregar Dados do Zoho"):
            st.cache_data.clear()
            st.success("Dados recarregados!")
            st.rerun()
        
        if st.button("🧹 Limpar Cache"):
            st.cache_data.clear()
            st.success("Cache limpo!")
        
        if st.button("🔌 Reiniciar Brain"):
            st.session_state['brain'] = ApexBrain()
            st.success("Brain reiniciado!")
    
    st.markdown("---")
    
    # Informações adicionais
    with st.expander("📚 Comandos Disponíveis"):
        st.markdown("""
        **Consultas de Projetos:**
        - "Qual a situação do projeto X?"
        - "Quantos projetos estão em implantação?"
        - "Me fala dos projetos atrasados"
        
        **Ações:**
        - "Manda email para [pessoa] sobre [assunto]"
        - "Checa meus emails não lidos"
        - "Avisa [pessoa] que [mensagem]"
        
        **Anotações:**
        - "Anote que [informação] no projeto X"
        - "Lembre que [fato]"
        
        **Sistema:**
        - "Limpar histórico"
        """)

# --- BARRA LATERAL ---
with st.sidebar:
    # Logo/Imagem
    if os.path.exists("robot.png"):
        st.image("iron.gif", width=400)
    elif os.path.exists("/mnt/user-data/uploads/robot.png"):
        st.image("/mnt/user-data/uploads/robot.png", width=200)
    
    st.markdown(f'<h2 style="text-align:center;">APEX CORE {VERSAO_BRAIN}</h2>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Status do sistema
    st.markdown("### 📊 Status")
    st.metric("Projetos Ativos", len(dados))
    st.metric("Versão Brain", VERSAO_BRAIN)
    
    st.markdown("---")
    
    # Acesso rápido
    st.markdown("### ⚡ Acesso Rápido")
    
    if st.button("🔄 Sincronizar Zoho", use_container_width=True):
        with st.spinner("Sincronizando..."):
            try:
                import zoho_sync
                bot = zoho_sync.ZohoSync()
                bot.sync_my_data()
                st.success("✅ Sincronização concluída!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    
    if st.button("📊 Atualizar Tracker", use_container_width=True):
        with st.spinner("Atualizando..."):
            try:
                import tracker
                tracker.salvar_snapshot()
                st.success("✅ Snapshot salvo!")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    
    st.markdown("---")
    st.caption(f"Dashboard ativo desde: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
