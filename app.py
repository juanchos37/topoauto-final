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

LICENCIAS_VALIDAS = {
    "TOPO150-ABC123-2026-12-31": "2026-12-31",
    "TOPO300-XYZ789-2027-06-30": "2027-06-30",
    "TOPO450-EMP001-2027-12-31": "2027-12-31",
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

def extraer_datos_foto(archivo_foto):
    try:
        bytes_foto = archivo_foto
            