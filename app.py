import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import io
import datetime
import requests
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from exif import Image as ExifImage

# CONFIG
TELEGRAM_TOKEN = "9115675773:AAHIeiGqf3tYG78HqvLn0iiZp_10kQtFJnk"
TELEGRAM_CHAT_ID = "8632454326"
LICENCIAS_VALIDAS = {"TOPO150-ABC123-2026-12-31": "2026-12-31", "TOPO300-XYZ789-2027-06-30": "2027-06-30", "TOPO450-EMP001-2027-12-31": "2027-12-31", "SENA2026": "2027-12-31"}
MARCA = "TopoAuto Pro"
NOMBRE = "Ing. Juan David Ospino M."
CELULAR = "300 239 0779"

# FUNCIONES IGUALES: enviar_telegram, validar_licencia, convertir_a_grados_decimales, extraer_datos_foto, generar_dwg_texto, generar_pdf_igac, generar_pdf_bitacora
# ... Pega aquí todas las funciones del código anterior ...

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, data=data, timeout=5)
    except: pass

def validar_licencia(clave):
    if clave == "SENA2026": return True, "Acceso de Desarrollador Autorizado sin límite", "EMPRESA"
    if clave in LICENCIAS_VALIDAS:
        fecha_vence = datetime.datetime.strptime(LICENCIAS_VALIDAS[clave], "%Y-%m-%d").date()
        if datetime.date.today() <= fecha_vence:
            tipo = "EMPRESA" if "450" in clave else "PRO" if "300" in clave else "BASICO"
            return True, f"Licencia {tipo} Válida hasta {fecha_vence}", tipo
    return False, "Licencia Inválida o Vencida", "NINGUNA"

def convertir_a_grados_decimales(coordenadas, referencia):
    if not coordenadas or len(coordenadas) < 3: return 0.0
    grados, minutos, segundos = coordenadas[0], coordenadas[1], coordenadas[2]
    decimal = grados + (minutos / 60.0) + (segundos / 3600.0)
    if referencia in ['S', 'W']: decimal = -decimal
    return decimal

def extraer_datos_foto(archivo_foto):
    try:
        bytes_foto = archivo_foto.read(); imagen_exif = ExifImage(bytes_foto)
        if imagen_exif.has_exif:
            lat_raw = getattr(imagen_exif, 'gps_latitude', None); lat_ref = getattr(imagen_exif, 'gps_latitude_ref', 'N')
            lon_raw = getattr(imagen_exif, 'gps_longitude', None); lon_ref = getattr(imagen_exif, 'gps_longitude_ref', 'E')
            cota = getattr(imagen_exif, 'gps_altitude', 0.0)
            if lat_raw and lon_raw: return convertir_a_grados_decimales(lat_raw, lat_ref), convertir_a_grados_decimales(lon_raw, lon_ref), cota
    except: pass
    return None

def generar_dwg_texto(df):
    contenido = "HEADER\nVERSION TOPOAUTO\nENTITIES\n"
    for i, row in df.iterrows(): contenido += f"POINT\nP:{row.get('Punto', i)}\nE:{row.get('Este', 0.0)}\nN:{row.get('Norte', 0.0)}\nC:{row.get('Cota', 0.0)}\n"
    return io.BytesIO(contenido.encode())

def generar_pdf_igac(df, nombre_cliente, clave_usada):
    buffer = io.BytesIO(); c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 14); c.drawString(100, 750, "CUADRO DE COORDENADAS - FORMATO IGAC")
    c.setFont("Helvetica", 10); c.drawString(100, 730, f"Cliente: {nombre_cliente}"); c.drawString(100, 710, f"Licencia: {clave_usada} | {datetime.date.today()}")
    y = 670; c.setFont("Helvetica-Bold", 10); c.drawString(100, y, "PUNTO | NORTE | ESTE | COTA"); c.line(100, y-5, 500, y-5); y -= 20; c.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        if y < 80: c.showPage(); y = 750
        c.drawString(100, y, f"{row.get('Punto', i)} | {row.get('Norte', 0.0)} | {row.get('Este', 0.0)} | {row.get('Cota', 0.0)}"); y -= 18
    c.drawString(100, 50, f"TOPOAUTO PRO v4.9.1 — {NOMBRE} - {CELULAR}"); c.save(); buffer.seek(0); return buffer

def generar_pdf_bitacora(fecha, proyecto, ubicacion, personal, equipo, clima, actividades, observaciones, nombre):
    buffer = io.BytesIO(); c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.drawString(100, 750, "BITÁCORA DE ACTIVIDADES TOPOGRÁFICAS")
    c.setFont("Helvetica-Bold", 12); c.drawString(100, 720, f"PROYECTO: {proyecto}")
    c.setFont("Helvetica", 10); c.drawString(100, 700, f"Fecha: {fecha} | {ubicacion}"); c.drawString(100, 680, f"Resp: {nombre}"); c.line(100, 670, 500, 670)
    y=650; c.setFont("Helvetica-Bold", 11); c.drawString(100, y, "1. PERSONAL Y EQUIPO:"); y-=20; c.setFont("Helvetica", 10)
    c.drawString(120, y, f"Personal: {personal}"); y-=15; c.drawString(120, y, f"Equipo: {equipo}"); y-=15; c.drawString(120, y, f"Clima: {clima}")
    y-=30; c.setFont("Helvetica-Bold", 11); c.drawString(100, y, "2. ACTIVIDADES:"); y-=20; c.setFont("Helvetica", 10)
    for linea in actividades.split('\n'): c.drawString(120, y, f"- {linea}"); y-=15
    y-=20; c.setFont("Helvetica-Bold", 11); c.drawString(100, y, "3. OBSERVACIONES:"); y-=20; c.setFont("Helvetica", 10); c.drawString(120, y, observaciones)
    c.drawString(100, 50, f"Firma: ____________________   {MARCA} - {CELULAR}"); c.save(); buffer.seek(0); return buffer

# ========= CSS SANTA MARTA LOS CERROS =========
st.set_page_config(page_title=f"{MARCA}", layout="wide", page_icon="⛰️")

st.markdown("""
<style>
    .main {background-color: #f8fafc;}
    .stApp header {background: linear-gradient(90deg, #0ea5e9 0%, #059669 100%);} /* Azul mar + Verde sierra */
    h1 {color: #0c4a6e !important; font-weight: 800;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg, #0c4a6e 0%, #134e4a 100%) !important; color: #f8fafc !important;}
    div[data-testid="stMetric"] {background: white; padding: 20px; border-radius: 15px; border-left: 5px solid #059669; box-shadow: 0 4px 12px rgba(0,0,0,0.05);}
    .stButton>button {background: linear-gradient(90deg, #0ea5e9 0%, #059669 100%); color: white; border-radius: 10px; border: none; font-weight: 700; padding: 12px 24px;}
    .stButton>button:hover {transform: scale(1.03);}
    .header-container {display: flex; align-items: center; gap: 20px; padding: 10px 0 20px 0; border-bottom: 3px solid #0ea5e9;}
    .logo-text {font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg, #0ea5e9 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
</style>
""", unsafe_allow_html=True)

# ========= HEADER CON LOGO =========
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.markdown("### ⛰️") # Si tienes logo PNG lo subes y lo pones aquí
with col_titulo:
    st.markdown('<p class="logo-text">TopoAuto Pro</p>', unsafe_allow_html=True)
    st.caption("Solución Topográfica para la Sierra Nevada y el Caribe | Por: Ing. Juan David Ospino M.")

st.markdown("---")

# ========= LOGIN Y APP IGUAL =========
if 'logueado' not in st.session_state: st.session_state.logueado = False

if not st.session_state.logueado:
    st.header("🔑 Activación de Licencia")
    with st.container():
        clave_input = st.text_input("Llave de Licencia Comercial:", type="password")
        nombre_input = st.text