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
PRECIO_LICENCIA = 50000
DIAS_PRUEBA = 1

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title=f"{MARCA} - {NOMBRE}", layout="wide", page_icon="🗺️")

# INYECCIÓN DE CSS AVANZADO PARA EMBELLECER LA INTERFAZ
st.markdown("""
    <style>
    /* Estilo general del contenedor principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Personalización de la barra lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important; /* Gris oscuro elegante */
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #f8fafc !important;
    }
    
    /* Tarjetas de Métricas Estilizadas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2563eb; /* Línea azul de software de ingeniería */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px); /* Efecto visual flotante */
    }
    
    /* Estilo de las Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
        color: #475569 !important;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important; /* Fondo azul para la pestaña activa */
        color: #ffffff !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Caja de carga de archivos (File Uploader) */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 10px;
        background-color: #f8fafc;
    }
    
    /* Inputs de texto limpios */
    div[data-testid="stTextInput"] input {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.image("https://flaticon.com", width=70)
    st.markdown(f"## **{MARCA} Pro**")
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
    st.header("Adquiera su Licencia Comercial")
    st.subheader(f"Valor: ${PRECIO_LICENCIA:,} COP (Pago Único)")
    
    st.write("Para continuar procesando carteras topográficas sin límites, realice el pago mediante:")
    
    col_pago1, col_pago2 = st.columns(2)
    with col_pago1:
        st.info(f"📱 **Nequi / Daviplata**\n\n{CELULAR}")
    with col_pago2:
        st.info(f"🏦 **Transferencia Bancaria**\n\nSolicitar datos al contacto")
    
    st.markdown("---")
    st.markdown(f"📞 **Soporte Directo:** {NOMBRE} | {CELULAR}")
    st.markdown(f"📧 **Correo:** {EMAIL}")
    st.warning("Envíe su comprobante vía WhatsApp y activaremos su licencia en menos de 30 minutos.")
    
    if st.button("💬 NOTIFICAR PAGO POR WHATSAPP"):
        st.success(f"Perfecto. Comunícate al número {CELULAR} para la activación inmediata.")
    st.stop()

# 4. BANNERS DE EVALUACIÓN
if dias_restantes >= 0 and not st.session_state.licencia_activa:
    st.info(f"🎁 **Versión de Evaluación:** Te queda {dias_restantes} día de uso gratuito. Licencia comercial: ${PRECIO_LICENCIA:,} COP")
elif st.session_state.licencia_activa:
    st.success("⚡ **Modo Corporativo Activo** | Soporte premium habilitado.")

# ENCABEZADO
st.title("🗺️ Procesador de Carteras Topográficas")
st.markdown("Convierte tus datos de campo en informes ejecutivos y planos base de ingeniería de forma instantánea.")
st.markdown("---")

# PASO 1: CARGA DE ARCHIVO
st.subheader("📋 Paso 1: Carga de Datos de Campo")
archivo = st.file_uploader("Arrastra aquí tu archivo de cartera en formato Excel (.xlsx)", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df = df.dropna(subset=['Punto', 'Este', 'Norte', 'Cota', 'Descripcion'])
    
    st.success(f"✔️ ¡Excelente! Se han cargado con éxito {len(df)} puntos topográficos.")
    
    # FILTRO AVANZADO
    st.markdown("### 🔍 Configuración del Filtro")
    opciones = ['TODOS LOS PUNTOS'] + sorted(list(df['Descripcion'].unique().astype(str)))
    filtro = st.selectbox("Seleccionar grupo o descripción de puntos a procesar:", opciones)
    
    df_filtrado = df[df['Descripcion'] == filtro].copy() if filtro != 'TODOS LOS PUNTOS' else df.copy()
    
    # CÁLCULOS
    df_filtrado['Distancia_m'] = np.sqrt(
        (df_filtrado['Este'] - df_filtrado['Este'].shift(1))**2 + 
        (df_filtrado['Norte'] - df_filtrado['Norte'].shift(1))**2
    )
    df_filtrado['Distancia_m'] = df_filtrado['Distancia_m'].fillna(0).round(3)
    
    area_total = 0
    poligono_geom = None
    if len(df_filtrado) > 2:
        try:
            gdf_temp = gpd.GeoDataFrame(df_filtrado, geometry=gpd.points_from_xy(df_filtrado.Este, df_filtrado.Norte), crs="EPSG:9377")
            poligono_geom = gdf_temp.unary_union.convex_hull
            area_total = poligono_geom.area
        except:
            area_total = 0

    st.markdown("---")
    st.subheader("📊 Paso 2: Análisis e Información del Levantamiento")

    # ESTRUCTURA DE PESTAÑAS (TABS ENBELLECIDAS POR CSS)
    tab_resumen, tab_tabla, tab_plano, tab_exportar = st.tabs([
        "📈 Resumen y Métricas", 
        "📄 Tabla de Coordenadas", 
        "📐 Plano Planimétrico", 
        "📥 Módulo de Descargas"
    ])
    
    with tab_resumen:
        st.markdown("#### Indicadores Clave")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="🔢 Densidad de Puntos", value=f"{len(df_filtrado)} pts")
        with c2:
            st.metric(label="⛰️ Altura / Cota Promedio", value=f"{round(df_filtrado['Cota'].mean(), 2)} m")
        with c3:
            st.metric(label="📐 Superficie de Polígono", value=f"{round(area_total, 2)} m²")
            
    with tab_tabla:
        st.markdown("#### Registros Filtrados con Distancias entre Vértices")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
    with tab_plano:
        st.markdown("#### Vista de Planta del Levantamiento (Esquema de Ingeniería)")
        fig, ax = plt.subplots(figsize=(9, 6), facecolor='#f8fafc')
        ax.set_facecolor('#ffffff')
        
        if poligono_geom and not poligono_geom.is_empty and isinstance(poligono_geom, Polygon):
            x_pol, y_pol = poligono_geom.exterior.xy
            ax.fill(x_pol, y_pol, alpha=0.12, fc='#10b981', ec='#047857', linewidth=2, label='Polígono de Terreno')
        
        ax.scatter(df_filtrado['Este'], df_filtrado['Norte'], color='#2563eb', s=45, zorder=5, label='Vértices/Detalles')
        
        for idx, row in df_filtrado.iterrows():
            ax.text(row['Este'], row['Norte'], f" {int(row['Punto'])}", fontsize=9, fontweight='bold', ha='left', va='center', color='#1e293b')
            
        ax.set_xlabel("Coordenada ESTE (X)", fontsize=10, fontweight='bold', color='#475569')
        ax.set_ylabel("Coordenada NORTE (Y)", fontsize=10, fontweight='bold', color='#475569')
        ax.grid(True, linestyle=':', alpha=0.5, color='#cbd5e1')
        ax.axis('equal')
        ax.legend(loc='upper right')
        st.pyplot(fig)
        
    with tab_exportar:
        st.markdown("#### Generación Automática de Entregables")
        st.write("Genera memorias de cálculo listas para adjuntar al informe final de oficina.")
        
        col_dl1, col_dl2 = st.columns(2)
        
        # Generar Excel
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Cartera_Procesada')
        processed_data_excel = output_excel.getvalue()
        
        with col_dl1:
            st.download_button(
                label="🟢 DESCARGAR CARTERA EN EXCEL (.xlsx)",
                data=processed_data_excel,
                file_name=f"Cartera_{filtro}_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        # Generar PDF
        output_pdf = io.BytesIO()
        fig_pdf, ax_pdf = plt.subplots(figsize=(6, 4))
        if poligono_geom and not poligono_geom.is_empty and isinstance(poligono_geom, Polygon):
