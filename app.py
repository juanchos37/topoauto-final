
import streamlit as st
import pandas as pd
import numpy as np
import gpd as gpd # Nota: Si en tu requirements pusiste geopandas, se importa como geopandas
import geopandas as gpd
import io
import datetime
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# 1. TUS DATOS PROFESIONALES
MARCA = "TopoAuto"
NOMBRE = "Juan David Ospino M."
CARGO = "Cadenero Topográfico SENA | Desarrollador"
CELULAR = "300 239 0779"
EMAIL = "juanospimoscote33@gmail.com"
PRECIO_LICENCIA = 50000
DIAS_PRUEBA = 1

st.set_page_config(page_title=f"{MARCA} - {NOMBRE}", layout="wide")
st.title(f"🗺️ {MARCA}")
st.caption("Procesamiento automático de carteras topográficas - Desarrollado por un Cadenero para Cadeneros")

# 2. CONTROL DE PRUEBA Y ACTIVACIÓN
if 'primer_ingreso' not in st.session_state:
    st.session_state.primer_ingreso = datetime.date.today()
    st.session_state.licencia_activa = False

dias_transcurridos = (datetime.date.today() - st.session_state.primer_ingreso).days
dias_restantes = DIAS_PRUEBA - dias_transcurridos

# Barra lateral discreta para tu acceso gratis
with st.sidebar:
    st.markdown("### 🔐 Activación")
    codigo_admin = st.text_input("Código de activación:", type="password")
    if codigo_admin == "SENA2026":
        st.session_state.licencia_activa = True
        st.success("¡Licencia Activada!")

# 3. BLOQUEO SI SE ACABÓ LA PRUEBA
if dias_restantes < 0 and not st.session_state.licencia_activa:
    st.error(f"SU PERIODO DE PRUEBA DE {DIAS_PRUEBA} DÍA HA FINALIZADO")
    st.header(f"Adquiera su Licencia: ${PRECIO_LICENCIA:,} COP")
    
    st.write("Gracias por probar TopoAuto. Para continuar procesando sin límites:")
    
    st.subheader("Formas de Pago Seguras")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"*1. Nequi / Daviplata*\n {CELULAR}")
    with col2:
        st.markdown(f"*2. Transferencia*\n *Solicitar datos bancarios")
    
    st.info(f"📞 *Contacto Directo*: {NOMBRE} | {CELULAR}")
    st.info(f"📧 *Correo*: {EMAIL}")
    st.warning("Envíe su comprobante y activo su licencia en máximo 30 minutos")
    
    if st.button("SOLICITAR ACTIVACIÓN AHORA"):
        st.success(f"Perfecto. Escríbame al WhatsApp {CELULAR} con su comprobante.")
    
    st.stop()

# 4. BANNER DE PRUEBA
if dias_restantes >= 0 and not st.session_state.licencia_activa:
    st.success(f"🎁 ACCESO DE PRUEBA: Le queda {dias_restantes} día(s) para evaluar TopoAuto sin costo. Al finalizar: ${PRECIO_LICENCIA:,}")
elif st.session_state.licencia_activa:
    st.success("✅ LICENCIA ACTIVA - Gracias por confiar en TopoAuto")

# 5. APP PRINCIPAL
st.markdown("---")
st.write("*Instrucciones*: Cargue su archivo Excel con columnas: Punto, Este, Norte, Cota, Descripcion")

archivo = st.file_uploader("Cargar Cartera .xlsx", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df = df.dropna(subset=['Punto', 'Este', 'Norte', 'Cota', 'Descripcion'])
    st.success(f"Archivo cargado correctamente. {len(df)} puntos detectados")
    
    st.subheader("1. Filtro por Descripción")
    opciones = ['TODOS'] + sorted(list(df['Descripcion'].unique().astype(str)))
    filtro = st.selectbox("Seleccione tipo de punto:", opciones)
    df_filtrado = df[df['Descripcion'] == filtro].copy() if filtro != 'TODOS' else df.copy()
    
    # CÁLCULOS
    df_filtrado['Distancia_m'] = np.sqrt(
        (df_filtrado['Este'] - df_filtrado['Este'].shift(1))**2 + 
        (df_filtrado['Norte'] - df_filtrado['Norte'].shift(1))**2
    )
    df_filtrado['Distancia_m'] = df_filtrado['Distancia_m'].fillna(0).round(3)
    
    st.dataframe(df_filtrado, use_container_width=True)

    area_total = 0
    poligono_geom = None
    if len(df_filtrado) > 2:
        try:
            gdf_temp = gpd.GeoDataFrame(df_filtrado, geometry=gpd.points_from_xy(df_filtrado.Este, df_filtrado.Norte), crs="EPSG:9377")
            poligono_geom = gdf_temp.unary_union.convex_hull
            area_total = poligono_geom.area
        except:
            area_total = 0
    
    st.subheader("2. Resumen del Levantamiento")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Puntos", len(df_filtrado))
    col2.metric("Cota Promedio", f"{round(df_filtrado['Cota'].mean(), 2)} m")
    col3.metric("Área Polígono (Aprox)", f"{round(area_total, 2)} m²")
    
    st.subheader("3. Visualización Gráfica Planimétrica")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if poligono_geom and not poligono_geom.is_empty and isinstance(poligono_geom, Polygon):
        x_pol, y_pol = poligono_geom.exterior.xy
        ax.fill(x_pol, y_pol, alpha=0.2, fc='green', ec='darkgreen', label='Área Levantada')
    
    ax.scatter(df_filtrado['Este'], df_filtrado['Norte'], color='blue', zorder=5, label='Puntos')
    for idx, row in df_filtrado.iterrows():
        ax.text(row['Este'], row['Norte'], str(row['Punto']), fontsize=8, ha='right', va='bottom')
        
    ax.set_xlabel("Este (X)")
    ax.set_ylabel("Norte (Y)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axis('equal')
    ax.legend()
    st.pyplot(fig)
    
    st.subheader("4. Exportar Resultados")
    col_dl1, col_dl2 = st.columns(2)
    
    output_excel = io.BytesIO()
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Cartera_Procesada')
    processed_data_excel = output_excel.getvalue()
    
    col_dl1.download_button(
        label="📥 Descargar Cartera en Excel (.xlsx)",
        data=processed_data_excel,
        file_name=f"Cartera_{filtro}_{datetime.date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    output_pdf = io.BytesIO()
    fig_pdf, ax_pdf = plt.subplots(figsize=(6, 4))
    if poligono_geom and not poligono_geom.is_empty and isinstance(poligono_geom, Polygon):
        x_p, y_p = poligono_geom.exterior.xy
        ax_pdf.fill(x_p, y_p, alpha=0.2, fc='green', ec='darkgreen')
    ax_pdf.scatter(df_filtrado['Este'], df_filtrado['Norte'], color='blue')
    ax_pdf.set_title(f"Levantamiento Planimétrico - Filtro: {filtro}")
    ax_pdf.grid(True, linestyle='--')
    ax_pdf.axis('equal')
    
    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig_pdf)
        plt.close(fig_pdf)
    processed_data_pdf = output_pdf.getvalue()
    
    col_dl2.download_button(
        label="📄 Descargar Plano Base en PDF",
        data=processed_data_pdf,
        file_name=f"Plano_{filtro}_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )
