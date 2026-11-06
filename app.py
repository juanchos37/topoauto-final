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
# 🛠️ ZONA DE CONFIGURACIÓN SEGURA 
# =========================================================================
TELEGRAM_TOKEN = "9115675773:AAHIeiGqf3tYG78HqvLn0iiZp_10kQtFJnk"
TELEGRAM_CHAT_ID = "8632454326"

# Base de datos local de licencias comerciales
LICENCIAS_VALIDAS = {
    "TOPO150-ABC123-2026-12-31": "2026-12-31", # Plan BÁSICO $150.000
    "TOPO300-XYZ789-2027-06-30": "2027-06-30", # Plan PRO $300.000
    "TOPO450-EMP001-2027-12-31": "2027-12-31", # Plan EMPRESA $450.000
    "SENA2026": "2027-12-31", # Tu acceso maestro
}

# ========= TUS DATOS PROFESIONALES =========
MARCA = "TopoAuto Pro"
NOMBRE = "Ing. Juan David Ospino M."
CARGO = "Cadenero Topográfico SENA | Desarrollador"
CELULAR = "300 239 0779"
EMAIL = "juanospimoscote33@gmail.com"

# ========= FUNCIONES CORE =========
def enviar_telegram(mensaje):
    """Envía alertas a tu Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" # ARREGLADO
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
    grados = coordenadas[0] # ARREGLADO
    minutos = coordenadas[1] # ARREGLADO
    segundos = coordenadas[2] # ARREGLADO
    decimal = grados + (minutos / 60.0) + (segundos / 3600.0) # ARREGLADO 3600
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
        este_val = row.get('Este', 0.0)
        norte_val = row.get('Norte', 0.0)
        cota_val = row.get('Cota', 0.0)
        punto_val = row.get('Punto', i)
        contenido += f"POINT\nP:{punto_val}\nE:{este_val}\nN:{norte_val}\nC:{cota_val}\n"
    return io.BytesIO(contenido