import streamlit as st
import pandas as pd
import math
import urllib.parse
import json

st.set_page_config(page_title="Central de Mistura Eric", page_icon="🚜", layout="wide")

# --- BANCO DE DADOS TÉCNICO (Doses Oficiais de Bula) ---
DB_PRODUTOS = {
    "Bim Max": {"dose_bula": "1,0 a 1,2 L/ha", "un": "L", "form": "SC / FS (Suspensão)"},
    "Aproach Power": {"dose_bula": "0,4 a 0,6 L/ha", "un": "L", "form": "SC / FS (Suspensão)"},
    "Shenzi": {"dose_bula": "80 a 100 ml/ha", "un": "ml", "form": "SC / FS (Suspensão)"},
    "Fulltec Max": {"dose_bula": "50 ml/ha", "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Nutrol Max": {"dose_bula": "100 a 200 ml/ha", "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Engeo Pleno S": {"dose_bula": "150 a 250 ml/ha", "un": "ml", "form": "ZC (Suspensão Encapsulada)"},
    "Unanime": {"dose_bula": "0,75 a 1,5 L/ha", "un": "L", "form": "SL (Líquido Solúvel)"},
    "Crucial": {"dose_bula": "2,0 a 4,0 L/ha", "un": "L", "form": "SL (Líquido Solúvel)"},
    "Expedition": {"dose_bula": "150 a 300 ml/ha", "un": "ml", "form": "SC / FS (Suspensão)"},
    "PingBR (Ouro Fino)": {"dose_bula": "0,75 a 1,5 L/ha", "un": "L", "form": "EC (Emulsão)"},
    "Joint Ultra": {"dose_bula": "0,4 a 0,6 L/ha", "un": "L", "form": "SC / FS (Suspensão)"},
    "Evolution": {"dose_bula": "1,5 a 2,5 kg/ha", "un": "kg", "form": "WG / DF (Grânulos)"},
    "Blindado (Adama)": {"dose_bula": "0,5 a 1,0 L/ha", "un": "L", "form": "EC (Emulsão)"},
    "Fox Xpro": {"dose_bula": "0,4 a 0,5 L/ha", "un": "L", "form": "SC / FS (Suspensão)"},
    "Kifix": {"dose_bula": "140 g/ha", "un": "g", "form": "WG / DF (Grânulos)"},
    "Select": {"dose_bula": "0,4 a 0,5 L/ha", "un": "L", "form": "EC (Emulsão)"},
    "Outro (Novo)": {"dose_bula": "Consulte a Bula", "un": "L", "form": "SL (Líquido Solúvel)"}
}

ORDEM_TECNICA = {
    "Condicionador (Adjuvante)": 1, "WG / DF (Grânulos)": 2, "WP (Pó Molhável)": 3,
    "SC / FS (Suspensão)": 4, "ZC (Suspensão Encapsulada)": 4, "EC (Emulsão)": 5, "SL (Líquido Solúvel)": 6
}

st.title("🚜 Central de Mistura Eric")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Operação")
    fazenda = st.text_input("Fazenda / Talhão", value="Geral")
    area = st.number_input("Área Total (ha)", value=60.0)
    taxa = st.number_input("Taxa (L/ha)", value=12.0)
    tanque = st.number_input("Misturador (L)", value=200.0)
    
    st.header("🧪 Calda")
    n_prod = st.slider("Produtos", 1, 10, 5)
    
    escolhidos = []
    for i in range(n_prod):
        st.markdown(f"---")
        p_ref = st.selectbox(f"Produto {i+1}", list(DB_PRODUTOS.keys()), key=f"sel_{i}")
        dados_p = DB_PRODUTOS[p_ref]
        
        # CAMPO NOVO: Exibe a dose recomendada seguindo a bula
        st.info(f"📖 **Bula:** {dados_p['dose_bula']}")
        
        nome = st.text_input("Nome", value=p_ref, key=f"n_{i}") if p_ref == "Outro (Novo)" else p_ref
        
        c1, col_v = st.columns([1,1])
        # Aqui você insere a dose que VAI usar no dia
        minha_dose = c1.number_input("Sua Dose/ha", value=0.0, key=f"d_{i}", format="%.3f")
        
        c_un, c_tipo = st.columns(2)
        un = c_un.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(dados_p["un"]), key=f"u_{i}")
        form = c_tipo.selectbox("Tipo", list(ORDEM_TECNICA.keys()), index=list(ORDEM_TECNICA.keys()).index(dados_p["form"]), key=f"f_{i}_{p_ref}")
        
        # Link mantido conforme solicitado
        link = f"https://www.google.com.br/search?q=site%3Aagrolink.com.br%2Fagrolinkfito+{nome.replace(' ', '+')}"
        escolhidos.append({"nome": nome, "dose": minha_dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link, "bula_info": dados_p['dose_bula']})

# --- PROCESSAMENTO ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

# --- EXIBIÇÃO ---
st.subheader(f"📝 Plano de Mistura: {fazenda}")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L"); c2.metric("Batidas Cheias", int(batidas)); c3.metric("Última Batida", f"{int(sobra)} L")

if batidas > 0:
    st.success(f"✅ **Batidas de {int(tanque)}L**")
    df = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(tanque/taxa)):.2f} {p['un']}", "Ref. Bula": p['bula_info'], "Link": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df, column_config={"Link": st.column_config.LinkColumn("Bula (Google)")}, hide_index=True)

if sobra > 0:
    st.warning(f"⚠️ **Última Batida ({int(sobra)}L)**")
    df_s = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Qtd": f"{(p['dose']*(sobra/taxa)):.2f} {p['un']}", "Ref. Bula": p['bula_info'], "Link": p['bula']} for i, p in enumerate(ordenados)])
    st.dataframe(df_s, column_config={"Link": st.column_config.LinkColumn("Bula (Google)")}, hide_index=True)
