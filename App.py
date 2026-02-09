import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Calculadora Agrícola Eric", page_icon="🚜")

st.title("🚜 Minha Calculadora de Calda")
st.markdown("---")

# CONFIGURAÇÕES DA ÁREA
with st.sidebar:
    st.header("⚙️ Configurações")
    area_total = st.number_input("Área Total (ha)", value=60.0)
    taxa_aplicacao = st.number_input("Taxa de Aplicação (L/ha)", value=12.0)
    misturador_cap = st.number_input("Capacidade do Misturador (L)", value=200.0)
    
    st.header("🧪 Produtos e Doses")
    num_produtos = st.slider("Quantos produtos na mistura?", 1, 8, 5)
    
    produtos = []
    for i in range(num_produtos):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            nome = st.text_input(f"Produto {i+1}", f"Prod {i+1}")
        with col2:
            dose = st.number_input(f"Dose", key=f"d{i}", value=1.0, format="%.3f")
        with col3:
            unidade = st.selectbox("Un.", ["L", "ml"], key=f"u{i}")
        produtos.append({"nome": nome, "dose": dose, "unidade": unidade})

# CÁLCULOS
volume_total_calda = area_total * taxa_aplicacao
num_batidas_cheias = math.floor(volume_total_calda / misturador_cap)
volume_restante = volume_total_calda % misturador_cap

# EXIBIÇÃO
st.subheader("📊 Planejamento")
c1, c2, c3 = st.columns(3)
c1.metric("Volume Total", f"{volume_total_calda} L")
c2.metric(f"Batidas de {int(misturador_cap)}L", int(num_batidas_cheias))
c3.metric("Batida Final", f"{volume_restante} L")

def gerar_tabela(volume_batida):
    ha_batida = volume_batida / taxa_aplicacao
    lista_final = []
    for p in produtos:
        valor = p['dose'] * ha_batida
        # Ajuste de unidade para visualização
        txt_valor = f"{valor:.2f} {p['unidade']}"
        lista_final.append({"Ordem": produtos.index(p)+1, "Produto": p['nome'], "Qtd por Batida": txt_valor})
    return pd.DataFrame(lista_final)

if num_batidas_cheias > 0:
    st.write(f"### ✅ Batidas de {misturador_cap} Litros")
    st.table(gerar_tabela(misturador_cap))

if volume_restante > 0:
    st.write(f"### ⚠️ Última Batida ({volume_restante} Litros)")
    st.table(gerar_tabela(volume_restante))

st.info("💡 Dica: Mantenha o agitador ligado e siga a ordem de mistura da calda conforme a formulação (WG > SC > EC).")
