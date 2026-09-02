import streamlit as st
import pandas as pd
import math
import numpy as np
import base64
from fpdf import FPDF
import pickle
from datetime import datetime
import pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# ==========================================
# SALVAR E CARREGAR PROJETO (.DIRPROJ)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("💾 Salvar / Carregar Projeto")

# 1. Carregar Projeto (Upload)
st.sidebar.write("**Carregar Projeto (.dirproj)**")
arquivo_upload = st.sidebar.file_uploader("Upload", type=["dirproj"], key="upload_projeto", label_visibility="collapsed")

if arquivo_upload is not None:
    if st.sidebar.button("Restaurar Dados", use_container_width=True):
        try:
            estado_recuperado = pickle.loads(arquivo_upload.getvalue())
            # Injeta todos os dados de volta no app
            for k, v in estado_recuperado.items():
                st.session_state[k] = v
            st.sidebar.success("✅ Projeto restaurado!")
            st.rerun() # Atualiza a tela automaticamente
        except Exception as e:
            st.sidebar.error(f"Erro ao ler arquivo: {e}")

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# 2. Exportar Projeto Atual
st.sidebar.write("**Exportar Projeto Atual**")

# Separa as chaves pesadas (Tabelas)
chaves_pesadas = ['df_trajetoria', 'df_plan', 'last_md', 'last_inc', 'last_az', 'last_tvd', 'last_ns', 'last_ew']
dados_salvar = {k: st.session_state[k] for k in chaves_pesadas if k in st.session_state}

# Mantém a sua lógica genial de salvar todos os textos/números dos inputs da tela!
for k, v in st.session_state.items():
    if isinstance(v, (int, float, str, bool)) and k not in dados_salvar:
        dados_salvar[k] = v

if dados_salvar:
    dados_binarios = pickle.dumps(dados_salvar)
    nome_arquivo = f"Projeto_Direcional_{datetime.now().strftime('%Y%m%d_%H%M')}.dirproj"    

    st.sidebar.download_button(
        label="📥 Exportar Projeto Atual", 
        data=dados_binarios, 
        file_name=nome_arquivo, 
        mime="application/octet-stream",
        use_container_width=True
    )
else:
    st.sidebar.info("Calcule dados para salvar.")

# Continuação original do seu layout
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
# MÓDULO DE MÚLTIPLOS SURVEYS E IMPORTAÇÃO
# ==========================================
st.markdown("---")
st.header("🛤️ Trajetória Completa (Múltiplos Surveys)")

# 1. Estrutura Base na Memória com Todas as Colunas
if "df_surveys_data" not in st.session_state:
    st.session_state["df_surveys_data"] = pd.DataFrame({
        "MD (m)": [0.0, 30.0, 60.0],
        "Inc (°)": [0.0, 2.0, 5.0],
        "Az (°)": [0.0, 45.0, 50.0],
        "TVD (m)": [0.0, 29.99, 59.94],
        "N/S (m)": [0.0, 0.37, 2.01],
        "E/W (m)": [0.0, 0.37, 2.39],
        "DLS (°/30m)": [0.0, 2.0, 3.0]
    })

# 2. Escolha do Método de Entrada
modo_surveys = st.radio("Método de Entrada de Surveys:", ["Inserção Manual / Colar do Excel", "Importar Well Seeker (Innova)"])

if modo_surveys == "Importar Well Seeker (Innova)":
    arquivo_innova = st.file_uploader("Upload: Survey Report (.xlsx)", type=["xlsx", "xls"], key="upload_innova")
    
    if arquivo_innova is not None:
        try:
            df_raw = pd.read_excel(arquivo_innova, header=None)
            # Varre a primeira coluna procurando a string "MD"
            idx_md = df_raw[df_raw.iloc[:, 0].astype(str).str.strip().str.upper() == 'MD'].index
            
            if len(idx_md) > 0:
                row_start = idx_md[0] + 2 # Pula o cabeçalho 'MD' e a linha de unidades 'm'
                # Filtra as colunas exatas do relatório da Innova (0=MD, 1=INC, 2=AZI, 3=TVD, 4=NS, 5=EW, 7=DLS)
                df_ext = df_raw.iloc[row_start:, [0, 1, 2, 3, 4, 5, 7]].copy()
                df_ext.columns = ["MD (m)", "Inc (°)", "Az (°)", "TVD (m)", "N/S (m)", "E/W (m)", "DLS (°/30m)"]
                df_ext = df_ext.apply(pd.to_numeric, errors='coerce').dropna(subset=["MD (m)", "Inc (°)", "Az (°)"]).reset_index(drop=True)
                
                # Trava para não atualizar em loop infinito
                if not st.session_state.get("innova_loaded") or st.session_state.get("last_innova") != arquivo_innova.name:
                    st.session_state["df_surveys_data"] = df_ext
                    st.session_state["innova_loaded"] = True
                    st.session_state["last_innova"] = arquivo_innova.name
                    st.rerun()
            else:
                st.warning("⚠️ Não foi possível localizar a coluna de 'MD' neste arquivo.")
        except Exception as e:
            st.error(f"Erro ao processar o relatório da Innova: {e}")

st.write("**Tabela de Surveys (Edite os valores base ou cole do Excel):**")

# 3. Tabela Dinâmica
df_surveys_input = st.data_editor(
    st.session_state["df_surveys_data"], 
    num_rows="dynamic", 
    use_container_width=True,
    key="editor_surveys_mult"
)

# Atualiza a memória com o que o usuário digitar ou colar
st.session_state["df_surveys_data"] = df_surveys_input

# ==========================================
# EXTRAÇÃO AUTOMÁTICA DOS ÚLTIMOS SURVEYS
# ==========================================
# Atualiza a tabela na memória e extrai os dados precisos das duas últimas linhas
df_valida = df_surveys_input.apply(pd.to_numeric, errors='coerce').dropna(subset=["MD (m)", "Inc (°)", "Az (°)"])

if len(df_valida) >= 2:
    prev_md = float(df_valida.iloc[-2]["MD (m)"])
    prev_inc = float(df_valida.iloc[-2]["Inc (°)"])
    prev_az = float(df_valida.iloc[-2]["Az (°)"])
else:
    prev_md, prev_inc, prev_az = 0.0, 0.0, 0.0
    
if len(df_valida) >= 1:
    last_md = float(df_valida.iloc[-1]["MD (m)"])
    last_inc = float(df_valida.iloc[-1]["Inc (°)"])
    last_az = float(df_valida.iloc[-1]["Az (°)"])
    last_tvd = float(df_valida.iloc[-1].get("TVD (m)", 0.0))
    last_ns = float(df_valida.iloc[-1].get("N/S (m)", 0.0))
    last_ew = float(df_valida.iloc[-1].get("E/W (m)", 0.0))
    last_dls = float(df_valida.iloc[-1].get("DLS (°/30m)", 0.0))
else:
    last_md, last_inc, last_az, last_tvd, last_ns, last_ew, last_dls = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# Gatilho de Memória: Se a tabela for modificada, reseta os valores do painel abaixo.
current_tail_str = f"{prev_md}_{prev_inc}_{prev_az}_{last_md}_{last_inc}_{last_az}"
if st.session_state.get("last_tail_str") != current_tail_str:
    st.session_state["md_ant"], st.session_state["inc_ant"], st.session_state["az_ant"] = prev_md, prev_inc, prev_az
    st.session_state["md_atual"], st.session_state["inc_atual"], st.session_state["az_atual"] = last_md, last_inc, last_az
    st.session_state["md_alvo"] = last_md + 30.0
    st.session_state["last_tail_str"] = current_tail_str

# 4. Cálculo de Mínima Curvatura para toda a trajetória
if st.button("🔄 Calcular Coordenadas (Mínima Curvatura)"):
    df_calc = df_valida.copy()
    
    tvd_list, ns_list, ew_list, dls_list = [0.0], [0.0], [0.0], [0.0]
    
    for i in range(1, len(df_calc)):
        md1, inc1, az1 = df_calc.iloc[i-1][["MD (m)", "Inc (°)", "Az (°)"]]
        md2, inc2, az2 = df_calc.iloc[i][["MD (m)", "Inc (°)", "Az (°)"]]
        
        pm = md2 - md1
        if pm <= 0:
            tvd_list.append(tvd_list[-1])
            ns_list.append(ns_list[-1])
            ew_list.append(ew_list[-1])
            dls_list.append(0.0)
            continue
            
        i1_rad, i2_rad = math.radians(inc1), math.radians(inc2)
        a1_rad, a2_rad = math.radians(az1), math.radians(az2)
        
        cos_beta = max(-1.0, min(1.0, math.cos(i2_rad - i1_rad) - (math.sin(i1_rad) * math.sin(i2_rad) * (1.0 - math.cos(a2_rad - a1_rad)))))
        beta_rad = math.acos(cos_beta)
        
        if beta_rad == 0:
            F, dls = 1.0, 0.0
        else:
            F = (2.0 / beta_rad) * math.tan(beta_rad / 2.0)
            dls = math.degrees(beta_rad) * (30.0 / pm)
            
        delta_ns = (pm / 2.0) * (math.sin(i1_rad) * math.cos(a1_rad) + math.sin(i2_rad) * math.cos(a2_rad)) * F
        delta_ew = (pm / 2.0) * (math.sin(i1_rad) * math.sin(a1_rad) + math.sin(i2_rad) * math.sin(a2_rad)) * F
        pv = (pm / 2.0) * (math.cos(i1_rad) + math.cos(i2_rad)) * F
        
        tvd_list.append(tvd_list[-1] + pv)
        ns_list.append(ns_list[-1] + delta_ns)
        ew_list.append(ew_list[-1] + delta_ew)
        dls_list.append(dls)
        
    df_calc["TVD (m)"] = np.round(tvd_list, 2)
    df_calc["N/S (m)"] = np.round(ns_list, 2)
    df_calc["E/W (m)"] = np.round(ew_list, 2)
    df_calc["DLS (°/30m)"] = np.round(dls_list, 2)
    
    st.session_state["df_surveys_data"] = df_calc
    st.session_state['df_trajetoria'] = df_calc
    st.rerun()

# ==========================================
# TELA PRINCIPAL - PROJEÇÃO E RENDIMENTO DO MOTOR
# ==========================================
st.markdown("---")
st.header(t["well_data"])
st.write("💡 *Os campos abaixo e as coordenadas foram sincronizados automaticamente com o último survey da tabela.*")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader(t["prev_surv"])
    md_ant = st.number_input("MD (m)", value=prev_md, step=1.0, key="md_ant")
    inc_ant = st.number_input("Inc (°)", value=prev_inc, step=0.1, key="inc_ant")
    az_ant = st.number_input("Az (°)", value=prev_az, step=0.1, key="az_ant")
with col2:
    st.subheader(t["curr_surv"])
    md_atual = st.number_input("MD (m)", value=last_md, step=1.0, key="md_atual")
    inc_atual = st.number_input("Inc (°)", value=last_inc, step=0.1, key="inc_atual")
    az_atual = st.number_input("Az (°)", value=last_az, step=0.1, key="az_atual")
    st.markdown("---")
    lbl_slide = "Slide Realizado (m)" if idioma == "Português" else "Slide Drilled (m)" if idioma == "English" else "Slide Realizado (m)"
    slide_realizado = st.number_input(lbl_slide, value=0.0, step=0.1)
with col3:
    st.subheader(t["target"])
    md_alvo = st.number_input("MD (m)", value=last_md + 30.0, step=1.0, key="md_alvo")
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
        pm_alvo = md_alvo - md_atual 
        slide_m = (dls_req / rendimento_usado) * pm_alvo 
        
        if slide_m > pm_alvo:
            st.error("Alvo inatingível com o Build Rate atual!" if idioma == "Português" else "Unreachable target with current Build Rate!" if idioma == "English" else "¡Objetivo inalcanzable con el Build Rate actual!")
        else:
            col6.metric(label="Slide (m)", value=f"{slide_m:.1f} m", delta=origem_rendimento, delta_color="off")
    else:
        col6.metric(label="Slide (m)", value="-")

# ==========================================
# MÓDULO DE ACOMPANHAMENTO DIRECIONAL (MÍNIMA CURVATURA) E OUIJA-BOARD
# ==========================================
st.markdown("---")
st.header(t["head_proj"])

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.write(f"**{t['curr_surv']}** (Ancorado no Ponto Atual)")
    
    # As coordenadas viraram apenas painéis (espelhando a tabela)
    c_tie1, c_tie2, c_tie3 = st.columns(3)
    c_tie1.metric("MD 1 (m)", f"{last_md:.2f}")
    c_tie2.metric("I1 (°)", f"{last_inc:.2f}")
    c_tie3.metric("A1 (°)", f"{last_az:.2f}")
    
    c_tvd1, c_ns1, c_ew1 = st.columns(3)
    c_tvd1.metric("TVD 1 (m)", f"{last_tvd:.2f}")
    c_ns1.metric("N/S 1 (m)", f"{last_ns:.2f}")
    c_ew1.metric("E/W 1 (m)", f"{last_ew:.2f}")

with col_s2:
    st.write(f"**{t['target']}**")
    md2 = st.number_input("MD 2 (m)", min_value=last_md, value=last_md + 30.0, step=1.0, format="%.2f", key="mc_md2")
    inc2 = st.number_input("I2 (°)", min_value=0.0, max_value=180.0, value=last_inc, step=0.1, format="%.2f", key="mc_i2")
    az2 = st.number_input("A2 (°)", min_value=0.0, max_value=360.0, value=last_az, step=0.1, format="%.2f", key="mc_a2")

tf_deg, dls, pm = 0.0, 0.0, md2 - last_md 

if pm > 0:
    # 1. Matemática de Mínima Curvatura para o Target
    i1_rad, i2_rad = math.radians(last_inc), math.radians(inc2)
    a1_rad, a2_rad = math.radians(last_az), math.radians(az2)
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
    tvd2, ns2, ew2 = last_tvd + pv, last_ns + delta_ns, last_ew + delta_ew
    
    st.write("---")
    res1, res2, res3, res4, res5 = st.columns(5)
    res1.metric("TVD (m)", f"{tvd2:.2f}", f"+ {pv:.2f} m", delta_color="off")
    res2.metric("N/S (m)", f"{ns2:.2f}", f"{delta_ns:+.2f} m", delta_color="off")
    res3.metric("E/W (m)", f"{ew2:.2f}", f"{delta_ew:+.2f} m", delta_color="off")
    res4.metric("DLS (°/30m)", f"{dls:.2f}")
    res5.metric("Disp. Total (m)", f"{math.sqrt(ns2**2 + ew2**2):.2f}")
    
    st.write("### 🧭 Ouija-Board Vetorial (Rotary Compensado)")
    
    # 2. Direção (GTF) do Alvo
    if beta_rad > 0:
        tf_y = math.sin(a2_rad - a1_rad) * math.sin(i2_rad)
        tf_x = math.sin(i2_rad) * math.cos(i1_rad) * math.cos(a2_rad - a1_rad) - math.sin(i1_rad) * math.cos(i2_rad)
        tf_deg = math.degrees(math.atan2(tf_y, tf_x)) % 360.0
    else:
        tf_deg = 0.0

    # 3. Direção (GTF) do Survey Anterior (Tendência)
    if prev_md > 0 and last_md > prev_md:
        pi_rad, pa_rad = math.radians(prev_inc), math.radians(prev_az)
        tf_y_prev = math.sin(a1_rad - pa_rad) * math.sin(i1_rad)
        tf_x_prev = math.sin(i1_rad) * math.cos(pi_rad) * math.cos(a1_rad - pa_rad) - math.sin(pi_rad) * math.cos(i1_rad)
        last_tf = math.degrees(math.atan2(tf_y_prev, tf_x_prev)) % 360.0
    else:
        last_tf = 0.0

    # Interface de Inserção Vetorial
    st.write("**Tendência Natural da BHA (Modo Rotary / Hold)**")
    col_rot1, col_rot2 = st.columns(2)
    rot_dls = col_rot1.number_input("DLS de Rotary (°/30m)", value=float(last_dls), step=0.1, help="Padrão: DLS herdado do último survey.")
    rot_tf = col_rot2.number_input("Toolface de Tendência (°)", value=float(last_tf), step=1.0, help="Padrão: Direção herdada do último survey.")
    
    st.write("**Parâmetros do Motor e Decisão**")
    c_ob1, c_ob2, c_ob3 = st.columns(3)
    c_ob1.metric("GTF Final (Reta p/ Alvo)", f"{tf_deg:.0f}°")
    c_ob2.metric("DLS Requerido", f"{dls:.2f} °/30m")
    
    # Resgata o Build Rate Real ou do Banco
    build_rate_banco_30m = 0.0
    try:
        df_m_clean = df_motores.copy()
        filtro_motor = df_m_clean[(df_m_clean['Modelo'].str.upper() == str(modelo).upper()) & 
                                  (df_m_clean['Diametro_Externo_OD'] == str(od)) &
                                  (df_m_clean['Bent_Housing_Graus'] == float(bent)) &
                                  (df_m_clean['Tipo_Estabilizacao'].str.upper() == str(estabilizacao).upper())]
        if not filtro_motor.empty and 'Build_Rate' in filtro_motor.columns:
            build_rate_banco_30m = float(filtro_motor.iloc[0]['Build_Rate']) * (30.0 / 30.48)
    except Exception: pass

    motor_yield_real_var = motor_yield_real if 'motor_yield_real' in locals() else 0.0
    br_recomendado = motor_yield_real_var if motor_yield_real_var > 0 else build_rate_banco_30m
    valor_padrao_br = float(br_recomendado) if br_recomendado > 0 else float(max(round(dls + 0.5, 1), 2.0))
    
    build_rate = c_ob3.number_input("Build Rate do Motor (°/30m)", value=valor_padrao_br, step=0.1, help="Padrão: Motor Yield Real ou Teórico do DB.")
    
    # 4. Cálculo Vetorial Duplo (Motor x Tendência)
    if build_rate > 0:
        q_rad, r_rad = math.radians(tf_deg), math.radians(rot_tf)
        
        Qx, Qy = dls * math.cos(q_rad), dls * math.sin(q_rad)
        Rx, Ry = rot_dls * math.cos(r_rad), rot_dls * math.sin(r_rad)
        
        Dx, Dy = Qx - Rx, Qy - Ry
        
        A = build_rate**2 - rot_dls**2
        B = -2 * (Dx * Rx + Dy * Ry)
        C = -(Dx**2 + Dy**2)
        
        f = -1
        if A == 0:
            if B != 0: f = -C / B
            else: f = 0
        else:
            disc = B**2 - 4*A*C
            if disc >= 0:
                f1, f2 = (-B + math.sqrt(disc)) / (2*A), (-B - math.sqrt(disc)) / (2*A)
                f = max(f1, f2)
                
        if f > 1.0 or f < 0.0:
            st.error(f"⚠️ **Falha Vetorial:** O Motor não possui agressividade suficiente ({build_rate:.2f}°/30m) para compensar a tendência do poço ({rot_dls:.2f}° @ {rot_tf:.0f}°) e ainda chegar ao alvo. Reavalie o Target ou o BHA.")
        else:
            slide_meters = f * pm
            rotary_meters = pm - slide_meters
            
            if f > 0:
                tf_motor = math.degrees(math.atan2(Dy/f + Ry, Dx/f + Rx)) % 360.0
            else:
                tf_motor = tf_deg
                
            # 💡 SALVANDO NA MEMÓRIA DA SESSÃO
            st.session_state['out_slide'] = slide_meters
            st.session_state['out_rotary'] = rotary_meters
            st.session_state['out_pm'] = pm
            st.session_state['out_tf_motor'] = tf_motor
                
            st.success(f"✅ **Estratégia Compensada:** Deslize **{slide_meters:.1f} m** apontando sua ferramenta para **{tf_motor:.0f}°**, e depois gire (Rotary) o restante de **{rotary_meters:.1f} m**.")

# ==========================================
# VISUALIZAÇÃO GRÁFICA DA TRAJETÓRIA (2D / 3D)
# ==========================================
st.markdown("---")
st.header("📊 Visualização da Trajetória (Real vs Plano)")

col_graf1, col_graf2 = st.columns([1, 2])
with col_graf1:
    st.write("**Carregar Arquivo do Projeto (Plan)**")
    arquivo_plan = st.file_uploader("Upload: Plan Report (.xls, .xlsx)", type=["xlsx", "xls"], key="upload_plan")
    
    if arquivo_plan is not None:
        try:
            df_raw_plan = pd.read_excel(arquivo_plan, header=None)
            
            import re
            def limpa_numero(x):
                if pd.isna(x): return np.nan
                x_str = str(x).strip()
                if x_str in ['--', '-', '']: return np.nan
                if ',' in x_str and '.' in x_str: x_str = x_str.replace(',', '')
                elif ',' in x_str and '.' not in x_str: x_str = x_str.replace(',', '.')
                x_str = re.sub(r'[^\d\.\-]', '', x_str)
                try: return float(x_str)
                except ValueError: return np.nan

            df_plan_ext = None
            origem_dados = ""
            
            # 1. TENTA ACHAR A TABELA RESUMIDA: "PLAN SECTIONS"
            mask_plan = df_raw_plan.astype(str).apply(lambda col: col.str.strip().str.lower().str.startswith('measured'))
            idx_plan_sec = df_raw_plan[mask_plan.any(axis=1)].index
            
            if len(idx_plan_sec) > 0:
                header_idx = idx_plan_sec[0]
                h_row_1 = df_raw_plan.iloc[header_idx].astype(str).str.strip().str.lower()
                h_row_2 = df_raw_plan.iloc[header_idx + 1].astype(str).str.strip().str.lower() if header_idx + 1 < len(df_raw_plan) else pd.Series()
                
                def find_col_multi(keywords, exclude=None):
                    for k in keywords:
                        for idx, val in h_row_1.items():
                            val_str = str(val) + " " + str(h_row_2.get(idx, ""))
                            val_str = val_str.strip().lower()
                            if k in val_str:
                                if exclude and exclude in val_str: continue
                                return idx
                    return None
                    
                c_md = find_col_multi(['measured'])
                c_inc = find_col_multi(['inclination', 'inc'])
                c_az = find_col_multi(['azimuth', 'azi'])
                c_tvd = find_col_multi(['vertical depth', 'tvd'])
                c_ns = find_col_multi(['+n/-s'])
                c_ew = find_col_multi(['+e/-w'])
                
                if None not in [c_md, c_inc, c_az, c_tvd, c_ns, c_ew]:
                    df_plan_ext = df_raw_plan.iloc[header_idx + 2:, [c_md, c_inc, c_az, c_tvd, c_ns, c_ew]].copy()
                    df_plan_ext.columns = ["MD", "Inc", "Az", "TVD", "Northing", "Easting"]
                    origem_dados = "Plan Sections"
            
            # 2. SE FALHAR, TENTA ACHAR A TABELA DETALHADA: "PLANNED SURVEY"
            if df_plan_ext is None:
                mask_surv = df_raw_plan.astype(str).apply(lambda col: col.str.strip().str.upper().str.startswith('MD'))
                idx_md_plan = df_raw_plan[mask_surv.any(axis=1)].index
                
                if len(idx_md_plan) > 0:
                    header_idx = idx_md_plan[0]
                    header_row = df_raw_plan.iloc[header_idx] 
                    
                    def find_col(keywords, exclude=None):
                        for k in keywords:
                            for idx, val in header_row.items():
                                val_str = str(val).strip().lower()
                                if k in val_str:
                                    if exclude and exclude in val_str: continue
                                    return idx
                        return None
                    
                    c_md = find_col(['md'])
                    c_inc = find_col(['inc'])
                    c_az = find_col(['azi', 'azim'])
                    c_tvd = find_col(['tvd'], exclude='tvdss')
                    c_ns = find_col(['northing', 'norte', '+n/-s', 'n/s'])
                    c_ew = find_col(['easting', 'leste', '+e/-w', 'e/w'])
                    
                    if None not in [c_md, c_inc, c_az, c_tvd, c_ns, c_ew]:
                        df_plan_ext = df_raw_plan.iloc[header_idx + 1:, [c_md, c_inc, c_az, c_tvd, c_ns, c_ew]].copy()
                        df_plan_ext.columns = ["MD", "Inc", "Az", "TVD", "Northing", "Easting"]
                        origem_dados = "Planned Survey"
            
            # 3. PROCESSAMENTO FINAL E CORTADOR DE TABELAS DUPLAS
            if df_plan_ext is not None:
                # Aplica a limpeza de vírgulas e letras em todas as colunas
                for c in df_plan_ext.columns: 
                    df_plan_ext[c] = df_plan_ext[c].apply(limpa_numero)
                
                # Remove linhas vazias
                df_plan_ext = df_plan_ext.dropna(subset=['MD', 'Inc', 'Az']).reset_index(drop=True)
                
                # 💡 O DETECTOR DE QUEDA: Se o MD diminuir, significa que invadimos uma segunda tabela. Cortamos aqui!
                if len(df_plan_ext) > 1:
                    quedas = df_plan_ext[df_plan_ext['MD'] < df_plan_ext['MD'].shift(1)].index
                    if len(quedas) > 0:
                        df_plan_ext = df_plan_ext.iloc[:quedas[0]]
                
                if not df_plan_ext.empty:
                    df_plan_ext = df_plan_ext.sort_values(by="MD").reset_index(drop=True)
                    
                    tie_northing = float(df_plan_ext.iloc[0]['Northing'])
                    tie_easting = float(df_plan_ext.iloc[0]['Easting'])
                    
                    df_plan_ext['N/S (m)'] = df_plan_ext['Northing'] - tie_northing
                    df_plan_ext['E/W (m)'] = df_plan_ext['Easting'] - tie_easting
                    df_plan_ext["Desl. Total (m)"] = np.sqrt(df_plan_ext["N/S (m)"]**2 + df_plan_ext["E/W (m)"]**2)
                    
                    st.session_state['df_plan'] = df_plan_ext
                    st.success(f"✅ Projeto carregado via: **{origem_dados}**")
                    with st.expander("🔍 Ver Dados Extraídos do Plano"):
                        st.dataframe(df_plan_ext.head(15))
                else:
                    st.warning("Nenhum dado numérico válido extraído da tabela.")
            else:
                st.error("⚠️ Não foi possível localizar colunas válidas nem na 'Plan Sections' nem na 'Planned Survey'.")
                
        except Exception as e:
            st.error(f"Erro ao processar arquivo do Projeto: {e}")

# ===============================
# LÓGICA DE PLOTAGEM INDEPENDENTE
# ===============================
has_real = 'df_trajetoria' in st.session_state and not st.session_state['df_trajetoria'].empty
has_plan = 'df_plan' in st.session_state and not st.session_state['df_plan'].empty

if has_real or has_plan:
    tab_3d, tab_top, tab_sec = st.tabs(["🌐 Visão 3D", "🗺️ Visão de Topo (N/S x E/W)", "📉 Visão de Seção (Desloc. x TVD)"])
    
    with tab_3d:
        fig_3d = go.Figure()
        
        if has_real:
            df_plot = st.session_state['df_trajetoria'].copy()
            df_plot["Desl. Total (m)"] = np.sqrt(df_plot["N/S (m)"]**2 + df_plot["E/W (m)"]**2)
            fig_3d.add_trace(go.Scatter3d(
                x=df_plot["E/W (m)"], y=df_plot["N/S (m)"], z=df_plot["TVD (m)"],
                mode='lines+markers',
                marker=dict(size=4, color=df_plot["MD (m)"], colorscale='Viridis', showscale=True, colorbar=dict(title="MD (m)", x=-0.1)),
                line=dict(color='darkblue', width=4),
                name='Trajetória Real',
                hovertemplate="<b>Real MD:</b> %{marker.color:.1f} m<br><b>TVD:</b> %{z:.1f} m<br><b>N/S:</b> %{y:.1f} m<br><b>E/W:</b> %{x:.1f} m<extra></extra>"
            ))
            
        if has_plan:
            df_p = st.session_state['df_plan']
            fig_3d.add_trace(go.Scatter3d(
                x=df_p["E/W (m)"], y=df_p["N/S (m)"], z=df_p["TVD"],
                mode='lines',
                line=dict(color='red', width=3, dash='dash'),
                name='Plano / Projeto',
                hovertemplate="<b>Plan MD:</b> %{text:.1f} m<br><b>TVD:</b> %{z:.1f} m<br><b>N/S:</b> %{y:.1f} m<br><b>E/W:</b> %{x:.1f} m<extra></extra>",
                text=df_p["MD"]
            ))

        fig_3d.update_layout(
            scene=dict(xaxis_title='Leste/Oeste (m)', yaxis_title='Norte/Sul (m)', zaxis_title='TVD (m)', zaxis_autorange='reversed'),
            margin=dict(l=0, r=0, b=0, t=30), height=600, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig_3d, use_container_width=True)

    with tab_top:
        fig_top = go.Figure()
        if has_real:
            fig_top.add_trace(go.Scatter(
                x=df_plot["E/W (m)"], y=df_plot["N/S (m)"], mode='lines+markers',
                marker=dict(size=6, color=df_plot["MD (m)"], colorscale='Viridis'), name='Real',
                hovertemplate="<b>N/S:</b> %{y:.1f} m<br><b>E/W:</b> %{x:.1f} m<extra></extra>"
            ))
        if has_plan:
            df_p = st.session_state['df_plan']
            fig_top.add_trace(go.Scatter(x=df_p["E/W (m)"], y=df_p["N/S (m)"], mode='lines', line=dict(color='red', dash='dash'), name='Plano'))
            
        fig_top.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=12, color='black', symbol='star'), name='Superfície'))
        fig_top.update_layout(xaxis_title="E/W (m)", yaxis_title="N/S (m)", height=500, xaxis=dict(scaleanchor="y", scaleratio=1))
        st.plotly_chart(fig_top, use_container_width=True)

    with tab_sec:
        fig_sec = go.Figure()
        if has_real:
            fig_sec.add_trace(go.Scatter(
                x=df_plot["Desl. Total (m)"], y=df_plot["TVD (m)"], mode='lines+markers',
                marker=dict(size=6, color=df_plot["MD (m)"], colorscale='Viridis'), name='Real',
                hovertemplate="<b>Desloc:</b> %{x:.1f} m<br><b>TVD:</b> %{y:.1f} m<extra></extra>"
            ))
        if has_plan:
            df_p = st.session_state['df_plan']
            fig_sec.add_trace(go.Scatter(x=df_p["Desl. Total (m)"], y=df_p["TVD"], mode='lines', line=dict(color='red', dash='dash'), name='Plano'))
            
        fig_sec.update_layout(xaxis_title="Deslocamento Total (Disp. m)", yaxis_title="TVD (m)", yaxis_autorange='reversed', height=500)
        st.plotly_chart(fig_sec, use_container_width=True)
else:
    st.info("👆 Importe a Trajetória na seção acima para visualizar os gráficos.")

# ==========================================
# PARÂMETROS DE FLUIDO E POÇO
# ==========================================
st.markdown("---")
st.header("🌊 Parâmetros de Fluido e Poço")
col_f1, col_f2, col_f3, col_f4 = st.columns(4)
peso_lama_ppg = col_f1.number_input("Mud Weight (ppg)", value=9.0, step=0.1, key="peso_lama_ppg")
vazao_gpm = col_f2.number_input("Flow Rate (GPM)", value=450.0, step=10.0, key="vazao_gpm")
pv = col_f3.number_input("PV (cP)", value=15.0, step=1.0, key="pv")
yp = col_f4.number_input("YP (lb/100ft²)", value=25.0, step=1.0, key="yp")

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

st.write("**Parâmetros Base do Poço, Broca e Superfície**")
col_poco1, col_poco2, col_poco3 = st.columns(3)
dh = col_poco1.number_input("Diâmetro do Poço (in)", value=dh_manual if modo_bha == t["opt_smart"] else 8.5, step=0.125, key="dh")
tfa = col_poco2.number_input("TFA da Broca (in²)", value=0.450, step=0.001, format="%.3f", key="tfa")
peso_top_drive = col_poco3.number_input("Peso Top Drive / Bloco (klbs)", value=30.0, step=1.0, key="peso_top_drive")

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
    hook_load_estatico = peso_flutuado_coluna + peso_top_drive
    
    col_dpr4.metric("Peso Ar Coluna", f"{peso_total_coluna:.1f} klbs")
    col_dpr5.metric("Hook Load Estático", f"{hook_load_estatico:.1f} klbs", help="Coluna Flutuada + Bloco/Top Drive")

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
    st.write("**Análise de Jar e Linha Neutra**")
    
    wob_planejado = st.number_input("WOB Max Planejado (klbf)", 
                                    step=5.0, 
                                    key="wob_main", 
                                    on_change=sync_from_main)
    
    if len(resultados_bha) > 0:
        fator_flutuacao = 1 - (peso_lama_ppg / 65.5)
        fator_inclinacao = math.cos(math.radians(inc1)) if 'inc1' in locals() and inc1 > 0 else 1.0
        margem_seguranca = wob_planejado * 1.2
        
        # --- 1. CÁLCULO DA LINHA NEUTRA (Neutral Point) ---
        peso_acumulado = 0.0
        distancia_np = 0.0
        componente_np = "Não encontrado"
        np_encontrado = False

        for item in resultados_bha:
            comp_nome = str(item.get('Componente', ''))
            comp_m = float(item.get('C Total (m)', item.get('C Unitário (m)', item.get('C (m)', 0.0))))
            peso_item_ar = float(item.get('Peso Total (klbs)', item.get('Peso Unit (klbs)', item.get('Comp(klbs)', 0.0))))
            
            peso_item_flutuado = peso_item_ar * fator_flutuacao * fator_inclinacao

            if peso_acumulado + peso_item_flutuado >= wob_planejado:
                peso_faltante = wob_planejado - peso_acumulado
                fracao_comp = peso_faltante / peso_item_flutuado if peso_item_flutuado > 0 else 0
                distancia_np += (fracao_comp * comp_m)
                componente_np = comp_nome
                np_encontrado = True
                break
            else:
                peso_acumulado += peso_item_flutuado
                distancia_np += comp_m

        # Se não encontrou na BHA, calcula o quanto subiu no Drill Pipe
        if not np_encontrado:
            peso_faltante = wob_planejado - peso_acumulado
            peso_linear_dp_klbs_m = ((peso_linear_dp * 3.28084) / 1000) * fator_flutuacao * fator_inclinacao if 'peso_linear_dp' in locals() else 0.015
            
            if peso_linear_dp_klbs_m > 0:
                distancia_np += (peso_faltante / peso_linear_dp_klbs_m)
            componente_np = "Drill Pipe"

        # Exibe o valor da Linha Neutra SEMPRE
        st.info(f"⚖️ **Linha Neutra (NP):** A **{distancia_np:.1f} m** da broca (Ferramenta: **{componente_np}**)")

        # Se subiu para o DP, exibe o alerta logo abaixo
        if not np_encontrado:
            st.warning("⚠️ **Atenção:** O WOB planejado excede o peso flutuado da BHA. A Linha Neutra subiu para o Drill Pipe (Risco de Fadiga)!")

        # --- 2. POSICIONAMENTO DO DRILLING JAR ---
        posicao_jar_atual = next((item for item in resultados_bha if "JAR" in str(item.get('Componente', '')).upper()), None)
        if posicao_jar_atual:
            peso_efetivo = parse_weight(posicao_jar_atual.get('Acum(klbs)', '0')) * fator_flutuacao * fator_inclinacao
            if peso_efetivo < margem_seguranca: 
                st.error(f"🚨 **Alerta de Fadiga:** Peso no Jar ({peso_efetivo:.1f} klbf) < Margem Segura ({margem_seguranca:.1f} klbf). Jar operando em compressão ou neutro.")
            else: 
                st.success(f"✅ **Jar Bem Posicionado:** {peso_efetivo:.1f} klbf (Operando tracionado de forma segura).")
        else:
            item_recomendado = None
            for item in resultados_bha:
                peso_efetivo_acumulado = parse_weight(item.get('Acum(klbs)', '0')) * fator_flutuacao * fator_inclinacao
                if peso_efetivo_acumulado >= margem_seguranca:
                    item_recomendado = item.get('Componente', 'Desconhecido')
                    break
            if item_recomendado: 
                st.success(f"💡 **Recomendação de Jar:** Posicione **acima** da ferramenta: **{item_recomendado}**.")
            else: 
                st.error("🚨 **Atenção:** Peso TOTAL da BHA insuficiente para garantir tração no Jar com este WOB.")

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
    
    # Cargas da coluna isolada (Para análise de flambagem no fundo)
    puw_string = T_axial + arrasto_axial
    sow_string = T_axial - arrasto_axial
    
    # Cargas Lidas no Indicador de Peso na Cabine (Somando o Bloco/Top Drive)
    peso_top_drive_val = peso_top_drive if 'peso_top_drive' in locals() else 30.0
    rot_w = T_axial + peso_top_drive_val
    puw = puw_string + peso_top_drive_val
    sow = sow_string + peso_top_drive_val
    max_pull = puw + overpull_margin
    
    st.write("**Previsão de Cargas no Gancho (Lidas no Painel da Sonda)**")
    c_td_a, c_td_b, c_td_c, c_td_d, c_td_e = st.columns(5)
    c_td_a.metric("Rotary Wt", f"{rot_w:.1f} klbs")
    c_td_b.metric("Pick-Up Wt", f"{puw:.1f} klbs", f"+{arrasto_axial:.1f}k Drag", delta_color="inverse")
    c_td_c.metric("Slack-Off Wt", f"{sow:.1f} klbs", f"-{arrasto_axial:.1f}k Drag", delta_color="normal")
    c_td_d.metric("Max Pull", f"{max_pull:.1f} klbs", f"Overpull {overpull_margin:.0f}k", delta_color="off")
    c_td_e.metric("Torque (M)", f"{torque_friccao_lbft:.0f} lb-ft")
    
    st.write("**Análise de Risco Operacional e Transferência de WOB**")
    wob_alvo = st.session_state.wob_main
    peso_disponivel = sow_string - (wob_alvo * 1.2)
    
    if sow_string < wob_alvo:
        st.error(f"🚨 **Risco Crítico de Buckling:** Peso disponível da coluna descendo ({sow_string:.1f} klbs) é menor que o WOB Planejado ({wob_alvo:.1f} klbs). Sem peso na broca.")
    elif peso_disponivel < 0:
        st.warning(f"⚠️ **Atenção (Sliding):** Slack-off marginal. Risco de pendurar a coluna ao tentar transferir {wob_alvo:.1f} klbs de peso.")
    else:
        st.success(f"✅ **Transferência Segura:** Slack-Off da coluna ({sow_string:.1f} klbs) permite deslizar e transferir {wob_alvo:.1f} klbs na broca com segurança.")

# ==========================================
# MÓDULO DE ANÁLISE ECONÔMICA (CUSTO POR METRO)
# ==========================================
st.markdown("---")
st.header("💰 Análise Econômica Operacional")
st.write("Avalie o impacto financeiro da estratégia calculada no Ouija-Board.")

col_eco1, col_eco2, col_eco3 = st.columns(3)

with col_eco1:
    st.subheader("Custos Operacionais Diários")
    sonda_dia = st.number_input("Custo da Sonda ($/dia)", value=50000.0, step=1000.0)
    bha_dia = st.number_input("Custo Ferramentas/Direcional ($/dia)", value=15000.0, step=500.0)
    
    custo_hora = (sonda_dia + bha_dia) / 24.0

with col_eco2:
    st.subheader("Desempenho (ROP)")
    rop_rotary = st.number_input("ROP Estimada - Rotary (m/h)", value=30.0, step=1.0)
    rop_slide = st.number_input("ROP Estimada - Slide (m/h)", value=10.0, step=1.0)

with col_eco3:
    st.subheader("Resumo do Trecho Projetado")
    st.metric("Custo Fixo por Hora", f"$ {custo_hora:,.2f}")
    
    # 💡 LENDO DA MEMÓRIA DA SESSÃO
    if 'out_pm' in st.session_state and st.session_state['out_pm'] > 0:
        pm_calc = st.session_state['out_pm']
        slide_calc = st.session_state['out_slide']
        rotary_calc = st.session_state['out_rotary']
        
        if rop_rotary > 0 and rop_slide > 0:
            tempo_slide = slide_calc / rop_slide
            tempo_rotary = rotary_calc / rop_rotary
            tempo_total = tempo_slide + tempo_rotary
            
            custo_trecho = tempo_total * custo_hora
            custo_por_metro = custo_trecho / pm_calc
            
            st.metric("Custo do Trecho Projetado", f"$ {custo_trecho:,.2f}")
            st.metric("Custo por Metro ($/m)", f"$ {custo_por_metro:,.2f}", help="Custo médio baseado no ratio de Slide vs Rotary.")
        else:
            st.info("Insira uma ROP maior que zero para calcular.")
    else:
         st.info("Calcule uma projeção direcional acima para visualizar os custos.")

# ==========================================
# RELATÓRIO INTERATIVO DE HIDRÁULICA E FLUIDOS
# ==========================================
st.markdown("---")
st.header("🌊 Relatório de Hidráulica e Limpeza de Poço")
st.write("Análise de perfilagem dinâmica cruzando a trajetória real com os parâmetros globais de fluido e poço.")

if 'df_trajetoria' in st.session_state and not st.session_state['df_trajetoria'].empty:
    df_hyd = st.session_state['df_trajetoria'].copy()
    
    # --- ROTEAMENTO DE VARIÁVEIS GLOBAIS ---
    # Substituímos as caixas de digitação manuais pelas variáveis já declaradas acima
    mw = peso_lama_ppg
    gpm = vazao_gpm
    dh_in = dh
    dp_in = od_dp if 'od_dp' in locals() else 5.0
    
    # --- MOTOR MATEMÁTICO DE HIDRÁULICA ---
    prof_md = df_hyd["MD (m)"]
    angulo = df_hyd["Inc (°)"] if "Inc (°)" in df_hyd.columns else prof_md * 0.0
    
    va_base = (24.5 * gpm) / ((dh_in**2) - (dp_in**2))
    va_curva = np.full(len(prof_md), va_base)
    
    esd_curva = np.full(len(prof_md), mw)
    fator_atrito = (pv + yp) / 100.0
    ecd_curva = mw + (prof_md / 1000.0) * fator_atrito * (gpm / 300.0)

    # --- CONSTRUÇÃO DO GRÁFICO (MULTI-TRACK CLEAN) ---
        
    st.markdown("#### 📊 Perfil de Geometria e Pressões")
    
    # Removemos os subplot_titles. Os próprios eixos farão a função de cabeçalho para evitar sobreposição.
    fig_hyd = make_subplots(rows=1, cols=4, shared_yaxes=True, horizontal_spacing=0.02)

    r_poco = dh_in / 2.0
    r_tubo = dp_in / 2.0

    # Track 1: Geometria (Minimalista - Sem blocos pesados)
    fig_hyd.add_trace(go.Scatter(x=[-r_poco, -r_poco], y=[0, prof_md.max()], mode='lines', name='Poço', line=dict(color='lightgray', width=2), showlegend=False), row=1, col=1)
    fig_hyd.add_trace(go.Scatter(x=[r_poco, r_poco], y=[0, prof_md.max()], mode='lines', line=dict(color='lightgray', width=2), showlegend=False), row=1, col=1)
    fig_hyd.add_trace(go.Scatter(x=[0, 0], y=[0, prof_md.max()], mode='lines', name='Coluna (DP)', line=dict(color='#87CEFA', width=8), showlegend=False), row=1, col=1) # Linha grossa central simulando o tubo
    fig_hyd.add_trace(go.Scatter(x=[-r_poco, r_poco], y=[prof_md.max(), prof_md.max()], mode='lines', name='Broca', line=dict(color='gold', width=4), showlegend=False), row=1, col=1)

    # Track 2: Trajetória (Cores vivas, sem preenchimento)
    fig_hyd.add_trace(go.Scatter(x=angulo, y=prof_md, mode='lines', name='Inclinação (°)', line=dict(color='#00FFFF', width=3)), row=1, col=2)
    
    # Track 3: Pressões e Densidades (Linhas nítidas contrastantes)
    fig_hyd.add_trace(go.Scatter(x=esd_curva, y=prof_md, mode='lines', name='ESD (Estático)', line=dict(color='#1E90FF', width=2, dash='dash')), row=1, col=3)
    fig_hyd.add_trace(go.Scatter(x=ecd_curva, y=prof_md, mode='lines', name='ECD (Circulando)', line=dict(color='#FF3333', width=3)), row=1, col=3)

    # Track 4: Limpeza do Poço
    fig_hyd.add_trace(go.Scatter(x=va_curva, y=prof_md, mode='lines', name='Vel. Anular (ft/min)', line=dict(color='#FFD700', width=3)), row=1, col=4)

    # Configurações Clean Dark Mode
    fig_hyd.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=750,
        margin=dict(t=90, b=40, l=40, r=20), # Margem superior 't=90' dá espaço seguro para os textos
        hovermode='y unified',               # 💡 MÁGICA: Uma linha horizontal mostra todos os dados juntos!
        
        yaxis=dict(title='MD (m)', autorange='reversed', showgrid=True, gridcolor='#333333', zeroline=False),
        
        # Eixos no topo com os nomes organizados
        xaxis=dict(side='top', title='<b>Geometria</b>', range=[-dh_in, dh_in], showticklabels=False, showgrid=False, zeroline=False),
        xaxis2=dict(side='top', title='<b>Graus (°)</b>', range=[0, 90], showgrid=True, gridcolor='#333333', zeroline=False),
        xaxis3=dict(side='top', title='<b>Densidade (lb/gal)</b>', range=[mw - 0.5, mw + 1.5], showgrid=True, gridcolor='#333333', zeroline=False),
        xaxis4=dict(side='top', title='<b>Va (ft/min)</b>', range=[50, 300], showgrid=True, gridcolor='#333333', zeroline=False),
        
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig_hyd, use_container_width=True)
    
else:
    st.info("👆 Importe a Trajetória na primeira seção para liberar o Módulo de Hidráulica.")

# ==========================================
# RELATÓRIO PDF
# ==========================================
st.markdown("---")
st.header(t["head_pdf"])

md1 = last_md if 'last_md' in locals() else 0.0
inc1 = last_inc if 'last_inc' in locals() else 0.0
az1 = last_az if 'last_az' in locals() else 0.0
tvd1 = last_tvd if 'last_tvd' in locals() else 0.0
ns1 = last_ns if 'last_ns' in locals() else 0.0
ew1 = last_ew if 'last_ew' in locals() else 0.0

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
        
        # Define o fuso horário oficial
        fuso_br = pytz.timezone('America/Bahia') 

        # Pega a hora exata já convertida
        dt_atual = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")

        # Imprime no PDF usando a variável dt_atual corrigida
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
        
        # 💡 RESGATA AS VARIÁVEIS SALVAS NO COFRE DA SESSÃO
        slide_pdf = st.session_state.get('out_slide', 0.0)
        rotary_pdf = st.session_state.get('out_rotary', 0.0)
        tf_pdf = st.session_state.get('out_tf_motor', tf_deg) 
        
        pdf.cell(47, 8, f'MD1: {md1}m', border=1)
        pdf.cell(47, 8, f'MD2: {md2}m', border=1)
        pdf.cell(48, 8, f'Toolface: {tf_pdf:.0f} graus', border=1)
        pdf.cell(48, 8, f'DLS: {dls:.2f} /30m', border=1, ln=True)
        pdf.cell(0, 8, f'Slide Recomendado: {slide_pdf:.1f} m  |  Rotary: {rotary_pdf:.1f} m', border=1, ln=True)
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
