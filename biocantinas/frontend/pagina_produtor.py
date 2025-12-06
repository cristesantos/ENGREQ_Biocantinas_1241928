import streamlit as st
import requests
from datetime import date

def create_fornecedor(API_URL, payload):
    r = requests.post(f"{API_URL}/fornecedores", json=payload)
    r.raise_for_status()
    return r.json()

def pagina_produtor(API_URL):
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
        novo = create_fornecedor(API_URL, payload)
        st.success(f"Produtor criado com id {novo['id']} (aguarda aprovação).")
