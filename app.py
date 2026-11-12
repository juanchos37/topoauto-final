# GeoLegal Pro - Juan SAS - v12.3 - Topografía + Despacho - TODO
import streamlit as st
import pandas as pd
import numpy as np
import math
import io
from datetime import date, timedelta

st.set_page_config(page_title="GeoLegal Pro - Juan SAS", page_icon="⚖️", layout="centered")
st.title("⚖️ GeoLegal Pro - Juan SAS")
st.write("Bienvenido: **Juan SAS** | Montería, Córdoba")
st.divider()
modo = st.radio("¿En qué modo quieres trabajar hoy?", ["👷 MODO TOPÓGRAFO - Juan SAS", "⚖️ MODO DESPACHO - Dra. Norma"], horizontal=True, key="modo_v122")
st.divider()

# ---------- FUNCION RED NEURONAL SIMPLIFICADA - NO NECESITA SKLEARN ----------
def predecir_caso_v122(tipo, demandado, valor):
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
    if demandado == "Estado / Alcaldía":
        base = base - 5
    if valor > 15000000:
        base = base + 5
    if valor < 2000000:
        base = base - 5
    prob = max(12, min(92, int(base)))
    if prob >= 70:
        consejo = "Caso FUERTE, Prioridad ALTA, haz este primero"
    elif prob >= 50:
        consejo = "Caso MEDIO, revisa pruebas antes de radicar"
    else:
        consejo = "Caso DÉBIL, habla con el cliente, riesgo alto, cobra por adelantado"
    return prob, consejo

# ---------- FUNCION DOCUMENTO IA ----------
def generar_doc_ia_v122(tipo, cliente, hechos):
    texto = "DOCUMENTO: " + tipo + "\nCLIENTE: " + cliente + "\n\n"
    texto = texto + "Señor Juez, por medio del presente escrito, yo, " + cliente + ", actuando en nombre propio, me permito presentar " + tipo + " con base en los siguientes hechos:\n\n"
    texto = texto + "HECHOS:\n" + hechos + "\n\n"
    texto = texto + "PRETENSIONES:\n1. Se declare lo solicitado en favor de mi representado.\n2. Se ordene al demandado cumplir con sus obligaciones legales.\n\n"
    texto = texto + "FUNDAMENTOS DE DERECHO:\nConstitución Política de Colombia, Código General del Proceso, y normas concordantes.\n\n"
    texto = texto + "PRUEBAS:\nSe aportan las pruebas documentales que se encuentran en el expediente.\n\n"
    texto = texto + "Atentamente,\nDra. Norma - Apoderada\nMontería, Córdoba - " + str(date.today())
    return texto

# ============================================================
# MODO 1 - TOPOGRAFO
# ============================================================
if modo == "👷 MODO TOPÓGRAFO - Juan SAS":
    st.header("👷 Modo Topógrafo - Juan SAS")
    st.caption("Solo topografía. No toca nada del despacho.")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Procesar Excel", "📸 Dron", "📍 Replanteo", "📏 Nivelación", "💰 Presupuesto", "📓 Bitácora", "🔄 Conversor"])
    with tab1:
        st.subheader("📋 Carga de Cartera")
        archivo = st.file_uploader("Subir Excel", type=["xlsx", "xls"], key="v122_topo_excel", label_visibility="collapsed")
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
                st.success(f"✅ Cargados {len(df)} puntos")
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
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Puntos", len(df))
                    c2.metric("Dist. Total (m)", f"{sum(distancias):.2f}")
                    c3.metric("Cota Max", f"{df['Cota'].max():.2f}")
                    st.dataframe(df, use_container_width=True)
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Procesado")
                    st.download_button(label="📥 Descargar Excel Procesado", data=output.getvalue(), file_name=f"TopoAuto_Procesado_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="v122_topo_dl", use_container_width=True)
                else:
                    st.warning("⚠️ Tu Excel debe tener: Punto, Norte, Este, Cota
