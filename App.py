import streamlit as st
import pandas as pd
import math
import urllib.parse
import json

# Configuração para facilitar a leitura no campo e no notebook Samsung
st.set_page_config(page_title="Central de Mistura Eric", page_icon="🚜", layout="wide")

# CSS para aumentar a fonte e destacar as informações sob o sol
st.markdown("""
    <style>
    .stTable { font-size: 24px !important; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; }
    .stMarkdown p { font-size: 21px; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS TÉCNICO ---
DB_PRODUTOS = {
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

st.title("🚜 Central de Mistura Eric")
st.markdown("---")

# --- SISTEMA DE CARREGAMENTO ---
with st.expander("💾 Salvar ou Carregar Receitas"):
    col_save, col_load = st.columns(2)
    with col_load:
        uploaded_file = st.file_uploader("Carregar arquivo de receita (.json)", type="json")
        loaded_data = json.load(uploaded_file) if uploaded_file else None

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Operação")
    fazenda = st.text_input("Fazenda / Talhão", value=loaded_data['fazenda'] if loaded_data else "Geral")
    area = st.number_input("Área Total (ha)", value=loaded_data['area'] if loaded_data else 60.0)
    taxa = st.number_input("Taxa (L/ha)", value=loaded_data['taxa'] if loaded_data else 12.0)
    tanque = st.number_input("Misturador (L)", value=loaded_data['tanque'] if loaded_data else 200.0)
    
    st.header("🧪 Calda")
    n_prod = st.slider("Produtos", 1, 10, len(loaded_data['produtos']) if loaded_data else 5)
    
    escolhidos = []
    for i in range(n_prod):
        st.markdown(f"---")
        p_def = loaded_data['produtos'][i]['p_ref'] if loaded_data and i < len(loaded_data['produtos']) else "Bim Max"
        p_ref = st.selectbox(f"Produto {i+1}", list(DB_PRODUTOS.keys()), index=list(DB_PRODUTOS.keys()).index(p_ref if (p_ref := p_def) in DB_PRODUTOS else "Bim Max"), key=f"sel_{i}")
        dados_p = DB_PRODUTOS[p_ref]
        st.caption(f"📖 Bula: {dados_p['dose_bula']}")
        
        nome = p_ref if p_ref != "Outro (Novo)" else st.text_input("Nome", value=loaded_data['produtos'][i]['nome'] if loaded_data and i < len(loaded_data['produtos']) else "Novo", key=f"n_{i}")
        dose = st.number_input("Dose/ha", value=float(loaded_data['produtos'][i]['dose'] if loaded_data and i < len(loaded_data['produtos']) else 0.0), key=f"d_{i}", format="%.3f")
        un = st.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(loaded_data['produtos'][i]['un'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["un"]), key=f"u_{i}")
        form = st.selectbox("Tipo", list(ORDEM_TECNICA.keys()), index=list(ORDEM_TECNICA.keys()).index(loaded_data['produtos'][i]['form'] if loaded_data and i < len(loaded_data['produtos']) else dados_p["form"]), key=f"f_{i}_{p_ref}")
        
        link = f"https://www.google.com/search?q=site:agrolink.com.br/agrolinkfito+{nome.replace(' ', '+')}"
        escolhidos.append({"p_ref": p_ref, "nome": nome, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link})

# --- BOTÃO DE SALVAR ---
with col_save:
    receita_atual = {"fazenda": fazenda, "area": area, "taxa": taxa, "tanque": tanque, "produtos": escolhidos}
    st.download_button("📥 Baixar Receita (JSON)", json.dumps(receita_atual, indent=4), f"receita_{fazenda}.json", "application/json")

# --- PROCESSAMENTO ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

# --- WHATSAPP ---
def gerar_zap(volume, tipo):
    ha = volume / taxa
    texto = f"*🚜 PLANO ERIC - {fazenda.upper()}*\n"
    texto += f"💧 Água: {int(volume)}L ({tipo})\n"
    texto += "----------------------------\n"
    for i, p in enumerate(ordenados):
        texto += f"{i+1}º {p['nome']} ({p['form']}): *{(p['dose']*ha):.2f} {p['un']}*\n"
    return f"https://wa.me/?text={urllib.parse.quote(texto)}"

# --- EXIBIÇÃO ---
st.subheader(f"📝 Plano de Trabalho: {fazenda}")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L")
c2.metric("Batidas Cheias", int(batidas))
c3.metric("Última Batida", f"{int(sobra)} L")

def exibir_tabela(volume, titulo, emoji):
    if volume > 0:
        st.markdown(f"### {emoji} {titulo} ({int(volume)}L)")
        df = pd.DataFrame([
            {
                "Ordem": i+1, 
                "Produto": p['nome'], 
                "Tipo": p['form'],
                "Dose/ha": f"{p['dose']} {p['un']}",
                "Qtd p/ Misturar": f"{(p['dose']*(volume/taxa)):.2f} {p['un']}",
                "🔗": p['bula']
            } for i, p in enumerate(ordenados)
        ])
        st.dataframe(df, column_config={"🔗": st.column_config.LinkColumn(width="small")}, hide_index=True, use_container_width=True)
        st.link_button(f"📲 Enviar via WhatsApp", gerar_zap(volume, titulo))

exibir_tabela(tanque if batidas > 0 else 0, "BATIDA CHEIA", "✅")
exibir_tabela(sobra, "BATIDA FINAL", "⚠️")
