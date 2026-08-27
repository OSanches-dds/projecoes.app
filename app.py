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

# ==========================================
# BARRA LATERAL (SIDEBAR) - Configuração
# ==========================================
st.sidebar.header("📁 Importar Dados")

# O parâmetro 'key' garante que o Streamlit saiba quem é quem!
# BANCO DE DADOS DE MOTORES EMBUTIDO (Substitui o arquivo CSV/Excel)
dados_motores = [
    # GyroDrill 4 3/4" 7/8 2.6 (Furo 6") - Extraído do Manual Intrepid (Pág. 34)
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 3.80, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 6.83, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 6.20, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 9.08, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 9.71, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 11.21, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26},

    # GyroDrill 4 3/4" 7/8 3.8 (Furo 6") - Extraído do Manual Intrepid (Pág. 36)
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 3.90, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.08, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 6.79, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.60, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 10.90, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 12.97, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52},

    # GyroDrill 8" 7/8 4.0 (Furo 12 1/4") - Extraído do Manual Intrepid (Pág. 60)
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 1.20, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.24, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.21, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.15, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.74, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 11.96, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17},

    # GyroDrill 6 3/4" 7/8 5.7 (Mantido)
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.7", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 7.29, "Torque_Max": 13720, "Pressao_D": 1280, "Rev_Gal": 0.24},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.7", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.97, "Torque_Max": 13720, "Pressao_D": 1280, "Rev_Gal": 0.24},

    # Tomahawk 6 3/4" (Mantido)
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.5, "Tipo_Estabilizacao": "Slick", "Build_Rate": 5.7, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.5},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.5, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.71, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.5},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 8.3, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.5},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.65, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.5},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.5, "Tipo_Estabilizacao": "Slick", "Build_Rate": 9.8, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.3},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.5, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 9.2, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.3},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.75, "Tipo_Estabilizacao": "Slick", "Build_Rate": 11.2, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.3},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.75, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.7, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.3}
]
df_motores = pd.DataFrame(dados_motores)
arquivo_bha = st.sidebar.file_uploader("Carregar Tally da BHA (Excel)", type=["xlsx", "xls"], key="bha_excel")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuração do Motor")
modelo = st.sidebar.selectbox("Modelo do Motor", ["GyroDrill", "Tomahawk"], key="modelo_motor")
od = st.sidebar.selectbox("Diâmetro Externo (OD)", ["4 3/4", "5", "6 1/2", "6 3/4", "7", "7 3/4", "8", "9 5/8"], key="od_motor")
lobulos = st.sidebar.text_input("Lóbulos e Estágios (ex: 7/8 5.7)", "7/8 5.7", key="lobulos")
bent = st.sidebar.selectbox("Bent Housing (Graus)", [1.15, 1.25, 1.50, 1.75, 1.83, 2.00, 2.12, 2.38, 2.60, 2.77, 3.00], key="bent")
estabilizacao = st.sidebar.radio("Tipo de BHA", ["Slick", "Stabilized"], key="tipo_bha")

# Apague qualquer outro 'arquivo_banco = st.sidebar.file_uploader(...)' que estiver sobrando para baixo no seu código!

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
        
# ==========================================
# MÓDULO DE ACOMPANHAMENTO DIRECIONAL E PROJEÇÕES
# Baseado no Petroguia (Pág. D-19) e Ouija-Board
# ==========================================
st.markdown("---")
st.header("🎯 Acompanhamento Direcional (Mínima Curvatura)")

import math

col_s1, col_s2 = st.columns(2)

with col_s1:
    st.write("**Estação Atual (Último Survey)**")
    md1 = st.number_input("Profundidade Medida - MD 1 (m)", min_value=0.0, value=1000.0, step=10.0, format="%.2f")
    inc1 = st.number_input("Inclinação - I1 (graus)", min_value=0.0, max_value=180.0, value=10.0, step=0.1, format="%.2f")
    az1 = st.number_input("Azimute - A1 (graus)", min_value=0.0, max_value=360.0, value=45.0, step=0.1, format="%.2f")
    
    st.write("*Coordenadas Atuais:*")
    c_tvd1, c_ns1, c_ew1 = st.columns(3)
    tvd1 = c_tvd1.number_input("TVD 1 (m)", value=995.0, step=1.0)
    ns1 = c_ns1.number_input("N/S 1 (m)", value=50.0, step=1.0)
    ew1 = c_ew1.number_input("E/W 1 (m)", value=50.0, step=1.0)

with col_s2:
    st.write("**Estação Projetada (Próximo Survey / Alvo)**")
    md2 = st.number_input("Profundidade Medida - MD 2 (m)", min_value=md1, value=md1 + 30.0, step=1.0, format="%.2f")
    inc2 = st.number_input("Inclinação - I2 (graus)", min_value=0.0, max_value=180.0, value=12.0, step=0.1, format="%.2f")
    az2 = st.number_input("Azimute - A2 (graus)", min_value=0.0, max_value=360.0, value=50.0, step=0.1, format="%.2f")

# --- CÁLCULO DAS FÓRMULAS DO PETROGUIA (PÁG. D-19) ---
pm = md2 - md1 # Intervalo medido (Pm)

if pm > 0:
    # Conversão de graus para radianos para uso trigonométrico
    i1_rad = math.radians(inc1)
    i2_rad = math.radians(inc2)
    a1_rad = math.radians(az1)
    a2_rad = math.radians(az2)
    
    # Cálculo do Beta em radianos (Severidade entre estações)
    cos_beta = math.cos(i2_rad - i1_rad) - (math.sin(i1_rad) * math.sin(i2_rad) * (1.0 - math.cos(a2_rad - a1_rad)))
    cos_beta = max(-1.0, min(1.0, cos_beta)) # Segurança matemática
    beta_rad = math.acos(cos_beta)
    
    if beta_rad == 0:
        F = 1.0
        dls = 0.0
    else:
        # Fator de suavização (F) e DLS (°/30m)
        F = (2.0 / beta_rad) * math.tan(beta_rad / 2.0)
        dls = beta_rad * (180.0 / math.pi) * (30.0 / pm)
        
    # Variações Parciais e Coordenadas Finais
    delta_ns = (pm / 2.0) * (math.sin(i1_rad) * math.cos(a1_rad) + math.sin(i2_rad) * math.cos(a2_rad)) * F
    delta_ew = (pm / 2.0) * (math.sin(i1_rad) * math.sin(a1_rad) + math.sin(i2_rad) * math.sin(a2_rad)) * F
    pv = (pm / 2.0) * (math.cos(i1_rad) + math.cos(i2_rad)) * F
    af = (pm / 2.0) * (math.sin(i1_rad) + math.sin(i2_rad)) * F
    
    tvd2 = tvd1 + pv
    ns2 = ns1 + delta_ns
    ew2 = ew1 + delta_ew
    
    st.write("---")
    st.write("**📍 Resultados da Projeção de Mínima Curvatura**")
    
    res1, res2, res3, res4, res5 = st.columns(5)
    res1.metric("TVD Final (m)", f"{tvd2:.2f}", f"+ {pv:.2f} m", delta_color="off")
    res2.metric("N/S Final (m)", f"{ns2:.2f}", f"{delta_ns:+.2f} m", delta_color="off")
    res3.metric("E/W Final (m)", f"{ew2:.2f}", f"{delta_ew:+.2f} m", delta_color="off")
    res4.metric("DLS Total (°/30m)", f"{dls:.2f}")
    res5.metric("Afastamento (m)", f"{math.sqrt(ns2**2 + ew2**2):.2f}")
    
   # ==========================================
    # OUIJA-BOARD E ESTRATÉGIA DE SLIDE
    # ==========================================
    st.write("---")
    st.write("### 🧭 Ouija-Board (Orientação da Ferramenta de Desvio)")
    st.markdown("Cálculo da Toolface (GTF) necessária para convergir do Survey 1 para o Alvo 2.")
    
    # Cálculo da Toolface Gravitacional Requerida
    if beta_rad > 0:
        tf_y = math.sin(a2_rad - a1_rad) * math.sin(i2_rad)
        tf_x = math.cos(i2_rad) * math.sin(i1_rad) - math.sin(i2_rad) * math.cos(i1_rad) * math.cos(a2_rad - a1_rad)
        tf_rad = math.atan2(tf_y, tf_x)
        tf_deg = math.degrees(tf_rad)
        if tf_deg < 0:
            tf_deg += 360.0
    else:
        tf_deg = 0.0

    c_ob1, c_ob2, c_ob3 = st.columns(3)
    c_ob1.metric("Toolface Requerida (GTF)", f"{tf_deg:.0f}°")
    c_ob2.metric("DLS Necessário na Seção", f"{dls:.2f} °/30m")
    
    # --- BUSCA INSTANTÂNEA NO BANCO EMBUTIDO ---
    build_rate_banco = 0.0
    try:
        filtro_motor = df_motores[
            (df_motores['Modelo'] == modelo) & 
            (df_motores['Diametro_Externo_OD'] == od) &
            (df_motores['Bent_Housing_Graus'] == float(bent)) &
            (df_motores['Tipo_Estabilizacao'] == estabilizacao)
        ]
        
        if not filtro_motor.empty and 'Build_Rate' in filtro_motor.columns:
            build_rate_banco = float(filtro_motor.iloc[0]['Build_Rate'])
    except Exception as e:
        pass

    # Define o valor final: usa o do banco se achar, senão faz a estimativa
    valor_padrao_br = build_rate_banco if build_rate_banco > 0 else float(max(round(dls + 0.5, 1), 2.0))

    # Input do Build Rate
    build_rate = c_ob3.number_input("Build Rate da Ferramenta (°/30m)", 
                                    value=valor_padrao_br, 
                                    step=0.1, 
                                    help="Dogleg severity (DLS) esperado do conjunto em modo Slide.")
    
    if build_rate_banco > 0:
        c_ob3.success(f"✅ Motor Encontrado!")
    else:
        c_ob3.warning(f"⚠️ Motor não cadastrado. Usando estimativa.")
    
    if build_rate > 0:
        # Lógica de perfuração (Slide vs Rotate)
        slide_meters = (dls / build_rate) * pm
        
        if slide_meters > pm:
            st.warning(f"⚠️ **Atenção:** O Build Rate do seu motor ({build_rate:.1f} °/30m) é INSUFICIENTE para atingir esse alvo. Para convergir em {pm:.0f}m, você precisa de um conjunto com pelo menos **{dls:.2f} °/30m** ou precisará aumentar a metragem de avanço (MD 2).")
        else:
            rotary_meters = pm - slide_meters
            st.success(f"✅ **Estratégia Recomendada:**\n1. Deslize (Slide) **{slide_meters:.1f} m** orientando a Toolface em **{tf_deg:.0f}°**.\n2. Perfure Rotativo os **{rotary_meters:.1f} m** restantes para atingir o alvo de {inc2}° de Inc e {az2}° de Azimute.")

    with st.expander("Ver Variáveis de Cálculo (Mínima Curvatura)"):
        st.code(f"Intervalo (Pm) = {pm:.2f} m\nFator de Suavização (F) = {F:.6f}\nÂngulo Beta (rad) = {beta_rad:.6f}\nIntervalo Vertical (pv) = {pv:.2f} m", language="text")

elif pm == 0:
    st.info("Altere a MD 2 para calcular a projeção.")
else:
    st.error("A MD Projetada (MD 2) não pode ser menor que a MD Atual.")

# ==========================================
# MÓDULO DE ANÁLISE DE BHA (TENDÊNCIA)
# ==========================================
st.markdown("---")
st.header("🔧 Análise de Tendência da BHA")
st.markdown("Verifique o comportamento natural da ferramenta em modo rotativo com base na posição dos estabilizadores.")

col7, col8 = st.columns(2)

with col7:
    st.write("**Posição dos Estabilizadores**")
    dist_primeiro_estab = st.number_input("Distância da broca até o 1º Estabilizador (m)", value=1.5, step=0.5)
    dist_segundo_estab = st.number_input("Distância da broca até o 2º Estabilizador (m)", value=10.5, step=0.5)

with col8:
    st.write("**Diagnóstico da BHA**")
    
    tendencia = ""
    efeito = ""
    cor = "normal"
    
    # LÓGICA BÁSICA DE COMPORTAMENTO DA BHA
    # 1. Avalia se o 1º Estabilizador é Near Bit (muito perto da broca, ex: < 2.5m)
    if dist_primeiro_estab <= 2.5:
        # Se o 2º Estabilizador estiver perto (Packed) ou longe (Fulcrum)
        if (dist_segundo_estab - dist_primeiro_estab) <= 6.0:
            tendencia = "PACKED HOLE (Rígida)"
            efeito = "Tendência de MANTER o ângulo e azimute (Hold)."
            cor = "blue"
        else:
            tendencia = "FULCRUM (Alavanca)"
            efeito = "Tendência de GANHO de ângulo (Build)."
            cor = "red"
            
    # 2. Avalia se o 1º Estabilizador está distante da broca (Pendulum)
    elif dist_primeiro_estab > 2.5 and dist_primeiro_estab <= 15.0:
        tendencia = "PENDULUM (Pêndulo)"
        efeito = "Tendência de QUEDA de ângulo (Drop)."
        cor = "orange"
        
    else:
        tendencia = "BHA LISa (Slick) / Indefinida"
        efeito = "Comportamento instável. Depende da rigidez dos comandos."
        cor = "gray"

    # Exibição do Resultado
    st.info(f"**Tipo de Montagem:** {tendencia}")
    st.success(f"**Efeito no Poço:** {efeito}")
    
    # Explicação interativa
    with st.expander("Por que isso acontece?"):
        st.write("A distância entre os estabilizadores altera onde a ferramenta encosta na parede do poço. Em uma BHA Fulcrum, o peso aplicado (WOB) dobra a ferramenta acima do primeiro estabilizador, forçando a broca para a parede superior do poço. Já no Pendulum, o peso dos comandos abaixo do primeiro estabilizador age como um pêndulo, puxando a broca para o centro da terra.")

# ==========================================
# MÓDULO DE ENGENHARIA E HIDRÁULICA DO MOTOR
# ==========================================
st.markdown("---")
st.header("⚙️ Dashboard de Engenharia e Desempenho")
st.markdown("Cálculos de RPM, Potência, Eficiência e Perda de Carga do Motor.")

col9, col10, col11 = st.columns(3)

with col9:
    st.write("**Parâmetros Operacionais**")
    vazao_gpm = st.number_input("Vazão da Bomba (GPM)", value=400.0, step=10.0)
    rpm_superficie = st.number_input("Rotação da Superfície/Top Drive (RPM)", value=40.0, step=5.0)
    
    # BUSCA DIRETO NO BANCO DE DADOS EMBUTIDO
    rev_gal_teorico = 0.0
    try:
        filtro = df_motores[(df_motores['Modelo'] == modelo) & 
                            (df_motores['Diametro_Externo_OD'] == od) & 
                            (df_motores['Bent_Housing_Graus'] == float(bent)) & 
                            (df_motores['Tipo_Estabilizacao'] == estabilizacao)]
        if not filtro.empty and 'Rev_Gal' in filtro.columns:
            rev_gal_teorico = float(filtro.iloc[0]['Rev_Gal'])
    except Exception:
        pass
            
    rev_gal = st.number_input("Fator do Motor (Rev/Gal)", value=float(rev_gal_teorico), step=0.01)
    peso_lama_ppg = st.number_input("Peso da Lama (ppg)", value=9.0, step=0.1)

with col10:
    st.write("**Parâmetros de Fundo e PDM**")
    tvd_m = st.number_input("TVD (m)", value=1000.0, step=10.0)
    torque_lbft = st.number_input("Torque Gerado (lb-ft)", value=2500.0, step=100.0)
    pressao_dif = st.number_input("Pressão Diferencial Lida (psi)", value=300.0, step=10.0)
    
    # BUSCA DE OFF-BOTTOM (Se existir na tabela, senão usa estimativa padrão)
    off_bottom_manual = 0.0
    try:
        if not filtro.empty and 'Off_Bottom_psi' in filtro.columns:
            off_bottom_manual = float(filtro.iloc[0]['Off_Bottom_psi'])
    except Exception:
        pass
            
    off_bottom_calc = st.number_input("Off-Bottom (psi)", value=float(off_bottom_manual) if off_bottom_manual > 0 else 250.0, step=10.0)
    motor_total_press_drop = off_bottom_calc + pressao_dif

with col11:
    st.write("**Desempenho Calculado**")
    
    rpm_motor = vazao_gpm * rev_gal
    st.metric(label="Velocidade Total da Broca", value=f"{(rpm_motor + rpm_superficie):.0f} RPM", 
              delta=f"Motor: {rpm_motor:.0f} | Mesa: {rpm_superficie:.0f}", delta_color="off")
    
    hp_mec = (torque_lbft * rpm_motor) / 5252 if rpm_motor > 0 else 0
    st.metric(label="Potência Mecânica (Motor)", value=f"{hp_mec:.1f} HP")
    
    st.metric(label="ΔP Total do Motor", value=f"{motor_total_press_drop:.0f} psi", 
              delta=f"Diff: {pressao_dif:.0f} | Off-Bot: {off_bottom_calc:.0f}", delta_color="off")# ==========================================

# ==========================================
# MÓDULO DE HIDRÁULICA DA BROCA E POÇO
# ==========================================
st.markdown("---")
st.header("🌊 Dashboard de Hidráulica")

col12, col13 = st.columns(2)

with col12:
    st.write("**Parâmetros da Broca e Poço**")
    tfa = st.number_input("TFA da Broca (in²)", value=0.450, step=0.001, format="%.3f")
    dh = st.number_input("Diâmetro do Poço / Hole Diameter (in)", value=8.5, step=0.125)

with col13:
    st.write("**Resultados Hidráulicos na Broca**")
    if tfa > 0:
        bit_press_drop = (vazao_gpm**2 * peso_lama_ppg) / (10858 * (tfa**2))
        jet_velocity_m = ((0.32086 * vazao_gpm) / tfa) * 0.3048
    else:
        bit_press_drop = 0
        jet_velocity_m = 0
        
    st.metric(label="Queda de Pressão na Broca (ΔP)", value=f"{bit_press_drop:.0f} psi")
    st.metric(label="Velocidade do Jato", value=f"{jet_velocity_m:.1f} m/s")
    
# ==========================================
# MÓDULO DE COMPOSIÇÃO DA COLUNA (BHA + DP)
# ==========================================
st.markdown("---")
st.header("📊 Composição da Coluna e Análise de Seção")

# Variáveis globais de rastreamento
vol_total_interno_bha = 0.0
vol_total_anular_bha = 0.0
peso_total_bha = 0.0
comp_total_bha = 0.0 

if arquivo_bha is not None:
    try:
        df_bha = pd.read_excel(arquivo_bha, header=None, skiprows=11, nrows=8)
        resultados_bha = []
        
        for index, row in df_bha.iterrows():
            comp_nome = str(row[4]) if pd.notna(row[4]) else str(row[3]) 
            desc_upper = comp_nome.upper()
            od_ferramenta = pd.to_numeric(row[5], errors='coerce')
            id_val = row[6]
            
            # RESGATE DOS PESOS COMPLETOS
            peso_raw = str(row[9]) if pd.notna(row[9]) else ""
            wt_lb_ft, comp_wt_klbs, tot_wt_klbs = "-", "-", "-"
            if peso_raw and "/" in peso_raw:
                partes = [p.strip() for p in peso_raw.split("/")]
                if len(partes) >= 1: wt_lb_ft = partes[0]
                if len(partes) >= 2: 
                    comp_wt_klbs = partes[1]
                    try: peso_total_bha += float(comp_wt_klbs.replace(',', '.'))
                    except: pass
                if len(partes) >= 3: tot_wt_klbs = partes[2]
            
            comp_individual = pd.to_numeric(row[10], errors='coerce')
            if pd.isna(comp_individual): comp_individual = 0.0
            
            id_ferramenta, v_anular_m, vol_interno_bbl, vol_anular_bbl = "-", 0, 0, 0
            
            if pd.notna(od_ferramenta) and od_ferramenta > 0:
                comp_total_bha += comp_individual
                
                if "BROCA" in desc_upper:
                    id_ferramenta = "TFA"
                    if tfa > 0: v_anular_m = ((0.32086 * vazao_gpm) / tfa) * 60 * 0.3048
                else:
                    if "PDM" in desc_upper or "CAMISA" in desc_upper or "MOTOR" in desc_upper: id_ferramenta = 2.50
                    elif "STB" in desc_upper or "ESTABILIZADOR" in desc_upper or "DRILL COLLAR" in desc_upper or "DC " in desc_upper: id_ferramenta = 2.8125
                    elif pd.isna(id_val) or str(id_val).strip() == "" or id_val == 0:
                        if any(ferramenta in desc_upper for ferramenta in ["UBHO", "GAP", "MONEL"]): id_ferramenta = 3.25
                        else: id_ferramenta = "-"
                    else:
                        id_ferramenta = pd.to_numeric(id_val, errors='coerce')
                        if pd.isna(id_ferramenta): id_ferramenta = "-"
                    
                    if (dh**2 - od_ferramenta**2) > 0:
                        v_anular_m = ((24.51 * vazao_gpm) / (dh**2 - od_ferramenta**2)) * 0.3048
                        cap_anular_bbl_m = (((dh**2) - (od_ferramenta**2)) / 1029.4) * 3.28084
                        vol_anular_bbl = cap_anular_bbl_m * comp_individual
                        vol_total_anular_bha += vol_anular_bbl
                    
                    if isinstance(id_ferramenta, (int, float)) and id_ferramenta > 0:
                        cap_int_bbl_m = ((id_ferramenta**2) / 1029.4) * 3.28084
                        vol_interno_bbl = cap_int_bbl_m * comp_individual
                        vol_total_interno_bha += vol_interno_bbl
                
                resultados_bha.append({
                    "Componente": comp_nome, "OD": od_ferramenta, "ID": id_ferramenta,
                    "lb/ft": wt_lb_ft, "Comp(klbs)": comp_wt_klbs, "Acum(klbs)": tot_wt_klbs,
                    "C (m)": round(comp_individual, 2), "Vel (m/min)": round(v_anular_m, 1),
                    "V Int (bbl)": round(vol_interno_bbl, 2) if vol_interno_bbl > 0 else "-",
                    "V Anu (bbl)": round(vol_anular_bbl, 2) if vol_anular_bbl > 0 else "-"
                })
        
        if len(resultados_bha) > 0:
            st.write(f"**1. Bottom Hole Assembly (BHA)** - Comprimento Total: {comp_total_bha:.2f} m")
            df_resultados = pd.DataFrame(resultados_bha)
            def colorir(val):
                if isinstance(val, (int, float)):
                    if val < 30: return 'background-color: #ffcccc; color: black;'
                    elif val > 60 and val < 1000: return 'background-color: #ffe6cc; color: black;'
                    elif val >= 1000: return 'background-color: #cce5ff; color: black;'
                    return 'background-color: #ccffcc; color: black;'
                return ''
            st.dataframe(df_resultados.style.map(colorir, subset=['Vel (m/min)']), use_container_width=True)
            
            # WOB disponível na BHA
            bf = 1.0 - (peso_lama_ppg / 65.5)
            peso_disp = peso_total_bha * bf
            st.info(f"⚖️ **WOB Máximo Disponível (BHA Flutuada):** {peso_disp:.1f} klbs | **Peso no Ar:** {peso_total_bha:.1f} klbs")
            
    except Exception as e:
        st.error(f"Erro ao processar BHA: {e}")
else:
    st.info("👆 Carregue o Tally da BHA (Excel) para ver a seção inferior.")

# --- SEÇÃO DOS DRILL PIPES ---
st.write("**2. Drill Pipes (DP)**")
dp_specs = {
    "DP 5\" - 19.5 lb/ft (S135)": {"OD": 5.0, "ID": 4.276, "Peso": 19.5},
    "DP 5\" - 25.6 lb/ft (HWDP)": {"OD": 5.0, "ID": 3.000, "Peso": 25.6},
    "DP 4\" - 14.0 lb/ft (S135)": {"OD": 4.0, "ID": 3.340, "Peso": 14.0}
}

col_dp1, col_dp2 = st.columns(2)
with col_dp1: dp_escolhido = st.selectbox("Selecione o Drill Pipe:", list(dp_specs.keys()), key="dp_select")
with col_dp2:
    # PERMITE CASAS DECIMAIS PARA FRAÇÃO DE JUNTA
    qtd_dp = st.number_input("Quantidade (Juntas)", min_value=0.00, value=50.00, step=0.01, format="%.2f", key="dp_qtd")
    comp_medio_dp = st.number_input("Comp. Médio (m/junta)", min_value=0.0, value=9.5, step=0.1, key="dp_comp")

comp_total_dp = qtd_dp * comp_medio_dp
od_dp = dp_specs[dp_escolhido]["OD"]
id_dp = dp_specs[dp_escolhido]["ID"]
peso_linear_dp = dp_specs[dp_escolhido]["Peso"]

v_anular_dp_m, vol_int_dp, vol_anular_dp, peso_total_dp_klbs = 0, 0, 0, 0

if comp_total_dp > 0:
    if (dh**2 - od_dp**2) > 0: v_anular_dp_m = ((24.51 * vazao_gpm) / (dh**2 - od_dp**2)) * 0.3048
    vol_anular_dp = ((((dh**2) - (od_dp**2)) / 1029.4) * 3.28084) * comp_total_dp
    vol_int_dp = (((id_dp**2) / 1029.4) * 3.28084) * comp_total_dp
    peso_total_dp_klbs = (comp_total_dp * 3.28084 * peso_linear_dp) / 1000

    col_dpr1, col_dpr2, col_dpr3 = st.columns(3)
    col_dpr1.metric("Metragem de DP", f"{comp_total_dp:.2f} m")
    col_dpr2.metric("Vel. Anular no DP", f"{v_anular_dp_m:.1f} m/min")
    col_dpr3.metric("Peso no Ar (DP)", f"{peso_total_dp_klbs:.1f} klbs")

# ==========================================
# RESUMO GLOBAL: PESO, VOLUMETRIA, TEMPOS E ECD
# ==========================================
st.markdown("---")
st.header("⚖️ Resumo Global e Dinâmica do Poço")

# Somatórios
profundidade_md = comp_total_bha + comp_total_dp
vol_int_poco = vol_total_interno_bha + vol_int_dp
vol_anu_poco = vol_total_anular_bha + vol_anular_dp
vol_total_sistema = vol_int_poco + vol_anu_poco
peso_total_coluna = peso_total_bha + peso_total_dp_klbs

# Flutuação
bf = 1.0 - (peso_lama_ppg / 65.5)
peso_flutuado_coluna = peso_total_coluna * bf

st.write("**Profundidade e Peso da Coluna**")
col_g1, col_g2, col_g3, col_g4 = st.columns(4)
col_g1.metric("Profundidade (MD)", f"{profundidade_md:.1f} m", help="Soma total do comprimento BHA + DP.")
col_g2.metric("Hook Load (Flutuado)", f"{peso_flutuado_coluna:.1f} klbs")
col_g3.metric("Volume Anular", f"{vol_anu_poco:.1f} bbl")
col_g4.metric("Volume Total (Ciclo)", f"{vol_total_sistema:.1f} bbl")

# --- NOVO: SEÇÃO DE TELEMETRIA E ECD ---
st.write("**Telemetria MWD e Leitura de ECD**")
telemetria = st.radio("Selecione o tipo de transmissão MWD:", ["EM (Eletromagnético)", "PP (Mud Pulse)"], horizontal=True)

if "EM" in telemetria:
    st.info("📡 **Telemetria EM:** ECD calculado com base na leitura direta do PWD ou estimativa calibrada.")
else:
    st.warning("📳 **Telemetria PP:** Valor de ECD **ESTIMADO** matematicamente. Como não há PWD acoplado, o cálculo baseia-se na perda de carga anular teórica e pressão (SPP).")

# O campo e o cálculo agora ficam fora do "if", aparecendo para ambos os casos!
delta_p_anular = st.number_input("Perda de Carga Anular Estimada (psi)", value=150.0, step=10.0, help="Pressão gasta para elevar o fluido pelo anular (estimada ou via PWD).")

tvd_ft = tvd_m * 3.28084
if tvd_ft > 0:
    ecd_ppg = peso_lama_ppg + (delta_p_anular / (0.052 * tvd_ft))
else:
    ecd_ppg = peso_lama_ppg
    
st.metric("Equivalent Circulating Density (ECD)", f"{ecd_ppg:.2f} ppg", delta=f"+ {(ecd_ppg - peso_lama_ppg):.2f} ppg", delta_color="inverse")

# --- TEMPOS DE CIRCULAÇÃO ---
st.write("**Tempos de Circulação e Bomba**")
bbl_stroke = st.number_input("Capacidade da Bomba (bbl/stk)", value=0.117, step=0.001, format="%.3f")

if vazao_gpm > 0 and bbl_stroke > 0:
    vazao_bbl_min = vazao_gpm / 42.0 
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Surface to Bit (Descer Pílula)", f"{(vol_int_poco / vazao_bbl_min):.0f} min", f"{(vol_int_poco / bbl_stroke):.0f} stks", delta_color="off")
    c2.metric("Bottom Up (Retorno de Fundo)", f"{(vol_anu_poco / vazao_bbl_min):.0f} min", f"{(vol_anu_poco / bbl_stroke):.0f} stks", delta_color="off")
    c3.metric("Ciclo Completo", f"{(vol_total_sistema / vazao_bbl_min):.0f} min", f"{(vol_total_sistema / bbl_stroke):.0f} stks", delta_color="off")
