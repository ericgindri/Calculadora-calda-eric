import streamlit as st
import pandas as pd
import math
import urllib.parse
import json
from fpdf import FPDF

st.set_page_config(page_title="Eric Agro - Central de Mistura", page_icon="🚜", layout="wide")

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

# --- FUNÇÃO GERADORA DE PDF ---
def exportar_pdf(nome_fazenda, area, taxa, tanque, batidas, sobra, produtos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, f"PLANO DE MISTURA - {nome_fazenda.upper()}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 8, f"Responsável: Eric | Área: {area} ha | Taxa: {taxa} L/ha", ln=True)
    pdf.cell(190, 8, f"Misturador: {tanque} L | Calda Total: {area*taxa} L", ln=True)
    pdf.ln(10)
    if batidas > 0:
        pdf.set_font("Arial", "B", 12); pdf.cell(190, 10, f"BATIDA DE {tanque}L", ln=True); pdf.set_font("Arial", "", 10)
        for i, p in enumerate(produtos):
            qtd = (p['dose'] * (tanque/taxa))
            pdf.cell(190, 7, f"{i+1}. {p['nome']} ({p['form']}): {qtd:.2f} {p['un']}", ln=True)
        pdf.ln(10)
    if sobra > 0:
        pdf.set_font("Arial", "B", 12); pdf.cell(190, 10, f"ULTIMA BATIDA ({int(sobra)}L)", ln=True); pdf.set_font("Arial", "", 10)
        for i, p in enumerate(produtos):
            qtd = (p['dose'] * (sobra/taxa))
            pdf.cell(190, 7, f"{i+1}. {p['nome']} ({p['form']}): {qtd:.2f} {p['un']}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

st.title("🚜 Central de Mistura Eric")

# --- SALVAR/CARREGAR ---
with st.expander("💾 Salvar ou Carregar Receitas"):
    col_save, col_load = st.columns(2)
    with col_load:
        uploaded_file = st.file_uploader("Carregar JSON", type="json")
        loaded_data = json.load(uploaded_file) if uploaded_file else None

with st.sidebar:
    st.header("📋 Identificação")
    fazenda = st.text_input("Fazenda / Talhão", value="Geral")
    st.header("📋 Operação")
    area = st.number_input("Área Total (ha)", value=loaded_data['area'] if loaded_data else 60.0)
    taxa = st.number_input("Taxa (L/ha)", value=loaded_data['taxa'] if loaded_data else 12.0)
    tanque = st.number_input("Misturador (L)", value=loaded_data['tanque'] if loaded_data else 200.0)
    st.header("🧪 Calda")
    n_prod = st.slider("Produtos", 1, 10, len(loaded_data['produtos']) if loaded_data else 5)
    escolhidos = []
    for i in range(n_prod):
        p_def = loaded_data['produtos'][i]['p_ref'] if loaded_data and i < len(loaded_data['produtos']) else "Bim Max"
        p_ref = st.selectbox(f"Produto {i+1}", list(DB_PRODUTOS.keys()), index=list(DB_PRODUTOS.keys()).index(p_ref if (p_ref := p_def) in DB_PRODUTOS else "Outro (Novo)"), key=f"sel_{i}")
        dados_p = DB_PRODUTOS[p_ref]
        nome = st.text_input("Nome", value=loaded_data['produtos'][i]['nome'] if loaded_data and i < len(loaded_data['produtos']) else p_ref, key=f"n_{i}")
        col1, col2 = st.columns(2)
        dose = col1.number_input("Dose", value=float(loaded_data['produtos'][i]['dose'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["dose"]), key=f"d_{i}")
        un = col2.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(loaded_data['produtos'][i]['un'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["un"]), key=f"u_{i}")
        form = st.selectbox("Tipo", list(ORDEM_TECNICA.keys()), index=list(ORDEM_TECNICA.keys()).index(loaded_data['produtos'][i]['form'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["form"]), key=f"f_{i}_{p_ref}")
        link = f"https://www.google.com.br/search?q=site%3Aagrolink.com.br%2Fagrolinkfito+{nome.replace(' ', '+')}"
        escolhidos.append({"p_ref": p_ref, "nome": nome, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link})

# --- PROCESSAMENTO ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

# Botão PDF
st.sidebar.markdown("---")
if st.sidebar.download_button("📄 Baixar Plano em PDF", exportar_pdf(fazenda, area, taxa, tanque, batidas, sobra, ordenados), f"Plano_{fazenda}.pdf", "application/pdf"):
    st.sidebar.success("PDF Pronto!")

# Botão Salvar JSON
with col_save:
    json_data = json.dumps({"area": area, "taxa": taxa, "tanque": tanque, "produtos": escolhidos}, indent=4)
    st.download_button("📥 Salvar Receita (JSON)", json_data, "receita.json", "application/json")

def preparar_zap(volume, tipo):
    ha = volume / taxa
    msg = f"*📋 PLANO {tipo} - {fazenda.upper()}*\n💧 Água: {int(volume)}L\n---\n"
    for i, p in enumerate(ordenados):
        msg += f"{i+1}º - {p['nome']}: *{(p['dose']*ha):.2f} {p['un']}*\n"
    return f"https://wa.me/?text={urllib.parse.quote(msg)}"

# --- VISUALIZAÇÃO ---
st.subheader(f"📝 Guia de Preparo: {fazenda}")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L"); c2.metric("Batidas Cheias", int(batidas)); c3.metric("Última Batida", f"{int(sobra)} L")

if batidas > 0:
    st.success(f"✅ **Batidas de {int(tanque)}L**")
    df = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(tanque/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df, column_config={"Bula": st.column_config.LinkColumn("Bula (Google)")}, hide_index=True)
    st.link_button("📲 Zap: Batida Cheia", preparar_zap(tanque, "BATIDA CHEIA"))

if sobra > 0:
    st.warning(f"⚠️ **Batida Final ({int(sobra)}L)**")
    df_s = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(sobra/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df_s, column_config={"Bula": st.column_config.LinkColumn("Bula (Google)")}, hide_index=True)
    st.link_button("📲 Zap: Batida Final", preparar_zap(sobra, "ÚLTIMA BATIDA"))
