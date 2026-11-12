# TopoAuto Pro v12.1 FIX - UNIFICADA - SIN ERRORES
import streamlit as st
import pandas as pd
import numpy as np
import math
import io
from datetime import date

st.set_page_config(page_title="TopoAuto Pro v12", page_icon="📍", layout="centered")
st.title("📍 TopoAuto Pro v12 UNIFICADA")
st.write("Bienvenido: **Juan SAS** | Montería, Córdoba")
st.divider()
modo = st.radio("¿En qué modo quieres trabajar hoy?", ["👷 MODO TOPÓGRAFO - Juan SAS", "⚖️ MODO DESPACHO - Dra. Norma"], horizontal=True, key="modo_v121")
st.divider()

if modo == "👷 MODO TOPÓGRAFO - Juan SAS":
    st.header("👷 Modo Topógrafo - Juan SAS")
    st.caption("Solo topografía. No toca nada del despacho.")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Procesar Excel", "📸 Dron", "📍 Replanteo", "📏 Nivelación", "💰 Presupuesto", "📓 Bitácora", "🔄 Conversor"])
    with tab1:
        st.subheader("📋 Carga de Cartera")
        archivo = st.file_uploader("Subir Excel", type=["xlsx", "xls"], key="v121_topo_excel", label_visibility="collapsed")
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
                    st.download_button(label="📥 Descargar Excel Procesado", data=output.getvalue(), file_name=f"TopoAuto_Procesado_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="v121_topo_dl", use_container_width=True)
                else:
                    st.warning("⚠️ Tu Excel debe tener: Punto, Norte, Este, Cota")
            except Exception as e:
                st.error(f"Error leyendo el Excel: {e}")
        else:
            st.info("👆 Sube tu Excel de cartera para empezar.")
    with tab2:
        st.subheader("📸 Módulo Dron")
        altura = st.number_input("Altura de vuelo (m)", value=100, min_value=20, max_value=300, key="v121_dron_alt")
        area = st.number_input("Área a levantar (Ha)", value=10.0, min_value=0.5, key="v121_dron_area")
        traslape = st.slider("Traslape (%)", 60, 90, 75, key="v121_dron_tras")
        if st.button("🚁 Calcular Vuelo Dron", key="v121_dron_btn", use_container_width=True):
            tiempo_min = round((area * 12) / (altura / 100) + 10, 1)
            num_fotos = int(area * 45 * (traslape / 75))
            baterias = max(1, math.ceil(tiempo_min / 22))
            c1, c2, c3 = st.columns(3)
            c1.metric("Tiempo aprox.", f"{tiempo_min} min")
            c2.metric("Fotos aprox.", num_fotos)
            c3.metric("Baterías", baterias)
            st.success("✅ Cálculo listo")
        foto_dron = st.file_uploader("Sube una foto del levantamiento", type=["jpg", "jpeg", "png"], key="v121_dron_foto")
        if foto_dron is not None:
            st.image(foto_dron, caption="Foto del levantamiento", use_container_width=True)
    with tab3:
        st.subheader("📍 Replanteo")
        n1 = st.number_input("Norte Base", value=1700000.0, key="v121_rep_n1")
        e1 = st.number_input("Este Base", value=800000.0, key="v121_rep_e1")
        n2 = st.number_input("Norte Destino", value=1700100.0, key="v121_rep_n2")
        e2 = st.number_input("Este Destino", value=800100.0, key="v121_rep_e2")
        if st.button("📍 Calcular Replanteo", key="v121_rep_btn", use_container_width=True):
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
        st.subheader("📏 Nivelación")
        vista_atras = st.number_input("Vista Atrás (m)", value=1.500, step=0.001, format="%.3f", key="v121_niv_atras")
        cota_bm = st.number_input("Cota BM (m)", value=10.000, step=0.001, format="%.3f", key="v121_niv_bm")
        vista_adelante = st.number_input("Vista Adelante (m)", value=1.200, step=0.001, format="%.3f", key="v121_niv_adel")
        if st.button("📏 Calcular Nivelación", key="v121_niv_btn", use_container_width=True):
            altura_inst = cota_bm + vista_atras
            cota_nueva = altura_inst - vista_adelante
            desnivel = cota_nueva - cota_bm
            n1, n2, n3 = st.columns(3)
            n1.metric("Altura Instrumental", f"{altura_inst:.3f} m")
            n2.metric("Cota Nueva", f"{cota_nueva:.3f} m")
            n3.metric("Desnivel", f"{desnivel:.3f} m")
    with tab5:
        st.subheader("💰 Presupuesto Rápido")
        tipo = st.selectbox("Tipo de trabajo", ["Levantamiento Topográfico", "Replanteo", "Vuelo Dron", "Nivelación", "Desenglobe / Loteo"], key="v121_pres_tipo")
        hectareas = st.number_input("Hectáreas / Área", value=1.0, min_value=0.1, key="v121_pres_ha")
        precio_ha = st.number_input("Precio por Ha ($ COP)", value=350000, step=10000, key="v121_pres_precio")
        transporte = st.number_input("Transporte ($ COP)", value=80000, step=10000, key="v121_pres_transp")
        if st.button("💰 Calcular Presupuesto", key="v121_pres_btn", use_container_width=True):
            subtotal = hectareas * precio_ha
            total = subtotal + transporte
            p1, p2, p3 = st.columns(3)
            p1.metric("Subtotal", f"${subtotal:,.0f}")
            p2.metric("Transporte", f"${transporte:,.0f}")
            p3.metric("TOTAL", f"${total:,.0f}")
            st.success(f"✅ Total: ${total:,.0f} COP")
    with tab6:
        st.subheader("📓 Bitácora de Campo")
        if "bitacora_topo_v121" not in st.session_state:
            st.session_state["bitacora_topo_v121"] = []
        with st.form("form_bitacora_v121", clear_on_submit=True):
            fecha_b = st.date_input("Fecha", value=date.today(), key="v121_bit_fecha")
            proyecto = st.text_input("Proyecto / Cliente", placeholder="Ej: Lote Juan SAS - Montería", key="v121_bit_proy")
            actividad = st.selectbox("Actividad", ["Levantamiento Topográfico", "Replanteo", "Vuelo Dron", "Nivelación", "Otro"], key="v121_bit_act")
            notas = st.text_area("Notas de campo", placeholder="Ej: Se levantaron 45 puntos...", key="v121_bit_notas")
            guardar_b = st.form_submit_button("💾 Guardar en Bitácora", use_container_width=True)
            if guardar_b:
                if proyecto.strip() == "":
                    st.warning("Escribe el nombre del proyecto.")
                else:
                    st.session_state["bitacora_topo_v121"].append({"Fecha": str(fecha_b), "Proyecto": proyecto, "Actividad": actividad, "Notas": notas})
                    st.success("✅ Guardado en bitácora")
        if len(st.session_state["bitacora_topo_v121"]) > 0:
            df_bit = pd.DataFrame(st.session_state["bitacora_topo_v121"])
            st.dataframe(df_bit, use_container_width=True)
            output2 = io.BytesIO()
            with pd.ExcelWriter(output2, engine="openpyxl") as writer:
                df_bit.to_excel(writer, index=False, sheet_name="Bitacora")
            st.download_button(label="📥 Descargar Bitácora en Excel", data=output2.getvalue(), file_name=f"Bitacora_TopoAuto_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="v121_bit_dl", use_container_width=True)
    with tab7:
        st.subheader("🔄 Conversor Rápido")
        metros = st.number_input("Metros cuadrados (m2)", value=10000.0, key="v121_conv_m2")
        if st.button("🔄 Convertir a Ha", key="v121_conv_btn1", use_container_width=True):
            st.success(f"✅ {metros:,.0f} m2 = {metros / 10000:.4f} Ha")
        dist_m = st.number_input("Distancia en metros", value=100.0, key="v121_conv_m")
        if st.button("🔄 Convertir a Km", key="v121_conv_btn2", use_container_width=True):
            st.success(f"✅ {dist_m} m = {dist_m / 1000:.3f} Km")

if modo == "⚖️ MODO DESPACHO - Dra. Norma":
    st.header("⚖️ Modo Despacho - Dra. Norma")
    st.caption("Solo despacho. No toca nada de topografía.")
    if "clientes_desp_v121" not in st.session_state:
        st.session_state["clientes_desp_v121"] = []
    if "procesos_desp_v121" not in st.session_state:
        st.session_state["procesos_desp_v121"] = []
    if "facturas_desp_v121" not in st.session_state:
        st.session_state["facturas_desp_v121"] = []
    vista_desp = st.radio("Vista:", ["🟢 Vista Doctora - Súper Fácil", "🔵 Vista Admin - Completa (Juan)"], horizontal=True, key="v121_desp_vista")
    if vista_desp == "🟢 Vista Doctora - Súper Fácil":
        st.subheader("Inicio Despacho - Dra. Norma")
        total_clientes = len(st.session_state["clientes_desp_v121"])
        total_procesos = len(st.session_state["procesos_desp_v121"])
        total_cobrar = 0
        for f in st.session_state["facturas_desp_v121"]:
            if f["Estado"] == "Por cobrar":
                total_cobrar = total_cobrar + f["Valor"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Clientes", total_clientes)
        c2.metric("Procesos Activos", total_procesos)
        c3.metric("Por Cobrar", f"${total_cobrar:,.0f}")
        st.divider()
        dtab1, dtab2, dtab3 = st.tabs(["📄 Hacer Documento", "📅 Ver Procesos", "💰 Ver Mi Plata"])
        with dtab1:
            st.write("Generar Documento en Word")
            cliente_doc = st.text_input("Cliente", placeholder="Ej: María López", key="v121_desp_doc_cli")
            tipo_doc = st.selectbox("Tipo de documento", ["Poder", "Demanda", "Tutela", "Derecho de Petición"], key="v121_desp_doc_tipo")
            hechos = st.text_area("Cuéntame los hechos en 2 líneas", placeholder="Ej: Lo despidieron sin justa causa...", key="v121_desp_doc_hechos")
            if st.button("📄 Generar Word", key="v121_desp_doc_btn", use_container_width=True):
                if cliente_doc.strip() == "":
                    st.warning("Escribe el nombre del cliente.")
                else:
                    texto = "DOCUMENTO: " + tipo_doc + "\nCLIENTE: " + cliente_doc + "\nHECHOS: " + hechos
                    st.success("✅ Documento listo para revisar")
                    st.text_area("Vista previa", texto, height=150, key="v121_desp_doc_prev")
                    st.download_button(label="📥 Descargar Documento (.txt)", data=texto, file_name="Documento.txt", mime="text/plain", key="v121_desp_doc_dl", use_container_width=True)
        with dtab2:
            st.write("Mis Procesos")
            if len(st.session_state["procesos_desp_v121"]) > 0:
                st.dataframe(pd.DataFrame(st.session_state["procesos_desp_v121"]), use_container_width=True)
            else:
                st.info("No hay procesos todavía. Juan los agrega en Vista Admin.")
        with dtab3:
            st.write("Mi Plata")
            if len(st.session_state["facturas_desp_v121"]) > 0:
                st.dataframe(pd.DataFrame(st.session_state["facturas_desp_v121"]), use_container_width=True)
            else:
                st.info("No hay facturas todavía.")
    if vista_desp == "🔵 Vista Admin - Completa (Juan)":
        st.subheader("Vista Admin - Completa - Solo Juan")
        atab1, atab2, atab3, atab4 = st.tabs(["👥 Clientes", "📅 Procesos", "💰 Facturación", "📊 Análisis de Datos"])
        with atab1:
            st.write("Agregar Cliente - Despacho")
            with st.form("form_cliente_v121", clear_on_submit=True):
                nom_c = st.text_input("Nombre completo", key="v121_admin_cli_nom")
                cel_c = st.text_input("Celular", key="v121_admin_cli_cel")
                btn_c = st.form_submit_button("💾 Guardar Cliente", use_container_width=True)
                if btn_c:
                    if nom_c.strip() == "":
                        st.warning("Escribe el nombre.")
                    else:
                        st.session_state["clientes_desp_v121"].append({"Nombre": nom_c, "Celular": cel_c})
                        st.success("✅ Cliente guardado en Despacho")
            if len(st.session_state["clientes_desp_v121"]) > 0:
                st.dataframe(pd.DataFrame(st.session_state["clientes_desp_v121"]), use_container_width=True)
        with atab2:
            st.write("Agregar Proceso - Despacho")
            with st.form("form_proceso_v121", clear_on_submit=True):
                cli_p = st.text_input("Cliente del proceso", key="v121_admin_proc_cli")
                tipo_p = st.selectbox("Tipo", ["Tutela", "Demanda Laboral", "Nulidad", "Divorcio", "Otro"], key="v121_admin_proc_tipo")
                vence_p = st.date_input("Fecha de vencimiento", value=date.today(), key="v121_admin_proc_vence")
                btn_p = st.form_submit_button("💾 Guardar Proceso", use_container_width=True)
                if btn_p:
                    if cli_p.strip() == "":
                        st.warning("Escribe el cliente.")
                    else:
                        st.session_state["procesos_desp_v121"].append({"Cliente": cli_p, "Tipo": tipo_p, "Vence": str(vence_p)})
                        st.success("✅ Proceso guardado")
            if len(st.session_state["procesos_desp_v121"]) > 0:
                st.dataframe(pd.DataFrame(st.session_state["procesos_desp_v121"]), use_container_width=True)
        with atab3:
            st.write("Facturación - Despacho")
            with st.form("form_factura_v121", clear_on_submit=True):
                cli_f = st.text_input("Cliente a facturar", key="v121_admin_fac_cli")
                concepto_f = st.text_input("Concepto", placeholder="Ej: Poder - Tutela", key="v121_admin_fac_con")
                valor_f = st.number_input("Valor ($ COP)", value=500000, step=10000, key="v121_admin_fac_valor")
                estado_f = st.selectbox("Estado", ["Por cobrar", "Pagado"], key="v121_admin_fac_estado")
                btn_f = st.form_submit_button("💾 Guardar Factura", use_container_width=True)
                if btn_f:
                    if cli_f.strip() == "":
                        st.warning("Escribe el cliente.")
                    else:
                        st.session_state["facturas_desp_v121"].append({"Cliente": cli_f, "Concepto": concepto_f, "Valor": valor_f, "Estado": estado_f})
                        st.success("✅ Factura guardada")
            if len(st.session_state["facturas_desp_v121"]) > 0:
                df_fac = pd.DataFrame(st.session_state["facturas_desp_v121"])
                st.dataframe(df_fac, use_container_width=True)
                total_cobrar2 = df_fac[df_fac["Estado"] == "Por cobrar"]["Valor"].sum()
                total_pagado2 = df_fac[df_fac["Estado"] == "Pagado"]["Valor"].sum()
                f1, f2 = st.columns(2)
                f1.metric("Por Cobrar", f"${total_cobrar2:,.0f}")
                f2.metric("Pagado", f"${total_pagado2:,.0f}")
        with atab4:
            st.write("Análisis de Datos del Despacho")
            if len(st.session_state["facturas_desp_v121"]) > 0:
                df_a = pd.DataFrame(st.session_state["facturas_desp_v121"])
                st.bar_chart(df_a.groupby("Estado")["Valor"].sum())
                st.dataframe(df_a.groupby("Estado")["Valor"].sum(), use_container_width=True)
            else:
                st.info("Agrega facturas para ver el análisis. Esto no toca Topografía.")

st.divider()
st.caption("TopoAuto Pro v12 UNIFICADA - Juan SAS + Despacho Dra. Norma - Hecho en Montería")
