import streamlit as st
import pandas as pd
import datetime
import requests
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ========= CONFIGURACIÓN SEGURA =========
# CAMBIA ESTOS 3 DATOS
TELEGRAM_TOKEN = "PON_AQUI_TU_TOKEN"
TELEGRAM_CHAT_ID = "PON_AQUI_TU_CHAT_ID"
CLAVE_SECRETA = "TOPOAUTO2026" # Clave para generar licencias

# Base de datos de licencias. Formato: "CLAVE": "FECHA_VENCIMIENTO"
LICENCIAS_VALIDAS = {
    "TOPO150-ABC123-2026-12-31": "2026-12-31", # Plan BÁSICO $150.000
    "TOPO300-XYZ789-2027-06-30": "2027-06-30", # Plan PRO $300.000
    "TOPO450-EMP001-2027-12-31": "2027-12-31", # Plan EMPRESA $450.000
}

# ========= FUNCIONES =========
def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, data=data, timeout=5)
    except:
        pass # Si falla la red no daña el flujo de la aplicación

def validar_licencia(clave):
    if clave in LICENCIAS_VALIDAS:
        fecha_vence = datetime.datetime.strptime(LICENCIAS_VALIDAS[clave], "%Y-%m-%d").date()
        if datetime.date.today() <= fecha_vence:
            return True, f"Licencia Válida hasta {fecha_vence}"
    return False, "Licencia Inválida o Vencida"

def generar_dwg(df):
    # Base de estructura de texto simulando entidades de intercambio
    contenido = "HEADER\nVERSION TOPOAUTO\nENTITIES\n"
    for i, row in df.iterrows():
        # CORREGIDO: Mapeo correcto de variables desde las columnas del DataFrame
        contenido += f"POINT\nE:{row['Este']}\nN:{row['Norte']}\nC:{row['Cota']}\n"
    return BytesIO(contenido.encode())

def generar_pdf(df, nombre_cliente):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "CUADRO DE COORDENADAS - FORMATO IGAC")
    c.setFont("Helvetica", 10)
    c.drawString(100, 730, f"Cliente: {nombre_cliente} | Licencia: {st.session_state.clave}")
    c.drawString(100, 710, f"Fecha: {datetime.date.today()}")
    
    y = 670
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y, "PUNTO  |  NORTE (Y)  |  ESTE (X)  |  COTA (Z)")
    c.line(100, y-5, 500, y-5)
    
    y -= 20
    c.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        if y < 80: # Control básico para no salirse de la página
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750
        c.drawString(100, y, f"{row['Punto']}  |  {row['Norte']}  |  {row['Este']}  |  {row['Cota']}")
        y -= 18
        
    c.drawString(100, 50, f"MARCA DE AGUA: TOPOAUTO PRO - LICENCIA ACTIVA: {nombre_cliente}")
    c.save()
    buffer.seek(0)
    return buffer

# ========= PÁGINA WEB =========
st.set_page_config(page_title="TopoAuto v4.8 PRO", layout="wide", page_icon="📍")
st.title("📍 TopoAuto v4.8 PRO")
st.caption("De Excel a DWG + PDF IGAC en 10 segundos")
st.markdown("---")

# 1. PANTALLA DE LOGIN
if 'logueado' not in st.session_state:
    st.session_state.logueado = False

if not st.session_state.logueado:
    st.header("1. INGRESAR LICENCIA")
    clave = st.text_input("Pega tu clave de licencia aquí:", type="password")
    nombre = st.text_input("Nombre del Cliente/Empresa:")
    
    if st.button("ACTIVAR SOFTWARE"):
        if not clave or not nombre:
            st.warning("⚠️ Por favor rellena ambos campos para continuar.")
        else:
            valido, mensaje = validar_licencia(clave)
            if valido:
                st.session_state.logueado = True
                st.session_state.clave = clave
                st.session_state.nombre = nombre
                st.success(mensaje)
                enviar_telegram(f"✅ ACCESO AUTORIZADO: {nombre} | Clave: {clave}")
                st.rerun()
            else:
                st.error(mensaje)
                enviar_telegram(f"⚠️ INTENTO DE ACCESO RECHAZADO: {clave} por {nombre}")
    st.stop()

# 2. SI YA ESTÁ LOGUEADO
st.success(f"🔓 Licencia autorizada para: {st.session_state.nombre}")

st.header("2. SUBIR CARTERA DE CAMPO .XLSX")
st.write("Asegúrate de que las columnas se llamen exactamente: **Punto, Norte, Este, Cota**")
archivo = st.file_uploader("Cargar archivo de Excel", type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    # Limpieza básica para evitar procesar filas completamente vacías
    df = df.dropna(subset=['Punto', 'Norte', 'Este', 'Cota'])
    
    st.subheader("Datos de terreno detectados")
    st.dataframe(df, use_container_width=True)

    st.subheader("3. Procesamiento y Descarga")
    
    # CORREGIDO: Los botones de descarga se autogeneran de forma estable al cargar el archivo
    dwg = generar_dwg(df)
    pdf = generar_pdf(df, st.session_state.nombre)
    
    col_dwg, col_pdf = st.columns(2)
    
    with col_dwg:
        st.download_button(
            label="📐 DESCARGAR ARCHIVO DWG", 
            data=dwg, 
            file_name=f"Plano_{st.session_state.nombre}.dwg",
            mime="application/octet-stream",
            use_container_width=True
        )
        
    with col_pdf:
        st.download_button(
            label="📄 DESCARGAR CUADRO PDF IGAC", 
            data=pdf, 
            file_name=f"Cuadro_IGAC_{st.session_state.nombre}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    # Mensaje de éxito al cargar
    st.toast("¡Plano y cuadro IGAC procesados con éxito!", icon="🚀")
