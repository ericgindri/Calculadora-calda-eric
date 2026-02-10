import streamlit as st
import pandas as pd
import math
import urllib.parse

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
    "Condicionador (Adjuvante)": 1,
    "WG / DF (Grânulos)": 2,
    "WP (Pó Molhável)": 3,
    "SC / FS (Suspensão)": 4,
    "ZC (Suspensão Encapsulada)": 4,
    "EC (Emulsão)": 5,
    "SL (Líquido Solúvel)": 6
}

st.title("🚜 Central de Mistura Eric - WhatsApp Integrado")
st.markdown("---")

with st.sidebar:
    st.header("📋 Operação")
    area = st.number_input("Área Total (ha)", value=60.0)
    taxa = st.number_input("Taxa (L/ha)", value=12.0)
    tanque = st.number_input("Misturador (L)", value=200.0)
    st.header("🧪 Calda")
    n_prod = st.slider("Produtos", 1, 10, 5)
    
    escolhidos = []
    for i in range(n_prod):
        p_ref = st.selectbox(f"Produto {i+1}", list(DB_PRODUTOS.keys()), key=f"sel_{i}")
        dados_p = DB_PRODUTOS[p_ref]
        nome = p_ref if p_ref != "Outro (Novo)" else st.text_input("Nome", key=f"n_{i}")
        
        c1, c2 = st.columns(2)
        dose = c1.number_input("Dose", value=float(dados_p["dose"]), key=f"d_{i}")
        un = c2.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(dados_p["un"]), key=f"u_{i}")
        
        form = st.selectbox("Tipo", list(ORDEM_TECNICA.keys()), 
                            index=list(ORDEM_TECNICA.keys()).index(dados_p["form"]), key=f"f_{i}_{p_ref}")
        
        link = f"https://www.agrolink.com.br/agrolinkfito/busca.aspx?q={nome.replace(' ', '+')}"
        escolhidos.append({"nome": nome, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link})

# --- PROCESSAMENTO ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

def preparar_zap(volume, tipo_batida):
    ha = volume / taxa
    msg = f"*📋 PLANO DE MISTURA - ERIC*\n"
    msg += f"📍 *{tipo_batida}*\n"
    msg += f"💧 Volume de Água: {int(volume)} Litros\n"
    msg += f"----------------------------\n"
    for i, p in enumerate(ordenados):
        msg += f"{i+1}º - {p['nome']}: *{(p['dose']*ha):.2f} {p['un']}*\n"
    msg += f"----------------------------\n"
    msg += "⚠️ Mantenha a agitação ligada!"
    return f"https://wa.me/?text={urllib.parse.quote(msg)}"

# --- EXIBIÇÃO ---
st.subheader("📝 Guia de Preparo")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L")
c2.metric("Batidas Cheias", int(batidas))
c3.metric("Última Batida", f"{int(sobra)} L")

if batidas > 0:
    st.success(f"✅ **Batidas de {int(tanque)}L**")
    df = pd.DataFrame([{"#": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(tanque/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df, column_config={"Bula": st.column_config.LinkColumn("Bula")}, hide_index=True)
    st.link_button("📲 Enviar Batida Cheia via WhatsApp", preparar_zap(tanque, f"BATIDA DE {int(tanque)}L"))

if sobra > 0:
    st.warning(f"⚠️ **Batida Final ({int(sobra)}L)**")
    df_s = pd.DataFrame([{"#": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(sobra/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df_s, column_config={"Bula": st.column_config.LinkColumn("Bula")}, hide_index=True)
    st.link_button("📲 Enviar Batida Final via WhatsApp", preparar_zap(sobra, f"ÚLTIMA BATIDA ({int(sobra)}L)"))
