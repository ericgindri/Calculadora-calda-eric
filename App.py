import streamlit as st
import pandas as pd
import math
import urllib.parse
import json

# Configuração para facilitar a leitura no campo
st.set_page_config(page_title="Central de Mistura Eric", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    .stTable { font-size: 24px !important; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; }
    .stMarkdown p { font-size: 21px; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DATOS TÉCNICO ---
DB_PRODUTOS = {
    "- Selecionar -": {"dose_bula": "", "un": "L", "form": "Adjuvante"},
    "Bim Max": {"dose_bula": "1,0 a 1,2 L/ha", "un": "L", "form": "SC (Suspensão)"},
    "Aproach Power": {"dose_bula": "0,4 a 0,6 L/ha", "un": "L", "form": "SC (Suspensão)"},
    "Shenzi": {"dose_bula": "80 a 100 ml/ha", "un": "ml", "form": "SC (Suspensão)"},
    "Fulltec Max": {"dose_bula": "50 ml/ha", "un": "ml", "form": "Adjuvante"},
    "Nutrol Max": {"dose_bula": "100 a 200 ml/ha", "un": "ml", "form": "Adjuvante"},
    "Engeo Pleno S": {"dose_bula": "150 a 250 ml/ha", "un": "ml", "form": "ZC (Encapsulada)"},
    "Unanime": {"dose_bula": "0,75 a 1,5 L/ha", "un": "L", "form": "SL (Líquido)"},
    "Crucial": {"dose_bula": "2,0 a 4,0 L/ha", "un": "L", "form": "SL (Líquido)"},
    "Expedition": {"dose_bula": "150 a 300 ml/ha", "un": "ml", "form": "SC (Suspensão)"},
    "PingBR (Ouro Fino)": {"dose_bula": "0,75 a 1,5 L/ha", "un": "L", "form": "EC (Emulsão)"},
    "Joint Ultra": {"dose_bula": "0,4 a 0,6 L/ha", "un": "L", "form": "SC (Suspensão)"},
    "Evolution": {"dose_bula": "1,5 a 2,5 kg/ha", "un": "kg", "form": "WG (Grânulos)"},
    "Blindado (Adama)": {"dose_bula": "0,5 a 1,0 L/ha", "un": "L", "form": "EC (Emulsão)"},
    "Fox Xpro": {"dose_bula": "0,4 a 0,5 L/ha", "un": "L", "form": "SC (Suspensão)"},
    "Kifix": {"dose_bula": "140 g/ha", "un": "g", "form": "WG (Grânulos)"},
    "Select": {"dose_bula": "0,4 a 0,5 L/ha", "un": "L", "form": "EC (Emulsão)"},
    "Outro (Novo)": {"dose_bula": "Consulte Bula", "un": "L", "form": "SL (Líquido)"}
}

ORDEM_TECNICA = {
    "Adjuvante": 1, "WG (Grânulos)": 2, "SC (Suspensão)": 3, 
    "ZC (Encapsulada)": 3, "EC (Emulsão)": 4, "SL (Líquido)": 5
}

def limpar_campos():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.title("🚜 Central de Mistura Eric")
st.markdown("---")

# --- LÓGICA DE CARREGAMENTO ROBUSTA ---
with st.expander("💾 Salvar ou Carregar Receitas"):
    col_save, col_load = st.columns(2)
    with col_load:
        uploaded_file = st.file_uploader("Subir arquivo de receita (.json)", type="json")
        if uploaded_file:
            data = json.load(uploaded_file)
            # Injeta os dados na sessão do Streamlit
            st.session_state['fazenda'] = data.get('fazenda', 'Geral')
            st.session_state['area_total'] = data.get('area', 60.0)
            st.session_state['taxa'] = data.get('taxa', 12.0)
            st.session_state['tanque'] = data.get('tanque', 200.0)
            st.session_state['n_prod_slider'] = len(data.get('produtos', []))
            # Salva os produtos para preenchimento posterior
            st.session_state['produtos_salvos'] = data.get('produtos', [])
            st.success("Dados carregados! Ajuste o slider se necessário.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Operação")
    st.button("🗑️ Limpar Tudo", on_click=limpar_campos, type="primary")
    
    fazenda = st.text_input("Fazenda / Talhão", value=st.session_state.get('fazenda', 'Geral'), key='fazenda_input')
    area_total = st.number_input("Área Total (ha)", value=st.session_state.get('area_total', 60.0), key='area_input')
    taxa = st.number_input("Taxa (L/ha)", value=st.session_state.get('taxa', 12.0), key='taxa_input')
    tanque = st.number_input("Misturador (L)", value=st.session_state.get('tanque', 200.0), key='tanque_input')
    
    st.header("🧪 Calda")
    n_prod = st.slider("Quantidade de Produtos", 1, 15, value=st.session_state.get('n_prod_slider', 5), key='n_prod_slider')
    
    escolhidos = []
    produtos_salvos = st.session_state.get('produtos_salvos', [])

    for i in range(n_prod):
        st.markdown(f"---")
        
        # Recupera dados do produto salvo, se existir
        salvo = produtos_salvos[i] if i < len(produtos_salvos) else None
        p_ref_default = salvo['p_ref'] if salvo and salvo['p_ref'] in DB_PRODUTOS else "- Selecionar -"
        
        p_ref = st.selectbox(f"Produto {i+1}", list(DB_PRODUTOS.keys()), 
                             index=list(DB_PRODUTOS.keys()).index(p_ref_default), key=f"sel_{i}")
        
        if p_ref != "- Selecionar -":
            dados_p = DB_PRODUTOS[p_ref]
            st.caption(f"📖 Bula: {dados_p['dose_bula']}")
            
            nome_default = salvo['nome'] if salvo else p_ref
            nome = p_ref if p_ref != "Outro (Novo)" else st.text_input("Nome", value=nome_default, key=f"n_{i}")
            
            dose_default = float(salvo['dose']) if salvo else 0.0
            dose = st.number_input("Dose/ha", value=dose_default, key=f"d_{i}", format="%.3f")
            
            un_default = salvo['un'] if salvo else dados_p["un"]
            un = st.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(un_default), key=f"u_{i}")
            
            form_default = salvo['form'] if salvo else dados_p["form"]
            form = st.selectbox("Tipo", list(ORDEM_TECNICA.keys()), index=list(ORDEM_TECNICA.keys()).index(form_default), key=f"f_{i}_{p_ref}")
            
            link = f"https://www.google.com/search?q=site:agrolink.com.br/agrolinkfito+{nome.replace(' ', '+')}"
            escolhidos.append({"p_ref": p_ref, "nome": nome, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link})

# --- PROCESSAMENTO E TOTAIS ---
vol_total = area_total * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
area_por_batida = tanque / taxa
area_sobra = sobra / taxa
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

# Função para resumo de insumos totais
def exibir_totais():
    if escolhidos:
        st.markdown("### 📦 Total de Insumos para a Área")
        totais = []
        for p in escolhidos:
            total_area = p['dose'] * area_total
            totais.append({"Produto": p['nome'], "Total Necessário": f"{total_area:.2f} {p['un']}"})
        st.table(totais)

with col_save:
    receita_json = json.dumps({"fazenda": fazenda, "area": area_total, "taxa": taxa, "tanque": tanque, "produtos": escolhidos}, indent=4)
    st.download_button("📥 Salvar JSON", receita_json, f"receita_{fazenda}.json", "application/json")

def gerar_zap(volume, tipo, area_c):
    ha = volume / taxa
    texto = f"*🚜 PLANO ERIC - {fazenda.upper()}*\n💧 Água: {int(volume)}L ({tipo})\n📍 Cobertura: *{area_c:.2f} ha*\n---\n"
    for i, p in enumerate(ordenados):
        texto += f"{i+1}º {p['nome']} ({p['form']}): *{(p['dose']*ha):.2f} {p['un']}*\n"
    return f"https://wa.me/?text={urllib.parse.quote(texto)}"

# --- EXIBIÇÃO ---
st.subheader(f"📝 Plano: {fazenda}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Calda Total", f"{vol_total} L")
c2.metric("Batidas 200L", int(batidas))
c3.metric("Área/Batida", f"{area_por_batida:.2f} ha")
c4.metric("Batida Final", f"{int(sobra)} L")

if ordenados:
    exibir_totais() # Exibe quanto de cada veneno você precisa comprar/pegar no galpão
    
    if batidas > 0:
        st.success(f"✅ **BATIDA CHEIA ({int(tanque)}L) - Cobre {area_por_batida:.2f} ha**")
        df = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Tipo": p['form'], "Dose/ha": f"{p['dose']} {p['un']}", "Misturar": f"{(p['dose']*(tanque/taxa)):.2f} {p['un']}", "🔗": p['bula']} for i, p in enumerate(ordenados)])
        st.dataframe(df, column_config={"🔗": st.column_config.LinkColumn(width="small")}, hide_index=True, use_container_width=True)
        st.link_button(f"📲 WhatsApp: Batida Cheia", gerar_zap(tanque, "CHEIA", area_por_batida))

    if sobra > 0:
        st.warning(f"⚠️ **BATIDA FINAL ({int(sobra)}L) - Cobre {area_sobra:.2f} ha**")
        df_s = pd.DataFrame([{"Ordem": i+1, "Produto": p['nome'], "Tipo": p['form'], "Dose/ha": f"{p['dose']} {p['un']}", "Misturar": f"{(p['dose']*(sobra/taxa)):.2f} {p['un']}", "🔗": p['bula']} for i, p in enumerate(ordenados)])
        st.dataframe(df_s, column_config={"🔗": st.column_config.LinkColumn(width="small")}, hide_index=True, use_container_width=True)
        st.link_button(f"📲 WhatsApp: Batida Final", gerar_zap(sobra, "FINAL", area_sobra))
