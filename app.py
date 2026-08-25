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
arquivo_banco = st.sidebar.file_uploader("Carregar Banco de Motores (CSV)", type=["csv"], key="banco_csv")
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
st.markdown("Cálculos de RPM, Potência e Eficiência baseados nas fórmulas oficiais da Intrepid.")

col9, col10, col11 = st.columns(3)

with col9:
    st.write("**Parâmetros Operacionais**")
    vazao_gpm = st.number_input("Vazão da Bomba (GPM)", value=400.0, step=10.0)
    rpm_superficie = st.number_input("Rotação da Superfície/Top Drive (RPM)", value=40.0, step=5.0)
    
    # Busca automática do Fator do Motor (Rev/Gal) no Banco de Dados
    rev_gal_teorico = 0.0
    if arquivo_banco is not None:
        try:
            df = pd.read_csv(arquivo_banco)
            filtro = df[(df['Modelo'] == modelo) & 
                        (df['Diametro_Externo_OD'] == od) & 
                        (df['Bent_Housing_Graus'] == float(bent)) & 
                        (df['Tipo_Estabilizacao'] == estabilizacao)]
            
            if not filtro.empty and 'Rev_Gal' in filtro.columns:
                rev_gal_teorico = filtro.iloc[0]['Rev_Gal']
        except Exception as e:
            st.error("Erro ao ler o Fator do Motor do arquivo.")
            
    rev_gal = st.number_input("Fator do Motor (Rev/Gal)", value=float(rev_gal_teorico), step=0.01)
    peso_lama_ppg = st.number_input("Peso da Lama (ppg)", value=9.0, step=0.1)

with col10:
    st.write("**Parâmetros de Fundo**")
    tvd_m = st.number_input("TVD (m)", value=1000.0, step=10.0)
    pressao_dif = st.number_input("Pressão Diferencial Lida (psi)", value=300.0, step=10.0)
    torque_lbft = st.number_input("Torque Gerado (lb-ft)", value=2500.0, step=100.0)

with col11:
    st.write("**Desempenho Calculado**")
    
    # 1. Rotações (RPM do Motor + Superfície)
    rpm_motor = vazao_gpm * rev_gal
    bit_speed_total = rpm_motor + rpm_superficie
    
    st.metric(label="Velocidade Total da Broca", 
              value=f"{bit_speed_total:.0f} RPM", 
              delta=f"Motor: {rpm_motor:.0f} RPM | Superfície: {rpm_superficie:.0f} RPM", 
              delta_color="off")
    
    # 2. Potência Mecânica (HPm) - O cálculo de engenharia usa apenas o RPM interno do Motor
    hp_mec = (torque_lbft * rpm_motor) / 5252 if rpm_motor > 0 else 0
    st.metric(label="Potência Mecânica (Motor)", value=f"{hp_mec:.1f} HP")
    
    # 3. Eficiência do Motor (%) - Também baseada apenas no desempenho hidráulico/mecânico do motor
    if (vazao_gpm * pressao_dif) > 0:
        eficiencia = (32.64 * torque_lbft * rpm_motor) / (vazao_gpm * pressao_dif)
    else:
        eficiencia = 0
        
    if eficiencia > 80:
        st.success(f"**Eficiência do Motor:** {eficiencia:.1f} %")
    elif eficiencia > 50:
        st.warning(f"**Eficiência do Motor:** {eficiencia:.1f} %")
    else:
        st.error(f"**Eficiência do Motor:** {eficiencia:.1f} %")
    
    # 4. Pressão Hidrostática (psi)
    tvd_ft = tvd_m * 3.28084
    ph = 0.052 * tvd_ft * peso_lama_ppg
    st.info(f"**Pressão Hidrostática:** {ph:.0f} psi")

# ==========================================
# MÓDULO DE HIDRÁULICA AVANÇADA (BHA REAL)
# ==========================================
st.markdown("---")
st.header("🌊 Dashboard de Hidráulica Avançada")
st.markdown("Cálculos de velocidade anular com base nas seções reais da BHA carregada.")

col12, col13 = st.columns(2)

with col12:
    st.write("**Parâmetros da Broca**")
    tfa = st.number_input("TFA da Broca (in²)", value=0.450, step=0.001, format="%.3f")
    dh = st.number_input("Diâmetro do Poço / Hole Diameter (in)", value=8.5, step=0.125)

with col13:
    st.write("**Resultados Hidráulicos na Broca**")
    
    # 1. Queda de Pressão na Broca
    if tfa > 0:
        bit_press_drop = (vazao_gpm**2 * peso_lama_ppg) / (10858 * (tfa**2))
    else:
        bit_press_drop = 0
    
    st.metric(label="Queda de Pressão na Broca (ΔP)", value=f"{bit_press_drop:.0f} psi")
    if bit_press_drop > 1500:
        st.error("⚠️ Queda de pressão na broca excedeu 1500 psi. Risco ao mancal do motor!")
        
    # 2. Velocidade do Jato (convertido para m/s)
    if tfa > 0:
        jet_velocity_m = ((0.32086 * vazao_gpm) / tfa) * 0.3048
    else:
        jet_velocity_m = 0
    st.metric(label="Velocidade do Jato", value=f"{jet_velocity_m:.1f} m/s")

# ==========================================
# ANÁLISE SEÇÃO POR SEÇÃO (HIDRÁULICA, VOLUMETRIA E PESOS)
# ==========================================
st.subheader("📊 Análise Completa da BHA (Hidráulica, Volumes e Pesos)")

if arquivo_bha is not None:
    try:
        # Leitura Direta: Pula as 11 primeiras linhas e lê da linha 12 até a 19
        df_bha = pd.read_excel(arquivo_bha, header=None, skiprows=11, nrows=8)
        
        resultados_bha = []
        vol_total_interno = 0.0
        vol_total_anular = 0.0
        peso_total_bha = 0.0
        
        for index, row in df_bha.iterrows():
            comp_nome = str(row[4]) if pd.notna(row[4]) else str(row[3]) 
            desc_upper = comp_nome.upper()
            
            # Coluna F (OD) e G (ID)
            od_ferramenta = pd.to_numeric(row[5], errors='coerce')
            id_val = row[6]
            
            # Coluna J (Índice 9) -> Tratamento da string "Wt[lb/ft] / Comp Wt[klbs] / Tot Wt[klbs]"
            peso_raw = str(row[9]) if pd.notna(row[9]) else ""
            wt_lb_ft, comp_wt_klbs, tot_wt_klbs = "-", "-", "-"
            
            if peso_raw and "/" in peso_raw:
                partes = [p.strip() for p in peso_raw.split("/")]
                if len(partes) >= 1: 
                    wt_lb_ft = partes[0]
                if len(partes) >= 2: 
                    comp_wt_klbs = partes[1]
                    # Soma o peso do componente (em klbs) ao Totalizador Geral da BHA
                    try:
                        peso_total_bha += float(comp_wt_klbs.replace(',', '.'))
                    except:
                        pass
                if len(partes) >= 3:
                    tot_wt_klbs = partes[2]
            
            # Coluna K (Comprimento individual) e L (Comprimento acumulado)
            comp_individual = pd.to_numeric(row[10], errors='coerce')
            comp_acumulado = pd.to_numeric(row[11], errors='coerce')
            
            if pd.isna(comp_individual):
                comp_individual = 0.0
            
            id_ferramenta = "-"
            v_anular_m = 0
            vol_interno_bbl = 0
            vol_anular_bbl = 0
            
            if pd.notna(od_ferramenta) and od_ferramenta > 0:
                
                # ----------------------------------------------------
                # LÓGICA DA BROCA
                # ----------------------------------------------------
                if "BROCA" in desc_upper:
                    id_ferramenta = "TFA"
                    if tfa > 0:
                        v_anular_m = ((0.32086 * vazao_gpm) / tfa) * 60 * 0.3048
                    
                # ----------------------------------------------------
                # LÓGICA TUBULARES E MOTOR
                # ----------------------------------------------------
                else:
                    # Regras de Negócio de ID
                    if "PDM" in desc_upper or "CAMISA" in desc_upper or "MOTOR" in desc_upper:
                        id_ferramenta = 2.50
                    elif "STB" in desc_upper or "ESTABILIZADOR" in desc_upper:
                        id_ferramenta = 2.8125
                    elif "DRILL COLLAR" in desc_upper or "DC " in desc_upper:
                        id_ferramenta = 2.8125
                    elif pd.isna(id_val) or str(id_val).strip() == "" or id_val == 0:
                        if any(ferramenta in desc_upper for ferramenta in ["UBHO", "GAP", "MONEL"]):
                            id_ferramenta = 3.25
                        else:
                            id_ferramenta = "-"
                    else:
                        id_ferramenta = pd.to_numeric(id_val, errors='coerce')
                        if pd.isna(id_ferramenta):
                            id_ferramenta = "-"
                    
                    # Cálculos Hidráulicos
                    if (dh**2 - od_ferramenta**2) > 0:
                        v_anular_ft = (24.51 * vazao_gpm) / (dh**2 - od_ferramenta**2)
                        v_anular_m = v_anular_ft * 0.3048
                        
                        cap_anular_bbl_m = (((dh**2) - (od_ferramenta**2)) / 1029.4) * 3.28084
                        vol_anular_bbl = cap_anular_bbl_m * comp_individual
                        vol_total_anular += vol_anular_bbl
                    
                    if isinstance(id_ferramenta, (int, float)) and id_ferramenta > 0:
                        cap_int_bbl_m = ((id_ferramenta**2) / 1029.4) * 3.28084
                        vol_interno_bbl = cap_int_bbl_m * comp_individual
                        vol_total_interno += vol_interno_bbl
                
                # Adiciona à lista final
                resultados_bha.append({
                    "Componente": comp_nome,
                    "OD (in)": od_ferramenta,
                    "ID (in)": id_ferramenta,
                    "Peso Comp (klbs)": comp_wt_klbs,
                    "Peso Acum (klbs)": tot_wt_klbs,
                    "Comp (m)": round(comp_individual, 2),
                    "Vel (m/min)": round(v_anular_m, 1),
                    "Vol Int (bbl)": round(vol_interno_bbl, 2) if vol_interno_bbl > 0 else "-",
                    "Vol Anu (bbl)": round(vol_anular_bbl, 2) if vol_anular_bbl > 0 else "-"
                })
        
        if len(resultados_bha) > 0:
            df_resultados = pd.DataFrame(resultados_bha)
            
            def colorir_velocidade(val):
                if isinstance(val, (int, float)):
                    if val < 30: return 'background-color: #ffcccc; color: black;'
                    elif val > 60 and val < 1000: return 'background-color: #ffe6cc; color: black;'
                    elif val >= 1000: return 'background-color: #cce5ff; color: black;'
                    return 'background-color: #ccffcc; color: black;'
                return ''
            
            st.dataframe(df_resultados.style.map(colorir_velocidade, subset=['Vel (m/min)']), use_container_width=True)
            
            # ==========================================
            # CÁLCULOS DE ENGENHARIA (FLUTUAÇÃO E PESOS)
            # ==========================================
            # Fator de Flutuação (BF) para Aço Carbono
            # O peso_lama_ppg é puxado do input lá do início do painel!
            bf = 1.0 - (peso_lama_ppg / 65.5)
            peso_disponivel = peso_total_bha * bf
            
            st.write("---")
            st.write("### ⚖️ Resumo de Peso e Volumetria")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric(label="Volume Interno da BHA", value=f"{vol_total_interno:.2f} bbl")
            col_v2.metric(label="Volume Anular da BHA", value=f"{vol_total_anular:.2f} bbl")
            col_v3.metric(label="Peso Total da BHA (Ar)", value=f"{peso_total_bha:.2f} klbs")
            
            col_v4, col_v5, col_v6 = st.columns(3)
            col_v4.metric(label="Fator de Flutuação (BF)", value=f"{bf:.4f}")
            col_v5.metric(label="Peso Disponível (Flutuado)", value=f"{peso_disponivel:.2f} klbs")
            col_v6.info(f"Baseado na lama de {peso_lama_ppg:.1f} ppg")
            
        else:
            st.warning("Não foram encontrados dados de OD válidos nas linhas 12 a 19.")
            
    except Exception as e:
        st.error(f"Erro ao processar as células do Excel: {e}")
else:
    st.info("👆 Carregue o Tally da BHA (Excel) na barra lateral para calcular a Hidráulica Seção por Seção.")

# ==========================================
# MÓDULO DE DRILL PIPES E MOTOR (PERDA DE CARGA)
# ==========================================
st.markdown("---")
st.header("🪈 Drill Pipes e Especificações do Motor")

# Dicionário de Drill Pipes: Substitua esses valores pelos pesos e IDs reais que você me passar!
# Formato: "Nome no Menu": {"OD": polegadas, "ID": polegadas, "Peso": lb/ft}
dp_specs = {
    "DP 5\" - 19.5 lb/ft (S135)": {"OD": 5.0, "ID": 4.276, "Peso": 19.5},
    "DP 5\" - 25.6 lb/ft (HWDP)": {"OD": 5.0, "ID": 3.000, "Peso": 25.6},
    "DP 4\" - 14.0 lb/ft (S135)": {"OD": 4.0, "ID": 3.340, "Peso": 14.0}
}

col_dp1, col_dp2, col_dp3 = st.columns(3)

with col_dp1:
    st.write("**Especificação dos Tubos**")
    dp_escolhido = st.selectbox("Selecione o Drill Pipe:", list(dp_specs.keys()))
    
with col_dp2:
    st.write("**Metragem na Coluna**")
    qtd_dp = st.number_input("Quantidade (Juntas)", min_value=0, value=50, step=10)
    comp_medio_dp = st.number_input("Comprimento Médio (m/junta)", min_value=0.0, value=9.5, step=0.1)

with col_dp3:
    st.write("**Perda de Carga do Motor**")
    # Este campo permite ao direcional inserir a perda de carga do motor girando em vazio (Off-bottom pressure drop) 
    # ou a pressão diferencial máxima, conforme o manual da Intrepid.
    motor_no_load = st.number_input("Perda de Carga (psi)", value=250.0, step=10.0, help="Pressão gasta pelo fluxo da lama passando pelo motor, conforme o manual.")

# ==========================================
# MÓDULO DE DRILL PIPES E MOTOR (PERDA DE CARGA)
# ==========================================
st.markdown("---")
st.header("🪈 Drill Pipes e Hidráulica do Motor")

# Dicionário de Drill Pipes: Substitua pelo OD, ID e Peso reais da sua operação
dp_specs = {
    "DP 5\" - 19.5 lb/ft (S135)": {"OD": 5.0, "ID": 4.276, "Peso": 19.5},
    "DP 5\" - 25.6 lb/ft (HWDP)": {"OD": 5.0, "ID": 3.000, "Peso": 25.6},
    "DP 4\" - 14.0 lb/ft (S135)": {"OD": 4.0, "ID": 3.340, "Peso": 14.0}
}

col_dp1, col_dp2, col_dp3 = st.columns(3)

with col_dp1:
    st.write("**Especificação dos Tubos**")
    dp_escolhido = st.selectbox("Selecione o Drill Pipe:", list(dp_specs.keys()), key="dp_select")
    
with col_dp2:
    st.write("**Metragem na Coluna**")
    qtd_dp = st.number_input("Quantidade (Juntas)", min_value=0, value=50, step=10, key="dp_qtd")
    comp_medio_dp = st.number_input("Comprimento Médio (m/junta)", min_value=0.0, value=9.5, step=0.1, key="dp_comp")

with col_dp3:
    st.write("**Perda de Carga do Motor (PDM)**")
    
    # Valor padrão de segurança caso o arquivo falhe
    off_bottom_calc = 250.0 
    
    if arquivo_banco is not None:
        try:
            # Lê o banco de motores carregado na barra lateral
            df_motores = pd.read_csv(arquivo_banco)
            
            # Filtra o motor exato que o direcional escolheu
            filtro_motor = df_motores[(df_motores['Modelo'] == modelo) & 
                                      (df_motores['Diametro_Externo_OD'] == od) &
                                      (df_motores['Lobulos'] == lobulos)]
            
            if not filtro_motor.empty and 'Off_Bottom_psi' in filtro_motor.columns:
                off_bottom_calc = float(filtro_motor.iloc[0]['Off_Bottom_psi'])
                st.success("✅ Off-Bottom importado do Banco de Dados!")
            else:
                st.warning("⚠️ Motor não encontrado no CSV. Usando 250 psi como padrão.")
        except Exception as e:
            st.error("Erro ao ler o manual no CSV.")
    else:
        st.info("ℹ️ Banco de Motores não carregado. Usando 250 psi como padrão.")
            
    # Cálculo automático: Off-Bottom (Manual) + Pressão Diferencial Aplicada (WOB)
    motor_total_press_drop = off_bottom_calc + pressao_dif
    
    st.metric(label="ΔP Total do Motor", value=f"{motor_total_press_drop:.0f} psi", 
              delta=f"Off-Bot: {off_bottom_calc:.0f} | Diff: {pressao_dif:.0f}", 
              delta_color="off")

# ----------------------------------------------------
# CÁLCULOS TOTAIS DA STRING (DP)
# ----------------------------------------------------
comp_total_dp = qtd_dp * comp_medio_dp
od_dp = dp_specs[dp_escolhido]["OD"]
id_dp = dp_specs[dp_escolhido]["ID"]
peso_linear_dp = dp_specs[dp_escolhido]["Peso"]

if comp_total_dp > 0:
    # 1. Velocidade Anular ao redor do DP
    if (dh**2 - od_dp**2) > 0:
        v_anular_dp_ft = (24.51 * vazao_gpm) / (dh**2 - od_dp**2)
        v_anular_dp_m = v_anular_dp_ft * 0.3048
    else:
        v_anular_dp_m = 0
        
    # 2. Volumes do DP (bbl)
    cap_anular_dp_m = (((dh**2) - (od_dp**2)) / 1029.4) * 3.28084
    vol_anular_dp = cap_anular_dp_m * comp_total_dp
    
    cap_int_dp_m = ((id_dp**2) / 1029.4) * 3.28084
    vol_int_dp = cap_int_dp_m * comp_total_dp
    
    # 3. Peso do DP (klbs)
    peso_total_dp_klbs = (comp_total_dp * 3.28084 * peso_linear_dp) / 1000
    
    st.success(f"✅ **Coluna Adicionada:** {comp_total_dp:.1f} metros de {dp_escolhido}")
    
    # Exibe os dados do Drill Pipe calculados
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Vel. Anular (DP)", f"{v_anular_dp_m:.1f} m/min")
    col_r2.metric("Vol. Interno (DP)", f"{vol_int_dp:.1f} bbl")
    col_r3.metric("Vol. Anular (DP)", f"{vol_anular_dp:.1f} bbl")
    col_r4.metric("Peso no Ar (DP)", f"{peso_total_dp_klbs:.1f} klbs")
