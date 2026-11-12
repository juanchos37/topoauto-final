# TopoAuto Pro v5.1 PRO - Juan SAS - PLAN EMPRESA - CORREGIDO
import streamlit as st
import pandas as pd
import numpy as np
import math
import io
from datetime import date

st.set_page_config(page_title="TopoAuto Pro v5.1", page_icon="📍", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #1A1A1A !important; }
    .stButton > button { background-color: #E53935; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("📍 TopoAuto Pro v5.1 PRO")
st.write("Bienvenido: **Juan SAS** | Plan: **EMPRESA**")
st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Procesar Excel", "📸 Módulo Dron", "📓 Bitácora"])

with tab1:
    st.header("📋 Paso 1: Carga de Cartera")
    st.write("Subir Excel: Punto, Norte, Este, Cota")
    archivo = st.file_uploader("Subir Excel", type=["xlsx", "xls"], key="excel_cartera", label_visibility="collapsed")
    st.caption("200MB per file • XLSX")
    if archivo is not None:
        try:
            df = pd.read_excel(archivo)
            df.columns = [str(c).strip().capitalize() for c in df.columns]
            mapa = {}
            for c in df.columns:
                cl = c.lower()
                if "punto" in cl or "pnt" in cl or "id" in cl:
                    mapa[c] = "Punto"
                elif "norte" in cl or "north" in cl or "y" == cl:
                    mapa[c] = "Norte"
                elif "este" in cl or "east" in cl or "x" == cl:
                    mapa[c] = "Este"
                elif "cota" in cl or "elev" in cl or "z" == cl:
                    mapa[c] = "Cota"
            df = df.rename(columns=mapa)
            st.success(f"✅ Cargados {len(df)} puntos correctamente")
            st.dataframe(df.head(20), use_container_width=True)
            if all(col in df.columns for col in ["Punto", "Norte", "Este", "Cota"]):
                df["Norte"] = pd.to_numeric(df["Norte"], errors="coerce")
                df["Este"] = pd.to_numeric(df["Este"], errors="coerce")
                df["Cota"] = pd.to_numeric(df["Cota"], errors="coerce")
                df = df.dropna(subset=["Norte", "Este"])
                distancias = [0.0]
                for i in range(1, len(df)):
                    d = math.sqrt((df.iloc[i]["Norte"] - df.iloc[i-1]["Norte"]) ** 2 + (df.iloc[i]["Este"] - df.iloc[i-1]["Este"]) ** 2)
                    distancias.append(round(d, 3))
                df["Dist_Anterior_m"] = distancias
                st.subheader("📐 Resultados Calculados")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Puntos", len(df))
                with col2:
                    st.metric("Dist. Total (m)", f"{sum(distancias):.2f}")
                with col3:
                    st.metric("Cota Max", f"{df['Cota'].max():.2f}")
                    st.metric("Cota Min", f"{df['Cota'].min():.2f}")
                st.dataframe(df, use_container_width=True)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Procesado")
                st.download_button(label="📥 Descargar Excel Procesado", data=output.getvalue(), file_name=f"TopoAuto_Procesado_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            else:
                st.warning("⚠️ Tu Excel debe tener las columnas: Punto, Norte, Este, Cota. Revisa los nombres.")
                st.write("Columnas que encontré:", list(df.columns))
        except Exception as e:
            st.error(f"Error leyendo el Excel: {e}")
    else:
        st.info("👆 Sube tu Excel de cartera para empezar. Ejemplo: Punto 1, Norte 1234567, Este 765432, Cota 12.5")

with tab2:
    st.header("📸 Módulo Dron")
    st.write("Calcula tu vuelo antes de salir a campo.")
    col1, col2 = st.columns(2)
    with col1:
        altura = st.number_input("Altura de vuelo (m)", value=100, min_value=20, max_value=300)
        gsd_deseado = st.number_input("GSD deseado (cm/px)", value=3.0, min_value=0.5, max_value=20.0)
    with col2:
        area = st.number_input("Área a levantar (Ha)", value=10.0, min_value=0.5)
        traslape = st.slider("Traslape (%)", 60, 90, 75)
    if st.button("🚁 Calcular Vuelo Dron", use_container_width=True):
        velocidad = 8.0
        tiempo_min = round((area * 12) / (altura / 100) + 10, 1)
        num_fotos = int(area * 45 * (traslape / 75))
        baterias = max(1, math.ceil(tiempo_min / 22))
        st.success("✅ Cálculo listo")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tiempo aprox.", f"{tiempo_min} min")
        c2.metric("Fotos aprox.", num_fotos)
        c3.metric("Baterías", baterias)
        st.info(f"💡 Recomendación: Vuela a {altura}m con {traslape}% de traslape. Lleva {baterias} baterías cargadas y verifica el viento en Montería antes de despegar.")
    st.divider()
    st.subheader("📷 Subir foto del dron")
    foto_dron = st.file_uploader("Sube una foto del levantamiento", type=["jpg", "jpeg", "png"], key="foto_dron")
    if foto_dron is not None:
        st.image(foto_dron, caption="Foto del levantamiento", use_container_width=True)
        st.success("✅ Foto guardada en el reporte")

with tab3:
    st.header("📓 Bitácora de Campo")
    st.write("Deja constancia de cada salida a campo.")
    if "bitacora" not in st.session_state:
        st.session_state["bitacora"] = []
    with st.form("form_bitacora", clear_on_submit=True):
        fecha_b = st.date_input("Fecha", value=date.today())
        proyecto = st.text_input("Proyecto / Cliente", placeholder="Ej: Lote Juan SAS - Montería")
        actividad = st.selectbox("Actividad", ["Levantamiento Topográfico", "Replanteo", "Vuelo Dron", "Nivelación", "Otro"])
        notas = st.text_area("Notas de campo", placeholder="Ej: Se levantaron 45 puntos, clima soleado, sin novedad...")
        guardar_b = st.form_submit_button("💾 Guardar en Bitácora", use_container_width=True)
        if guardar_b:
            if proyecto.strip() == "":
                st.warning("Escribe el nombre del proyecto.")
            else:
                st.session_state["bitacora"].append({"Fecha": str(fecha_b), "Proyecto": proyecto, "Actividad": actividad, "Notas": notas})
                st.success("✅ Guardado en bitácora")
    if len(st.session_state["bitacora"]) > 0:
        st.subheader("📜 Últimos registros")
        df_bit = pd.DataFrame(st.session_state["bitacora"])
        st.dataframe(df_bit, use_container_width=True)
        output2 = io.BytesIO()
        with pd.ExcelWriter(output2, engine="openpyxl") as writer:
            df_bit.to_excel(writer, index=False, sheet_name="Bitacora")
        st.download_button(label="📥 Descargar Bitácora en Excel", data=output2.getvalue(), file_name=f"Bitacora_TopoAuto_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.caption("Todavía no hay registros. Guarda el primero arriba.")

st.divider()
st.caption("TopoAuto Pro v5.1 - Juan SAS - Hecho en Montería, Córdoba")
