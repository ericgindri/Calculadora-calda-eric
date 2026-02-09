import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Calculadora Eric - Ordem Técnica", page_icon="🚜")

st.title("🚜 Mistura Inteligente do Eric")
st.markdown("---")

# --- DICIONÁRIO DE PESOS PARA ORDEM DE MISTURA ---
ordem_tecnica = {
    "Condicionador (Adjuvante)": 1,
    "WG / DF (Grânulos)": 2,
    "WP (Pó Molhável)": 3,
    "SC / FS (Suspensão)": 4,
    "EC (Emulsão)": 5,
    "SL (Líquido Solúvel)": 6
}

# --- CONFIGURAÇÕES NA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    area_total = st.number_input("Área Total (ha)", value=60.0)
    taxa_aplicacao = st.number_input("Taxa de Aplicação (L/ha)", value=12.0)
    misturador_cap = st.number_input("Capacidade do Misturador (L)", value=200.0)
    
    st.header("🧪 Produtos")
    num_produtos = st.slider("Quantos produtos?", 1, 8, 5)
    
    lista_produtos = []
    for i in range(num_produtos):
        st.markdown(f"**Produto {i+1}**")
        nome = st.text_input("Nome", f"Prod {i+1}", key=f"n{i}")
        col1, col2 = st.columns(2)
        with col1:
            dose = st.number_input("Dose/ha", key=f"d{i}", value=1.0, format="%.3f")
        with col2:
            un = st.selectbox("Unid.", ["L", "ml"], key=f"u{i}")
        
        tipo = st.selectbox("Formulação", list(ordem_tecnica.keys()), key=f"t{i}")
        
        lista_produtos.append({
            "nome": nome, 
            "dose": dose, 
            "unidade": un, 
            "tipo": tipo,
            "peso": ordem_tecnica[tipo]
        })

# --- CÁLCULOS LOGÍSTICOS ---
volume_total_calda = area_total * taxa_aplicacao
num_batidas_cheias = math.floor(volume_total_calda / misturador_cap)
volume_restante = volume_total_calda % misturador_cap

# --- ORGANIZAÇÃO PELA ORDEM TÉCNICA ---
# Aqui o Python ordena os produtos pelo peso da formulação
produtos_ordenados = sorted(lista_produtos, key=lambda x: x['peso'])

def gerar_tabela(volume_batida):
    ha_batida = volume_batida / taxa_aplicacao
    dados = []
    for pos, p in enumerate(produtos_ordenados):
        valor = p['dose'] * ha_batida
        txt_valor = f"{valor:.2f} {p['unidade']}"
        dados.append({
            "Ordem": pos + 1,
            "Produto": p['nome'],
            "Formulação": p['tipo'],
            "Qtd por Batida": txt_valor
        })
    return pd.DataFrame(dados)

# --- EXIBIÇÃO ---
st.subheader("📊 Planejamento de Batidas")
c1, c2, c3 = st.columns(3)
c1.metric("Volume Total", f"{volume_total_calda} L")
c2.metric(f"Batidas de {int(misturador_cap)}L", int(num_batidas_cheias))
c3.metric("Batida Final", f"{volume_restante} L")

if num_batidas_cheias > 0:
    st.success(f"📋 **FAÇA {int(num_batidas_cheias)} VEZES:** Mistura para 200 Litros")
    st.table(gerar_tabela(misturador_cap))

if volume_restante > 0:
    st.warning(f"⚠️ **NA ÚLTIMA VEZ:** Mistura para apenas {volume_restante} Litros")
    st.table(gerar_tabela(volume_restante))

st.info("💡 O aplicativo ordenou os produtos automaticamente seguindo as normas técnicas de compatibilidade.")
