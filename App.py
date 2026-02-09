import streamlit as st
import pandas as pd
import math

# Configuração da página
st.set_page_config(page_title="Calculadora de Calda - Eric", page_icon="🚜")

st.title("🚜 Calculadora de Mistura de Calda")
st.markdown("---")

# --- ENTRADAS DE DADOS ---
st.sidebar.header("Configurações da Área")
area_total = st.sidebar.number_input("Área Total (ha)", value=60.0)
taxa_aplicacao = st.sidebar.number_input("Taxa de Aplicação (L/ha)", value=12.0)
capacidade_tanque = st.sidebar.number_input("Capacidade do Misturador (L)", value=200.0)

st.sidebar.header("Produtos e Doses (por ha)")
# Doses padrão baseadas na nossa conversa
dose_fulltec = st.sidebar.number_input("Fulltec Max (ml/ha)", value=50.0)
dose_nutrol = st.sidebar.number_input("Nutrol Max (ml/ha)", value=150.0)
dose_bim = st.sidebar.number_input("Bim Max (L/ha)", value=1.2)
dose_shenzi = st.sidebar.number_input("Shenzi (ml/ha)", value=80.0)
dose_aproach = st.sidebar.number_input("Aproach Power (ml/ha)", value=600.0)

# --- CÁLCULOS LOGÍSTICOS ---
volume_total_calda = area_total * taxa_aplicacao
num_batidas_cheias = math.floor(volume_total_calda / capacidade_tanque)
volume_restante = volume_total_calda % capacidade_tanque

# --- FUNÇÃO DE CÁLCULO DE PRODUTOS ---
def calcular_produtos(volume_batida):
    ha_por_batida = volume_batida / taxa_aplicacao
    return {
        "Fulltec Max": f"{(dose_fulltec * ha_por_batida):.2f} ml",
        "Nutrol Max": f"{(dose_nutrol * ha_por_batida):.2f} ml",
        "Bim Max": f"{(dose_bim * ha_por_batida):.2f} L",
        "Shenzi": f"{(dose_shenzi * ha_por_batida):.2f} ml",
        "Aproach Power": f"{(dose_aproach * ha_por_batida):.2f} ml"
    }

# --- EXIBIÇÃO DOS RESULTADOS ---
st.subheader("📊 Resumo da Operação")
col1, col2, col3 = st.columns(3)
col1.metric("Volume Total", f"{volume_total_calda} L")
col2.metric("Batidas de {int(capacidade_tanque)}L", int(num_batidas_cheias))
col3.metric("Batida Final", f"{volume_restante} L")

# Tabela para as batidas cheias
if num_batidas_cheias > 0:
    st.write(f"### 📋 Dosagem: Batidas de {capacidade_tanque}L")
    prod_cheios = calcular_produtos(capacidade_tanque)
    df_cheio = pd.DataFrame(list(prod_cheios.items()), columns=["Produto", "Quantidade por Batida"])
    st.table(df_cheio)

# Tabela para a batida de sobra
if volume_restante > 0:
    st.write(f"### 📋 Dosagem: Última Batida ({volume_restante}L)")
    prod_sobra = calcular_produtos(volume_restante)
    df_sobra = pd.DataFrame(list(prod_sobra.items()), columns=["Produto", "Quantidade por Batida"])
    st.table(df_sobra)

st.markdown("---")
st.warning("⚠️ **Ordem de Mistura:** 1. Água (60%) > 2. Fulltec > 3. Nutrol > 4. Bim Max > 5. Shenzi > 6. Aproach > 7. Completar Água.")
