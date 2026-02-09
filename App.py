import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Eric Agro - Ordem de Bula", page_icon="🚜", layout="wide")

# --- BANCO DE DATOS TÉCNICO (Bula Oficial) ---
DB_PRODUTOS = {
    "Bim Max": {"dose": 1.2, "un": "L", "form": "SC / FS (Suspensão)"},
    "Aproach Power": {"dose": 0.6, "un": "L", "form": "SC / FS (Suspensão)"},
    "Shenzi": {"dose": 80.0, "un": "ml", "form": "SC / FS (Suspensão)"},
    "Fulltec Max": {"dose": 50.0, "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Nutrol Max": {"dose": 150.0, "un": "ml", "form": "Condicionador (Adjuvante)"},
    "Engeo Pleno S": {"dose": 200.0, "un": "ml", "form": "ZC (Suspensão Encapsulada)"},
    "Fox Xpro": {"dose": 0.5, "un": "L", "form": "SC / FS (Suspensão)"},
    "Priori Xtra": {"dose": 0.3, "un": "L", "form": "SC / FS (Suspensão)"},
    "Elatus": {"dose": 200.0, "un": "g", "form": "WG / DF (Grânulos)"},
    "Kifix": {"dose": 140.0, "un": "g", "form": "WG / DF (Grânulos)"},
    "Roundup WG": {"dose": 1.0, "un": "kg", "form": "WG / DF (Grânulos)"},
    "Select": {"dose": 0.4, "un": "L", "form": "EC (Emulsão)"},
    "Nominee": {"dose": 150.0, "un": "ml", "form": "SC / FS (Suspensão)"},
    "Outro (Novo)": {"dose": 0.0, "un": "L", "form": "SL (Líquido Solúvel)"}
}

# Hierarquia técnica de mistura (Baseada em normas globais)
ORDEM_TECNICA = {
    "Condicionador (Adjuvante)": 1,
    "WG / DF (Grânulos)": 2,
    "WP (Pó Molhável)": 3,
    "SC / FS (Suspensão)": 4,
    "ZC (Suspensão Encapsulada)": 4, # Mesma prioridade do SC
    "EC (Emulsão)": 5,
    "SL (Líquido Solúvel)": 6
}

st.title("🚜 Sistema de Mistura Técnica - Eric")
st.markdown("---")

with st.sidebar:
    st.header("📋 Operação")
    area = st.number_input("Área Total (ha)", value=60.0)
    taxa = st.number_input("Taxa (L/ha)", value=12.0)
    tanque = st.number_input("Misturador (L)", value=200.0)
    
    st.header("🧪 Calda")
    n_prod = st.slider("Produtos na mistura", 1, 10, 5)
    
    escolhidos = []
    for i in range(n_prod):
        st.markdown(f"**Produto {i+1}**")
        p_ref = st.selectbox(f"Nome", list(DB_PRODUTOS.keys()), key=f"s{i}")
        
        # Lógica de preenchimento automático
        if p_ref == "Outro (Novo)":
            nome = st.text_input("Nome Real", "Ex: Glifosato", key=f"t{i}")
            # Tenta adivinhar a formulação pelo nome
            sugestao = "SL (Líquido Solúvel)"
            if "WG" in nome.upper(): sugestao = "WG / DF (Grânulos)"
            elif "SC" in nome.upper(): sugestao = "SC / FS (Suspensão)"
            elif "EC" in nome.upper(): sugestao = "EC (Emulsão)"
            
            form = st.selectbox("Formulação (Bula)", list(ORDEM_TECNICA.keys()), 
                                index=list(ORDEM_TECNICA.keys()).index(sugestao), key=f"f{i}")
            d_padrao, u_padrao = 0.0, "L"
        else:
            nome = p_ref
            form = DB_PRODUTOS[p_ref]["form"]
            d_padrao = DB_PRODUTOS[p_ref]["dose"]
            u_padrao = DB_PRODUTOS[p_ref]["un"]

        col1, col2 = st.columns(2)
        with col1:
            dose = st.number_input("Dose/ha", value=d_padrao, key=f"d{i}", format="%.3f")
        with col2:
            un = st.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(u_padrao), key=f"u{i}")
        
        # Exibe a formulação (pode ser alterada se necessário)
        f_final = st.selectbox("Formulação", list(ORDEM_TECNICA.keys()), 
                               index=list(ORDEM_TECNICA.keys()).index(form), key=f"ff{i}")
        
        escolhidos.append({"nome": nome, "dose": dose, "un": un, "form": f_final, "peso": ORDEM_TECNICA[f_final]})

# --- PROCESSAMENTO ---
vol_total = area * taxa
batidas_cheias = math.floor(vol_total / tanque)
sobra = vol_total % tanque

# ORDENAÇÃO POR BULA (O pulo do gato)
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

def mostrar_tabela(volume):
    ha = volume / taxa
    dados = []
    for pos, p in enumerate(ordenados):
        qtd = p['dose'] * ha
        dados.append({"#": pos+1, "Produto": p['nome'], "Bula (Tipo)": p['form'], "Qtd": f"{qtd:.2f} {p['un']}"})
    return pd.DataFrame(dados)

# --- TELA PRINCIPAL ---
st.subheader("📝 Guia de Preparo")
c1, c2, c3 = st.columns(3)
c1.metric("Volume de Calda", f"{vol_total} L")
c2.metric("Batidas de {int(tanque)}L", int(batidas_cheias))
c3.metric("Batida de Encerramento", f"{int(sobra)} L")

if batidas_cheias > 0:
    st.success(f"✅ **ORDEM DE MISTURA ({int(batidas_cheias)}x)**")
    st.table(mostrar_tabela(tanque))

if sobra > 0:
    st.warning(f"⚠️ **ORDEM DA ÚLTIMA BATIDA ({int(sobra)}L)**")
    st.table(mostrar_tabela(sobra))

st.info("💡 A ordem acima respeita a sequência técnica: Condicionadores > Grânulos > Suspensões > Emulsões > Líquidos.")
