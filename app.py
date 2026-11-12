# GeoLegal Pro v12.6 FINAL
import streamlit as st
import pandas as pd
import math
import io
from datetime import date

st.set_page_config(
    page_title="GeoLegal Pro",
    page_icon="⚖️",
    layout="centered"
)
st.title("GeoLegal Pro - Juan SAS")
st.write("Juan SAS | Monteria")
st.divider()
modo = st.radio(
    "Modo",
    ["TOPOGRAFO", "DESPACHO"],
    horizontal=True
)
st.divider()

def predecir(tipo, dem, valor):
    base = 50.0
    if tipo == "Nulidad":
        base += 18
    if tipo == "Tutela":
        base += 22
    if tipo == "Demanda Laboral":
        base += 12
    if tipo == "Divorcio":
        base += 8
    if tipo == "Otro":
        base += 5
    if dem == "Colpensiones":
        base += 10
    if dem == "EPS":
        base += 8
    if dem == "Empresa Privada":
        base += 2
    if dem == "Estado":
        base -= 5
    if valor > 15000000:
        base += 5
    if valor < 2000000:
        base -= 5
    prob = max(12, min(92, int(base)))
    if prob >= 70:
        c = "Caso FUERTE, Prioridad ALTA"
    elif prob >= 50:
        c = "Caso MEDIO, revisa pruebas"
    else:
        c = "Caso DEBIL, cobra adelantado"
    return prob, c

def hacer_doc(tipo, cliente, hechos):
    t = "DOCUMENTO: " + tipo + "\n"
    t += "CLIENTE: " + cliente + "\n\n"
    t += "Senor Juez, presento " + tipo + "\n\n"
    t += "HECHOS:\n" + hechos + "\n\n"
    t += "PRETENSIONES:\n"
    t += "1. Se declare lo solicitado.\n"
    t += "2. Se ordene cumplir.\n\n"
    t += "FUNDAMENTOS: Constitucion y CGP.\n\n"
    t += "Atentamente, Dra. Norma\n"
    t += "Monteria, " + str(date.today())
    return t

if modo == "TOPOGRAFO":
    st.header("Modo Topografo")
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(
        ["Excel", "Dron", "Replanteo",
         "Nivelacion", "Presupuesto",
         "Bitacora", "Conversor"]
    )
    with t1:
        st.subheader("Carga de Cartera")
        archivo = st.file_uploader(
            "Subir Excel",
            type=["xlsx", "xls"]
        )
        if archivo is None:
            st.info("Sube tu Excel")
        if archivo is not None:
            df = pd.read_excel(archivo)
            df.columns = [
                str(c).strip().capitalize()
                for c in df.columns
            ]
            mapa = {}
            for c in df.columns:
                cl = c.lower()
                if "punto" in cl:
                    mapa[c] = "Punto"
                elif "norte" in cl:
                    mapa[c] = "Norte"
                elif "este" in cl:
                    mapa[c] = "Este"
                elif "cota" in cl:
                    mapa[c] = "Cota"
            df = df.rename(columns=mapa)
            st.success("Cargados puntos")
            st.dataframe(df.head(20))
            ok = "Punto" in df.columns
            ok = ok and "Norte" in df.columns
            ok = ok and "Este" in df.columns
            ok = ok and "Cota" in df.columns
            if ok:
                df["Norte"] = pd.to_numeric(
                    df["Norte"], errors="coerce"
                )
                df["Este"] = pd.to_numeric(
                    df["Este"], errors="coerce"
                )
                df["Cota"] = pd.to_numeric(
                    df["Cota"], errors="coerce"
                )
                df = df.dropna(
                    subset=["Norte", "Este"]
                )
                dists = [0.0]
                for i in range(1, len(df)):
                    dn = df.iloc[i]["Norte"]
                    dn -= df.iloc[i-1]["Norte"]
                    de = df.iloc[i]["Este"]
                    de -= df.iloc[i-1]["Este"]
                    d = math.sqrt(dn*dn + de*de)
                    dists.append(round(d, 3))
                df["Dist_m"] = dists
                c1, c2, c3 = st.columns(3)
                c1.metric("Puntos", len(df))
                c2.metric(
                    "Dist Total",
                    round(sum(dists), 2)
                )
                c3.metric(
                    "Cota Max",
                    round(float(df["Cota"].max()), 2)
                )
                st.dataframe(df)
                out = io.BytesIO()
                with pd.ExcelWriter(
                    out, engine="openpyxl"
                ) as w:
                    df.to_excel(
                        w,
                        index=False,
                        sheet_name="Procesado"
                    )
                st.download_button(
                    "Descargar Excel",
                    data=out.getvalue(),
                    file_name="Procesado.xlsx"
                )
            else:
                st.warning(
                    "Tu Excel debe tener:"
                )
                st.warning(
                    "Punto, Norte, Este, Cota"
                )
    with t2:
        st.subheader("Modulo Dron")
        altura = st.number_input(
            "Altura (m)", value=100
        )
        area = st.number_input(
            "Area (Ha)", value=10.0
        )
        tras = st.slider(
            "Traslape (%)", 60, 90, 75
        )
        if st.button("Calcular Vuelo"):
            tiempo = (area * 12)
            tiempo = tiempo / (altura/100)
            tiempo = round(tiempo + 10, 1)
            fotos = int(area * 45 * (tras/75))
            bats = max(1, math.ceil(tiempo/22))
            c1, c2, c3 = st.columns(3)
            c1.metric("Tiempo", tiempo)
            c2.metric("Fotos", fotos)
            c3.metric("Baterias", bats)
            st.success("Calculo listo")
        foto = st.file_uploader(
            "Sube foto",
            type=["jpg", "png"]
        )
        if foto is not None:
            st.image(foto)
    with t3:
        st.subheader("Replanteo")
        n1 = st.number_input(
            "Norte Base", value=1700000.0
        )
        e1 = st.number_input(
            "Este Base", value=800000.0
        )
        n2 = st.number_input(
            "Norte Destino", value=1700100.0
        )
        e2 = st.number_input(
            "Este Destino", value=800100.0
        )
        if st.button("Calcular Replanteo"):
            dn = n2 - n1
            de = e2 - e1
            dist = math.sqrt(dn*dn + de*de)
            az = math.degrees(
                math.atan2(de, dn)
            )
            if az < 0:
                az = az + 360
            c1, c2 = st.columns(2)
            c1.metric("Distancia", round(dist, 3))
            c2.metric("Azimut", round(az, 3))
            st.success("Calculo listo")
    with t4:
        st.subheader("Nivelacion")
        va = st.number_input(
            "Vista Atras", value=1.5
        )
        bm = st.number_input(
            "Cota BM", value=10.0
        )
        vd = st.number_input(
            "Vista Adelante", value=1.2
        )
        if st.button("Calcular Nivelacion"):
            ai = bm + va
            cn = ai - vd
            des = cn - bm
            c1, c2, c3 = st.columns(3)
            c1.metric("Altura", round(ai, 3))
            c2.metric("Cota Nueva", round(cn, 3))
            c3.metric("Desnivel", round(des, 3))
    with t5:
        st.subheader("Presupuesto")
        tipo = st.selectbox(
            "Tipo",
            ["Levantamiento", "Replanteo",
             "Dron", "Nivelacion", "Loteo"]
        )
        ha = st.number_input(
            "Hectareas", value=1.0
        )
        precio = st.number_input(
            "Precio por Ha", value=350000
        )
        transp = st.number_input(
            "Transporte", value=80000
        )
        if st.button("Calcular Presupuesto"):
            sub = ha * precio
            tot = sub + transp
            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal", int(sub))
            c2.metric("Transporte", int(transp))
            c3.metric("TOTAL", int(tot))
    with t6:
        st.subheader("Bitacora")
        if "bit" not in st.session_state:
            st.session_state["bit"] = []
        with st.form("f_bit", clear_on_submit=True):
            fb = st.date_input(
                "Fecha", value=date.today()
            )
            proy = st.text_input("Proyecto")
            act = st.selectbox(
                "Actividad",
                ["Levantamiento", "Replanteo",
                 "Dron", "Nivelacion", "Otro"]
            )
            notas = st.text_area("Notas")
            gb = st.form_submit_button("Guardar")
            if gb:
                if proy.strip() == "":
                    st.warning("Escribe proyecto")
                else:
                    st.session_state["bit"].append(
                        {"Fecha": str(fb),
                         "Proyecto": proy,
                         "Actividad": act,
                         "Notas": notas}
                    )
                    st.success("Guardado")
        if len(st.session_state["bit"]) > 0:
            st.dataframe(
                pd.DataFrame(st.session_state["bit"])
            )
    with t7:
        st.subheader("Conversor")
        m2 = st.number_input(
            "Metros cuadrados", value=10000.0
        )
        if st.button("Convertir a Ha"):
            st.success("Resultado en Ha")
            st.write(m2 / 10000)
        dm = st.number_input(
            "Distancia en metros", value=100.0
        )
        if st.button("Convertir a Km"):
            st.success("Resultado en Km")
            st.write(dm / 1000)

if modo == "DESPACHO":
    st.header("Modo Despacho - Dra. Norma")
    if "cli" not in st.session_state:
        st.session_state["cli"] = []
    if "proc" not in st.session_state:
        st.session_state["proc"] = []
    if "fac" not in st.session_state:
        st.session_state["fac"] = []
    if "gas" not in st.session_state:
        st.session_state["gas"] = []
    vista = st.radio(
        "Vista",
        ["Vista Doctora", "Vista Admin"],
        horizontal=True
    )
    if vista == "Vista Doctora":
        st.subheader("Inicio - Dra. Norma")
        cob = 0
        for f in st.session_state["fac"]:
            if f["Estado"] == "Por cobrar":
                cob += f["Valor"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Clientes", len(st.session_state["cli"]))
        c2.metric("Procesos", len(st.session_state["proc"]))
        c3.metric("Por Cobrar", int(cob))
        st.info("Doctora, solo use botones grandes")
        d1, d2, d3, d4 = st.tabs(
            ["Documento", "Documento IA",
             "Procesos", "Mi Plata"]
        )
        with d1:
            cli = st.text_input("Cliente")
            td = st.selectbox(
                "Tipo",
                ["Poder", "Demanda",
                 "Tutela", "Derecho de Peticion"]
            )
            he = st.text_area("Hechos en 2 lineas")
            if st.button("Generar Documento"):
                if cli.strip() == "":
                    st.warning("Escribe cliente")
                else:
                    tx = hacer_doc(td, cli, he)
                    st.success("Documento listo")
                    st.text_area(
                        "Vista previa", tx, height=200
                    )
                    st.download_button(
                        "Descargar",
                        data=tx,
                        file_name="Documento.txt"
                    )
        with d2:
            cli2 = st.text_input("Cliente IA")
            td2 = st.selectbox(
                "Tipo IA",
                ["Poder", "Demanda",
                 "Tutela", "Derecho de Peticion"]
            )
            he2 = st.text_area("Habla aqui")
            if st.button("Generar con IA"):
                if cli2.strip() == "":
                    st.warning("Escribe cliente")
                else:
                    tx2 = hacer_doc(td2, cli2, he2)
                    st.success("IA genero documento")
                    st.text_area(
                        "Documento IA", tx2, height=220
                    )
                    st.download_button(
                        "Descargar IA",
                        data=tx2,
                        file_name="Documento_IA.txt"
                    )
        with d3:
            if len(st.session_state["proc"]) > 0:
                st.dataframe(
                    pd.DataFrame(st.session_state["proc"])
                )
            else:
                st.info("No hay procesos todavia")
        with d4:
            if len(st.session_state["fac"]) > 0:
                st.dataframe(
                    pd.DataFrame(st.session_state["fac"])
                )
            else:
                st.info("No hay facturas todavia")
    if vista == "Vista Admin":
        st.subheader("Vista Admin - Solo Juan")
        a1, a2, a3, a4, a5, a6, a7, a8 = st.tabs(
            ["Inicio", "Clientes", "Procesos",
             "Documentos", "Facturacion",
             "Flujo Caja", "Red Neuronal",
             "Analisis"]
        )
        with a1:
            cob = 0
            pag = 0
            for f in st.session_state["fac"]:
                if f["Estado"] == "Por cobrar":
                    cob += f["Valor"]
                if f["Estado"] == "Pagado":
                    pag += f["Valor"]
            tg = 0
            for g in st.session_state["gas"]:
                tg += g["Valor"]
            caja = pag - tg
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Procesos", len(st.session_state["proc"]))
            c2.metric("Clientes", len(st.session_state["cli"]))
            c3.metric("Por Cobrar", int(cob))
            c4.metric("En Caja", int(caja))
            if len(st.session_state["proc"]) > 0:
                st.dataframe(
                    pd.DataFrame(st.session_state["proc"])
                )
            else:
                st.info("No hay procesos todavia")
        with a2:
            with st.form("f_cli", clear_on_submit=True):
                nc = st.text_input("Nombre completo")
                cc = st.text_input("Celular")
                bc = st.form_submit_button("Guardar")
                if bc:
                    if nc.strip() == "":
                        st.warning("Escribe nombre")
                    else:
                        st.session_state["cli"].append(
                            {"Nombre": nc, "Celular": cc}
                        )
                        st.success("Cliente guardado")
            if len(st.session_state["cli"]) > 0:
                st.dataframe(
                    pd.DataFrame(st.session_state["cli"])
                )
        with a3:
            with st.form("f_proc", clear_on_submit=True):
                cp = st.text_input("Cliente proceso")
                tp = st.selectbox(
                    "Tipo",
                    ["Tutela", "Demanda Laboral",
                     "Nulidad", "Divorcio", "Otro"]
                )
                vp = st.date_input(
                    "Vencimiento", value=date.today()
                )
                bp = st.form_submit_button("Guardar")
                if bp:
                    if cp.strip() == "":
                        st.warning("Escribe cliente")
                    else:
                        st.session_state["proc"].append(
                            {"Cliente": cp,
                             "Tipo": tp,
                             "Vence": str(vp)}
                        )
                        st.success("Proceso guardado")
            if len(st.session_state["proc"]) > 0:
                st.dataframe(
                    pd.DataFrame(st.session_state["proc"])
                )
        with a4:
            cd = st.text_input("Cliente documento")
            td3 = st.selectbox(
                "Tipo doc",
                ["Poder", "Demanda",
                 "Tutela", "Derecho de Peticion"]
            )
            hd = st.text_area("Hechos")
            if st.button("Generar Doc Completo"):
                if cd.strip() == "":
                    st.warning("Escribe cliente")
                else:
                    tx3 = hacer_doc(td3, cd, hd)
                    st.text_area(
                        "Documento", tx3, height=220
                    )
                    st.download_button(
                        "Descargar",
                        data=tx3,
                        file_name="Documento.txt"
                    )
        with a5:
            with st.form("f_fac", clear_on_submit=True):
                cf = st.text_input("Cliente a facturar")
                conf = st.text_input("Concepto")
                vf = st.number_input("Valor", value=500000)
                ef = st.selectbox(
                    "Estado",
                    ["Por cobrar", "Pagado"]
                )
                bf = st.form_submit_button("Guardar")
                if bf:
                    if cf.strip() == "":
                        st.warning("Escribe cliente")
                    else:
                        st.session_state["fac"].append(
                            {"Cliente": cf,
                             "Concepto": conf,
                             "Valor": vf,
                             "Estado": ef}
                        )
                        st.success("Factura guardada")
            if len(st.session_state["fac"]) > 0:
                dff = pd.DataFrame(
                    st.session_state["fac"]
                )
                st.dataframe(dff)
                tc = dff[
                    dff["Estado"] == "
