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

    # Inicializar estado
    if 'ordens' not in st.session_state:
        st.session_state['ordens'] = None

    if st.button("Calcular ordem"):
        try:
            st.session_state['ordens'] = get_ordem(API_URL)
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao calcular ordem: {e.response.status_code} - {e.response.text}")
            st.session_state['ordens'] = []

    ordens = st.session_state.get('ordens')

    if ordens is None:
        st.info("Clique em 'Calcular ordem' para carregar ordens.")
    elif ordens:
        # mapa id -> nome para apresentar os nomes dos agricultores
        id_to_nome = {f['id']: f['nome'] for f in fornecedores}

        produtos = sorted([o['produto'] for o in ordens], key=lambda s: s.lower())
        produto_sel = st.selectbox("Produto", options=produtos, key='produto_sel')

        ordem = next((o for o in ordens if o['produto'] == produto_sel), None)
        if ordem:
            nomes = [id_to_nome.get(i, str(i)) for i in ordem['fornecedores_ids']]
            st.write("Lista de agricultores por ordem de inscrição:")
            for idx, nome in enumerate(nomes, start=1):
                st.write(f"{idx}. {nome}")
        else:
            st.info("Ordem não encontrada para o produto selecionado.")

        if st.button("Limpar ordens"):
            st.session_state['ordens'] = None
            st.rerun()
    else:
        st.info("Ainda não há ordens calculadas.")
