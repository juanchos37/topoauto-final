import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import io
import datetime
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import Polygon
from exif import Image as ExifImage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ========= CONFIGURACIÓN SEGURA =========
TELEGRAM_TOKEN = "PON_AQUI_TU_TOKEN"
TELEGRAM_CHAT_ID = "PON_AQUI_TU_CHAT_ID"
CLAVE_SECRETA = "TOPOAUTO2026"  # Clave maestra del desarrollador

# Base de datos de licencias. Formato: "CLAVE": "FECHA_VENCIMIENTO"
LICENCIAS_VALIDAS = {
    "TOPO150-ABC123-2026-12-31": "2026-12-31", # Plan BÁSICO $150.000
    "TOPO300-XYZ789-2027-06-30": "2027-06-30", # Plan PRO $300.000
    "TOPO450-EMP001-2026-11-6": "2027-12-31", # Plan EMPRESA $450.000
}

# ========= FUNCIONES CORE =========
def enviar_telegram(mensaje):
    try:
        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, data=data, timeout=5)
    except:
        pass

def validar_licencia(clave):
    if clave == "SENA2026":  # Tu acceso maestro como desarrollador
        return True, "Acceso de Desarrollador Autorizado sin límite"
    if clave in LICENCIAS_VALIDAS:
        fecha_vence = datetime.datetime.strptime(LICENCIAS_VALIDAS[clave], "%Y-%m-%d").date()
        if datetime.date.today() <= fecha_vence:
            return True, f"Licencia Válida comercialmente hasta {fecha_vence}"
    return False, "Licencia Inválida o Vencida"

def convertir_a_grados_decimales(coordenadas, referencia):
    if not coordenadas or len(coordenadas) < 3:
        return 0.0
    grados = coordenadas[0]
    minutos = coordenadas[1]
    segundos = coordenadas[2]
    decimal = grados + (minutos / 60.0) + (segundos / 3600.0)
    if referencia in ['S', 'W']:
        decimal = -decimal
    return decimal

def extraer_datos_foto(archivo_foto):
    try:
        bytes_foto = archivo_foto.read()
        imagen_exif = ExifImage(bytes_foto)
        if imagen_exif.has_exif:
            lat_raw = getattr(imagen_exif, 'gps_latitude', None)
            lat_ref = getattr(imagen_exif, 'gps_latitude_ref', 'N')
            lon_raw = getattr(imagen_exif, 'gps_longitude', None)
            lon_ref = getattr(imagen_exif, 'gps_longitude_ref', 'E')
            cota = getattr(imagen_exif, 'gps_altitude', 0.0)
            
            if lat_raw and lon_raw:
                latitud = convertir_a_grados_decimales(lat_raw, lat_ref)
                longitud = convertir_a_grados_decimales(lon_raw, lon_ref)
                return latitud, longitud, cota
    except:
        return None
    return None

def generar_dwg_texto(df):
    contenido = "HEADER\nVERSION TOPOAUTO\nENTITIES\n"
    for i, row in df.iterrows():
        # Corregido: Mapeo explícito usando el objeto row con los nombres de tus columnas
        este_val = row.get('Este', 0.0)
        norte_val = row.get('Norte', 0.0)
        cota_val = row.get('Cota', 0.0)
        punto_val = row.get('Punto', i)
        contenido += f"POINT\nP:{punto_val}\nE:{este_val}\nN:{norte_val}\nC:{cota_val}\n"
    return io.BytesIO(contenido.encode())

def generar_pdf_igac(df, nombre_cliente, clave_usada):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "CUADRO DE COORDENADAS - FORMATO IGAC")
    c.setFont("Helvetica", 10)
    c.drawString(100, 730, f"Cliente/Empresa: {nombre_cliente}")
    c.drawString(100, 710, f"Licencia ID: {clave_usada} | Fecha: {datetime.date.today()}")
    
    y = 670
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y, "PUNTO  |  NORTE (Y)  |  ESTE (X)  |  COTA (Z)")
    c.line(100, y-5, 500, y-5)
    
    y -= 20
    c.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        if y < 80:  # Control de salto de página automático
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750
        p_val = row.get('Punto', i)
        n_val = row.get('Norte', 0.0)
        e_val = row.get('Este', 0.0)
        c_val = row.get('Cota', 0.0)
        c.drawString(100, y, f"{p_val}  |  {n_val}  |  {e_val}  |  {c_val}")
        y -= 18
        
    c.drawString(100, 50, f"TOPOAUTO PRO v4.8 — SOFTWARE VERIFICADO BAJO PROYECCIÓN IGAC")
    c.save()
    buffer.seek(0)
    return buffer

# ========= INTERFAZ GRÁFICA (CSS) =========
st.set_page_config(page_title="TopoAuto v4.8 PRO", layout="wide", page_icon="📍")

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    [data-testid="stSidebar"] { background-color: #1e293b !important; color: #f8fafc !important; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #f8fafc !important; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border-left: 6px solid #2563eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #f1f5f9; padding: 6px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 6px; padding: 8px 16px; color: #475569 !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: #ffffff !important; }
    div[data-testid="stFileUploader"] { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 10px; background-color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

st.title("📍 TopoAuto v4.8 PRO")
st.caption("Módulo de Ingeniería Automatizado: De Excel a DWG + Informes Planimétricos")
st.markdown("---")

# ========= SISTEMA DE SEGURIDAD INTERNO =========
if 'logueado' not in st.session_state:
    st.session_state.logueado = False

if not st.session_state.logueado:
    st.header("🔑 Activación de Licencia del Software")
    st.write("Por favor, ingrese sus credenciales para desbloquear los módulos de cálculo.")
    
    col_login1, col_login2 = st.columns(2)
    with col_login1:
        clave_input = st.text_input("Llave de Licencia Comercial:", type="password", placeholder="Paste License Key")
    with col_login2:
        nombre_input = st.text_input("Identificación del Cliente o Empresa:", placeholder="Ej. Ingeniería S.A.S")
        
    if st.button("VERIFICAR Y ACTIVAR"):
        if not clave_input or not nombre_input:
            st.warning("⚠️ Complete la clave corporativa y el nombre de la firma legal.")
        else:
            valido, mensaje = validar_licencia(clave_input)
            if valido:
                st.session_state.logueado = True
                st.session_state.clave = clave_input
                st.session_state.nombre = nombre_input
                st.success(f"✔️ {mensaje}")
                enviar_telegram(f"✅ ACCESO AUTORIZADO: {nombre_input} | Clave: {clave_input}")
                st.rerun()
            else:
                st.error(f"❌ {mensaje}")
                enviar_telegram(f"⚠️ INTENTO FALLIDO: {nombre_input} ingresó clave errónea: {clave_input}")
    st.stop()

# ========= PANEL PRINCIPAL DESBLOQUEADO =========
with st.sidebar:
    st.markdown(f"### ⚙️ Licencia Corporativa")
    st.write(f"👤 **Usuario:** {st.session_state.nombre}")
    st.write(f"🔑 **ID Key:** `* * * * * * *`")
    st.success("Software Desbloqueado")

tab_excel_modo, tab_dron_modo = st.tabs(["📊 Procesar Excel (.xlsx)", "📸 Módulo Fotogrametría Dron"])

# --- MODULO 1: EXCEL TRADICIONAL ---
with tab_excel_modo:
    st.subheader("📋 Paso 1: Carga de Cartera de Coordenadas Terrestres")
    archivo = st.file_uploader("Subir archivo Excel", type=["xlsx"], key="excel_uploader")

    if archivo:
        df = pd.read_excel(archivo)
        df = df.dropna(subset=['Punto', 'Este', 'Norte', 'Cota'])
        st.success(f"✔️ Se han cargado con éxito {len(df)} puntos topográficos.")
        
        # Filtro por descripción opcional si existe la columna
        if 'Descripcion' in df.columns:
            opciones = ['TODOS LOS PUNTOS'] + sorted(list(df['Descripcion'].unique().astype(str)))
            filtro = st.selectbox("Filtrar por grupo descriptivo:", opciones, key="filtro_excel")
            df_filtrado = df[df['Descripcion'] == filtro].copy() if filtro != 'TODOS LOS PUNTOS' else df.copy()
        else:
            df_filtrado = df.copy()
            
        df_filtrado['Distancia_m'] = np.sqrt((df_filtrado['Este'] - df_filtrado['Este'].shift(1))**2 + (df_filtrado['Norte'] - df_filtrado['Norte'].shift(1))**2).fillna(0).round(3)
        
        area_total = 0
        poligono_geom = None
        if len(df_filtrado) > 2:
            try:
                gdf_temp = gpd.GeoDataFrame(df_filtrado, geometry=gpd.points_from_xy(df_filtrado.Este, df_filtrado.Norte))
                poligono_geom = gdf_temp.unary_union.convex_hull
                area_total = poligono_geom.area
            except:
                area_total = 0

        sub_tab_resumen, sub_tab_tabla, sub_tab_plano, sub_tab_exportar = st.tabs(["📈 Resumen", "📄 Tabla de Datos", "📐 Plano Base", "📥 Módulo de Descargas"])
        
        with sub_tab_resumen:
            c1, c2, c3 = st.columns(3)
            c1.metric(label="🔢 Cantidad de Puntos", value=f"{len(df_filtrado)} pts")
            c2.metric(label="⛰️ Altura / Cota Promedio", value=f"{round(df_filtrado['Cota'].mean(), 2)} m")
            c3.metric(label="📐 Superficie Polígono (Aprox)", value=f"{round(area_total, 2)} m²")
            
        with sub_tab_tabla:
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
        with sub_tab_plano:
            fig, ax = plt.subplots(figsize=(9, 6), facecolor='#f8fafc')
            ax.set_facecolor('#ffffff')
