# GeoLegal Pro - Juan SAS - v12.5 FINAL
import streamlit as st
import pandas as pd
import math
import io
from datetime import date

st.set_page_config(page_title="GeoLegal Pro", page_icon="⚖️", layout="centered")
st.title("GeoLegal Pro - Juan SAS")
st.write("Bienvenido: Juan SAS | Monteria, Cordoba")
st.divider()
modo = st.radio("Modo de trabajo", ["MODO TOPOGRAFO - Juan SAS", "MODO DESPACHO - Dra. Norma"], horizontal=True, key="modo_final")
st.divider()

def predecir_caso(tipo, demandado, valor):
    base = 50.0
    if tipo == "Nulidad":
        base = base + 18
    if tipo == "Tutela":
        base = base + 22
    if tipo == "Demanda Laboral":
        base = base + 12
    if tipo == "Divorcio":
        base = base + 8
    if tipo == "Otro":
        base = base + 5
    if demandado == "Colpensiones":
        base = base + 10
    if demandado == "EPS":
        base = base + 8
    if demandado == "Empresa Privada":
        base = base + 2
    if demandado == "Estado / Alcaldia":
        base = base - 5
    if valor > 15000000:
        base = base + 5
    if valor < 2000000:
        base = base - 5
    prob = max(12, min(92, int(base)))
    if prob >= 70:
        consejo = "Caso FUERTE, Prioridad ALTA"
    elif prob >= 50:
        consejo = "Caso MEDIO, revisa pruebas"
    else:
        consejo = "Caso DEBIL, cobra por adelantado"
    return prob, consejo

def hacer_documento(tipo, cliente, hechos):
    t = "DOCUMENTO: " + tipo + "\n"
    t = t + "CLIENTE: " + cliente + "\n\n"
    t = t + "Senor Juez, presento " + tipo + "\n\n"
    t = t + "HECHOS:\n" + hechos + "\n\n"
    t = t + "PRETENSIONES:\n"
    t = t + "1. Se declare lo solicitado.\n"
    t = t + "2. Se ordene cumplir obligaciones.\n\n"
    t = t + "FUNDAMENTOS: Constitucion y CGP.\n\n"
    t = t + "Atentamente, Dra. Norma\n"
    t = t + "Monteria, " + str(date.today())
    return t

if modo == "MODO TOPOGRAFO - Juan SAS":
    st.header("Modo Topografo - Juan SAS")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Procesar Excel", "Dron", "Replanteo", "Nivelacion", "Presupuesto", "Bitacora", "Conversor"])
    with tab1:
        st.subheader("Carga de Cartera")
        archivo = st.file_uploader("Subir Excel", type=["xlsx", "xls"], key="f_excel")
        if archivo is None:
            st.info("Sube tu Excel de cartera para empezar.")
        if archivo is not None:
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
            st.success("Cargados puntos")
            st.dataframe(df.head(20), use_container_width=True)
            if "Punto" in df.columns and "Norte" in df.columns and "Este" in df.columns and "Cota" in df.columns:
                df["Norte"] = pd.to_numeric(df["Norte"], errors="coerce")
                df["Este"] = pd.to_numeric(df["Este"], errors="coerce")
                df["Cota"] = pd.to_numeric(df["Cota"], errors="coerce")
                df = df.dropna(subset=["Norte", "Este"])
                distancias = [0.0]
                for i in range(1, len(df)):
                    dn = df.iloc[i]["Norte"] - df.iloc[i-1]["Norte"]
                    de = df.iloc[i]["Este"] - df.iloc[i-1]["Este"]
                    d = math.sqrt(dn * dn + de * de)
                    distancias.append(round(d, 3))
                df["Dist_Anterior_m"] = distancias
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Puntos", len(df))
                c2.metric("Dist Total", round(sum(distancias), 2))
                c3.metric("Cota Max", round(float(df["Cota"].max()), 2))
                st.dataframe(df, use_container_width=True)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Procesado")
                st.download_button("Descargar Excel Procesado", data=output.getvalue(), file_name="Procesado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="f_dl1")
            else:
                st.warning("Tu Excel debe tener: Punto, Norte, Este, Cota")
    with tab2:
        st.subheader("Modulo Dron")
        altura = st.number_input("Altura de vuelo (m)", value=100, min_value=20, max_value=300, key="f_alt")
        area = st.number_input("Area (Ha)", value=10.0, min_value=0.5, key="f_area")
        traslape = st.slider("Traslape (%)", 60, 90, 75, key="f_tras")
        if st.button("Calcular Vuelo Dron", key="f_d
