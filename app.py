import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import io
import datetime
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from exif import Image as ExifImage

TELEGRAM_TOKEN = "9115675773:AAHIeiGqf3tYG78HqvLn0iiZp_10kQtFJnk"
TELEGRAM_CHAT_ID = "8632454326"

LICENCIAS_VALIDAS = {
    "TOPO150-ABC123-2026-12-31": "2026-12-31",
    "TOPO300-XYZ789-2027-06-30": "2027-06-30",
    "TOPO450-EMP001-2027-12-31": "2027-12-31",
    "SENA2026": "2027-12-31",
}

MARCA = "TopoAuto Pro"
NOMBRE = "Ing. Juan David Ospino M."
CELULAR = "300 239 0779"

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, data=data, timeout=5)
    except:
        pass

def validar_licencia(clave):
    if clave == "SENA2026":
        return True, "Acceso de Desarrollador Autorizado sin límite"
    if clave in LICENCIAS_VALIDAS:
        fecha_vence = datetime.datetime.strptime(LICENCIAS_VALIDAS[clave], "%Y-%m-%d").date()
        if datetime.date.today() <= fecha_vence:
            return True, f"Licencia Válida hasta {fecha_vence}"
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

def extraer_datos_foto(archivo_foto): # <-- FUNCIÓN ARREGLADA
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
    except Exception as e:
        pass
    return None

def generar_dwg_texto(df):
    contenido = "HEADER\nVERSION TOPOAUTO\nENTITIES\n"
    for i, row in df.iterrows():
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
    c.drawString(100, y, "PUNTO | NORTE (Y) | ESTE (X) | COTA (Z)")
    c.line(100, y-5, 500, y-5)
    y -= 20
    c.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        if y < 80:
            c.showPage()
            y = 750
        p_val = row.get('Punto', i)
        n_val = row.get('Norte', 0.0)
        e_val = row.get('Este', 0.0)
        c_val = row.get('Cota', 0.0)
        c.drawString(100, y, f"{p_val} | {n_val} | {e_val} | {c_val}")
        y -= 18
    c.drawString(100, 50, f"TOPOAUTO PRO v4.8.2 — {NOMBRE} - {CELULAR}")
    c.save()
    buffer.seek(0)
    return buffer

st.set_page_config(page_title=f"{MARCA}", layout="wide", page_icon="📍")

if 'logueado' not in st.session_state:
    st.session_state.logueado = False

if not st.session_state.logueado:
    st.title(f"🔑 {MARCA} - Activación")
    clave_input = st.text_input("Llave de Licencia:", type="password")
    nombre_input = st.text_input("Nombre de Empresa:")
    if st.button("ACTIVAR"):
        valido, mensaje = validar_licencia(clave_input)
        if valido:
            st.session_state.logueado = True
            st.session_state.clave = clave_input
            st.session_state.nombre = nombre_input
            enviar_telegram(f"🚀 INGRESO: {nombre_input}")
            st.rerun()
        else:
            st.error(mensaje)
    st.stop()

st.title(f"📍 {MARCA} v4.8.2 PRO")
st.write(f"Bienvenido: **{st.session_state.nombre}**")

archivo = st.file_uploader("Subir Excel: Punto, Norte, Este, Cota", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df = df.dropna(subset=['Punto', 'Este', 'Norte', 'Cota'])
    st.dataframe(df)
    st.success(f"Cargados {len(df)} puntos")

    if st.button("🚀 GENERAR DWG + PDF"):
        enviar_telegram(f"💰 USO: {st.session_state.nombre} | Puntos: {len(df)}")
        dwg = generar_dwg_texto(df)
        pdf = generar_pdf_igac(df, st.session_state.nombre, st.session_state.clave)
        st.download_button("⬇️ DESCARGAR DWG", dwg, "plano.dwg")
        st.download_button("⬇️ DESCARGAR PDF IGAC", pdf, "cuadro.pdf")
        st.balloons()