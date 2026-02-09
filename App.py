import streamlit as st
import pandas as pd
import math
import urllib.parse

st.set_page_config(page_title="Eric AgroInteligente", page_icon="🚜", layout="wide")

# --- BANCO DE DADOS EXPANDIDO (Mais de 15 produtos comuns) ---
DB_PRODUTOS = {
    "Bim Max": {"dose": 1.2, "un": "L", "form": "SC / FS (Suspensão)"},
    "Aproach Power": {"dose": 0.6, "un": "L", "form": "SC / FS (Suspensão)"},
    "Shenzi": {"dose": 80.0, "un": "ml", "form": "SC / FS (Suspensão)"},
    "Fulltec Max": {"dose": 50.0, "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Nutrol Max": {"dose": 150.0, "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Engeo Pleno S": {"dose": 200.0, "un": "ml", "form": "SC / FS (Suspensão)"},
    "Fox Xpro": {"dose": 0.5, "un": "L", "form": "SC / FS (Suspensão)"},
    "Priori Xtra": {"dose": 0.3, "un": "L", "form": "SC / FS (Suspensão)"},
    "Elatus": {"dose": 200.0, "un": "g", "form": "WG / DF (Grânulos)"},
    "Standak Top": {"dose": 100.0, "un": "ml", "form": "SC / FS (Suspensão)"},
    "Nominee": {"dose": 150.0, "un": "ml", "form": "SC / FS (Suspensão)"},
    "Kifix": {"dose": 140.0, "un": "g", "form": "WG / DF (Grânulos)"},
    "Roundup WG": {"dose": 1.0, "un": "kg", "form": "WG / DF (Grânulos)"},
    "Select": {"dose": 0.4, "un": "L", "form": "EC (Emulsão)"},
    "Outro (Novo)": {"dose": 0.0, "un": "L", "form": "SL (Líquido Solúvel)"}
}

ORDEM_TECNICA = {
    "Condicionador (Adjuvante)": 1,
    "WG / DF (Grânulos)": 2,
    "WP (Pó Molhável)": 3,
    "SC / FS (Suspensão)": 4,
    "EC (Emulsão)": 5,
    "SL (Líquido Solúvel)": 6
}

st.title("🚜 Central de Mistura Inteligente do Eric")
st.markdown("---")

with st.sidebar:
    st.header("📋 Dados da Operação")
    area_total = st.number_input("Área Total (ha)", value=60.0)
    taxa_aplicacao = st.number_input("Taxa (L/ha)", value=12.0)
    misturador_cap = st.number_input("Misturador (L)", value=200.0)
    
    st.header("🧪 Defensivos")
    num_produtos = st.slider("Quantidade de produtos", 1, 10, 5)
    
    lista_escolhida = []
    for i in range(num_produtos):
        st.markdown(f"**Item {i+1}**")
        p_nome = st.selectbox(f"Selecione o produto", list(DB_PRODUTOS.keys()), key=f"sel{i}")
        
        if p_nome == "Outro (Novo)":
            nome_real = st.text_input("Nome do Produto", "Digite aqui", key=f"txt{i}")
            # Botão de busca automática
            query = urllib.parse.quote(f"bula {nome_real} dose recomendada bula pdf")
            st.markdown(f"[🔍 Buscar Bula no Google](https://www.google.com/search?q={query})")
            dados = DB_PRODUTOS["Outro (Novo)"]
        else:
            nome_real = p_nome
            dados = DB_PRODUTOS[p_nome]

        c1, c2 = st.columns(2)
        with c1:
            dose = st.number_input("Dose/ha", value=dados["dose"], key=f"d{i}", format="%.3f")
        with c2:
            un = st.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(dados["un"]), key=f"u{i}")
        
        form = st.selectbox("Formulação", list(ORDEM_TECNICA.keys()), 
                            index=list(ORDEM_TECNICA.keys()).index(dados["form"]), key=f"f{i}")
        
        lista_escolhida.append({"nome": nome_real, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form]})

# --- CÁLCULOS E EXIBIÇÃO ---
vol_total = area_total * taxa_aplicacao
num_batidas = math.floor(vol_total / misturador_cap)
sobra = vol_total % misturador_cap

produtos_ordenados = sorted(lista_escolhida, key=lambda x: x['peso'])

def tabela(volume):
    ha = volume / taxa_aplicacao
    res = []
    for pos, p in enumerate(produtos_ordenados):
        qtd = p['dose'] * ha
        res.append({"#": pos+1, "Produto": p['nome'], "Formul.": p['form'], "Qtd": f"{qtd:.2f} {p['un']}"})
    return pd.DataFrame(res)

st.subheader("📝 Plano de Trabalho")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Calda Total", f"{vol_total} L")
col_b.metric(f"Batidas de {int(misturador_cap)}L", int(num_batidas))
col_c.metric("Batida de Encerramento", f"{int(sobra)} L")

if num_batidas > 0:
    st.success(f"✅ **Siga esta ordem para as {int(num_batidas)} batidas cheias:**")
    st.table(tabela(misturador_cap))

if sobra > 0:
    st.warning(f"⚠️ **Siga esta ordem para a última batida ({int(sobra)}L):**")
    st.table(tabela(sobra))

st.info("💡 Se o produto for novo, use o link de busca na lateral para conferir a dose na bula oficial.")
