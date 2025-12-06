import streamlit as st
import requests

def list_fornecedores(API_URL):
    r = requests.get(f"{API_URL}/fornecedores")
    r.raise_for_status()
    return r.json()

def patch_aprovacao(API_URL, fid, aprovado: bool):
    r = requests.patch(
        f"{API_URL}/fornecedores/{fid}/aprovacao",
        json={"aprovado": aprovado},
    )
    r.raise_for_status()
    return r.json()

def get_ordem(API_URL):
    r = requests.get(f"{API_URL}/fornecedores/ordem_fornecedor")
    r.raise_for_status()
    return r.json()

def pagina_gestor(API_URL):
    st.header("Gestão de Fornecedores")

    if st.button("Recarregar lista"):
        st.rerun()

    fornecedores = list_fornecedores(API_URL)
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
                        patch_aprovacao(API_URL, f["id"], True)
                        st.rerun()
            with col3:
                if f["aprovado"]:
                    if st.button("Reprovar", key=f"rp_{f['id']}"):
                        patch_aprovacao(API_URL, f["id"], False)
                        st.rerun()
    else:
        st.info("Ainda não há fornecedores.")

    st.subheader("Ordem de fornecimento por produto")
    if st.button("Calcular ordem"):
        try:
            ordens = get_ordem(API_URL)
            for o in ordens:
                st.write(
                    f"Produto: {o['produto']} → ordem de fornecedores: "
                    f"{', '.join(map(str, o['fornecedores_ids']))}"
                )
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao calcular ordem: {e.response.status_code} - {e.response.text}")
