import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CONFIGURAÇÃO ---
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
        # 1. BUSCAR DADOS
        res_treinos = requests.get(f"{API_URL}?sheet=Treinos")
        res_logs = requests.get(f"{API_URL}?sheet=Logs")
        
        historico_dict = {}

        # Processar Histórico (Logs)
        if res_logs.status_code == 200:
            data_logs = res_logs.json()
            if isinstance(data_logs, list) and len(data_logs) > 0:
                df_logs = pd.DataFrame(data_logs)
                if 'Exercicio' in df_logs.columns and 'Data' in df_logs.columns:
                    df_logs['Data'] = pd.to_datetime(df_logs['Data'])
                    df_logs = df_logs.sort_values(by='Data', ascending=False)
                    df_last = df_logs.drop_duplicates(subset=['Exercicio'], keep='first')
                    for _, row_log in df_last.iterrows():
                        historico_dict[row_log['Exercicio']] = {
                            "Carga": row_log['Carga'],
                            "Data": row_log['Data'].strftime("%d/%m")
                        }

        # Processar Ficha de Treinos
        if res_treinos.status_code == 200:
            data = res_treinos.json()
            df_treinos = pd.DataFrame(data)
            
            if not df_treinos.empty and 'Treino_ID' in df_treinos.columns:
                lista_treinos = df_treinos['Treino_ID'].unique()
                treino_escolhido = st.selectbox("Selecione a Ficha:", lista_treinos)
                
                exercicios_do_dia = df_treinos[df_treinos['Treino_ID'] == treino_escolhido]
                
                st.divider()
                
                with st.form("form_treino"):
                    st.subheader(f"Ficha {treino_escolhido}")
                    resultados = []
                    
                    for index, row in exercicios_do_dia.iterrows():
                        # CORREÇÃO AQUI: Usando o nome exato da coluna da sua planilha
                        nome_ex = row['Exercicio'] 
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown(f"**{nome_ex}**")
                            st.caption(f"Séries/Rep: {row['Serie']}")
                            
                            # Mostrar carga anterior
                            if nome_ex in historico_dict:
                                last = historico_dict[nome_ex]
                                st.info(f"🔙 Último: {last['Carga']}kg ({last['Data']})")
                            else:
                                st.caption("Novo exercício")

                            if 'Imagem_URL' in row and str(row['Imagem_URL']).startswith('http'):
                                st.image(row['Imagem_URL'], use_container_width=True)
                        
                        with col2:
                            # Valor padrão baseado no histórico
                            val_padrao = 0.0
                            if nome_ex in historico_dict:
                                try: val_padrao = float(historico_dict[nome_ex]['Carga'])
                                except: val_padrao = 0.0

                            carga = st.number_input(f"Carga (kg)", key=f"c_{index}", value=val_padrao, step=0.5)
                            feito = st.checkbox("Concluído", key=f"f_{index}")
                            
                            if feito:
                                resultados.append({
                                    "Data": datetime.now().strftime("%Y-%m-%d"),
                                    "Treino": treino_escolhido,
                                    "Exercicio": nome_ex,
                                    "Carga": carga,
                                    "Concluido": "Sim"
                                })
                    
                    st.markdown("---")
                    if st.form_submit_button("Salvar Treino Completo"):
                        if resultados:
                            r = requests.post(f"{API_URL}?sheet=Logs", json=resultados)
                            if r.status_code == 200:
                                st.balloons()
                                st.success("Treino registrado com sucesso!")
                            else:
                                st.error("Erro ao salvar dados.")
                        else:
                            st.warning("Marque pelo menos um exercício como feito.")
    except Exception as e:
        st.error(f"Erro no carregamento: {e}")

# (O resto do código de Evolução permanece o mesmo)
elif pagina == "📈 Minha Evolução":
    # ... código de evolução que você já tem ...
    st.header("Gráficos de Progresso")
    # (Mantido conforme sua versão original)