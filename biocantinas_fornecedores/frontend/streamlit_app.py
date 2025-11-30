import streamlit as st
import requests
from datetime import date
import threading
import uvicorn

from biocantinas_fornecedores.backend.app.main import app as fastapi_app

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="BioCantinas - Fornecedores")

# Start FastAPI server once per Streamlit session
def _start_api():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")

if "api_thread_started" not in st.session_state:
    st.session_state.api_thread = threading.Thread(target=_start_api, daemon=True)
    st.session_state.api_thread.start()
    st.session_state.api_thread_started = True
    st.info("FastAPI iniciado em background na porta 8000")

st.set_page_config(page_title="BioCantinas - Fornecedores")

st.sidebar.title("BioCantinas")
papel = st.sidebar.radio("Perfil", ["Gestor", "Produtor"])

# Helpers simples
def list_fornecedores():
    r = requests.get(f"{API_URL}/fornecedores")
    r.raise_for_status()
    return r.json()

def create_fornecedor(payload):
    r = requests.post(f"{API_URL}/fornecedores", json=payload)
    r.raise_for_status()
    return r.json()

def patch_aprovacao(fid, aprovado: bool):
    r = requests.patch(
        f"{API_URL}/fornecedores/{fid}/aprovacao",
        json={"aprovado": aprovado},
    )
    r.raise_for_status()
    return r.json()

def get_ordem():
    r = requests.get(f"{API_URL}/fornecedores/ordem")
    r.raise_for_status()
    return r.json()

if papel == "Produtor":
    st.header("Inscrição de Produtor")

    nome = st.text_input("Nome do produtor")
    data_inscricao = st.date_input("Data de inscrição", value=date.today())

    st.subheader("Produtos")
    prod_nome = st.text_input("Nome do produto")
    prod_ini = st.date_input("Início intervalo produção", value=date.today())
    prod_fim = st.date_input("Fim intervalo produção", value=date.today())
    capacidade = st.number_input("Capacidade (unidade)", min_value=0, value=0)

    if st.button("Submeter inscrição"):
        payload = {
            "nome": nome,
            "data_inscricao": str(data_inscricao),
            "produtos": [
                {
                    "nome": prod_nome,
                    "intervalo_producao_inicio": str(prod_ini),
                    "intervalo_producao_fim": str(prod_fim),
                    "capacidade": int(capacidade),
                }
            ],
        }
        novo = create_fornecedor(payload)
        st.success(f"Produtor criado com id {novo['id']} (aguarda aprovação).")

elif papel == "Gestor":
    st.header("Gestão de Fornecedores")

    if st.button("Recarregar lista"):
        st.rerun()

    fornecedores = list_fornecedores()
    if fornecedores:
        st.subheader("Fornecedores")
        for f in fornecedores:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"#{f['id']} - {f['nome']}")
                st.caption(
                    f"Data inscrição: {f['data_inscricao']} | "
                    f"Aprovado: {f['aprovado']}"
                )
            with col2:
                if not f["aprovado"]:
                    if st.button("Aprovar", key=f"ap_{f['id']}"):
                        patch_aprovacao(f["id"], True)
                        st.rerun()
            with col3:
                if f["aprovado"]:
                    if st.button("Reprovar", key=f"rp_{f['id']}"):
                        patch_aprovacao(f["id"], False)
                        st.rerun()
    else:
        st.info("Ainda não há fornecedores.")

    st.subheader("Ordem de fornecimento por produto")
    if st.button("Calcular ordem"):
        ordens = get_ordem()
        for o in ordens:
            st.write(
                f"Produto: {o['produto']} → ordem de fornecedores: "
                f"{', '.join(map(str, o['fornecedores_ids']))}"
            )
