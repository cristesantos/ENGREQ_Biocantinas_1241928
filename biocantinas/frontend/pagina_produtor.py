import streamlit as st
import requests
from datetime import date

def create_fornecedor(API_URL, auth_token, payload):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.post(f"{API_URL}/fornecedores", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_produtor(API_URL, auth_token):
    st.header("Inscrição de Produtor")

    nome = st.text_input("Nome do produtor")
    data_inscricao = st.date_input("Data de inscrição", value=date.today())

    st.subheader("Produtos")

    # Lista única de produtos (sem categorias)
    produtos = [
        "kiwi",
        "mirtilo",
        "frutos vermelhos",
        "cereja",
        "maçã",
        "pera",
        "castanha",
        "couves",
        "alface",
        "rúcula",
        "espinafre",
        "tomate",
        "pimento",
        "beringela",
        "cenoura",
        "nabo",
        "beterraba",
        "abóbora",
        "curgete",
        "bovino",
        "suíno",
        "ovino",
        "caprino",
        "ovos de galinhas ao ar livre",
        "mel",
        "cogumelo shiitake",
    ]

    # Ordenar alfabeticamente (independente de maiúsculas/minúsculas)
    produtos = sorted(produtos, key=lambda s: s.lower())

    prod_nome = st.selectbox("Produto", options=produtos)
    # Opcional: permitir especificar outro texto caso necessário
    if st.checkbox("Outro (especificar manualmente)"):
        prod_nome = st.text_input("Especifique o produto", value=prod_nome)

    prod_ini = st.date_input("Início intervalo produção", value=date.today())
    prod_fim = st.date_input("Fim intervalo produção", value=date.today())
    capacidade = st.number_input("Capacidade (Kg)", min_value=0, value=0)

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
        novo = create_fornecedor(API_URL, auth_token, payload)
        st.success(f"Produtor criado com id {novo['id']} (aguarda aprovação).")
