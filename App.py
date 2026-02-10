import streamlit as st
import pandas as pd
import math
import urllib.parse

# Configuração visual para facilitar a leitura no campo em São Francisco de Assis
st.set_page_config(page_title="Central de Mistura Eric", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    .stTable { font-size: 22px !important; }
    div[data-testid="stExpander"] { font-size: 18px; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
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
        st.markdown(f"**Produto {i+1}**")
        p_ref = st.selectbox(f"Selecionar", list(DB_PRODUTOS.keys()), key=f"sel_{i}")
        dados_p = DB_PRODUTOS[p_ref]
        st.caption(f"📖 Bula: {dados_p['dose_bula']}")
        
        nome = p_ref if p_ref != "Outro (Novo)" else st.text_input("Nome", key=f"n_{i}")
        dose = st.number_input("Dose/ha", value=0.0, key=f"d_{i}", format="%.3f")
        un = st.selectbox("Un.", ["L", "ml", "g", "kg"], index=["L", "ml", "g", "kg"].index(dados_p["un"]), key=f"u_{i}")
        form = st.selectbox("Formulação", list(ORDEM_TECNICA.keys()), index=list(ORDEM_TECNICA.keys()).index(dados_p["form"]), key=f"f_{i}_{p_ref}")
        
        link = f"https://www.google.com.br/search?q=site%3Aagrolink.com.br%2Fagrolinkfito+{nome.replace(' ', '+')}"
        escolhidos.append({"nome": nome, "dose": dose, "un": un, "form": form, "peso": ORDEM_TECNICA[form], "bula": link})

# --- PROCESSAMENTO ---
vol_total = area * taxa
batidas = math.floor(vol_total / tanque)
sobra = vol_total % tanque
ordenados = sorted(escolhidos, key=lambda x: x['peso'])

# --- FUNÇÃO WHATSAPP ---
def gerar_link_whatsapp(volume, label):
    ha = volume / taxa
    texto = f"*🚜 PLANO DE MISTURA - ERIC*\n"
    texto += f"*📍 {fazenda.upper()} - {label}*\n"
    texto += f"💧 Água: {int(volume)} Litros\n"
    texto += f"----------------------------\n"
    for i, p in enumerate(ordenados):
        qtd = p['dose'] * ha
        texto += f"{i+1}º {p['nome']} ({p['form']}): *{qtd:.2f} {p['un']}*\n"
    texto += f"----------------------------\n"
    texto += "⚠️ _Mantenha a agitação constante!_"
    return f"https://wa.me/?text={urllib.parse.quote(texto)}"

# --- EXIBIÇÃO ---
st.subheader(f"📝 Plano de Trabalho: {fazenda}")
c1, c2, c3 = st.columns(3)
c1.metric("Calda Total", f"{vol_total} L")
c2.metric("Batidas Cheias", int(batidas))
c3.metric("Sobrou p/ Final", f"{int(sobra)} L")

def exibir_tabela(volume, titulo, emoji):
    if volume > 0:
        st.markdown(f"### {emoji} {titulo} ({int(volume)}L)")
        df = pd.DataFrame([
            {
                "Ordem": i+1, 
                "Produto": p['nome'], 
                "Tipo": p['form'],
                "Quantidade": f"{(p['dose']*(volume/taxa)):.2f} {p['un']}",
                "🔗": p['bula']
            } for i, p in enumerate(ordenados)
        ])
        st.dataframe(df, column_config={"🔗": st.column_config.LinkColumn(width="small")}, hide_index=True, use_container_width=True)
        st.link_button(f"📲 Enviar {titulo} via WhatsApp", gerar_link_whatsapp(volume, titulo))

exibir_tabela(tanque if batidas > 0 else 0, f"FAZER {int(batidas)} VEZES", "✅")
exibir_tabela(sobra, "ÚLTIMA BATIDA (FINAL)", "⚠️")
