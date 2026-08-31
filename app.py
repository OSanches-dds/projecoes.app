import streamlit as st
import pandas as pd
import math
import numpy as np
import base64
from fpdf import FPDF
import datetime

# ==========================================
# DICIONÁRIO DE IDIOMAS (i18n)
# ==========================================
textos = {
    "Português": {
        "title_main": "🎯 Assistente de Controle Direcional",
        "lang_header": "🌍 Idioma / Language",
        "bha_header": "📁 Entrada da BHA",
        "method": "Método de Entrada:",
        "opt_excel": "Excel (Tally)",
        "opt_smart": "Construtor Inteligente",
        "msg_smart": "🤖 Construtor Inteligente Ativado",
        "std_config": "Configuração Padrão (Petroguia)",
        "bit_label": "**Broca**",
        "bit_type": "Tipo",
        "bit_height": "Altura (m)",
        "lwd_label": "**Sensores LWD (Oliden)**",
        "lwd_select": "Adicionar Ferramentas:",
        "custom_options": "**Opções Customizadas**",
        "motor_config": "⚙️ Configuração do Motor",
        "well_data": "📍 Dados do Poço e Target",
        "btn_calc": "🚀 Calcular Projeção e Orientação",
        "res_inst": "📊 Resultados e Instruções",
        "prev_surv": "Survey Anterior",
        "curr_surv": "Survey Atual",
        "target": "Target (Alvo)",
        "head_proj": "🎯 Acompanhamento Direcional (Mínima Curvatura)",
        "head_eng": "⚙️ Engenharia e Hidráulica do Motor",
        "head_bha": "📊 Composição da Coluna e Análise de Seção",
        "head_auto": "🛠️ Análise Automática da BHA e Jar Placement",
        "head_hyd": "🌊 Dashboard de Hidráulica Integrado",
        "head_glob": "⚖️ Resumo Global e Dinâmica do Poço",
        "head_pdf": "📄 Relatório de Engenharia Direcional",
        "fluid_param": "**Parâmetros de Fluido e Vazão**",
        "rheology": "**Reologia**",
        "downhole_param": "**Parâmetros de Fundo e PDM**",
        "calc_perf": "**Desempenho Calculado**",
        "btn_pdf": "Gerar Relatório em PDF"
    },
    "English": {
        "title_main": "🎯 Directional Control Assistant",
        "lang_header": "🌍 Language",
        "bha_header": "📁 BHA Input",
        "method": "Input Method:",
        "opt_excel": "Excel (Tally)",
        "opt_smart": "Smart Builder",
        "msg_smart": "🤖 Smart Builder Activated",
        "std_config": "Standard Configuration",
        "bit_label": "**Drill Bit**",
        "bit_type": "Type",
        "bit_height": "Length (m)",
        "lwd_label": "**LWD Sensors (Oliden)**",
        "lwd_select": "Add Tools:",
        "custom_options": "**Custom Options**",
        "motor_config": "⚙️ Motor Configuration",
        "well_data": "📍 Well & Target Data",
        "btn_calc": "🚀 Calculate Projection & Orientation",
        "res_inst": "📊 Results & Instructions",
        "prev_surv": "Previous Survey",
        "curr_surv": "Current Survey",
        "target": "Target",
        "head_proj": "🎯 Directional Tracking (Minimum Curvature)",
        "head_eng": "⚙️ Motor Engineering & Hydraulics",
        "head_bha": "📊 String Composition & Section Analysis",
        "head_auto": "🛠️ Automatic BHA Analysis & Jar Placement",
        "head_hyd": "🌊 Integrated Hydraulics Dashboard",
        "head_glob": "⚖️ Global Summary & Well Dynamics",
        "head_pdf": "📄 Directional Engineering Report",
        "fluid_param": "**Fluid & Flow Parameters**",
        "rheology": "**Rheology**",
        "downhole_param": "**Downhole & PDM Parameters**",
        "calc_perf": "**Calculated Performance**",
        "btn_pdf": "Generate PDF Report"
    },
    "Español": {
        "title_main": "🎯 Asistente de Control Direccional",
        "lang_header": "🌍 Idioma",
        "bha_header": "📁 Entrada de BHA",
        "method": "Método de Entrada:",
        "opt_excel": "Excel (Tally)",
        "opt_smart": "Constructor Inteligente",
        "msg_smart": "🤖 Constructor Inteligente Activado",
        "std_config": "Configuración Estándar",
        "bit_label": "**Broca / Trépano**",
        "bit_type": "Tipo",
        "bit_height": "Altura (m)",
        "lwd_label": "**Sensores LWD (Oliden)**",
        "lwd_select": "Agregar Herramientas:",
        "custom_options": "**Opciones Personalizadas**",
        "motor_config": "⚙️ Configuración del Motor",
        "well_data": "📍 Datos del Pozo y Objetivo",
        "btn_calc": "🚀 Calcular Proyección y Orientación",
        "res_inst": "📊 Resultados e Instrucciones",
        "prev_surv": "Survey Anterior",
        "curr_surv": "Survey Actual",
        "target": "Objetivo (Target)",
        "head_proj": "🎯 Seguimiento Direccional (Mínima Curvatura)",
        "head_eng": "⚙️ Ingeniería e Hidráulica del Motor",
        "head_bha": "📊 Composición de la Sarta y Análisis de Sección",
        "head_auto": "🛠️ Análisis Automático de BHA y Jar Placement",
        "head_hyd": "🌊 Dashboard de Hidráulica Integrado",
        "head_glob": "⚖️ Resumen Global y Dinámica del Pozo",
        "head_pdf": "📄 Reporte de Ingeniería Direccional",
        "fluid_param": "**Parámetros de Fluido y Caudal**",
        "rheology": "**Reología**",
        "downhole_param": "**Parámetros de Fondo y PDM**",
        "calc_perf": "**Rendimiento Calculado**",
        "btn_pdf": "Generar Reporte PDF"
    }
}

# ==========================================
# CABEÇALHO COM LOGO E TÍTULO
# ==========================================
st.set_page_config(page_title="Intrepid Direcional", layout="wide")

col_logo, col_titulo = st.columns([1.5, 4.5])
try:
    col_logo.image("logo_intrepid.png", width=280) 
except Exception:
    pass

# --- SINCRONIZAÇÃO GLOBAL DE VARIÁVEIS ---
if 'wob_side' not in st.session_state:
    st.session_state.wob_side = 40.0
if 'wob_main' not in st.session_state:
    st.session_state.wob_main = 40.0

def sync_from_side():
    st.session_state.wob_main = st.session_state.wob_side

def sync_from_main():
    st.session_state.wob_side = st.session_state.wob_main
# ==========================================

# ==========================================
# FUNÇÕES MATEMÁTICAS
# ==========================================
def calcular_dogleg(inc1, az1, inc2, az2):
    i1, a1 = np.radians(inc1), np.radians(az1)
    i2, a2 = np.radians(inc2), np.radians(az2)
    dl_rad = np.arccos(np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(a2 - a1))
    return np.degrees(dl_rad)

def calcular_direcional(inc1, az1, md1, inc2, az2, md2):
    i1, a1 = np.radians(inc1), np.radians(az1)
    i2, a2 = np.radians(inc2), np.radians(az2)
    delta_md = md2 - md1
    if delta_md <= 0:
        return 0.0, 0.0
    dl_rad = np.arccos(np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(a2 - a1))
    dl_deg = np.degrees(dl_rad)
    dls_30m = dl_deg * (30.0 / delta_md)
    y = np.sin(i2) * np.sin(a2 - a1)
    x = np.sin(i2) * np.cos(i1) * np.cos(a2 - a1) - np.sin(i1) * np.cos(i2)
    tf_rad = np.arctan2(y, x)
    tf_deg = np.degrees(tf_rad)
    if tf_deg < 0:
        tf_deg += 360
    return dls_30m, tf_deg

def parse_weight(val):
    try:
        return float(str(val).replace(',', '.'))
    except ValueError:
        return 0.0
    
# ==========================================
# BANCO DE DADOS DE MOTORES EMBUTIDO
# ==========================================
dados_motores = [
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 3.80, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26, "Perda_Vazio_psi": 46},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 6.83, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26, "Perda_Vazio_psi": 46},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 6.20, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26, "Perda_Vazio_psi": 46},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 9.08, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26, "Perda_Vazio_psi": 46},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 9.71, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26, "Perda_Vazio_psi": 46},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 2.6", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 11.21, "Torque_Max": 5250, "Pressao_D": 590, "Rev_Gal": 0.26, "Perda_Vazio_psi": 46},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 3.90, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52, "Perda_Vazio_psi": 64},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.08, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52, "Perda_Vazio_psi": 64},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 6.79, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52, "Perda_Vazio_psi": 64},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.60, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52, "Perda_Vazio_psi": 64},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 10.90, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52, "Perda_Vazio_psi": 64},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "4 3/4", "Lobulos": "7/8 3.8", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 12.97, "Torque_Max": 4450, "Pressao_D": 860, "Rev_Gal": 0.52, "Perda_Vazio_psi": 64},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 1.20, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.24, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.21, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.15, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.74, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 11.96, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.7", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 7.29, "Torque_Max": 13720, "Pressao_D": 1280, "Rev_Gal": 0.24, "Perda_Vazio_psi": 106},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.7", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.97, "Torque_Max": 13720, "Pressao_D": 1280, "Rev_Gal": 0.24, "Perda_Vazio_psi": 106},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 5.70, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.50, "Perda_Vazio_psi": 184},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.71, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.50, "Perda_Vazio_psi": 184},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 8.30, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.50, "Perda_Vazio_psi": 184},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "4/5 7.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.65, "Torque_Max": 9090, "Pressao_D": 1580, "Rev_Gal": 0.50, "Perda_Vazio_psi": 184},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 9.80, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.30, "Perda_Vazio_psi": 150},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 9.20, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.30, "Perda_Vazio_psi": 150},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.75, "Tipo_Estabilizacao": "Slick", "Build_Rate": 11.20, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.30, "Perda_Vazio_psi": 150},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "6 3/4", "Lobulos": "7/8 5.0", "Bent_Housing_Graus": 1.75, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.70, "Torque_Max": 10460, "Pressao_D": 1130, "Rev_Gal": 0.30, "Perda_Vazio_psi": 150},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 3.4", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 1.20, "Torque_Max": 22530, "Pressao_D": 800, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 3.4", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 4.11, "Torque_Max": 22530, "Pressao_D": 800, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 3.4", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.74, "Torque_Max": 22530, "Pressao_D": 800, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 3.4", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 5.69, "Torque_Max": 22530, "Pressao_D": 800, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 3.4", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 4.49, "Torque_Max": 22530, "Pressao_D": 800, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 3.4", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 7.18, "Torque_Max": 22530, "Pressao_D": 800, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 5.9", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 1.20, "Torque_Max": 22020, "Pressao_D": 1330, "Rev_Gal": 0.17, "Perda_Vazio_psi": 134},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 5.9", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 4.11, "Torque_Max": 22020, "Pressao_D": 1330, "Rev_Gal": 0.17, "Perda_Vazio_psi": 134},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 5.9", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.74, "Torque_Max": 22020, "Pressao_D": 1330, "Rev_Gal": 0.17, "Perda_Vazio_psi": 134},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 5.9", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 5.69, "Torque_Max": 22020, "Pressao_D": 1330, "Rev_Gal": 0.17, "Perda_Vazio_psi": 134},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 5.9", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 4.49, "Torque_Max": 22020, "Pressao_D": 1330, "Rev_Gal": 0.17, "Perda_Vazio_psi": 134},
    {"Modelo": "GyroDrill", "Diametro_Externo_OD": "9 5/8", "Lobulos": "7/8 5.9", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 7.18, "Torque_Max": 22020, "Pressao_D": 1330, "Rev_Gal": 0.17, "Perda_Vazio_psi": 134},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Slick", "Build_Rate": 1.20, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.15, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.24, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.21, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 10.15, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Slick", "Build_Rate": 2.74, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "8", "Lobulos": "7/8 4.0", "Bent_Housing_Graus": 1.83, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 11.96, "Torque_Max": 14930, "Pressao_D": 900, "Rev_Gal": 0.17, "Perda_Vazio_psi": 126},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "9 5/8", "Lobulos": "5/6 4.0", "Bent_Housing_Graus": 1.25, "Tipo_Estabilizacao": "Slick", "Build_Rate": 4.70, "Torque_Max": 23990, "Pressao_D": 1000, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "9 5/8", "Lobulos": "5/6 4.0", "Bent_Housing_Graus": 1.25, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 7.30, "Torque_Max": 23990, "Pressao_D": 1000, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "9 5/8", "Lobulos": "5/6 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Slick", "Build_Rate": 5.80, "Torque_Max": 23990, "Pressao_D": 1000, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "9 5/8", "Lobulos": "5/6 4.0", "Bent_Housing_Graus": 1.50, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 8.60, "Torque_Max": 23990, "Pressao_D": 1000, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "9 5/8", "Lobulos": "5/6 4.0", "Bent_Housing_Graus": 1.75, "Tipo_Estabilizacao": "Slick", "Build_Rate": 7.00, "Torque_Max": 23990, "Pressao_D": 1000, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70},
    {"Modelo": "Tomahawk", "Diametro_Externo_OD": "9 5/8", "Lobulos": "5/6 4.0", "Bent_Housing_Graus": 1.75, "Tipo_Estabilizacao": "Stabilized", "Build_Rate": 9.90, "Torque_Max": 23990, "Pressao_D": 1000, "Rev_Gal": 0.09, "Perda_Vazio_psi": 70}
]
df_motores = pd.DataFrame(dados_motores)

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.header("🌍 Idioma / Language")
idioma = st.sidebar.selectbox("Selecione / Select:", ["Português", "English", "Español"])
t = textos[idioma]

col_titulo.markdown(f"<h1 style='margin-top: 10px;'>{t['title_main']}</h1>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header(t["bha_header"])
modo_bha = st.sidebar.radio(t["method"], [t["opt_excel"], t["opt_smart"]])

arquivo_bha = None
if modo_bha == t["opt_excel"]:
    arquivo_bha = st.sidebar.file_uploader(t["opt_excel"], type=["xlsx", "xls"], key="bha_excel")
elif modo_bha == t["opt_smart"]:
    st.sidebar.success(t["msg_smart"])
    config_bha = st.sidebar.selectbox(t["std_config"], 
        ["Fulcrum (Build)", "Semi-Fulcrum", "Empacada (Packed)", "Pendulum (Drop)", "Semi-Pendulum", "Customizada"])
    
    dh_manual = st.sidebar.number_input("Diâmetro da Broca/Poço (in)" if idioma == "Português" else "Bit/Hole Size (in)", value=8.5, step=0.125)
    
    st.sidebar.write(t["bit_label"])
    col_b1, col_b2 = st.sidebar.columns(2)
    tipo_broca = col_b1.selectbox(t["bit_type"], ["PDC", "Tricônica" if idioma == "Português" else "Tricone"])
    comp_broca = col_b2.number_input(t["bit_height"], value=0.25 if tipo_broca == "PDC" else 0.40, step=0.01)

    st.sidebar.write("**Sensores MWD Intrepid**")
    tipo_mwd = st.sidebar.selectbox("Tecnologia MWD", ["MWD PP", "MWD EM"])

    st.sidebar.write(t["lwd_label"])
    lwd_opcoes = st.sidebar.multiselect(t["lwd_select"], 
        ["Oliden - Azimuthal GR / Resistividade", "Oliden - Densidade / Neutrão", "Oliden - Sônico"])

    if config_bha == "Customizada":
        st.sidebar.write(t["custom_options"])
        usar_stb_custom = st.sidebar.checkbox("Incluir STB de Coluna?" if idioma == "Português" else "Include String STB?", value=True)
        pos_stb = "Nenhuma"
        if usar_stb_custom:
            opcoes_pos = ["Abaixo do MWD/LWD", "Acima do MWD/LWD", "Acima dos Comandos"] if idioma == "Português" else ["Below MWD/LWD", "Above MWD/LWD", "Above Drill Collars"]
            pos_stb_sel = st.sidebar.selectbox("Posição do STB" if idioma == "Português" else "STB Position", opcoes_pos)
            pos_stb = ["Abaixo do MWD/LWD", "Acima do MWD/LWD", "Acima dos Comandos"][opcoes_pos.index(pos_stb_sel)]
        
        col_c1, col_c2 = st.sidebar.columns(2)
        qtd_dc = col_c1.number_input("Qtd. Comandos (DC)" if idioma == "Português" else "DC Qty", min_value=0, value=2, step=1)
        qtd_hwdp_custom = col_c2.number_input("Qtd. HWDP" if idioma == "Português" else "HWDP Qty", min_value=0, value=15, step=1)
    
    st.sidebar.write("**Balanço de Peso e Jar**" if idioma == "Português" else "**Weight Balance & Jar**")
    wob_builder = st.sidebar.number_input("WOB Máximo Planejado (klbf)" if idioma == "Português" else "Max Planned WOB (klbf)", 
                                          step=5.0, 
                                          key="wob_side", 
                                          on_change=sync_from_side)
    usar_jar = st.sidebar.checkbox("Incluir Drilling Jar Automático" if idioma == "Português" else "Include Auto Drilling Jar", value=True)

st.sidebar.markdown("---")
st.sidebar.header(t["motor_config"])
modelo = st.sidebar.selectbox("Modelo do Motor", ["GyroDrill", "Tomahawk"], key="modelo_motor")
od = st.sidebar.selectbox("Diâmetro Externo (OD)", ["4 3/4", "5", "6 1/2", "6 3/4", "7", "7 3/4", "8", "9 5/8"], key="od_motor")

# Filtro dinâmico: busca os lóbulos exatos baseados no Modelo e OD selecionados
opcoes_lobulos = df_motores[(df_motores['Modelo'] == modelo) & (df_motores['Diametro_Externo_OD'] == od)]['Lobulos'].unique().tolist()

# Trava de segurança caso o usuário selecione uma combinação inexistente (ex: Tomahawk de 5")
if not opcoes_lobulos:
    opcoes_lobulos = ["Não disponível para este OD"]

lobulos = st.sidebar.selectbox("Lóbulos e Estágios", opcoes_lobulos, key="lobulos")
bent = st.sidebar.selectbox("Bent Housing (Graus)", [1.15, 1.25, 1.50, 1.75, 1.83, 2.00, 2.12, 2.38, 2.60, 2.77, 3.00], key="bent")
estabilizacao = st.sidebar.radio("Tipo de BHA", ["Slick", "Stabilized"], key="tipo_bha")

# ==========================================
# TELA PRINCIPAL - SURVEYS E PROJEÇÃO
# ==========================================
st.header(t["well_data"])
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader(t["prev_surv"])
    md_ant = st.number_input("MD (m)", value=970.0, step=1.0, key="md_ant")
    inc_ant = st.number_input("Inc (°)", value=8.5, step=0.1, key="inc_ant")
    az_ant = st.number_input("Az (°)", value=40.0, step=0.1, key="az_ant")
with col2:
    st.subheader(t["curr_surv"])
    md_atual = st.number_input("MD (m)", value=1000.0, step=1.0, key="md_atual")
    inc_atual = st.number_input("Inc (°)", value=10.0, step=0.1, key="inc_atual")
    az_atual = st.number_input("Az (°)", value=45.0, step=0.1, key="az_atual")
    st.markdown("---")
    lbl_slide = "Slide Realizado (m)" if idioma == "Português" else "Slide Drilled (m)" if idioma == "English" else "Slide Realizado (m)"
    slide_realizado = st.number_input(lbl_slide, value=0.0, step=0.1)
with col3:
    st.subheader(t["target"])
    md_alvo = st.number_input("MD (m)", value=1030.0, step=1.0, key="md_alvo")
    inc_alvo = st.number_input("Inc (°)", value=12.0, step=0.1, key="inc_alvo")
    az_alvo = st.number_input("Az (°)", value=48.0, step=0.1, key="az_alvo")

st.markdown("---")
if st.button(t["btn_calc"]):
    st.header(t["res_inst"])
    dl_trecho = calcular_dogleg(inc_ant, az_ant, inc_atual, az_atual)
    motor_yield_real = (dl_trecho * (30.0 / slide_realizado)) if slide_realizado > 0 else 0.0
    dls_req, tf_req = calcular_direcional(inc_atual, az_atual, md_atual, inc_alvo, az_alvo, md_alvo)
    
    build_rate_30m = 0.0
    filtro = df_motores[(df_motores['Modelo'] == modelo) & (df_motores['Diametro_Externo_OD'] == od) & (df_motores['Bent_Housing_Graus'] == float(bent)) & (df_motores['Tipo_Estabilizacao'] == estabilizacao)]
    if not filtro.empty:
        build_rate_30m = float(filtro.iloc[0]['Build_Rate']) * (30.0 / 30.48)
            
    rendimento_usado = motor_yield_real if motor_yield_real > 0 else build_rate_30m
    origem_rendimento = "REAL" if motor_yield_real > 0 else "TEÓRICO / THEORETICAL"
    
    st.info(f"**Motor:** {modelo} {od}\" | **Bent:** {bent}° | **BR:** {build_rate_30m:.2f} °/30m")
    if motor_yield_real > 0:
        st.success(f"**Motor Yield Real:** {motor_yield_real:.2f} °/30m")
    
    col4, col5, col6 = st.columns(3)
    col4.metric(label="DLS" if idioma == "English" else "DLS", value=f"{dls_req:.2f} °/30m")
    col5.metric(label="Toolface", value=f"{tf_req:.0f}° R")
    
    if rendimento_usado > 0:
        pm_alvo = md_alvo - md_atual # Calcula a distância real do trecho
        slide_m = (dls_req / rendimento_usado) * pm_alvo # Multiplica pela distância real
        
        if slide_m > pm_alvo:
            st.error("Alvo inatingível com o Build Rate atual!" if idioma == "Português" else "Unreachable target with current Build Rate!" if idioma == "English" else "¡Objetivo inalcanzable con el Build Rate actual!")
        else:
            col6.metric(label="Slide (m)", value=f"{slide_m:.1f} m", delta=origem_rendimento, delta_color="off")
    else:
        col6.metric(label="Slide (m)", value="-")

# ==========================================
# MÓDULO DE ACOMPANHAMENTO DIRECIONAL (MÍNIMA CURVATURA)
# ==========================================
st.markdown("---")
st.header(t["head_proj"])

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.write(f"**{t['curr_surv']}**")
    md1 = st.number_input("MD 1 (m)", min_value=0.0, value=1000.0, step=10.0, format="%.2f", key="mc_md1")
    inc1 = st.number_input("I1 (°)", min_value=0.0, max_value=180.0, value=10.0, step=0.1, format="%.2f", key="mc_i1")
    az1 = st.number_input("A1 (°)", min_value=0.0, max_value=360.0, value=45.0, step=0.1, format="%.2f", key="mc_a1")
    c_tvd1, c_ns1, c_ew1 = st.columns(3)
    tvd1 = c_tvd1.number_input("TVD 1 (m)", value=995.0, step=1.0)
    ns1 = c_ns1.number_input("N/S 1 (m)", value=50.0, step=1.0)
    ew1 = c_ew1.number_input("E/W 1 (m)", value=50.0, step=1.0)

with col_s2:
    st.write(f"**{t['target']}**")
    md2 = st.number_input("MD 2 (m)", min_value=md1, value=md1 + 30.0, step=1.0, format="%.2f", key="mc_md2")
    inc2 = st.number_input("I2 (°)", min_value=0.0, max_value=180.0, value=12.0, step=0.1, format="%.2f", key="mc_i2")
    az2 = st.number_input("A2 (°)", min_value=0.0, max_value=360.0, value=50.0, step=0.1, format="%.2f", key="mc_a2")

tf_deg, dls, slide_meters, rotary_meters = 0.0, 0.0, 0.0, 0.0 
pm = md2 - md1 

if pm > 0:
    i1_rad, i2_rad = math.radians(inc1), math.radians(inc2)
    a1_rad, a2_rad = math.radians(az1), math.radians(az2)
    cos_beta = max(-1.0, min(1.0, math.cos(i2_rad - i1_rad) - (math.sin(i1_rad) * math.sin(i2_rad) * (1.0 - math.cos(a2_rad - a1_rad)))))
    beta_rad = math.acos(cos_beta)
    
    if beta_rad == 0:
        F, dls = 1.0, 0.0
    else:
        F = (2.0 / beta_rad) * math.tan(beta_rad / 2.0)
        dls = beta_rad * (180.0 / math.pi) * (30.0 / pm)
        
    delta_ns = (pm / 2.0) * (math.sin(i1_rad) * math.cos(a1_rad) + math.sin(i2_rad) * math.cos(a2_rad)) * F
    delta_ew = (pm / 2.0) * (math.sin(i1_rad) * math.sin(a1_rad) + math.sin(i2_rad) * math.sin(a2_rad)) * F
    pv = (pm / 2.0) * (math.cos(i1_rad) + math.cos(i2_rad)) * F
    tvd2, ns2, ew2 = tvd1 + pv, ns1 + delta_ns, ew1 + delta_ew
    
    st.write("---")
    res1, res2, res3, res4, res5 = st.columns(5)
    res1.metric("TVD (m)", f"{tvd2:.2f}", f"+ {pv:.2f} m", delta_color="off")
    res2.metric("N/S (m)", f"{ns2:.2f}", f"{delta_ns:+.2f} m", delta_color="off")
    res3.metric("E/W (m)", f"{ew2:.2f}", f"{delta_ew:+.2f} m", delta_color="off")
    res4.metric("DLS (°/30m)", f"{dls:.2f}")
    res5.metric("Disp. (m)", f"{math.sqrt(ns2**2 + ew2**2):.2f}")
    
    st.write("### 🧭 Ouija-Board")
    if beta_rad > 0:
        # Fórmulas corrigidas para o vetor da Gravity Toolface (GTF)
        tf_y = math.sin(a2_rad - a1_rad) * math.sin(i2_rad)
        tf_x = math.sin(i2_rad) * math.cos(i1_rad) * math.cos(a2_rad - a1_rad) - math.sin(i1_rad) * math.cos(i2_rad)
        tf_deg = math.degrees(math.atan2(tf_y, tf_x))
        if tf_deg < 0: tf_deg += 360.0
    else:
        tf_deg = 0.0

    c_ob1, c_ob2, c_ob3 = st.columns(3)
    c_ob1.metric("GTF Requerida", f"{tf_deg:.0f}°")
    c_ob2.metric("DLS da Seção", f"{dls:.2f} °/30m")
    
    build_rate_banco = 0.0
    try:
        df_m_clean = df_motores.copy()
        filtro_motor = df_m_clean[(df_m_clean['Modelo'].str.upper() == str(modelo).upper()) & 
                                  (df_m_clean['Diametro_Externo_OD'] == str(od)) &
                                  (df_m_clean['Bent_Housing_Graus'] == float(bent)) &
                                  (df_m_clean['Tipo_Estabilizacao'].str.upper() == str(estabilizacao).upper())]
        if not filtro_motor.empty and 'Build_Rate' in filtro_motor.columns:
            build_rate_banco = float(filtro_motor.iloc[0]['Build_Rate'])
    except Exception: pass

    valor_padrao_br = build_rate_banco if build_rate_banco > 0 else float(max(round(dls + 0.5, 1), 2.0))
    build_rate = c_ob3.number_input("Build Rate (°/30m)", value=valor_padrao_br, step=0.1)
    
    if build_rate > 0:
        slide_meters = (dls / build_rate) * pm
        rotary_meters = max(0, pm - slide_meters)
        if slide_meters > pm:
            st.warning(f"⚠️ Build Rate INSUFICIENTE. Precisa de {dls:.2f} °/30m.")
        else:
            st.success(f"✅ Slide **{slide_meters:.1f} m** @ **{tf_deg:.0f}°** | Rotary **{rotary_meters:.1f} m**.")

# ==========================================
# PARÂMETROS DE FLUIDO E POÇO
# ==========================================
st.markdown("---")
st.header("🌊 Parâmetros de Fluido e Poço")
col_f1, col_f2, col_f3, col_f4 = st.columns(4)
peso_lama_ppg = col_f1.number_input("Mud Weight (ppg)", value=9.0, step=0.1)
vazao_gpm = col_f2.number_input("Flow Rate (GPM)", value=450.0, step=10.0)
pv = col_f3.number_input("PV (cP)", value=15.0, step=1.0)
yp = col_f4.number_input("YP (lb/100ft²)", value=25.0, step=1.0)

# ==========================================
# MÓDULO DE ENGENHARIA DO MOTOR (PDM)
# ==========================================
st.markdown("---")
st.header("⚙️ Parâmetros do Motor (PDM)")

col10, col11 = st.columns(2)
with col10:
    st.write("**Parâmetros Operacionais de Fundo**")
    rpm_superficie = st.number_input("Surface RPM", value=40.0, step=5.0)
    torque_lbft = st.number_input("Torque (lb-ft)", value=2500.0, step=100.0)
    pressao_dif = st.number_input("Diff Pressure (psi)", value=300.0, step=10.0)
    
    perda_vazio_banco, pressao_d_max, rev_gal = 150.0, 1000.0, 0.5 
    try:
        if 'filtro_motor' in locals() and not filtro_motor.empty:
            perda_vazio_banco = float(filtro_motor.iloc[0].get('Perda_Vazio_psi', 150.0))
            pressao_d_max = float(filtro_motor.iloc[0].get('Pressao_D', 1000.0))
            rev_gal = float(filtro_motor.iloc[0].get('Rev_Gal', 0.5))
    except Exception: pass
            
    st.info(f"⚙️ **No-Load Loss:** {perda_vazio_banco:.0f} psi")
    motor_total_press_drop = perda_vazio_banco + pressao_dif
    
with col11:
    st.write(t["calc_perf"])
    rpm_motor = vazao_gpm * rev_gal
    st.metric(label="Total Bit Speed (RPM)", value=f"{(rpm_motor + rpm_superficie):.0f}", delta=f"Motor: {rpm_motor:.0f} | Mesa: {rpm_superficie:.0f}", delta_color="off")
    hp_mec = (torque_lbft * rpm_motor) / 5252 if rpm_motor > 0 else 0
    st.metric(label="Motor HP", value=f"{hp_mec:.1f} HP")
    st.metric(label="Total ΔP Motor", value=f"{motor_total_press_drop:.0f} psi", delta=f"Diff: {pressao_dif:.0f} | Vazio: {perda_vazio_banco:.0f}", delta_color="off")
    eficiencia = (pressao_dif / pressao_d_max) * 100 if pressao_d_max > 0 else 0.0
    st.metric(label="Eficiência Motor", value=f"{eficiencia:.1f} %", help=f"Max ΔP = {pressao_d_max:.0f} psi")

# ==========================================
# MÓDULO DE COMPOSIÇÃO DA COLUNA (BHA + DP)
# ==========================================
st.markdown("---")
st.header(t["head_bha"])

st.write("**Parâmetros Base do Poço e Broca**")
col_poco1, col_poco2 = st.columns(2)
dh = col_poco1.number_input("Diâmetro do Poço / Hole Diameter (in)", value=dh_manual if modo_bha == t["opt_smart"] else 8.5, step=0.125)
tfa = col_poco2.number_input("TFA da Broca (in²)", value=0.450, step=0.001, format="%.3f")

vol_total_interno_bha = 0.0
vol_total_anular_bha = 0.0
peso_total_bha = 0.0
comp_total_bha = 0.0 
resultados_bha = []

if modo_bha == t["opt_excel"] and arquivo_bha is not None:
    try:
        df_bha = pd.read_excel(arquivo_bha, header=None, skiprows=11, nrows=8)
        for index, row in df_bha.iterrows():
            comp_nome = str(row[4]) if pd.notna(row[4]) else str(row[3]) 
            od_ferramenta = pd.to_numeric(row[5], errors='coerce')
            id_val, peso_raw = row[6], str(row[9]) if pd.notna(row[9]) else ""
            comp_individual = pd.to_numeric(row[10], errors='coerce')
            if pd.isna(comp_individual): comp_individual = 0.0
            comp_wt_klbs = 0.0
            if peso_raw and "/" in peso_raw:
                try: comp_wt_klbs = float([p.strip() for p in peso_raw.split("/")][1].replace(',', '.'))
                except: pass
            id_ferramenta = pd.to_numeric(id_val, errors='coerce') if not pd.isna(id_val) else "-"
            
            qtd_itens = 1
            if comp_individual > 12.0 and not comp_nome.strip()[0].isdigit():
                qtd_itens = max(1, round(comp_individual / 9.4))
                comp_individual = comp_individual / qtd_itens
                comp_wt_klbs = comp_wt_klbs / qtd_itens
            
            resultados_bha.append({
                "Ordem": len(resultados_bha) + 1, "Qtd": qtd_itens,
                "Componente": comp_nome.strip(), "OD": od_ferramenta, "ID": id_ferramenta,
                "C Unitário (m)": comp_individual, "Peso Unit (klbs)": comp_wt_klbs
            })
    except Exception as e: st.error(f"Erro Excel: {e}")

elif modo_bha == t["opt_smart"]:
    stb_fg, stb_ug = dh_manual - 0.125, dh_manual - 0.25
    
    # --- DIMENSIONAMENTO SEGUNDO PETROGUIA (SEÇÃO D) ---
    if dh_manual >= 16.0: od_tub, id_tub, fator_p = 9.5, 3.0, 2.5
    elif dh_manual >= 12.25: od_tub, id_tub, fator_p = 8.0, 2.8125, 1.8
    elif dh_manual >= 8.5: od_tub, id_tub, fator_p = 6.75, 2.25, 1.0
    else: od_tub, id_tub, fator_p = 4.75, 1.50, 0.5
        
    resultados_bha.append({"Qtd": 1, "Componente": f"BROCA {dh_manual}\"", "OD": dh_manual, "ID": "TFA", "C Unitário (m)": comp_broca, "Peso Unit (klbs)": 0.1})
    
    ferramentas_direcionais = []
    if tipo_mwd == "MWD PP":
        ferramentas_direcionais.append({"Qtd": 1, "Componente": f"UBHO {od_tub}\"", "OD": od_tub, "ID": 3.25, "C Unitário (m)": 0.8, "Peso Unit (klbs)": 0.5 * fator_p})
        ferramentas_direcionais.append({"Qtd": 1, "Componente": f"MWD PP {od_tub}\"", "OD": od_tub, "ID": id_tub, "C Unitário (m)": 9.2, "Peso Unit (klbs)": 3.0 * fator_p})
    else:
        ferramentas_direcionais.append({"Qtd": 1, "Componente": f"MWD EM {od_tub}\"", "OD": od_tub, "ID": id_tub, "C Unitário (m)": 9.2, "Peso Unit (klbs)": 3.0 * fator_p})
        ferramentas_direcionais.append({"Qtd": 1, "Componente": f"GAP SUB {od_tub}\"", "OD": od_tub, "ID": 3.25, "C Unitário (m)": 1.5, "Peso Unit (klbs)": 0.8 * fator_p})
        
    ferramentas_direcionais.append({"Qtd": 1, "Componente": f"MONEL NMDC {od_tub}\"", "OD": od_tub, "ID": 2.8125, "C Unitário (m)": 9.2, "Peso Unit (klbs)": 3.1 * fator_p})

    for lwd in lwd_opcoes:
        if "Resistividade" in lwd: ferramentas_direcionais.append({"Qtd": 1, "Componente": f"LWD RES {od_tub}\"", "OD": od_tub, "ID": id_tub, "C Unitário (m)": 5.5, "Peso Unit (klbs)": 1.8 * fator_p})
        elif "Densidade" in lwd: ferramentas_direcionais.append({"Qtd": 1, "Componente": f"LWD DENS {od_tub}\"", "OD": od_tub, "ID": id_tub, "C Unitário (m)": 6.5, "Peso Unit (klbs)": 2.2 * fator_p})
        elif "Sônico" in lwd: ferramentas_direcionais.append({"Qtd": 1, "Componente": f"LWD SONIC {od_tub}\"", "OD": od_tub, "ID": id_tub, "C Unitário (m)": 4.5, "Peso Unit (klbs)": 1.5 * fator_p})

    if config_bha in ["Fulcrum (Build)", "Semi-Fulcrum", "Empacada (Packed)"]:
        stb_escolhido = stb_fg if "Fulcrum" in config_bha or "Packed" in config_bha else stb_ug
        resultados_bha.append({"Qtd": 1, "Componente": f"PDM {od}\" @ CAMISA {stb_escolhido}\"", "OD": float(od.split()[0]), "ID": 2.50, "C Unitário (m)": 8.5, "Peso Unit (klbs)": 2.5})
        resultados_bha.extend(ferramentas_direcionais)
        if "Packed" in config_bha: resultados_bha.append({"Qtd": 1, "Componente": f"STB {stb_fg}\"", "OD": stb_fg, "ID": 2.8125, "C Unitário (m)": 1.5, "Peso Unit (klbs)": 0.5})
        resultados_bha.append({"Qtd": 1, "Componente": f"DRILL COLLAR {od_tub}\"", "OD": od_tub, "ID": 2.8125, "C Unitário (m)": 9.2, "Peso Unit (klbs)": 3.1 * fator_p})
        resultados_bha.append({"Qtd": 1, "Componente": f"STB {stb_ug}\"", "OD": stb_ug, "ID": 2.8125, "C Unitário (m)": 1.5, "Peso Unit (klbs)": 0.5})

    elif config_bha in ["Pendulum (Drop)", "Semi-Pendulum"]:
        stb_escolhido = stb_fg if "Pendulum" in config_bha else stb_ug
        resultados_bha.append({"Qtd": 1, "Componente": f"PDM {od}\" SLICK", "OD": float(od.split()[0]), "ID": 2.50, "C Unitário (m)": 8.5, "Peso Unit (klbs)": 2.5})
        resultados_bha.extend(ferramentas_direcionais)
        resultados_bha.append({"Qtd": 2, "Componente": f"DRILL COLLAR {od_tub}\"", "OD": od_tub, "ID": 2.8125, "C Unitário (m)": 9.2, "Peso Unit (klbs)": 3.1 * fator_p})
        resultados_bha.append({"Qtd": 1, "Componente": f"STB {stb_escolhido}\"", "OD": stb_escolhido, "ID": 2.8125, "C Unitário (m)": 1.5, "Peso Unit (klbs)": 0.5})

    elif config_bha == "Customizada":
        resultados_bha.append({"Qtd": 1, "Componente": f"PDM {od}\" {lobulos}", "OD": float(od.split()[0]), "ID": 2.50, "C Unitário (m)": 8.5, "Peso Unit (klbs)": 2.5})
        if usar_stb_custom and pos_stb == "Abaixo do MWD/LWD":
            resultados_bha.append({"Qtd": 1, "Componente": f"STB {stb_fg}\"", "OD": stb_fg, "ID": 2.8125, "C Unitário (m)": 1.5, "Peso Unit (klbs)": 0.5})
            
        resultados_bha.extend(ferramentas_direcionais)
        
        if usar_stb_custom and pos_stb == "Acima do MWD/LWD":
            resultados_bha.append({"Qtd": 1, "Componente": f"STB {stb_fg}\"", "OD": stb_fg, "ID": 2.8125, "C Unitário (m)": 1.5, "Peso Unit (klbs)": 0.5})
            
        if qtd_dc > 0:
            resultados_bha.append({"Qtd": int(qtd_dc), "Componente": f"DRILL COLLAR {od_tub}\"", "OD": od_tub, "ID": 2.8125, "C Unitário (m)": 9.2, "Peso Unit (klbs)": 3.1 * fator_p})
            
        if usar_stb_custom and pos_stb == "Acima dos Comandos":
            resultados_bha.append({"Qtd": 1, "Componente": f"STB {stb_fg}\"", "OD": stb_fg, "ID": 2.8125, "C Unitário (m)": 1.5, "Peso Unit (klbs)": 0.5})

   # Preenchimento Neutro / Drilling Jar
    # Atualizamos o nome da chave para o peso unitário e usamos o novo wob_side
    peso_atual = sum(item.get("Peso Unit (klbs)", 0.0) * item.get("Qtd", 1) for item in resultados_bha)
    deficit = (st.session_state.wob_side * 1.2 / 0.85) - peso_atual
    peso_hwdp_junta = 1.53 if dh_manual >= 8.5 else 0.8
    qtd_hwdp = max(15, math.ceil(deficit / peso_hwdp_junta)) if deficit > 0 else 15
    
    if usar_jar:
        qtd_hwdp_abaixo = math.ceil(deficit / peso_hwdp_junta) if deficit > 0 else 0
        if qtd_hwdp_abaixo > 0:
            resultados_bha.append({"Qtd": int(qtd_hwdp_abaixo), "Componente": "HWDP 5\"", "OD": 5.0, "ID": 3.0, "C Unitário (m)": 9.4, "Peso Unit (klbs)": peso_hwdp_junta})
        
        resultados_bha.append({"Qtd": 1, "Componente": f"DRILLING JAR {6.25 if dh_manual >= 8.5 else 4.75}\"", "OD": 6.25 if dh_manual >= 8.5 else 4.75, "ID": 2.75, "C Unitário (m)": 9.5, "Peso Unit (klbs)": 2.8 * fator_p})
        
        qtd_hwdp_acima = max(3, 15 - qtd_hwdp_abaixo) if config_bha != "Customizada" else max(1, qtd_hwdp_custom - qtd_hwdp_abaixo)
        resultados_bha.append({"Qtd": int(qtd_hwdp_acima), "Componente": "HWDP 5\"", "OD": 5.0, "ID": 3.0, "C Unitário (m)": 9.4, "Peso Unit (klbs)": peso_hwdp_junta})
    else:
        qtd_final_hwdp = qtd_hwdp if config_bha != "Customizada" else qtd_hwdp_custom
        if qtd_final_hwdp > 0:
            resultados_bha.append({"Qtd": int(qtd_final_hwdp), "Componente": "HWDP", "OD": 5.0, "ID": 3.0, "C Unitário (m)": 9.4, "Peso Unit (klbs)": peso_hwdp_junta})

    for i, item in enumerate(resultados_bha):
        item["Ordem"] = i + 1

# --- TABELA TOTALMENTE CUSTOMIZÁVEL (BHA EDITÁVEL) ---
bha_final = []
acum_klbs = 0.0

if len(resultados_bha) > 0:
    st.write("✏️ **1. Edição da BHA:** O modelo base foi gerado. Altere as **Quantidades (Qtd)** e a **Ordem**. Note que o 'C (m)' e o 'Peso' nesta tabela são valores UNITÁRIOS.")

    df_bha_inputs = pd.DataFrame(resultados_bha)[["Ordem", "Qtd", "Componente", "OD", "ID", "C Unitário (m)", "Peso Unit (klbs)"]]

    df_bha_editado = st.data_editor(
        df_bha_inputs,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_bha"
    )

    bha_para_calcular = df_bha_editado.to_dict('records')
    bha_para_calcular = sorted(bha_para_calcular, key=lambda x: pd.to_numeric(x.get("Ordem", 999), errors='coerce'))

    # Refaz a numeração da ordem para evitar furos ou duplicatas no relatório
    for i, item in enumerate(bha_para_calcular):
        item["Ordem"] = i + 1

    for item in bha_para_calcular:
        qtd = pd.to_numeric(item.get("Qtd", 1), errors='coerce')
        if pd.isna(qtd) or qtd <= 0: qtd = 1
        
        comp_nome = str(item.get("Componente", "")).upper()
        od_f = pd.to_numeric(item.get("OD"), errors='coerce')
        id_f = item.get("ID")
        
        comp_unit = pd.to_numeric(item.get("C Unitário (m)"), errors='coerce')
        peso_unit = pd.to_numeric(item.get("Peso Unit (klbs)"), errors='coerce')
        
        if pd.isna(comp_unit): comp_unit = 0.0
        if pd.isna(peso_unit): peso_unit = 0.0
        
        # O Pulo do Gato: Multiplica os valores unitários pela quantidade informada!
        comp_m = comp_unit * qtd
        peso_k = peso_unit * qtd
        
        v_anu, v_int, v_anu_bbl = 0, 0, 0
        
        if isinstance(od_f, (int, float)) and od_f > 0:
            comp_total_bha += comp_m
            peso_total_bha += peso_k
            acum_klbs += peso_k
            
            if "BROCA" in comp_nome and tfa > 0:
                v_anu = ((0.32086 * vazao_gpm) / tfa) * 60 * 0.3048 if 'vazao_gpm' in locals() else 0
            elif (dh**2 - od_f**2) > 0:
                v_anu = ((24.51 * vazao_gpm) / (dh**2 - od_f**2)) * 0.3048 if 'vazao_gpm' in locals() else 0
                v_anu_bbl = ((((dh**2) - (od_f**2)) / 1029.4) * 3.28084) * comp_m
                vol_total_anular_bha += v_anu_bbl
                
            id_numeric = pd.to_numeric(id_f, errors='coerce')
            if isinstance(id_numeric, (int, float)) and id_numeric > 0:
                v_int = (((id_numeric**2) / 1029.4) * 3.28084) * comp_m
                vol_total_interno_bha += v_int
            
            bha_final.append({
                "Ordem": item["Ordem"], "Qtd": int(qtd),
                "Componente": item["Componente"], "OD": od_f, "ID": id_f,
                "C Total (m)": round(comp_m, 2), "Peso Total (klbs)": round(peso_k, 2), 
                "Acum(klbs)": round(acum_klbs, 2),
                "Vel (m/min)": round(v_anu, 1),
                "V Int (bbl)": round(v_int, 2) if v_int > 0 else "-",
                "V Anu (bbl)": round(v_anu_bbl, 2) if v_anu_bbl > 0 else "-"
            })

    resultados_bha = bha_final

    st.write(f"✅ **2. Resumo Final Calculado da BHA (Com as suas edições)** - Comprimento Total: {comp_total_bha:.2f} m")
    df_resultados = pd.DataFrame(resultados_bha)
    
    def colorir(val):
        if isinstance(val, (int, float)):
            if val < 30: return 'background-color: #ffcccc; color: black;'
            elif val > 60 and val < 1000: return 'background-color: #ffe6cc; color: black;'
            elif val >= 1000: return 'background-color: #cce5ff; color: black;'
            return 'background-color: #ccffcc; color: black;'
        return ''
        
   # Mostramos o resultado final já ordenado e multiplicado!
    st.dataframe(df_resultados.style.map(colorir, subset=['Vel (m/min)']), use_container_width=True, hide_index=True)

else:
    st.info("👆 Utilize a barra lateral para carregar (Excel) ou montar (Construtor Inteligente) a BHA.")

# ==========================================
# SEÇÃO DOS DRILL PIPES
# ==========================================
st.write("**2. Drill Pipes (DP)**")
dp_specs = {
    "DP 5\" - 19.5 lb/ft (S135)": {"OD": 5.0, "ID": 4.276, "Peso": 19.5},
    "DP 5\" - 25.6 lb/ft (HWDP)": {"OD": 5.0, "ID": 3.000, "Peso": 25.6},
    "DP 4\" - 14.0 lb/ft (S135)": {"OD": 4.0, "ID": 3.340, "Peso": 14.0}
}
col_dp1, col_dp2 = st.columns(2)
with col_dp1: dp_escolhido = st.selectbox("Selecione o Drill Pipe:", list(dp_specs.keys()), key="dp_select")
with col_dp2:
    qtd_dp = st.number_input("Qtd Juntas", min_value=0.0, value=50.0, step=0.01, format="%.2f")
    comp_medio_dp = st.number_input("m/junta", min_value=0.0, value=9.5, step=0.1)

comp_total_dp = qtd_dp * comp_medio_dp
od_dp, id_dp, peso_linear_dp = dp_specs[dp_escolhido]["OD"], dp_specs[dp_escolhido]["ID"], dp_specs[dp_escolhido]["Peso"]
v_anular_dp_m, vol_int_dp, vol_anular_dp, peso_total_dp_klbs = 0, 0, 0, 0

if comp_total_dp > 0:
    if (dh**2 - od_dp**2) > 0: v_anular_dp_m = ((24.51 * vazao_gpm) / (dh**2 - od_dp**2)) * 0.3048
    vol_anular_dp = ((((dh**2) - (od_dp**2)) / 1029.4) * 3.28084) * comp_total_dp
    vol_int_dp = (((id_dp**2) / 1029.4) * 3.28084) * comp_total_dp
    peso_total_dp_klbs = (comp_total_dp * 3.28084 * peso_linear_dp) / 1000

    col_dpr1, col_dpr2, col_dpr3, col_dpr4, col_dpr5 = st.columns(5)
    col_dpr1.metric("DP (m)", f"{comp_total_dp:.2f} m")
    col_dpr2.metric("MD Poço", f"{comp_total_bha + comp_total_dp:.2f} m")
    col_dpr3.metric("Vel. Anular DP", f"{v_anular_dp_m:.1f} m/min")
    
    peso_total_coluna = peso_total_bha + peso_total_dp_klbs
    bf = 1.0 - (peso_lama_ppg / 65.5) if 'peso_lama_ppg' in locals() else 0.85
    peso_flutuado_coluna = peso_total_coluna * bf
    
    col_dpr4.metric("Peso Ar Total", f"{peso_total_coluna:.1f} klbs")
    col_dpr5.metric("Hook Load", f"{peso_flutuado_coluna:.1f} klbs")

# ==========================================
# ANÁLISE AUTOMÁTICA E JAR PLACEMENT
# ==========================================
st.markdown("---")
st.header(t["head_auto"])
col_bha1, col_bha2 = st.columns(2)

with col_bha1:
    st.write("**Tendência Geométrica**")
    if len(resultados_bha) > 0:
        distancia_acumulada = 0.0
        estabilizadores_dist = []
        for item in resultados_bha:
            nome_comp = str(item.get('Componente', '')).upper()
            comp_m = parse_weight(item.get('C Total (m)', item.get('C (m)', 0.0)))
            if any(termo in nome_comp for termo in ["PDM", "MOTOR"]) and (estabilizacao == "Stabilized" or "CAMISA" in nome_comp):
                estabilizadores_dist.append(distancia_acumulada + 1.2)
            distancia_acumulada += comp_m
            if any(termo in nome_comp for termo in ["STB", "ESTAB"]) and not any(termo in nome_comp for termo in ["PDM", "MOTOR"]):
                estabilizadores_dist.append(distancia_acumulada)
                
        if not estabilizadores_dist: st.info("📉 **Pendulum Assembly (Drop)**")
        else:
            primeiro_estab = estabilizadores_dist[0]
            if primeiro_estab <= 3.0: 
                if len(estabilizadores_dist) == 1: st.success("📈 **Fulcrum Assembly (Build)**")
                elif len(estabilizadores_dist) == 2:
                    if (estabilizadores_dist[1] - estabilizadores_dist[0]) > 9.0: st.success("📈 **Fulcrum (Build):** 2º STB distante.")
                    else: st.warning("⚖️ **BHA Steerable / Fulcrum Rígido**")
                elif len(estabilizadores_dist) >= 3:
                    if (estabilizadores_dist[1] - estabilizadores_dist[0]) <= 9.0: st.info("⚖️ **Packed Assembly (Hold)**")
                    else: st.success("📈 **Fulcrum Modificado**")
            else: st.info(f"📉 **Pendulum Assembly (Drop)** - Apoio a {primeiro_estab:.1f}m.")

with col_bha2:
    st.write("**Posicionamento do Drilling Jar**")
    
    wob_planejado = st.number_input("WOB Max Planejado (klbf)", 
                                    step=5.0, 
                                    key="wob_main", 
                                    on_change=sync_from_main)
    
    if len(resultados_bha) > 0:
        fator_flutuacao = 1 - (peso_lama_ppg / 65.5)
        fator_inclinacao = math.cos(math.radians(inc1)) if 'inc1' in locals() and inc1 > 0 else 1.0
        margem_seguranca = wob_planejado * 1.2
        
        posicao_jar_atual = next((item for item in resultados_bha if "JAR" in str(item.get('Componente', '')).upper()), None)
        if posicao_jar_atual:
            peso_efetivo = parse_weight(posicao_jar_atual.get('Acum(klbs)', '0')) * fator_flutuacao * fator_inclinacao
            if peso_efetivo < margem_seguranca: st.error(f"🚨 **Alerta de Fadiga:** Peso {peso_efetivo:.1f} klbf < {margem_seguranca:.1f} klbf. Risco de Ponto Neutro.")
            else: st.success(f"✅ **Jar Bem Posicionado:** {peso_efetivo:.1f} klbf operando tracionado.")
        else:
            item_recomendado = None
            for item in resultados_bha:
                peso_efetivo_acumulado = parse_weight(item.get('Acum(klbs)', '0')) * fator_flutuacao * fator_inclinacao
                if peso_efetivo_acumulado >= margem_seguranca:
                    item_recomendado = item.get('Componente', 'Desconhecido')
                    break
            if item_recomendado: st.success(f"💡 **Recomendação:** Posicione o Jar **acima** da ferramenta: **{item_recomendado}**.")
            else: st.error("🚨 **Atenção:** Peso TOTAL da BHA insuficiente para WOB.")

# ==========================================
# DASHBOARD DE HIDRÁULICA E LIMPEZA DE ANULAR
# ==========================================
st.markdown("---")
st.header("🌊 Dashboard de Hidráulica e Limpeza de Poço")

col_h_in1, col_h_in2, col_h_in3 = st.columns(3)
tvd_m = col_h_in1.number_input("TVD (m) - Usado no ECD", value=1000.0, step=10.0)
pressao_bomba = col_h_in2.number_input("Pressão da Bomba (psi)", value=3000.0, step=100.0)
ecd_mwd = col_h_in3.number_input("ECD Real MWD (ppg)", value=0.0, step=0.1)

st.write("---")
col_h1, col_h2 = st.columns(2)

with col_h1:
    st.write("**Performance da Broca (Bit Hydraulics)**")
    
    bit_press_drop = (vazao_gpm**2 * peso_lama_ppg) / (10858 * (tfa**2)) if tfa > 0 else 0
    jet_velocity_fps = (0.32086 * vazao_gpm) / tfa if tfa > 0 else 0
    jet_velocity_m = jet_velocity_fps * 0.3048
    
    hhp_bit = (bit_press_drop * vazao_gpm) / 1714
    area_poco = (math.pi * (dh**2)) / 4
    hsi = hhp_bit / area_poco if area_poco > 0 else 0
    
    jif = (0.000516 * peso_lama_ppg * (vazao_gpm**2)) / tfa if tfa > 0 else 0
    perc_bit_drop = (bit_press_drop / pressao_bomba) * 100 if pressao_bomba > 0 else 0

    status_hsi = "🔴 Baixo" if hsi < 2.0 else "🟢 Ideal" if hsi <= 4.0 else "🟡 Alto"
    status_jif = "🔴 Fraca" if jif < 500 else "🟢 Excelente"
    status_vel = "🔴 Baixa (< 75)" if jet_velocity_m < 75 else "🟢 Ideal" if jet_velocity_m <= 120 else "🟡 Erosiva (> 120)"
    status_perc = "🟢 Ideal" if 50 <= perc_bit_drop <= 65 else "🟡 Fora"

    c_h1a, c_h1b = st.columns(2)
    c_h1a.metric("ΔP Broca (Bit Drop)", f"{bit_press_drop:.0f} psi", f"{perc_bit_drop:.1f}% da Bomba ({status_perc})", delta_color="off")
    c_h1b.metric("Velocidade do Jato", f"{jet_velocity_m:.1f} m/s", status_vel, delta_color="off")
    
    c_h1c, c_h1d = st.columns(2)
    c_h1c.metric("HSI", f"{hsi:.1f} hp/in²", status_hsi, delta_color="off")
    c_h1d.metric("Jet Impact Force", f"{jif:.0f} lbf", status_jif, delta_color="off")

with col_h2:
    st.write("**Fricção Dinâmica e ECD (API RP 13D)**")
    
    delta_p_anular_total = 0.0
    for item in resultados_bha:
        od_f = item.get("OD", 0)
        comp_m = item.get("C Total (m)", item.get("C (m)", 0))
        vel_m_min = item.get("Vel (m/min)", 0)
        if isinstance(od_f, (int, float)) and od_f > 0 and comp_m > 0 and (dh - od_f) > 0:
            L_ft, v_ft_min = comp_m * 3.28084, vel_m_min * 3.28084
            delta_p_anular_total += ((L_ft * pv * v_ft_min) / (60000 * (dh - od_f)**2)) + ((L_ft * yp) / (200 * (dh - od_f)))

    if comp_total_dp > 0 and (dh - od_dp) > 0:
        L_dp_ft, v_dp_ft_min = comp_total_dp * 3.28084, v_anular_dp_m * 3.28084
        delta_p_anular_total += ((L_dp_ft * pv * v_dp_ft_min) / (60000 * (dh - od_dp)**2)) + ((L_dp_ft * yp) / (200 * (dh - od_dp)))

    tvd_ft = tvd_m * 3.28084
    ecd_calc = peso_lama_ppg + (delta_p_anular_total / (0.052 * tvd_ft)) if tvd_ft > 0 else peso_lama_ppg

    c_ecd1, c_ecd2 = st.columns(2)
    c_ecd1.metric("📉 Fricção Anular", f"{delta_p_anular_total:.0f} psi")
    c_ecd2.metric("ECD Teórico (Fundo)", f"{ecd_calc:.2f} ppg", delta=f"+ {(ecd_calc - peso_lama_ppg):.2f} ppg", delta_color="inverse")

    if ecd_mwd > 0:
        diff_ecd = ecd_mwd - ecd_calc
        st.metric("ECD Real", f"{ecd_mwd:.2f} ppg", delta=f"{diff_ecd:.2f} vs Teórico", delta_color="off")
        if diff_ecd > 0.3: st.error("⚠️ **Alerta de Pack-off:** ECD Real muito ACIMA do Teórico.")
        elif diff_ecd < -0.3: st.warning("⚠️ **Atenção:** ECD Real abaixo do esperado.")

st.write("---")
st.write("**Limpeza de Anular (Hole Cleaning Model)**")

# Seletor Inteligente de SG e Vs
col_lit1, col_lit2 = st.columns(2)
litologia = col_lit1.selectbox("Formação / Litologia (Auto SG)", [
    "Folhelho (Shale) - SG 2.60",
    "Arenito (Sandstone) - SG 2.65",
    "Calcário (Limestone) - SG 2.70",
    "Dolomita (Dolomite) - SG 2.85",
    "Sal (Halite) - SG 2.16",
    "Inserir Manualmente"
])

tamanho_cascalho = col_lit2.selectbox("Tamanho do Cascalho (Auto Vs)", [
    "Fino (PDC Alta RPM) - Vs ~35 ft/min",
    "Médio (PDC Normal) - Vs ~49 ft/min",
    "Grosso (Tricônica/Cavings) - Vs ~65 ft/min",
    "Inserir Manualmente"
])

col_hc_in1, col_hc_in2, col_hc_in3 = st.columns(3)
rop_mh = col_hc_in1.number_input("Taxa de Penetração (ROP) [m/h]", value=25.0, step=1.0)

# Lógica de preenchimento automático
if "Manualmente" in tamanho_cascalho:
    vs_ftmin = col_hc_in2.number_input("Vel. Sedimentação (Vs) [ft/min]", value=49.0, step=1.0)
else:
    vs_val = float(tamanho_cascalho.split("~")[1].split(" ")[0])
    vs_ftmin = col_hc_in2.number_input("Vel. Sedimentação (Vs) [ft/min]", value=vs_val, disabled=True)
    
if "Manualmente" in litologia:
    sg_cuttings = col_hc_in3.number_input("Densidade Específica (SG)", value=2.60, step=0.01)
else:
    sg_val = float(litologia.split("SG ")[1])
    sg_cuttings = col_hc_in3.number_input("Densidade Específica (SG)", value=sg_val, disabled=True)

# Validação do DP para a velocidade ascensional principal (Va)
if 'od_dp' in locals() and (dh**2 - od_dp**2) > 0:
    va_ftmin = (24.51 * vazao_gpm) / (dh**2 - od_dp**2)
else:
    va_ftmin = 0.0

if va_ftmin > 0:
    vt_ftmin = va_ftmin - vs_ftmin
    et_perc = (vt_ftmin / va_ftmin) * 100 if va_ftmin > 0 else 0
    
    rop_fthr = rop_mh * 3.28084
    ca_perc = (rop_fthr * (dh**2)) / (14.71 * et_perc * vazao_gpm) if (et_perc > 0 and vazao_gpm > 0) else 0
    
    de_ppg = (sg_cuttings * 8.34 * (ca_perc / 100)) + (peso_lama_ppg * (1 - (ca_perc / 100)))

    c_hc1, c_hc2, c_hc3, c_hc4, c_hc5 = st.columns(5)
    c_hc1.metric("Vel. Ascensional (Va)", f"{va_ftmin:.1f} ft/min")
    c_hc2.metric("Vel. Transporte (Vt)", f"{vt_ftmin:.1f} ft/min")
    
    status_et = "🟢 Boa" if et_perc >= 50 else "🔴 Baixa"
    c_hc3.metric("Eficiência (Et)", f"{et_perc:.1f} %", status_et, delta_color="off")
    
    status_ca = "🟢 Ideal" if ca_perc <= 5 else "🔴 Alta (Risco)"
    c_hc4.metric("Conc. Cascalhos (Ca)", f"{ca_perc:.2f} %", status_ca, delta_color="off")
    
    c_hc5.metric("Densidade Efetiva (De)", f"{de_ppg:.2f} ppg", f"+ {(de_ppg - peso_lama_ppg):.2f} ppg", delta_color="inverse")
else:
    st.warning("⚠️ Velocidade Ascensional não calculada. Verifique os diâmetros de poço e DP.")

st.write("---")
st.write("**Volumetria e Tempos de Circulação**")

vol_int_poco = vol_total_interno_bha + vol_int_dp
vol_anu_poco = vol_total_anular_bha + vol_anular_dp
vol_total_sistema = vol_int_poco + vol_anu_poco
vazao_bbl_min = vazao_gpm / 42.0 if vazao_gpm > 0 else 1.0

col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
col_v1.metric("Vol. Interno", f"{vol_int_poco:.1f} bbl")
col_v2.metric("Vol. Anular", f"{vol_anu_poco:.1f} bbl")
col_v3.metric("⏱️ Surface to Bit", f"{vol_int_poco / vazao_bbl_min:.0f} min")
col_v4.metric("⏱️ Bottoms Up", f"{vol_anu_poco / vazao_bbl_min:.0f} min")
col_v5.metric("⏱️ Ciclo Completo", f"{vol_total_sistema / vazao_bbl_min:.0f} min")

# ==========================================
# ANÁLISE DE ARRASTO E TORQUE (TORQUE & DRAG - PETROGUIA UNIFICADO)
# ==========================================
st.markdown("---")
st.header("⚖️ Análise de Arrasto e Torque (Modelo Petroguia Avançado)")

st.write("**Parâmetros Direcionais e Fator de Fricção**")

# Seletor inteligente no lugar da digitação manual
tipo_friccao = st.selectbox("Cenário de Fricção (Fluido / Condição do Poço)", [
    "Lama Sintética/Óleo (SBM/OBM) em Poço Aberto - f = 0.20",
    "Lama Sintética/Óleo (SBM/OBM) em Poço Revestido - f = 0.15",
    "Lama Base Água (WBM) em Poço Aberto - f = 0.30",
    "Lama Base Água (WBM) em Poço Revestido - f = 0.25",
    "Lubrificantes de Alta Performance - f = 0.12",
    "Inserir Manualmente (Back-calculation)"
])

col_td1, col_td2, col_td3, col_td4 = st.columns(4)

# Lógica de preenchimento automático do f
if "Inserir Manualmente" in tipo_friccao:
    ff_poco = col_td1.number_input("Coef. de Atrito (f)", value=0.25, step=0.01)
else:
    # Extrai automaticamente o valor do texto selecionado
    ff_val = float(tipo_friccao.split("f = ")[1])
    ff_poco = col_td1.number_input("Coef. de Atrito (f)", value=ff_val, disabled=True)

inc_media = col_td2.number_input("Inclinação Média (θ°)", value=inc1 if 'inc1' in locals() else 0.0, step=1.0)
delta_inc = col_td3.number_input("Variação Inclinação (Δθ°)", value=0.0, step=1.0)
delta_azi = col_td4.number_input("Variação Azimute (Δφ°)", value=0.0, step=1.0)

st.write("**Parâmetros da Coluna e Limites Operacionais**")
col_td5, col_td6, col_td7 = st.columns(3)
od_tubo = od_dp if 'od_dp' in locals() else 5.0
od_tj = col_td5.number_input("OD do Tool Joint (in)", value=od_tubo + 1.5, step=0.125)
overpull_margin = col_td6.number_input("Margem de Overpull (klbs)", value=50.0, step=10.0)

# Raio efetivo da tubulação (Modelo Petroguia)
r_in = (od_tubo + (2/3) * (od_tj - od_tubo)) / 2
r_ft = r_in / 12.0
col_td7.metric("Raio Efetivo (R)", f"{r_in:.2f} in")

if 'peso_flutuado_coluna' in locals() and peso_flutuado_coluna > 0:
    inc_rad = math.radians(inc_media)
    d_inc_rad = math.radians(delta_inc)
    d_azi_rad = math.radians(delta_azi)
    
    # Carga axial baseada no peso flutuado
    W_total = peso_flutuado_coluna
    T_axial = W_total * math.cos(inc_rad)
    
    # Força Normal (N) com Efeito Cabrestante (Capstan Effect)
    termo_azimute = T_axial * d_azi_rad * math.sin(inc_rad)
    termo_inclinacao = T_axial * d_inc_rad + W_total * math.sin(inc_rad)
    N_normal = math.sqrt(termo_azimute**2 + termo_inclinacao**2)
    
    # Cargas Dinâmicas e Torque
    arrasto_axial = ff_poco * N_normal
    torque_friccao_lbft = (ff_poco * (N_normal * 1000) * r_ft)
    
    rot_w = T_axial
    puw = T_axial + arrasto_axial
    sow = T_axial - arrasto_axial
    max_pull = puw + overpull_margin
    
    st.write("**Previsão de Cargas no Gancho (Hook Load) e Torque Friccional**")
    c_td_a, c_td_b, c_td_c, c_td_d, c_td_e = st.columns(5)
    c_td_a.metric("Rotary Wt", f"{rot_w:.1f} klbs")
    c_td_b.metric("Pick-Up Wt", f"{puw:.1f} klbs", f"+{arrasto_axial:.1f}k Drag", delta_color="inverse")
    c_td_c.metric("Slack-Off Wt", f"{sow:.1f} klbs", f"-{arrasto_axial:.1f}k Drag", delta_color="normal")
    c_td_d.metric("Max Pull", f"{max_pull:.1f} klbs", f"Overpull {overpull_margin:.0f}k", delta_color="off")
    c_td_e.metric("Torque (M)", f"{torque_friccao_lbft:.0f} lb-ft")
    
    st.write("**Análise de Risco Operacional e Transferência de WOB**")
    wob_alvo = st.session_state.wob_main
    peso_disponivel = sow - (wob_alvo * 1.2)
    
    if sow < wob_alvo:
        st.error(f"🚨 **Risco Crítico de Buckling:** Slack-Off ({sow:.1f} klbs) menor que WOB Planejado ({wob_alvo:.1f} klbs). Sem peso na broca no modo Slide.")
    elif peso_disponivel < 0:
        st.warning(f"⚠️ **Atenção (Sliding):** Slack-off marginal. Risco de pendurar a coluna ao tentar transferir {wob_alvo:.1f} klbs de peso.")
    else:
        st.success(f"✅ **Transferência Segura:** Slack-Off ({sow:.1f} klbs) permite deslizar e transferir {wob_alvo:.1f} klbs na broca com segurança.")

# ==========================================
# RELATÓRIO PDF
# ==========================================
st.markdown("---")
st.header(t["head_pdf"])
nome_poco = st.text_input("Poço / Sonda", value="Exploratório")
nome_operador = st.text_input("Operador Direcional", value="Engenheiro Chefe")

if st.button(t["btn_pdf"]):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_fill_color(200, 220, 255)
        
        try: pdf.image("logo_intrepid.png", x=10, y=8, w=40)
        except: pass
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Relatorio Diario de Engenharia', ln=True, align='C')
        pdf.set_font('Arial', '', 10)
        dt_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 10, f'Poco: {nome_poco} | Operador: {nome_operador} | Data: {dt_atual}', ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '1. Parametros Operacionais e Motor', ln=True, fill=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(95, 8, f'Modelo: {modelo} - {od}" - Lobos: {lobulos}', border=1)
        pdf.cell(95, 8, f'Bent Housing: {bent} graus ({estabilizacao})', border=1, ln=True)
        pdf.cell(63, 8, f'RPM Motor: {rpm_motor:.0f}', border=1)
        pdf.cell(63, 8, f'RPM Mesa: {rpm_superficie:.0f}', border=1)
        pdf.cell(64, 8, f'Total RPM: {(rpm_motor + rpm_superficie):.0f}', border=1, ln=True)
        pdf.cell(63, 8, f'Torque: {torque_lbft:.0f} lb-ft', border=1)
        pdf.cell(63, 8, f'Delta P Motor: {motor_total_press_drop:.0f} psi', border=1)
        pdf.cell(64, 8, f'Potencia: {hp_mec:.1f} HP', border=1, ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '2. Hidraulica, Performance da Broca e ECD', ln=True, fill=True)
        pdf.set_font('Arial', '', 10)
        
        # Primeira Linha - Reologia e ECD
        pdf.cell(63, 8, f'PV: {pv:.0f} cP | YP: {yp:.0f} lb/100ft2', border=1)
        pdf.cell(63, 8, f'Delta P Anular: {delta_p_anular_total:.0f} psi', border=1)
        pdf.cell(64, 8, f'ECD Calc: {ecd_calc:.2f} ppg', border=1, ln=True)
        
        # Segunda Linha - Performance da Broca (HSI, JIF e Velocidade)
        pdf.cell(63, 8, f'Bit Drop: {bit_press_drop:.0f} psi ({perc_bit_drop:.0f}%)', border=1)
        pdf.cell(63, 8, f'HSI: {hsi:.1f} hp/in2', border=1)
        pdf.cell(64, 8, f'Jet Impact Force: {jif:.0f} lbf', border=1, ln=True)
        
        # Terceira Linha - Volumetria
        pdf.cell(63, 8, f'Velocidade Jato: {jet_velocity_m:.1f} m/s', border=1)
        pdf.cell(63, 8, f'Vol. Ciclo: {vol_total_sistema:.0f} bbl', border=1)
        pdf.cell(64, 8, f'Bottoms Up: {(vol_anu_poco / vazao_bbl_min):.0f} min', border=1, ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '3. Limpeza de Poco e Torque & Drag', ln=True, fill=True)
        pdf.set_font('Arial', '', 10)
        
        # Resgate seguro de variáveis (Evita erro se o usuário não preencher algo)
        v_asc = locals().get('va_ftmin', 0)
        ef_t = locals().get('et_perc', 0)
        c_casc = locals().get('ca_perc', 0)
        p_up = locals().get('puw', 0)
        s_off = locals().get('sow', 0)
        t_fric = locals().get('torque_friccao_lbft', 0)
        
        # Primeira Linha - Hole Cleaning
        pdf.cell(63, 8, f'Vel. Ascensional: {v_asc:.1f} ft/min', border=1)
        pdf.cell(63, 8, f'Eficiencia de Transp.: {ef_t:.1f}%', border=1)
        pdf.cell(64, 8, f'Concentracao (Ca): {c_casc:.2f}%', border=1, ln=True)
        
        # Segunda Linha - Torque & Drag
        pdf.cell(63, 8, f'Pick-Up Wt (PUW): {p_up:.1f} klbs', border=1)
        pdf.cell(63, 8, f'Slack-Off Wt (SOW): {s_off:.1f} klbs', border=1)
        pdf.cell(64, 8, f'Torque Friccional: {t_fric:.0f} lb-ft', border=1, ln=True)
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '4. Projecao Direcional e Estrategia', ln=True, fill=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(47, 8, f'MD1: {md1}m', border=1)
        pdf.cell(47, 8, f'MD2: {md2}m', border=1)
        pdf.cell(48, 8, f'Toolface: {tf_deg:.0f} graus', border=1)
        pdf.cell(48, 8, f'DLS: {dls:.2f} /30m', border=1, ln=True)
        pdf.cell(0, 8, f'Slide Recomendado: {slide_meters:.1f} m  |  Rotary: {rotary_meters:.1f} m', border=1, ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '5. Composicao de Fundo (BHA)', ln=True, fill=True)
        pdf.set_font('Arial', 'B', 10)
        col_w = [10, 70, 20, 20, 35, 35]
        
        # Cabeçalho da tabela corrigido com os títulos fixos
        pdf.cell(col_w[0], 8, 'N', border=1)
        pdf.cell(col_w[1], 8, 'Componente', border=1)
        pdf.cell(col_w[2], 8, 'OD (in)', border=1)
        pdf.cell(col_w[3], 8, 'ID (in)', border=1)
        pdf.cell(col_w[4], 8, 'C Total (m)', border=1)
        pdf.cell(col_w[5], 8, 'Peso T.(klbs)', border=1, ln=True)
        
        pdf.set_font('Arial', '', 9)
        for i, item in enumerate(resultados_bha):
            # Obtém a Ordem correta definida na Tabela
            pdf.cell(col_w[0], 8, str(item.get('Ordem', i+1)), border=1)
            
            f_nome = str(item.get('Componente', '')).encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(col_w[1], 8, f_nome[:38], border=1)
            pdf.cell(col_w[2], 8, str(item.get('OD', '-')), border=1)
            pdf.cell(col_w[3], 8, str(item.get('ID', '-')), border=1)
            
            # Leitura correta das novas chaves (Metragem e Peso já calculados pela Qtd)
            c_val = item.get('C Total (m)', item.get('C Unitário (m)', item.get('C (m)', 0)))
            p_val = item.get('Peso Total (klbs)', item.get('Peso Unit (klbs)', item.get('Comp(klbs)', '-')))
            
            pdf.cell(col_w[4], 8, f"{float(c_val):.2f}", border=1)
            pdf.cell(col_w[5], 8, str(p_val), border=1, ln=True)

        b64 = base64.b64encode(pdf.output(dest='S').encode('latin-1')).decode()
        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="Relatorio_{dt_atual.replace("/","-").replace(":","")}.pdf" class="button">📥 Baixar Relatório PDF</a>', unsafe_allow_html=True)
    except Exception as e: 
        st.error(f"Erro no PDF: {e}")
