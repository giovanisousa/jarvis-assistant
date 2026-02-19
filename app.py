import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from brain import ApexBrain
from voz import ApexVoz

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Apex Dashboard - Animati",
    page_icon="🤖",
    layout="wide",
)

# --- ESTILO CSS FUTURISTA (DARK MODE) ---
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
    }
    .stButton > button:hover {
        background-color: #00ADB5;
        color: #0E1117;
        box-shadow: 0px 0px 20px #00FFF5;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO REAL COM OS DADOS (ZOHO) ---
@st.cache_data(ttl=60) # Atualiza o cache a cada minuto
def carregar_dados_reais():
    caminho = "db_projetos.json"
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# --- INTERFACE DO APEX ---
def acionar_apex():
    voz = ApexVoz()
    brain = ApexBrain()
    with st.sidebar:
        with st.spinner('⚡ Apex está a ouvir...'):
            comando = voz.ouvir()
            if comando:
                st.session_state['cmd'] = comando
                resposta = brain.analisar(comando)
                st.session_state['resp'] = resposta
                voz.falar(resposta.replace("*", "").replace("<b>", "").replace("</b>", ""))

# --- CARREGAMENTO ---
dados = carregar_dados_reais()
df = pd.DataFrame(dados)

# Renderização do Dashboard
st.title("📟 CENTRAL DE PROJETOS [ANIMATI]")

if not df.empty:
    # Cálculos Reais
    df['percent_complete'] = pd.to_numeric(df['percent_complete'], errors='coerce').fillna(0)
    total = len(df)
    concluidos = len(df[df['percent_complete'] == 100])
    media = df['percent_complete'].mean()

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Projetos em Sincronização", total)
    c2.metric("Média de Conclusão", f"{media:.1f}%")
    c3.metric("Projetos Finalizados", concluidos)

    st.markdown("---")

    # Gráfico de Barras Horizontal (Top 15 mais avançados)
    st.subheader("📈 Status de Implantação")
    top_df = df.nlargest(15, 'percent_complete').sort_values('percent_complete')
    
    fig = px.bar(
        top_df, x='percent_complete', y='name', orientation='h',
        color='percent_complete',
        color_continuous_scale=[(0, '#0E1117'), (0.5, '#00ADB5'), (1, '#00FFF5')],
        text_auto=True
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#FFF", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("⚠️ Ficheiro db_projetos.json não encontrado ou vazio.")

# --- BARRA LATERAL FUTURISTA ---
with st.sidebar:
    # Imagem local do Robô
    if os.path.exists("assets/robo_apex.png"):
        st.image("assets/robo_apex.png", width=220)
    
    st.markdown('<h2 style="text-align:center;">APEX CORE</h2>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🎙️ INICIAR COMANDO", width="stretch"):
        acionar_apex()
    
    if 'cmd' in st.session_state:
        st.caption("Última entrada:")
        st.info(st.session_state['cmd'])
    if 'resp' in st.session_state:
        st.caption("Resposta Apex:")
        st.markdown(st.session_state['resp'], unsafe_allow_html=True)