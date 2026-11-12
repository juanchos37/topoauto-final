# TopoAuto Pro v12 UNIFICADA - Juan SAS + Despacho Dra Norma - TODO EN UNO
import streamlit as st
import pandas as pd
import numpy as np
import math
import io
from datetime import date

st.set_page_config(page_title="TopoAuto Pro v12", page_icon="📍", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #1A1A1A !important; }
    .stButton > button { background-color: #E53935; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    .stDownloadButton > button { background-color: #1E88E5; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📍 TopoAuto Pro v12 UNIFICADA")
st.write("Bienvenido: **Juan SAS** | Montería, Córdoba")
st.divider()

# SELECTOR PRINCIPAL - NO SE MEZCLAN LOS MODOS
modo = st.radio("¿En qué modo quieres trabajar hoy?", ["👷 MODO TOPÓGRAFO - Juan SAS", "⚖️ MODO DESPACHO - Dra. Norma"], horizontal=True, key="modo_principal_v12")
st.divider()

# ============================================================
# MODO 1 - TOPOGRAFO - TODO INDEPENDIENTE
# ============================================================
if modo == "👷 MODO TOPÓGRAFO - Juan SAS":
    st.header("👷 Modo Topógrafo - Juan SAS")
    st.caption("Solo topografía. No toca nada del despacho.")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Procesar Excel", "📸 Dron", "📍 Replanteo", "📏 Nivelación", "💰 Presupuesto", "📓 Bitácora", "🔄 Conversor"])

    with tab1:
        st.subheader("📋 Carga de Cartera")
        st.write("Subir Excel: Punto, Norte, Este, Cota")
        archivo = st.file_uploader("Subir Excel", type=["xlsx", "xls"], key="v12_topo_excel", label_visibility="collapsed")
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
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Puntos", len(df))
                    c2.metric("Dist. Total (m)", f"{sum(distancias):.2f}")
                    c3.metric("Cota Max", f"{df['Cota'].max():.2f}")
                    st.dataframe(df, use_container_width=True)
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Procesado")
                    st.download_button(label="📥 Descargar Excel Procesado", data=output.getvalue(), file_name=f"TopoAuto_Procesado_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="v12_topo_descargar", use_container_width=True)
                else:
                    st.warning("⚠️ Tu Excel debe tener: Punto, Norte, Este, Cota")
            except Exception as e:
                st.error(f"Error leyendo el Excel: {e}")
        else:
            st.info("👆 Sube tu Excel de cartera para empezar.")

    with tab2:
        st.subheader("📸 Módulo Dron")
        col1, col2 = st.columns(2)
        with col1:
            altura = st.number_input("Altura de vuelo (m)", value=100, min_value=20, max_value=300, key="v12_dron_altura")
            gsd = st.number_input("GSD deseado (cm/px)", value=3.0, min_value=0.5, max_value=20.0, key="v12_dron_gsd")
        with col2:
            area = st.number_input("Área a levantar (Ha)", value=10.0, min_value=0.5, key="v12_dron_area")
            traslape = st.slider("Traslape (%)", 60, 90, 75, key="v12_dron_traslape")
        if st.button("🚁 Calcular Vuelo Dron", key="v12_dron_btn", use_container_width=True):
            tiempo_min = round((area * 12) / (altura / 100) + 10, 1)
            num_fotos = int(area * 45 * (traslape / 75))
            baterias = max(1, math.ceil(tiempo_min / 22))
            st.success("✅ Cálculo listo")
            c1, c2, c3 = st.columns(3)
            c1.metric("Tiempo aprox.", f"{tiempo_min} min")
            c2.metric("Fotos aprox.", num_fotos)
            c3.metric("Baterías", baterias)
            st.info(f"💡 Vuela a {altura}m con {traslape}% de traslape y GSD de {gsd} cm/px. Lleva {baterias} baterías.")
        st.divider()
        foto_dron = st.file_uploader("Sube una foto del levantamiento", type=["jpg", "jpeg", "png"], key="v12_dron_foto")
        if foto_dron is not None:
            st.image(foto_dron, caption="Foto del levantamiento", use_container_width=True)

    with tab3:
        st.subheader("📍 Replanteo por Coordenadas")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Punto Base")
            n1 = st.number_input("Norte Base", value=1700000.0, key="v12_rep_n1")
            e1 = st.number_input("Este Base", value=800000.0, key="v12_rep_e1")
        with c2:
            st.write("Punto a Replantear")
            n2 = st.number_input("Norte Destino", value=1700100.0, key="v12_rep_n2")
            e2 = st.number_input("Este Destino", value=800100.0, key="v12_rep_e2")
        if st.button("📍 Calcular Replanteo", key="v12_rep_btn", use_container_width=True):
            dn = n2 - n1
            de = e2 - e1
            dist = math.sqrt(dn ** 2 + de ** 2)
            az = math.degrees(math.atan2(de, dn))
            if az < 0:
                az = az + 360
            cc1, cc2 = st.columns(2)
            cc1.metric("Distancia (m)", f"{dist:.3f}")
            cc2.metric("Azimut", f"{az:.3f}°")
            st.success(f"✅ Gira {az:.2f}° y mide {dist:.2f} m")

    with tab4:
        st.subheader("📏 Nivelación Geométrica")
        vista_atras = st.number_input("Vista Atrás (m)", value=1.500, step=0.001, format="%.3f", key="v12_niv_atras")
        cota_bm = st.number_input("Cota BM (m)", value=10.000, step=0.001, format="%.3f", key="v12_niv_bm")
        vista_adelante = st.number_input("Vista Adelante (m)", value=1.200, step=0.001, format="%.3f", key="v12_niv_adelante")
        if st.button("📏 Calcular Nivelación", key="v12_niv_btn", use_container_width=True):
            altura_inst = cota_bm + vista_atras
            cota_nueva = altura_inst - vista_adelante
            desnivel = cota_nueva - cota_bm
            n1, n2, n3 = st.columns(3)
            n1.metric("Altura Instrumental", f"{altura_inst:.3f} m")
            n2.metric("Cota Nueva", f"{cota_nueva:.3f} m")
            n3.metric("Desnivel", f"{desnivel:.3f} m")

    with tab5:
        st.subheader("💰 Presupuesto Rápido")
        tipo = st.selectbox("Tipo de trabajo", ["Levantamiento Topográfico", "Replanteo", "Vuelo Dron", "Nivelación", "Desenglobe / Loteo"], key="v12_pres_tipo")
        hectareas = st.number_input("Hectáreas / Área", value=1.0, min_value=0.1, key="v12_pres_ha")
        precio_ha = st.number_input("Precio por Ha ($ COP)", value=350000, step=10000, key="v12_pres_precio")
        transporte = st.number_input("Transporte ($ COP)", value=80000, step=10000, key="v12_pres_transp")
        if st.button("💰 Calcular Presupuesto", key="v12_pres_btn", use_container_width=True):
            subtotal = hectareas * precio_ha
            total = subtotal + transporte
            p1, p2, p3 = st.columns(3)
            p1.metric("Subtotal", f"${subtotal:,.0f}")
            p2.metric("Transporte", f"${transporte:,.0f}")
            p3.metric("TOTAL", f"${total:,.0f}")
            st.success(f"✅ Presupuesto para {tipo} - {hectareas} Ha. Total: ${total:,.0f} COP")

    with tab6:
        st.subheader("📓 Bitácora de Campo - Solo Topografía")
        if "bitacora_topo_v12" not in st.session_state:
            st.session_state["bitacora_topo_v12"] = []
        with st.form("form_bitacora_topo_v12", clear_on_submit=True):
            fecha_b = st.date_input("Fecha", value=date.today(), key="v12_bit_fecha")
            proyecto = st.text_input("Proyecto / Cliente", placeholder="Ej: Lote Juan SAS - Montería", key="v12_bit_proyecto")
            actividad = st.selectbox("Actividad", ["Levantamiento Topográfico", "Replanteo", "Vuelo Dron", "Nivelación", "Otro"], key="v12_bit_actividad")
            notas = st.text_area("Notas de campo", placeholder="Ej: Se levantaron 45 puntos...", key="v12_bit_notas")
            guardar_b = st.form_submit_button("💾 Guardar en Bitácora", use_container_width=True)
            if guardar_b:
                if proyecto.strip() == "":
                    st.warning("Escribe el nombre del proyecto.")
                else:
                    st.session_state["bitacora_topo_v12"].append({"Fecha": str(fecha_b), "Proyecto": proyecto, "Actividad": actividad, "Notas": notas})
                    st.success("✅ Guardado en bitácora de topografía")
        if len(st.session_state["bitacora_topo_v12"]) > 0:
            df_bit = pd.DataFrame(st.session_state["bitacora_topo_v12"])
            st.dataframe(df_bit, use_container_width=True)
            output2 = io.BytesIO()
            with pd.ExcelWriter(output2, engine="openpyxl") as writer:
                df_bit.to_excel(writer, index=False, sheet_name="Bitacora")
            st.download_button(label="📥 Descargar Bitácora en Excel", data=output2.getvalue(), file_name=f"Bitacora_TopoAuto_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="v12_bit_descargar", use_container_width=True)

    with tab7:
        st.subheader("🔄 Conversor Rápido")
        metros = st.number_input("Metros cuadrados (m2)", value=10000.0, key="v12_conv_m2")
        if st.button("🔄 Convertir a Ha", key="v12_conv_btn1", use_container_width=True):
           
