import streamlit as st
import pandas as pd
import math
import urllib.parse
import json

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

st.title("🚜 Central de Mistura Eric")

# --- SISTEMA DE CARREGAMENTO ---
with st.expander("💾 Salvar ou Carregar Receitas"):
    col_save, col_load = st.columns(2)
    with col_load:
        uploaded_file = st.file_uploader("Carregar arquivo de receita (.json)", type="json")
        loaded_data = json.load(uploaded_file) if uploaded_file else None

# --- CONFIGURAÇÕES NA LATERAL ---
with st.sidebar:
    st.header("📋 Operação")
    area = st.number_input("Área Total (ha)", value=loaded_data['area'] if loaded_data else 60.0)
    taxa = st.number_input("Taxa (L/ha)", value=12.0)
    tanque = st.number_input("Misturador (L)", value=200.0)
    
    st.header("🧪 Calda")
    n_prod = st.slider("Produtos", 1, 10, len(loaded_data['produtos']) if loaded_data else 5)
    
    escolhidos = []
    for i in range(n_prod):
        st.markdown(f"**Item {i+1}**")
        p_default = loaded_data['produtos'][i]['p_ref'] if loaded_data and i < len(loaded_data['produtos']) else "Bim Max"
        p_ref = st.selectbox(f"Produto", list(DB_PRODUTOS.keys()), index=list(DB_PRODUTOS.keys()).index(p_ref_val := p_default if p_default in DB_PRODUTOS else "Outro (Novo)"), key=f"sel_{i}")
        
        dados_p = DB_PRODUTOS[p_ref]
        nome = st.text_input("Nome", value=loaded_data['produtos'][i]['nome'] if loaded_data and i < len(loaded_data['produtos']) else p_ref, key=f"n_{i}")
        
        c1, c2 = st.columns(2)
        dose = c1.number_input("Dose", value=float(loaded_data['produtos'][i]['dose'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["dose"]), key=f"d_{i}")
        un = c2.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(loaded_data['produtos'][i]['un'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["un"]), key=f"u_{i}")
        
        form = st.selectbox("Tipo", list(ORDEM_TECNICA.keys()), index=list(ORDEM_TECNICA.keys()).index(loaded_data['produtos'][i]['form'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["form"]), key=f"f_{i}_{p_ref}")
        
        # LINK CORRIGIDO: Busca via Google focada no AgrolinkFito
        link_bula = f"https://www.google.com.br/search?q=site%3Aagrolink.com.br%2Fagrolinkfito+{nome.replace(' ', '+')}"
        
        escolhidos.append({"p_ref": p_ref, "nome": nome, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link_bula})

# --- BOTÃO DE SALVAR ---
with col_save:
    receita_atual = {"area": area, "taxa": taxa, "tanque": tanque, "produtos": escolhidos}
    json_receita = json.dumps(receita_atual, indent=4)
    st.download_button(label="📥 Baixar Receita Atual", data=json_receita, file_name="receita_calda.json", mime="application/json")

# --- CÁLCULOS ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

def preparar_zap(volume, tipo):
    ha = volume / taxa
    msg = f"*📋 PLANO {tipo}*\n💧 Água: {int(volume)}L\n---\n"
    for i, p in enumerate(ordenados):
        msg += f"{i+1}º - {p['nome']}: *{(p['dose']*ha):.2f} {p['un']}*\n"
    msg += f"\n⚠️ Mantenha a agitação ligada!"
    return f"https://wa.me/?text={urllib.parse.quote(msg)}"

st.subheader("📝 Guia de Preparo")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L"); c2.metric("Batidas Cheias", int(batidas)); c3.metric("Última Batida", f"{int(sobra)} L")

if batidas > 0:
    st.success(f"✅ **Batidas de {int(tanque)}L**")
    df = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(tanque/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df, column_config={"Bula": st.column_config.LinkColumn("Bula (Google/Fito)")}, hide_index=True)
    st.link_button("📲 Zap: Batida Cheia", preparar_zap(tanque, "BATIDA CHEIA"))

if sobra > 0:
    st.warning(f"⚠️ **Batida Final ({int(sobra)}L)**")
    df_s = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(sobra/taxa)):.2f} {p['un']}", "Bula": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df_s, column_config={"Bula": st.column_config.LinkColumn("Bula (Google/Fito)")}, hide_index=True)
    st.link_button("📲 Zap: Batida Final", preparar_zap(sobra, f"ÚLTIMA BATIDA ({int(sobra)}L)"))
