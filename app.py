import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# FUNÇÕES MATEMÁTICAS
# ==========================================
def calcular_dogleg(inc1, az1, inc2, az2):
    i1, a1 = np.radians(inc1), np.radians(az1)
    i2, a2 = np.radians(inc2), np.radians(az2)
    dl_rad = np.arccos(np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(a2 - a1))
    return np.degrees(dl_rad)
def calcular_direcional(inc1, az1, md1, inc2, az2, md2):
    # Converte graus para radianos
    i1, a1 = np.radians(inc1), np.radians(az1)
    i2, a2 = np.radians(inc2), np.radians(az2)
    
    # Previne divisão por zero
    delta_md = md2 - md1
    if delta_md <= 0:
        return 0.0, 0.0
        
    # Calcula o Dogleg (DL)
    dl_rad = np.arccos(np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(a2 - a1))
    dl_deg = np.degrees(dl_rad)
    
    # Calcula DLS (Normalizado para 30 metros)
    dls_30m = dl_deg * (30.0 / delta_md)
    
    # Calcula a Toolface Recomendada (Gravity Toolface)
    y = np.sin(i2) * np.sin(a2 - a1)
    x = np.sin(i2) * np.cos(i1) * np.cos(a2 - a1) - np.sin(i1) * np.cos(i2)
    tf_rad = np.arctan2(y, x)
    tf_deg = np.degrees(tf_rad)
    if tf_deg < 0:
        tf_deg += 360
        
    return dls_30m, tf_deg

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.set_page_config(page_title="Intrepid Direcional", layout="wide")
st.title("🎯 Assistente de Controle Direcional - Intrepid Brasil")

# BARRA LATERAL (SIDEBAR)
st.sidebar.header("📁 Importar Dados")
arquivo_banco = st.sidebar.file_uploader("Carregar Banco de Motores (CSV)", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuração do Motor")
modelo = st.sidebar.selectbox("Modelo do Motor", ["GyroDrill", "Tomahawk"])
od = st.sidebar.selectbox("Diâmetro Externo (OD)", ["4 3/4", "5", "6 1/2", "6 3/4", "7", "7 3/4", "8", "9 5/8"])
lobulos = st.sidebar.text_input("Lóbulos e Estágios (ex: 7/8 5.7)", "7/8 5.7")
bent = st.sidebar.selectbox("Bent Housing (Graus)", [1.15, 1.25, 1.50, 1.75, 1.83, 2.00, 2.12, 2.38, 2.60, 2.77, 3.00])
estabilizacao = st.sidebar.radio("Tipo de BHA", ["Slick", "Stabilized"])

# ==========================================
# TELA PRINCIPAL - Inserção de Surveys e Slide
# ==========================================
st.header("📍 Dados do Poço e Target")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Survey Anterior")
    md_ant = st.number_input("MD Ant. (m)", value=970.0, step=1.0)
    inc_ant = st.number_input("Inc Ant. (°)", value=8.5, step=0.1)
    az_ant = st.number_input("Azimute Ant. (°)", value=40.0, step=0.1)

with col2:
    st.subheader("Survey Atual")
    md_atual = st.number_input("MD Atual (m)", value=1000.0, step=1.0)
    inc_atual = st.number_input("Inc Atual (°)", value=10.0, step=0.1)
    az_atual = st.number_input("Azim Atual (°)", value=45.0, step=0.1)
    st.markdown("---")
    slide_realizado = st.number_input("Slide Realizado no Trecho (m)", value=0.0, step=0.1)

with col3:
    st.subheader("Target (Alvo)")
    md_alvo = st.number_input("MD Alvo (m)", value=1030.0, step=1.0)
    inc_alvo = st.number_input("Inc Alvo (°)", value=12.0, step=0.1)
    az_alvo = st.number_input("Azim Alvo (°)", value=48.0, step=0.1)

st.markdown("---")

# ==========================================
# BOTÃO DE CÁLCULO INTELIGENTE
# ==========================================
if st.button("🚀 Calcular Projeção e Orientação"):
    st.header("📊 Resultados e Instruções")
    
    # 1. CÁLCULOS DO TRECHO ANTERIOR (MOTOR YIELD REAL)
    dl_trecho = calcular_dogleg(inc_ant, az_ant, inc_atual, az_atual)
    motor_yield_real = 0.0
    if slide_realizado > 0:
        motor_yield_real = dl_trecho * (30.0 / slide_realizado)
    
    # 2. CÁLCULO PARA O TARGET
    dls_req, tf_req = calcular_direcional(inc_atual, az_atual, md_atual, inc_alvo, az_alvo, md_alvo)
    
    # 3. BUSCA DO TEÓRICO NO BANCO DE DADOS
    build_rate_100ft = 0.0
    build_rate_30m = 0.0
    if arquivo_banco is not None:
        df = pd.read_csv(arquivo_banco)
        filtro = df[(df['Modelo'] == modelo) & 
                    (df['Diametro_Externo_OD'] == od) & 
                    (df['Bent_Housing_Graus'] == float(bent)) & 
                    (df['Tipo_Estabilizacao'] == estabilizacao)]
        if not filtro.empty:
            build_rate_100ft = filtro.iloc[0]['Build_Rate_Teorico']
            build_rate_30m = build_rate_100ft * (30.0 / 30.48)
            
    # 4. DECISÃO DE QUAL RENDIMENTO USAR
    rendimento_usado = motor_yield_real if motor_yield_real > 0 else build_rate_30m
    origem_rendimento = "REAL (Calculado do último stand)" if motor_yield_real > 0 else "TEÓRICO (Catálogo Intrepid)"
    
    st.info(f"**Motor:** {modelo} {od}\" | **Bent:** {bent}° | **BR Teórico:** {build_rate_30m:.2f} °/30m")
    if motor_yield_real > 0:
        st.success(f"**Motor Yield Real Observado:** {motor_yield_real:.2f} °/30m")
    else:
        st.warning("Sem dados de slide no trecho anterior. Utilizando Build Rate Teórico para as projeções.")
    
    # 5. RESULTADOS FINAIS
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label="DLS Requerido", value=f"{dls_req:.2f} °/30m")
    with col5:
        st.metric(label="Toolface Recomendada", value=f"{tf_req:.0f}° R")
    with col6:
        if rendimento_usado > 0:
            slide_m = (dls_req / rendimento_usado) * 30
            if slide_m > (md_alvo - md_atual):
                st.error("Alvo inatingível com este motor/rendimento!")
            else:
                st.metric(label="Metragem de Slide Sugerida", value=f"{slide_m:.1f} m", delta=origem_rendimento, delta_color="off")
        else:
            st.metric(label="Metragem de Slide", value="-")

# 6. RELATÓRIO PARA WHATSAPP
    st.markdown("---")
    st.subheader("📱 Copiar Instrução para a Sonda")
    
    if rendimento_usado > 0 and slide_m <= (md_alvo - md_atual):
        relatorio = f"""*INSTRUÇÃO DIRECIONAL - INTREPID* 🎯
*Motor:* {modelo} {od}" | Bent: {bent}°
*Trecho:* {md_atual}m até {md_alvo}m

*PARÂMETROS:*
- 🧭 *Toolface:* {tf_req:.0f}° R
- 📏 *Metragem de Slide:* {slide_m:.1f} m
- 🎯 *DLS Alvo:* {dls_req:.2f} °/30m

*DADOS DO MOTOR:*
- Rendimento Usado: {rendimento_usado:.2f} °/30m
- Base de Cálculo: {origem_rendimento}"""

        st.code(relatorio, language="markdown")
