# GeoLegal v12.8 PARTE 1
import streamlit as st
import pandas as pd
import math, io
from datetime import date
st.set_page_config(page_title="GeoLegal", layout="centered")
st.title("GeoLegal Pro - Juan SAS")
modo = st.radio("Modo", ["TOPOGRAFO", "DESPACHO"], horizontal=True)
st.divider()
def predecir(tipo, dem, valor):
    b = 50.0
    if tipo == "Nulidad": b += 18
    if tipo == "Tutela": b += 22
    if tipo == "Demanda Laboral": b += 12
    if tipo == "Divorcio": b += 8
    if tipo == "Otro": b += 5
    if dem == "Colpensiones": b += 10
    if dem == "EPS": b += 8
    if dem == "Empresa Privada": b += 2
    if dem == "Estado": b -= 5
    if valor > 15000000: b += 5
    if valor < 2000000: b -= 5
    p = max(12, min(92, int(b)))
    if p >= 70: c = "FUERTE, Prioridad ALTA"
    elif p >= 50: c = "MEDIO, revisa pruebas"
    else: c = "DEBIL, cobra adelantado"
    return p, c
def hacer_doc(tipo, cliente, hechos):
    t = "DOC: " + tipo + "\nCLIENTE: " + cliente + "\n\n"
    t += "HECHOS:\n" + hechos + "\n\n"
    t += "PRETENSIONES:\n1. Se declare lo solicitado.\n"
    t += "FUNDAMENTOS: Constitucion y CGP.\nDra. Norma\n"
    t += "Monteria, " + str(date.today())
    return t
if modo == "TOPOGRAFO":
    st.header("Topografo")
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["Excel","Dron","Replanteo","Nivelacion","Presupuesto","Bitacora","Conversor"])
    with t1:
        st.subheader("Cartera")
        a = st.file_uploader("Subir Excel", type=["xlsx","xls"])
        if a is not None:
            df = pd.read_excel(a)
            df.columns = [str(c).strip().capitalize() for c in df.columns]
            m = {}
            for c in df.columns:
                cl = c.lower()
                if "punto" in cl: m[c] = "Punto"
                elif "norte" in cl: m[c] = "Norte"
                elif "este" in cl: m[c] = "Este"
                elif "cota" in cl: m[c] = "Cota"
            df = df.rename(columns=m)
            st.dataframe(df.head(20))
            ok = "Punto" in df.columns and "Norte" in df.columns and "Este" in df.columns and "Cota" in df.columns
            if ok:
                df["Norte"] = pd.to_numeric(df["Norte"], errors="coerce")
                df["Este"] = pd.to_numeric(df["Este"], errors="coerce")
                df["Cota"] = pd.to_numeric(df["Cota"], errors="coerce")
                df = df.dropna(subset=["Norte","Este"])
                ds = [0.0]
                for i in range(1, len(df)):
                    dn = df.iloc[i]["Norte"] - df.iloc[i-1]["Norte"]
                    de = df.iloc[i]["Este"] - df.iloc[i-1]["Este"]
                    ds.append(round(math.sqrt(dn*dn+de*de),3))
                df["Dist_m"] = ds
                c1,c2,c3 = st.columns(3)
                c1.metric("Puntos", len(df))
                c2.metric("Dist", round(sum(ds),2))
                c3.metric("Cota Max", round(float(df["Cota"].max()),2))
                st.dataframe(df)
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine="openpyxl") as w:
                    df.to_excel(w, index=False, sheet_name="Procesado")
                st.download_button("Descargar", data=out.getvalue(), file_name="Procesado.xlsx")
            else:
                st.warning("Necesita: Punto, Norte, Este, Cota")
    with t2:
        st.subheader("Dron")
        alt = st.number_input("Altura", value=100)
        ar = st.number_input("Area Ha", value=10.0)
        tr = st.slider("Traslape", 60, 90, 75)
        if st.button("Calcular Vuelo"):
            ti = round((ar*12)/(alt/100)+10,1)
            fo = int(ar*45*(tr/75))
            ba = max(1, math.ceil(ti/22))
            c1,c2,c3 = st.columns(3)
            c1.metric("Tiempo", ti); c2.metric("Fotos", fo); c3.metric("Bat", ba)
        fo2 = st.file_uploader("Foto", type=["jpg","png"])
        if fo2 is not None: st.image(fo2)
    with t3:
        st.subheader("Replanteo")
        n1 = st.number_input("Norte Base", value=1700000.0)
        e1 = st.number_input("Este Base", value=800000.0)
        n2 = st.number_input("Norte Dest", value=1700100.0)
        e2 = st.number_input("Este Dest", value=800100.0)
        if st.button("Calcular Replanteo"):
            dn = n2-n1; de = e2-e1
            di = math.sqrt(dn*dn+de*de)
            az = math.degrees(math.atan2(de,dn))
            if az < 0: az += 360
            c1,c2 = st.columns(2)
            c1.metric("Dist", round(di,3)); c2.metric("Azimut", round(az,3))
    with t4:
        st.subheader("Nivelacion")
        va = st.number_input("Vista Atras", value=1.5)
        bm = st.number_input("Cota BM", value=10.0)
        vd = st.number_input("Vista Adel", value=1.2)
        if st.button("Calcular Nivel"):
            ai = bm+va; cn = ai-vd
            c1,c2,c3 = st.columns(3)
            c1.metric("Alt", round(ai,3)); c2.metric("Cota", round(cn,3)); c3.metric("Desn", round(cn-bm,3))
    with t5:
        st.subheader("Presupuesto")
        tp = st.selectbox("Tipo", ["Levantamiento","Replanteo","Dron","Nivelacion","Loteo"])
        ha = st.number_input("Ha", value=1.0)
        pr = st.number_input("Precio Ha", value=350000)
        tr2 = st.number_input("Transporte", value=80000)
        if st.button("Calcular Presup"):
            tot = ha*pr+tr2
            c1,c2 = st.columns(2)
            c1.metric("Sub", int(ha*pr)); c2.metric("TOTAL", int(tot))
    with t6:
        st.subheader("Bitacora")
        if "bit" not in st.session_state: st.session_state["bit"] = []
        with st.form("fbit", clear_on_submit=True):
            fb = st.date_input("Fecha", value=date.today())
            py = st.text_input("Proyecto")
            ac = st.selectbox("Actividad", ["Levantamiento","Replanteo","Dron","Nivelacion","Otro"])
            no = st.text_area("Notas")
            if st.form_submit_button("Guardar"):
                if py.strip() == "": st.warning("Escribe proyecto")
                else:
                    st.session_state["bit"].append({"Fecha":str(fb),"Proyecto":py,"Actividad":ac,"Notas":no})
                    st.success("Guardado")
        if len(st.session_state["bit"]) > 0: st.dataframe(pd.DataFrame(st.session_state["bit"]))
    with t7:
        st.subheader("Conversor")
        m2 = st.number_input("m2", value=10000.0)
        if st.button("A Ha"): st.write(m2/10000)
        dm = st.number_input("Metros", value=100.0)
        if st.button("A Km"): st.write(dm/1000)

        if modo == "DESPACHO":
    st.header("Despacho - Dra. Norma")
    if "cli" not in st.session_state: st.session_state["cli"] = []
    if "proc" not in st.session_state: st.session_state["proc"] = []
    if "fac" not in st.session_state: st.session_state["fac"] = []
    if "gas" not in st.session_state: st.session_state["gas"] = []
    vista = st.radio("Vista", ["Vista Doctora", "Vista Admin"], horizontal=True)
    if vista == "Vista Doctora":
        st.subheader("Inicio Doctora")
        cob = 0
        for f in st.session_state["fac"]:
            if f["Estado"] == "Por cobrar": cob += f["Valor"]
        c1,c2,c3 = st.columns(3)
        c1.metric("Clientes", len(st.session_state["cli"]))
        c2.metric("Procesos", len(st.session_state["proc"]))
        c3.metric("Por Cobrar", int(cob))
        d1,d2,d3,d4 = st.tabs(["Documento","Doc IA","Procesos","Plata"])
        with d1:
            cl = st.text_input("Cliente")
            td = st.selectbox("Tipo", ["Poder","Demanda","Tutela","Derecho de Peticion"])
            he = st.text_area("Hechos")
            if st.button("Generar Doc"):
                if cl.strip() == "": st.warning("Escribe cliente")
                else:
                    tx = hacer_doc(td, cl, he)
                    st.success("Listo")
                    st.text_area("Vista", tx, height=200)
                    st.download_button("Descargar", data=tx, file_name="Doc.txt")
        with d2:
            cl2 = st.text_input("Cliente IA")
            td2 = st.selectbox("Tipo IA", ["Poder","Demanda","Tutela","Derecho de Peticion"])
            he2 = st.text_area("Habla aqui")
            if st.button("Generar IA"):
                if cl2.strip() == "": st.warning("Escribe cliente")
                else:
                    tx2 = hacer_doc(td2, cl2, he2)
                    st.success("IA listo")
                    st.text_area("Doc IA", tx2, height=220)
                    st.download_button("Descargar IA", data=tx2, file_name="DocIA.txt")
        with d3:
            if len(st.session_state["proc"]) > 0: st.dataframe(pd.DataFrame(st.session_state["proc"]))
            else: st.info("Sin procesos")
        with d4:
            if len(st.session_state["fac"]) > 0: st.dataframe(pd.DataFrame(st.session_state["fac"]))
            else: st.info("Sin facturas")
    if vista == "Vista Admin":
        st.subheader("Admin - Solo Juan")
        a1,a2,a3,a4,a5,a6,a7,a8 = st.tabs(["Inicio","Clientes","Procesos","Docs","Facturacion","Caja","Red","Analisis"])
        with a1:
            cob = 0; pag = 0
            for f in st.session_state["fac"]:
                if f["Estado"] == "Por cobrar": cob += f["Valor"]
                if f["Estado"] == "Pagado": pag += f["Valor"]
            tg = 0
            for g in st.session_state["gas"]: tg += g["Valor"]
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Procesos", len(st.session_state["proc"]))
            c2.metric("Clientes", len(st.session_state["cli"]))
            c3.metric("Por Cobrar", int(cob))
            c4.metric("Caja", int(pag-tg))
            if len(st.session_state["proc"]) > 0: st.dataframe(pd.DataFrame(st.session_state["proc"]))
            else: st.info("Sin procesos")
        with a2:
            with st.form("fcli", clear_on_submit=True):
                nc = st.text_input("Nombre")
                cc = st.text_input("Celular")
                if st.form_submit_button("Guardar"):
                    if nc.strip() == "": st.warning("Escribe nombre")
                    else:
                        st.session_state["cli"].append({"Nombre":nc,"Celular":cc})
                        st.success("Guardado")
            if len(st.session_state["cli"]) > 0: st.dataframe(pd.DataFrame(st.session_state["cli"]))
        with a3:
            with st.form("fproc", clear_on_submit=True):
                cp = st.text_input("Cliente")
                tp = st.selectbox("Tipo", ["Tutela","Demanda Laboral","Nulidad","Divorcio","Otro"])
                vp = st.date_input("Vence", value=date.today())
                if st.form_submit_button("Guardar"):
                    if cp.strip() == "": st.warning("Escribe cliente")
                    else:
                        st.session_state["proc"].append({"Cliente":cp,"Tipo":tp,"Vence":str(vp)})
                        st.success("Guardado")
            if len(st.session_state["proc"]) > 0: st.dataframe(pd.DataFrame(st.session_state["proc"]))
        with a4:
            cd = st.text_input("Cliente doc")
            td3 = st.selectbox("Tipo doc", ["Poder","Demanda","Tutela","Derecho de Peticion"])
            hd = st.text_area("Hechos")
            if st.button("Generar Completo"):
                if cd.strip() == "": st.warning("Escribe cliente")
                else:
                    tx3 = hacer_doc(td3, cd, hd)
                    st.text_area("Doc", tx3, height=220)
                    st.download_button("Descargar", data=tx3, file_name="Doc.txt")
        with a5:
            with st.form("ffac", clear_on_submit=True):
                cf = st.text_input("Cliente")
                conf = st.text_input("Concepto")
                vf = st.number_input("Valor", value=500000)
                ef = st.selectbox("Estado", ["Por cobrar","Pagado"])
                if st.form_submit_button("Guardar"):
                    if cf.strip() == "": st.warning("Escribe cliente")
                    else:
                        st.session_state["fac"].append({"Cliente":cf,"Concepto":conf,"Valor":vf,"Estado":ef})
                        st.success("Guardada")
            if len(st.session_state["fac"]) > 0:
                st.dataframe(pd.DataFrame(st.session_state["fac"]))
                tc = 0; tp2 = 0
                for f in st.session_state["fac"]:
                    if f["Estado"] == "Por cobrar": tc += f["Valor"]
                    if f["Estado"] == "Pagado": tp2 += f["Valor"]
                f1,f2 = st.columns(2)
                f1.metric("Por Cobrar", int(tc)); f2.metric("Pagado", int(tp2))
            else: st.info("Sin facturas")
        with a6:
            with st.form("fgas", clear_on_submit=True):
                cg = st.text_input("Concepto")
                cat = st.selectbox("Categoria", ["Transporte","Papeleria","Arriendo","Servicios","Otro"])
                vg = st.number_input("Valor", value=50000)
                if st.form_submit_button("Guardar"):
                    if cg.strip() == "": st.warning("Escribe concepto")
                    else:
                       
