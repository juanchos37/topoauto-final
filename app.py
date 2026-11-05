import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import io
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import Polygon
import zipfile
import os

# 1. DATOS
MARCA = "TopoAuto"
NOMBRE = "Ing. Juan David Ospino M."
CARGO = "Cadenero Topográfico SENA | Desarrollador"
CELULAR = "300 239 0779"
EMAIL = "juanospimoscote33@gmail.com"
PRECIO_LICENCIA = 250000
DIAS_PRUEBA = 1

st.set_page_config(page_title=f"{MARCA} Pro", layout="wide", page_icon="🗺️")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e293b !important; color: #f8fafc !important; }
div[data-testid="stMetric"] { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 6px solid #2563eb; }
.stTabs [aria-selected="true"] { background-color: #2563eb !important; color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown(f"# 🗺️ **{MARCA} Pro**")
    st.markdown(f"*{CARGO}*")
    st.markdown(f"👤 **{NOMBRE}**")
    codigo_admin = st.text_input("Código de acceso:", type="password")
    if codigo_admin == "SENA2026":
        st.session_state.licencia_activa = True
        st.success("✨ Licencia Activa")

# CONTROL
if 'primer_ingreso' not in st.session_state:
    st.session_state.primer_ingreso = datetime.date.today()
    st.session_state.licencia_activa = False
dias_restantes = DIAS_PRUEBA - (datetime.date.today() - st.session_state.primer_ingreso).days

if dias_restantes < 0 and not st.session_state.licencia_act