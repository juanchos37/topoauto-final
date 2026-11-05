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

if dias_restantes < 0 and not st.session_state.licencia_activa:
    st.error("🚨 PRUEBA FINALIZADA")
    st.header(f"Licencia: ${PRECIO_LICENCIA:,} COP")
    st.info(f"Nequi: `{CELULAR}`")
    st.stop()

if dias_restantes >= 0 and not st.session_state.licencia_activa:
    st.info(f"🎁 Evaluación: {dias_restantes} día. Licencia Pro + Bitácora: ${PRECIO_LICENCIA:,} COP")

st.title("🗺️ Procesador de Carteras Topográficas Pro")
archivo = st.file_uploader("Carga tu Excel: Punto, Este, Norte, Cota, Descripcion", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo).dropna(subset=['Punto', 'Este', 'Norte', 'Cota', 'Descripcion'])
    st.success(f"✔️ {len(df)} puntos cargados.")
    
    filtro = st.selectbox("Filtrar por:", ['TODOS LOS PUNTOS'] + sorted(list(df['Descripcion'].unique().astype(str))))
    df_filtrado = df[df['Descripcion'] == filtro].copy() if filtro != 'TODOS LOS PUNTOS' else df.copy()
    
    df_filtrado['Distancia_m'] = np.sqrt((df_filtrado['Este'] - df_filtrado['Este'].shift(1))**2 + (df_filtrado['Norte'] - df_filtrado['Norte'].shift(1))**2).fillna(0).round(3)
    gdf = gpd.GeoDataFrame(df_filtrado, geometry=gpd.points_from_xy(df_filtrado.Este, df_filtrado.Norte), crs="EPSG:9377")
    
    area_total, poligono_geom = 0, None
    if len(df_filtrado) > 2:
        try:
            poligono_geom = gdf.unary_union.convex_hull
            area_total = poligono_geom.area
        except: pass

    tab_resumen, tab_tabla, tab_plano, tab_bitacora, tab_exportar = st.tabs([
        "📈 Resumen", "📄 Tabla", "📐 Plano", "📓 Bitácora", "📥 Descargas"
    ])

    with tab_resumen:
        c1, c2, c3 = st.columns(3)
        c1.metric("🔢 Puntos", f"{len(df_filtrado)}")
        c2.metric("⛰️ Cota Prom", f"{round(df_filtrado['Cota'].mean(), 2)} m")
        c3.metric("📐 Área", f"{round(area_total, 2)} m²")

    with tab_tabla:
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    with tab_plano:
        fig, ax = plt.subplots(figsize=(9, 6))
        if poligono_geom and isinstance(poligono_geom, Polygon):
            x_pol, y_pol = poligono_geom.exterior.xy
            ax.fill(x_pol, y_pol, alpha=0.12, fc='#10b981', ec='#047857')
        ax.scatter(df_filtrado['Este'], df_filtrado['Norte'], color='#2563eb', s=45)
        for _, row in df_filtrado.iterrows(): 
            ax.text(row['Este'], row['Norte'], f" {int(row['Punto'])}", fontweight='bold