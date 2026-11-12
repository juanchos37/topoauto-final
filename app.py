# TopoAuto Pro v5.0 PRO - Juan SAS - PLAN EMPRESA
import streamlit as st
import pandas as pd
import numpy as np
import math
import io
from datetime import date

st.set_page_config(page_title="TopoAuto Pro v5.0", page_icon="📍", layout="centered")

# ESTILO
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #1A1A1A !important; }
    .stButton > button { background-color: #E53935; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("📍 TopoAuto Pro v5.0 PRO")
st.write("Bienvenido: **Juan SAS** | Plan: **EMPRESA**")
st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Procesar Excel", "📸 Módulo Dron", "📓 Bitácora"])

# ============================================================
# TAB 1 - PROCESAR EXCEL
# ============================================================
with tab1:
    st.header("📋 Paso 1: Carga de Cartera")
    st.write("Subir Excel: Punto, Norte, Este, Cota")

    archivo = st.file_uploader("Subir Excel", type=["xlsx", "xls"], key="excel_cartera", label_visibility="collapsed")
    st.caption("200MB per file • XLSX")

    if archivo is not None:
        try:
            df = pd.read_excel(archivo)
            # Normalizar nombres de columnas
            df.columns = [str(c).strip().capitalize() for c in df.columns]
            # Buscar columnas parecidas
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

            # Validar que tenga las columnas
            if all(col in df.columns for col in ["Punto", "Norte", "Este", "Cota"]):
                # Calcular distancias entre puntos consecutivos
                df["Norte"] = pd.to_numeric(df["Norte"], errors="coerce")
                df["Este"] = pd.to_numeric(df["Este"], errors="coerce")
                df["Cota"] = pd.to_numeric(df["Cota"], errors="coerce")
                df = df.dropna(subset=["Norte", "Este"])

                distancias = [0.0]
                for i in range(1, len(df)):
                    d = math.sqrt((df.iloc[i]["Norte"]-df.iloc[i-1]["Norte"])**2 + (df.iloc[i]["Este"]-df.iloc[i-1]["Este"])**2)
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

                # Descargar resultado
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Procesado")
                st.download_button(
                    label="📥 Descargar Excel Procesado",
                    data=output.getvalue(),
                    file_name=f"TopoAuto_Procesado_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ Tu Excel debe tener las columnas: Punto, Norte, Este, Cota. Revisa los nombres.")
                st.write("Columnas que encontré:", list(df.columns))

        except Exception as e:
            st.error(f"Error leyendo el Excel: {e}")
    else:
        st.info("👆 Sube tu Excel de cartera para empezar. Ejemplo: Punto 1, Norte 1234567, Este 765432, Cota 12.5")

# ============================================================
# TAB 2 - MODULO DRON
# ============================================================
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
        # Estimación
