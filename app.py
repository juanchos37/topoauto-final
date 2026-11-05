import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import io
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import Polygon

# 1. TUS DATOS PROFESIONALES
MARCA = "TopoAuto"
NOMBRE = "Ing. Juan David Ospino M."
CARGO = "Cadenero Topográfico SENA | Desarrollador"
CELULAR = "300 239 0779"
EMAIL = "juanospimoscote33@gmail.com"
PRECIO_LICENCIA = 150000  # LE SUBIMOS EL PRECIO POR EL DISEÑO PRO
DIAS_PRUEBA = 1

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title=f"{MARCA} Pro - {NOMBRE}", layout="wide", page_icon="🗺️")

# INYECCIÓN DE CSS AVANZADO
st.markdown("""
<style>
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { background-color: #1e293b !important; color: #f8fafc !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #f8fafc !important; }
div[data-testid="stMetric"] { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 6px solid #2563eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); transition: transform 0.2s; }
div[data-testid="stMetric"]:hover { transform: translateY(-2px); }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #f1f5f9; padding: 6px; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 6px; padding: 8px 16px; color: #475569 !important; font-weight: 600; }
.stTabs [aria-selected="true"] { background-color: #2563eb !important; color: #ffffff !important; }
div[data-testid="stFileUploader"] { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 10px; background-color: #f8fafc; }
</style>
""", unsafe_allow_html=True)

# BARRA LATERAL
with st.sidebar:
    st.markdown(f"# 🗺️ **{MARCA} Pro**")
    st.markdown(f"*{CARGO}*")
    st.markdown("---")
    st.markdown(f"👤 **Desarrollador:**\n{NOMBRE}")
    st.markdown("---")
    st.markdown("### 🔐 Área de Activación")
    codigo_admin = st.text_input("Código de acceso:", type="password", placeholder="Llave de licencia")
    if codigo_admin == "SENA2026":
        st.session_state.licencia_activa = True
        st.success("✨ Licencia de Desarrollador Activa")

# 2. CONTROL DE PRUEBA Y ACTIVACIÓN
if 'primer_ingreso' not in st.session_state:
    st.session_state.primer_ingreso = datetime.date.today()
    st.session_state.licencia_activa = False

dias_transcurridos = (datetime.date.today() - st.session_state.primer_ingreso).days
dias_restantes = DIAS_PRUEBA - dias_transcurridos

# 3. BLOQUEO SI SE ACABÓ LA PRUEBA
if dias_restantes < 0 and not st.session_state.licencia_activa:
    st.error("🚨 SU PERIODO DE PRUEBA HA FINALIZADO")
    st.header(f"Adquiera su Licencia Comercial: ${PRECIO_LICENCIA:,} COP")
    st.write("Para continuar procesando carteras topográficas sin límites:")
    col_pago1, col_pago2 = st.columns(2)
    with col_pago1: st.info(f"📱 **Nequi / Daviplata**\n\n`{CELULAR}`")
    with col_pago2: st.info(f"🏦 **Transferencia**\n\nSolicitar datos al contacto")
    st.markdown("---")
    st.markdown(f"📞 **Soporte:** {NOMBRE} | {CELULAR}")
    st.markdown(f"📧 **Correo:** {EMAIL}")
    st.warning("Envíe su comprobante vía WhatsApp y activaremos su licencia en menos de 30 minutos.")
    if st.button("💬 NOTIFICAR PAGO POR WHATSAPP"):
        st.success(f"Perfecto. Comunícate al {CELULAR} para activación inmediata.")
    st.stop()

# 4. BANNERS
if dias_restantes >= 0 and not st.session_state.licencia_activa:
    st.info(f"🎁 **Versión de Evaluación:** Te queda {dias_restantes} día. Licencia Pro: ${PRECIO_LICENCIA:,} COP")
elif st.session_state.licencia_activa:
    st.success("⚡ **Modo Corporativo Activo** | Soporte premium habilitado.")

# ENCABEZADO
st.title("🗺️ Procesador de Carteras Topográficas Pro")
st.markdown("Convierte tus datos de campo en informes ejecutivos y planos base de ingeniería en 5 minutos.")
st.markdown("---")

# PASO 1: CARGA
st.subheader("📋 Paso 1: Carga de Datos de Campo")
archivo = st.file_uploader("Arrastra tu archivo Excel (.xlsx) con columnas: Punto, Este, Norte, Cota, Descripcion", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df = df.dropna(subset=['Punto', 'Este', 'Norte', 'Cota', 'Descripcion'])
    st.success(f"✔️ ¡Excelente! Se cargaron {len(df)} puntos topográficos.")

    # FILTRO
    st.markdown("### 🔍 Configuración del Filtro")
    opciones = ['TODOS LOS PUNTOS'] + sorted(list(df['Descripcion'].unique().astype(str)))
    filtro = st.selectbox("Seleccionar grupo de puntos:", opciones)
    df_filtrado = df[df['Descripcion'] == filtro].copy() if filtro != 'TODOS LOS PUNTOS' else df.copy()

    # CÁLCULOS
    df_filtrado['Distancia_m'] = np.sqrt((df_filtrado['Este'] - df_filtrado['Este'].shift(1))**2 + (df_filtrado['Norte'] - df_filtrado['Norte'].shift(1))**2)
    df_filtrado['Distancia_m'] = df_filtrado['Distancia_m'].fillna(0).round(3)
    
    area_total = 0
    poligono_geom = None
    if len(df_filtrado) > 2:
        try:
            gdf = gpd.GeoDataFrame(df_filtrado, geometry=gpd.points_from_xy(df_filtrado.Este, df_filtrado.Norte), crs="EPSG:9377")
            poligono_geom = gdf.unary_union.convex_hull
            area_total = poligono_geom.area
        except:
            gdf = gpd.GeoDataFrame(df_filtrado, geometry=gpd.points_from_xy(df_filtrado.Este, df_filtrado.Norte), crs="EPSG:9377")
            area_total = 0
    else:
        gdf = gpd.GeoDataFrame(df_filtrado, geometry=gpd.points_from_xy(df_filtrado.Este, df_filtrado.Norte), crs="EPSG:9377")

    st.markdown("---")
    st.subheader("📊 Paso 2: Análisis del Levantamiento")

    # TABS
    tab_resumen, tab_tabla, tab_plano, tab_exportar = st.tabs([
        "📈 Resumen y Métricas", "📄 Tabla de Coordenadas", "📐 Plano Planimétrico", "📥 Módulo de Descargas"
    ])

    with tab_resumen:
        st.markdown("#### Indicadores Clave")
        c1, c2, c3 = st.columns(3)
        c1.metric(label="🔢 Total Puntos", value=f"{len(df_filtrado)} pts")
        c2.metric(label="⛰️ Cota Promedio", value=f"{round(df_filtrado['Cota'].mean(), 2)} m")
        c3.metric(label="📐 Área Polígono", value=f"{round(area_total, 2)} m²")

    with tab_tabla:
        st.markdown("#### Registros Filtrados con Distancias")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    with tab_plano:
        st.markdown("#### Vista de Planta del Levantamiento")
        fig, ax = plt.subplots(figsize=(9, 6), facecolor='#f8fafc')
        ax.set_facecolor('#ffffff')
        if poligono_geom and not poligono_geom.is_empty and isinstance(poligono_geom, Polygon):
            x_pol, y_pol = poligono_geom.exterior.xy
            ax.fill(x_pol, y_pol, alpha=0.12, fc='#10b981', ec='#047857', linewidth=2, label='Polígono de Terreno')
        ax.scatter(df_filtrado['Este'], df_filtrado['Norte'], color='#2563eb', s=45, zorder=5, label='Puntos')
        for idx, row in df_filtrado.iterrows():
            ax.text(row['Este'], row['Norte'], f" {int(row['Punto'])}", fontsize=9, fontweight='bold', color='#1e293b')
        ax.set_xlabel("Coordenada ESTE (X)", fontweight='bold')
        ax.set_ylabel("Coordenada NORTE (Y)", fontweight='bold')
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.axis('equal'); ax.legend()
        st.pyplot(fig)

    with tab_exportar:
        st.markdown("#### Generación Automática de Entregables")
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        
        # EXCEL
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Cartera_Procesada')
        col_dl1.download_button("🟢 DESCARGAR EXCEL", output_excel.getvalue(), f"Cartera_{filtro}_{datetime.date.today()}.xlsx", use_container_width=True)
        
        # SHAPEFILE
        output_shp = io.BytesIO()
        gdf.to_file(output_shp, driver='ESRI Shapefile')
        col_dl2.download_button("🟡 DESCARGAR SHAPEFILE", output_shp.getvalue(), "puntos.shp", use_container_width=True)

        # PDF ARREGLADO
        output_pdf = io.BytesIO()
        with PdfPages(output_pdf) as pdf:
            fig_pdf, ax_pdf = plt.subplots(figsize=(8.5, 11))
            if poligono_geom and not poligono_geom.is_empty and isinstance(poligono_geom, Polygon):
                x_p, y_p = poligono_geom.exterior.xy
                ax_pdf.fill(x_p, y_p, alpha=0.12, fc='#10b981', ec='#047857')
            ax_pdf.scatter(df_filtrado['Este'], df_filtrado['Norte'], color='#2563eb', s=20)
            ax_pdf.set_title(f"PLANO PRELIMINAR - {MARCA}", fontsize=14, fontweight='bold')
            ax_pdf.set_xlabel("COORDENADA ESTE"); ax_pdf.set_ylabel("COORDENADA NORTE")
            ax_pdf.grid(True); ax_pdf.axis('equal')
            ax_pdf.text(0.5, 0.02, f"{NOMBRE} - {CARGO} | Cel: {CELULAR} | Email: {EMAIL}", transform=ax_pdf.transAxes, ha='center', fontsize=8, style='italic')
            pdf.savefig(fig_pdf, bbox_inches='tight'); plt.close(fig_pdf)
        col_dl3.download_button("🔴 DESCARGAR PDF", output_pdf.getvalue(), f"Plano_{filtro}.pdf", use_container_width=True)

    st.markdown("---")
    st.markdown(f"**{MARCA} Pro** | Desarrollado por {NOMBRE} - {CARGO}")
    st.markdown(f"Contacto: {CELULAR} | {EMAIL}")

else:
    st.info("Cargue un archivo para iniciar el procesamiento automático")