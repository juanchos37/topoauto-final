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

# =========================================================================
# 🛠️ CONFIGURACIÓN SEGURA 
# =========================================================================
TELEGRAM_TOKEN = "9115675773:AAHIeiGqf3tYG78HqvLn0iiZp_10kQtFJnk"
TELEGRAM_CHAT_ID = "8632454326"

LICENCIAS_VALIDAS = {
    "TOPO150-ABC123-2026-12-31": "2026-12-31", # BÁSICO $150.000
    "TOPO300-XYZ789-2027-06-30": "2027-06-30", # PRO $300.000
    "TOPO450-EMP001-2027-12-31": "2027-12-31", # EMPRESA $450.000 BITACORA
    "SENA2026": "2027-12-31", # Tu acceso
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
        return True, "Acceso de Desarrollador Autorizado sin límite", "EMPRESA"
    if clave in LICENCIAS_VALIDAS:
        fecha_vence = datetime.datetime.strptime(LICENCIAS_VALIDAS[clave], "%Y-%m-%d").date()
        if datetime.date.today() <= fecha_vence:
            tipo = "EMPRESA" if "450" in clave else "PRO" if "300" in clave else "BASICO"
            return True, f"Licencia {tipo} Válida hasta {fecha_vence}", tipo
    return False, "Licencia Inválida o Vencida", "NINGUNA"

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
    c.drawString(100, 50, f"TOPOAUTO PRO v4.9 — {NOMBRE} - {CELULAR}")
    c.save()
    buffer.seek(0)
    return buffer

def generar_pdf_bitacora(fecha, proyecto, ubicacion, personal, equipo, clima, actividades, observaciones, nombre):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "BITÁCORA DE ACTIVIDADES TOPOGRÁFICAS")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 720, f"PROYECTO: {proyecto}")
    c.setFont("Helvetica", 10)
    c.drawString(100, 700, f"Fecha: {fecha} | Ubicación: {ubicacion}")
    c.drawString(100, 680, f"Responsable: {nombre}")
    c.line(100, 670, 500, 670)
    
    y = 650
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, y, "1. PERSONAL Y EQUIPO:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(120, y, f"Personal: {personal}")
    y -= 15
    c.drawString(120, y, f"Equipo: {equipo}")
    y -= 15
    c.drawString(120, y, f"Clima: {clima}")
    
    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, y, "2. ACTIVIDADES REALIZADAS:")
    y -= 20
    c.setFont("Helvetica", 10)
    for linea in actividades.split('\n'):
        c.drawString(120, y, f"- {linea}")
        y -= 15
        
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, y, "3. OBSERVACIONES:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(120, y, observaciones)
    
    c.drawString(100, 50, f"Firma Responsable: ____________________   {MARCA} - {CELULAR}")
    c.save()
    buffer.seek(0)
    return buffer

# ========= INTERFAZ =========
st.set_page_config(page_title=f"{MARCA}", layout="wide", page_icon="📍")

if 'logueado' not in st.session_state:
    st.session_state.logueado = False

if not st.session_state.logueado:
    st.title(f"🔑 {MARCA} - Activación")
    clave_input = st.text_input("Llave de Licencia:", type="password")
    nombre_input = st.text_input("Nombre de Empresa:")
    if st.button("ACTIVAR"):
        valido, mensaje, tipo = validar_licencia(clave_input)
        if valido:
            st.session_state.logueado = True
            st.session_state.clave = clave_input
            st.session_state.nombre = nombre_input
            st.session_state.tipo = tipo
            enviar_telegram(f"🚀 INGRESO: {nombre_input} | Plan: {tipo}")
            st.rerun()
        else:
            st.error(mensaje)
    st.stop()

st.title(f"📍 {MARCA} v4.9 PRO")
st.write(f"Bienvenido: **{st.session_state.nombre}** | Plan: **{st.session_state.tipo}**")

tab_excel_modo, tab_dron_modo, tab_bitacora = st.tabs(["📊 Procesar Excel", "📸 Módulo Dron", "📒 Bitácora"])

# --- MODULO 1: EXCEL ---
with tab_excel_modo:
    st.subheader("📋 Paso 1: Carga de Cartera")
    archivo = st.file_uploader("Subir Excel: Punto, Norte, Este, Cota", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
        df = df.dropna(subset=['Punto', 'Este', 'Norte', 'Cota'])
        st.dataframe(df)
        st.success(f"Cargados {len(df)} puntos")
        
        df['Distancia_m'] = np.sqrt((df['Este'] - df['Este'].shift(1))**2 + (df['Norte'] - df['Norte'].shift(1))**2).fillna(0).round(3)
        area_total = 0
        if len(df) > 2:
            try:
                gdf_temp = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Este, df.Norte))
                area_total = gdf_temp.unary_union.convex_hull.area
            except: 
                area_total = 0
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Puntos", len(df))
        col_b.metric("Distancia", f"{df['Distancia_m'].sum():.2f} m")
        col_c.metric("Área", f"{area_total:.2f} m²")

        if st.button("🚀 GENERAR DWG + PDF"):
            enviar_telegram(f"💰 USO: {st.session_state.nombre} | Puntos: {len(df)}")
            dwg = generar_dwg_texto(df)
            pdf = generar_pdf_igac(df, st.session_state.nombre, st.session_state.clave)
            st.download_button("⬇️ DESCARGAR DWG", dwg, "plano.dwg")
            st.download_button("⬇️ DESCARGAR PDF IGAC", pdf, "cuadro.pdf")
            st.balloons()

# --- MODULO 2: DRON ---
with tab_dron_modo:
    st.subheader("📸 Extraer Coordenadas de Fotos")
    fotos = st.file_uploader("Sube fotos .JPG con GPS", type=["jpg", "jpeg"], accept_multiple_files=True)
    if fotos:
        datos = []
        for foto in fotos:
            res = extraer_datos_foto(foto)
            if res:
                datos.append({"Punto": foto.name, "Norte": res[0], "Este": res[1], "Cota": res[2]})
        if datos:
            df_foto = pd.DataFrame(datos)
            st.dataframe(df_foto)

# --- MODULO 3: BITACORA SOLO EMPRESA ---
with tab_bitacora:
    if st.session_state.tipo != "EMPRESA" and st.session_state.clave != "SENA2026":
        st.warning("🔒 Este módulo solo está disponible en Plan EMPRESA $450.000")
        st.stop()
        
    st.subheader("📒 Generar Bitácora de Actividades")
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.date.today())
        proyecto = st.text_input("Nombre del Proyecto")
        ubicacion = st.text_input("Ubicación/Municipio")
    with col2:
        personal = st.text_input("Personal", "Ing. Juan David + 1 Cadenero")
        equipo = st.text_input("Equipo", "Estación Total")
        clima = st.selectbox("Clima", ["Soleado", "Nublado", "Lluvia"])
    
    actividades = st.text_area("Actividades", "1. Reconocimiento\n2. Levantamiento de puntos")
    observaciones = st.text_area("Observaciones", "Sin novedad")
    
    if st.button("GENERAR BITÁCORA PDF"):
        pdf_bita = generar_pdf_bitacora(fecha, proyecto, ubicacion, personal, equipo, clima, actividades, observaciones, st.session_state.nombre)
        st.download_button("⬇️ DESCARGAR BITÁCORA PDF", pdf_bita, f"Bitacora_{fecha}.pdf")
        enviar_telegram(f"📒 BITACORA: {st.session_state.nombre} | {proyecto}")
        st.success("Bitácora generada")