import streamlit as st
import pandas as pd
import json
import os
import base64
from datetime import date
# Coloque logo no começo do arquivo
SENHA_MESTRA = "grego2026" # Substitua 1234 pela senha que você quiser
# --- 1. CONFIGURAÇÕES E MEMÓRIA ---
ARQUIVO_DADOS = "agendamentos.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=4)

# Inicializa os dados
if 'reservas' not in st.session_state:
    st.session_state.reservas = carregar_dados()

# --- 2. CONVERSÃO DA LOGO (Mesmo código que já usamos) ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("logo.png")

# --- 3. ESTILIZAÇÃO CSS (Atualizada) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(6, 78, 59, 0.85), rgba(0, 0, 0, 0.9)), url("data:image/png;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
        color: white;
    }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: rgba(0,0,0,0.8); color: white;
        text-align: center; padding: 10px; font-size: 12px;
    }}
    /* Estilo dos cards de horário */
    .status-card {{
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE PRINCIPAL ---
st.title("✂️ GREGO BARBEARIA")

aba1, aba2, aba3 = st.tabs(["📅 Agendar", "🕒 Ver Agenda", "✂️ Área do Barbeiro"])

horarios_todos = ["09:00", "10:00", "11:00", "12:00", "13:00" "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]

with aba1:
    st.header("Sua Reserva")
    with st.form("form_agendamento", clear_on_submit=True):
        nome = st.text_input("Nome do Cliente:")
        data_sel = st.date_input("Data do Corte:", min_value=date.today())
        
        # Lógica: Filtrar apenas horários que NÃO estão ocupados NESTE dia
        ocupados_no_dia = [r['hora'] for r in st.session_state.reservas if r['data'] == str(data_sel)]
        disponiveis = [h for h in horarios_todos if h not in ocupados_no_dia]
        
        hora_sel = st.selectbox("Horários Disponíveis:", disponiveis if disponiveis else ["Esgotado"])
        
        submit = st.form_submit_button("CONFIRMAR AGENDAMENTO")
        
        if submit:
            if nome and hora_sel != "Esgotado para hoje":
                # 1. Cria a reserva
                nova_reserva = {"nome": nome, "data": str(data_sel), "hora": hora_sel}
                st.session_state.reservas.append(nova_reserva)
                salvar_dados(st.session_state.reservas)
                
                # 2. Mostra a mensagem de sucesso (Toast é mais moderno!)
                st.toast(f"✅ Horário das {hora_sel} reservado para {nome}!", icon='✂️')
                
                # 3. Dá um aviso visual no meio da tela
                st.success(f"Tudo pronto, {nome}! Agendamento confirmado.")
                
                # Opcional: Se quiser que a página limpe os campos após 2 segundos
                # import time
                # time.sleep(2)
                # st.rerun()
            else:
                st.error("Erro: Preencha o nome ou verifique se há vagas.")

with aba2:
    st.header("Horários Disponíveis:")
    data_consulta = st.date_input("Consultar dia:", value=date.today(), key="consulta")
    
    cols = st.columns(3)
    ocupados_consulta = [r['hora'] for r in st.session_state.reservas if r['data'] == str(data_consulta)]
    
    for i, h in enumerate(horarios_todos):
        with cols[i % 3]:
            if h in ocupados_consulta:
                st.markdown(f"<div class='status-card' style='background-color: #7f1d1d; color: #fecaca;'>{h}<br>ESGOTADO</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='status-card' style='background-color: #064e3b; color: #d1fae5;'>{h}<br>LIVRE</div>", unsafe_allow_html=True)

with aba3:
    st.header("🔐 Acesso Restrito")
    
    # Campo para digitar a senha
    senha_digitada = st.text_input("Digite a senha do barbeiro:", type="password")

    if senha_digitada == SENHA_MESTRA:
        st.success("Acesso liberado, Gregory!")
        st.write("---")
        st.subheader("Gestão de Agendamentos")
        
        if not st.session_state.reservas:
            st.info("Nenhum agendamento no sistema.")
        else:
            # Lista os agendamentos com botão de remover
            for i, res in enumerate(st.session_state.reservas):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📌 **{res['data']}** às **{res['hora']}**")
                    st.write(f"👤 Cliente: {res['nome']}")
                with col2:
                    if st.button("Concluir", key=f"del_{i}"):
                        st.session_state.reservas.pop(i)
                        salvar_dados(st.session_state.reservas)
                        st.toast("Horário liberado com sucesso!")
                        st.rerun()
                st.write("---")
    
    elif senha_digitada == "":
        st.info("Por favor, insira a senha para gerenciar os horários.")
    else:
        st.error("Senha incorreta. Acesso negado.")

# --- 5. RODAPÉ ---
st.markdown(f"""
    <div class="footer">
        Grego Barbearia © 2026 | Criador e desenvolvedor do sistema: Vinicius
    </div>
    """, unsafe_allow_html=True)