import streamlit as st
import pandas as pd
import math
import urllib.parse
import json
from fpdf import FPDF

st.set_page_config(page_title="Eric Agro - Sistema Final", page_icon="🚜", layout="wide")

# --- BANCO DE DADOS TÉCNICO ---
DB_PRODUTOS = {
    "Bim Max": {"dose": 1.2, "un": "L", "form": "SC / FS (Suspensão)"},
    "Aproach Power": {"dose": 0.6, "un": "L", "form": "SC / FS (Suspensão)"},
    "Shenzi": {"dose": 0.08, "un": "L", "form": "SC / FS (Suspensão)"},
    "Fulltec Max": {"dose": 50.0, "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Nutrol Max": {"dose": 150.0, "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Engeo Pleno S": {"dose": 200.0, "un": "ml", "form": "ZC (Suspensão Encapsulada)"},
    "Unanime": {"dose": 1.0, "un": "L", "form": "SL (Líquido Solúvel)"},
    "WG (Grânulos)": {"dose": 0.2, "un": "kg", "form": "WG / DF (Grânulos)"},
    "Crucial": {"dose": 3.0, "un": "L", "form": "SL (Líquido Solúvel)"},
    "Expedition": {"dose": 0.15, "un": "L", "form": "SC / FS (Suspensão)"},
    "PingBR (Ouro Fino)": {"dose": 1.0, "un": "L", "form": "EC (Emulsão)"},
    "Joint Ultra": {"dose": 0.5, "un": "L", "form": "SC / FS (Suspensão)"},
    "Evolution": {"dose": 2.0, "un": "kg", "form": "WG / DF (Grânulos)"},
    "Blindado (Adama)": {"dose": 0.8, "un": "L", "form": "EC (Emulsão)"},
    "Fox Xpro": {"dose": 0.5, "un": "L", "form": "SC / FS (Suspensão)"},
    "Kifix": {"dose": 140.0, "un": "g", "form": "WG / DF (Grânulos)"},
    "Select": {"dose": 0.4, "un": "L", "form": "EC (Emulsão)"},
    "Outro (Novo)": {"dose": 0.0, "un": "L", "form": "SL (Líquido Solúvel)"}
}

ORDEM_TECNICA = {
    "Condicionador (Adjuvante)": 1, "WG / DF (Grânulos)": 2, "WP (Pó Molhável)": 3,
    "SC / FS (Suspensão)": 4, "ZC (Suspensão Encapsulada)": 4, "EC (Emulsão)": 5, "SL (Líquido Solúvel)": 6
}

# --- GERADOR DE PDF ---
def exportar_pdf(fazenda, area, taxa, tanque, batidas, sobra, produtos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(190, 10, f"PLANO DE MISTURA - {fazenda.upper()}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(190, 8, f"Area: {area} ha | Taxa: {taxa} L/ha | Misturador: {tanque} L", ln=True)
    pdf.ln(10)
    
    if batidas > 0:
        pdf.set_font("helvetica", "B", 12); pdf.cell(190, 10, f"BATIDAS DE {tanque}L", ln=True); pdf.set_font("helvetica", "", 10)
        for i, p in enumerate(produtos):
            qtd = (p['dose'] * (tanque/taxa))
            pdf.cell(190, 7, f"{i+1}. {p['nome']} ({p['form']}): {qtd:.2f} {p['un']}", ln=True)
        pdf.ln(10)
    
    if sobra > 0:
        pdf.set_font("helvetica", "B", 12); pdf.cell(190, 10, f"ULTIMA BATIDA ({int(sobra)}L)", ln=True); pdf.set_font("helvetica", "", 10)
        for i, p in enumerate(produtos):
            qtd = (p['dose'] * (sobra/taxa))
            pdf.cell(190, 7, f"{i+1}. {p['nome']} ({p['form']}): {qtd:.2f} {p['un']}", ln=True)
    return pdf.output()

st.title("🚜 Central de Mistura Wesley")

# --- INTERFACE ---
with st.sidebar:
    st.header("📋 Operação")
    fazenda = st.text_input("Fazenda / Talhão", "Geral")
    area = st.number_input("Área Total (ha)", 60.0)
    taxa = st.number_input("Taxa (L/ha)", 12.0)
    tanque = st.number_input("Misturador (L)", 200.0)
    n_prod = st.slider("Produtos", 1, 10, 5)
    
    escolhidos = []
    for i in range(n_prod):
        p_ref = st.selectbox(f"Produto {i+1}", list(DB_PRODUTOS.keys()), key=f"s_{i}")
        dados = DB_PRODUTOS[p_ref]
        nome = st.text_input("Nome", p_ref, key=f"n_{i}")
        c1, c2 = st.columns(2)
        dose = c1.number_input("Dose", float(dados["dose"]), key=f"d_{i}")
        un = c2.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(dados["un"]), key=f"u_{i}")
        form = st.selectbox("Tipo", list(ORDEM_TECNICA.keys()), index=list(ORDEM_TECNICA.keys()).index(dados["form"]), key=f"f_{i}_{p_ref}")
        
        # LINK CORRIGIDO PARA EVITAR ERRO 404
        link = f"https://www.google.com.br/search?q=site%3Aagrolink.com.br%2Fagrolinkfito+{nome.replace(' ', '+')}"
        escolhidos.append({"nome": nome, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link})

# --- CÁLCULOS ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

# Botão PDF
st.sidebar.markdown("---")
pdf_data = exportar_pdf(fazenda, area, taxa, tanque, batidas, sobra, ordenados)
st.sidebar.download_button("📄 Baixar Plano em PDF", pdf_data, f"Plano_{fazenda}.pdf", "application/pdf")

# --- TABELAS ---
st.subheader(f"📝 Plano para {fazenda}")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L"); c2.metric("Batidas Cheias", int(batidas)); c3.metric("Última Batida", f"{int(sobra)} L")

if batidas > 0:
    st.success(f"✅ **Batidas de {int(tanque)}L**")
    df = pd.DataFrame([{"#": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(tanque/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df, column_config={"Bula": st.column_config.LinkColumn("Bula (Google)")}, hide_index=True)

if sobra > 0:
    st.warning(f"⚠️ **Última Batida ({int(sobra)}L)**")
    df_s = pd.DataFrame([{"#": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(sobra/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df_s, column_config={"Bula": st.column_config.LinkColumn("Bula (Google)")}, hide_index=True)
