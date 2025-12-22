import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CONFIGURAÇÃO ---
# COLE O LINK QUE VOCÊ COPIOU DO APPS SCRIPT AQUI (termina em /exec)
API_URL = "https://script.google.com/macros/s/AKfycbzY36f-zGrXIIO7MeGlMqSkl-EknT3ZmtYEyg6lP8FRuzj9taYwzTJ3um07ZQAPDjPcKA/exec"

st.set_page_config(page_title="Gym Tracker", page_icon="💪", layout="wide")

st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["🏋️‍♂️ Registrar Treino", "📈 Minha Evolução"])
st.title("💪 Gym Tracker - Google Script Edition")

# ==================================================
# PÁGINA 1: REGISTRAR TREINO
# ==================================================
if pagina == "🏋️‍♂️ Registrar Treino":
    st.header("Hora do Treino")
    
    try:
        # LER DADOS (GET funciona normal)
        response = requests.get(f"{API_URL}?sheet=Treinos")
        if response.status_code == 200:
            data = response.json()
            # Se vier erro do script
            if isinstance(data, dict) and 'error' in data:
                st.error(f"Erro na planilha: {data['error']}")
            else:
                df_treinos = pd.DataFrame(data)
                
                if not df_treinos.empty and 'Treino_ID' in df_treinos.columns:
                    lista_treinos = df_treinos['Treino_ID'].unique()
                    treino_escolhido = st.selectbox("Ficha:", lista_treinos)
                    
                    exercicios_do_dia = df_treinos[df_treinos['Treino_ID'] == treino_escolhido]
                    
                    st.divider()
                    
                    with st.form("form_treino"):
                        st.subheader(f"Ficha {treino_escolhido}")
                        resultados = []
                        
                        for index, row in exercicios_do_dia.iterrows():
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.markdown(f"**{row['Exercicio']}**")
                                st.caption(f"Foco: {row['Serie']}")
                                if 'Imagem_URL' in row and str(row['Imagem_URL']).startswith('http'):
                                    st.image(row['Imagem_URL'], use_container_width=True)
                            
                            with col2:
                                carga = st.number_input(f"Carga (kg)", key=f"c_{index}", step=1.0)
                                feito = st.checkbox("Feito", key=f"f_{index}")
                                
                                if feito:
                                    resultados.append({
                                        "Data": datetime.now().strftime("%Y-%m-%d"),
                                        "Treino": treino_escolhido,
                                        "Exercicio": row['Exercicio'],
                                        "Carga": carga,
                                        "Concluido": "Sim"
                                    })
                        
                        st.markdown("---")
                        btn_salvar = st.form_submit_button("Salvar Treino")
                        
                        if btn_salvar:
                            if len(resultados) > 0:
                                # O Google Apps Script precisa do requests.post com json=...
                                # Usamos allow_redirects=True porque o Google redireciona a resposta
                                r = requests.post(f"{API_URL}?sheet=Logs", json=resultados)
                                
                                if r.status_code == 200:
                                    st.balloons()
                                    st.success("Salvo com sucesso via Apps Script!")
                                else:
                                    st.error(f"Erro ao salvar: {r.text}")
                            else:
                                st.warning("Marque algo feito.")
        else:
            st.error("Erro ao conectar no Script.")

    except Exception as e:
        st.error(f"Erro de conexão: {e}")

# ==================================================
# PÁGINA 2: EVOLUÇÃO
# ==================================================
elif pagina == "📈 Minha Evolução":
    st.header("Seus Resultados")
    
    with st.expander("➕ Nova Medição", expanded=False):
        with st.form("form_bio"):
            c1, c2 = st.columns(2)
            novo_peso = c1.number_input("Peso (kg)", format="%.2f")
            nova_massa = c2.number_input("Massa (kg)", format="%.2f")
            
            if st.form_submit_button("Salvar"):
                dados_bio = {
                    "Data": datetime.now().strftime("%Y-%m-%d"),
                    "Peso": novo_peso,
                    "Massa_Muscular": nova_massa
                }
                # Envia como lista porque nosso script espera lista ou objeto
                requests.post(f"{API_URL}?sheet=Bioimpedancia", json=dados_bio)
                st.success("Salvo!")

    st.divider()

    try:
        resp = requests.get(f"{API_URL}?sheet=Bioimpedancia")
        if resp.status_code == 200:
            df_bio = pd.DataFrame(resp.json())
            
            if not df_bio.empty and 'Peso' in df_bio.columns:
                df_bio['Data'] = pd.to_datetime(df_bio['Data'])
                df_bio['Peso'] = pd.to_numeric(df_bio['Peso'].astype(str).str.replace(',', '.'), errors='coerce')
                df_bio['Massa_Muscular'] = pd.to_numeric(df_bio['Massa_Muscular'].astype(str).str.replace(',', '.'), errors='coerce')
                
                st.line_chart(df_bio, x="Data", y=["Peso", "Massa_Muscular"])
            else:
                st.info("Sem dados ainda.")
    except Exception as e:
        st.error(f"Erro gráfico: {e}")