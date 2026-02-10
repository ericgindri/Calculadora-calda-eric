import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="App Agro Eric - Ordem Técnica", page_icon="🚜", layout="wide")

# --- BANCO DE DADOS TÉCNICO ATUALIZADO ---
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
    "PingBR (Ouro Fino)": {"dose": 1.0, "un": "L", "form": "EC (Emulsão)"}, # Atualizado: Inseticida EC
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

st.title("🚜 Central de Mistura Eric - Ordem de Bula")
st.markdown("---")

with st.sidebar:
    st.header("📋 Dados da Área")
    area = st.number_input("Área Total (ha)", value=60.0)
    taxa = st.number_input("Taxa (L/ha)", value=12.0)
    tanque = st.number_input("Misturador (L)", value=200.0)
    
    st.header("🧪 Configurar Calda")
    n_prod = st.slider("Produtos na mistura", 1, 10, 5)
    
    escolhidos = []
    for i in range(n_prod):
        st.markdown(f"**Item {i+1}**")
        p_ref = st.selectbox(f"Selecione o Produto", list(DB_PRODUTOS.keys()), key=f"sel_{i}")
        
        dados_prod = DB_PRODUTOS[p_ref]
        nome_final = p_ref
        
        if p_ref == "Outro (Novo)":
            nome_final = st.text_input("Nome do produto", key=f"nome_{i}")
        
        col1, col2 = st.columns(2)
        with col1:
            dose = st.number_input("Dose/ha", value=float(dados_prod["dose"]), key=f"d_{i}", format="%.3f")
        with col2:
            un = st.selectbox("Unid.", ["L", "ml", "g", "kg"], 
                              index=["L", "ml", "g", "kg"].index(dados_prod["un"]), key=f"u_{i}")
        
        # Lógica de reset da formulação automática
        form_idx = list(ORDEM_TECNICA.keys()).index(dados_prod["form"])
        form_final = st.selectbox("Formulação", list(ORDEM_TECNICA.keys()), 
                                  index=form_idx, key=f"form_{i}_{p_ref}")
        
        escolhidos.append({
            "nome": nome_final, "dose": dose, "un": un, 
            "form": form_final, "peso": ORDEM_TECNICA[form_final]
        })

# --- PROCESSAMENTO ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

def gera_tab(v):
    h = v / taxa
    return pd.DataFrame([{
        "Ordem": pos+1, "Produto": p['nome'], "Tipo (Bula)": p['form'], "Qtd/Batida": f"{(p['dose']*h):.2f} {p['un']}"
    } for pos, p in enumerate(ordenados)])

# --- VISUALIZAÇÃO ---
st.subheader("📝 Guia de Preparo da Calda")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L")
c2.metric("Batidas de 200L", int(batidas))
c3.metric("Batida Final", f"{int(sobra)} L")

if batidas > 0:
    st.success(f"✅ **Ordem para as {int(batidas)} batidas de {int(tanque)}L:**")
    st.table(gera_tab(tanque))

if sobra > 0:
    st.warning(f"⚠️ **Ordem para a última batida de {int(sobra)}L:**")
    st.table(gera_tab(sobra))

st.info("💡 Nota: O PingBR foi atualizado como inseticida EC, entrando após as suspensões na mistura.")
