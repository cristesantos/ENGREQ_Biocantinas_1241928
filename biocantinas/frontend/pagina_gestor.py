import streamlit as st
import requests

def list_fornecedores(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores", headers=headers)
    r.raise_for_status()
    return r.json()

def patch_aprovacao(API_URL, auth_token, fid, aprovado: bool):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.patch(
        f"{API_URL}/fornecedores/{fid}/aprovacao",
        json={"aprovado": aprovado},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()

def get_ordem(API_URL, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/fornecedores/ordem_fornecedor", headers=headers)
    r.raise_for_status()
    return r.json()

def pagina_gestor(API_URL, auth_token):
    st.header("Gestão de Fornecedores")

    if st.button("Recarregar lista"):
        st.rerun()

    fornecedores = list_fornecedores(API_URL, auth_token)
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
                        patch_aprovacao(API_URL, auth_token, f["id"], True)
                        st.rerun()
            with col3:
                if f["aprovado"]:
                    if st.button("Reprovar", key=f"rp_{f['id']}"):
                        patch_aprovacao(API_URL, auth_token, f["id"], False)
                        st.rerun()
    else:
        st.info("Ainda não há fornecedores.")

    st.subheader("Ordem de fornecimento por produto")

    # Inicializar estado
    if 'ordens' not in st.session_state:
        st.session_state['ordens'] = None

    if st.button("Calcular ordem"):
        try:
            st.session_state['ordens'] = get_ordem(API_URL, auth_token)
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro ao calcular ordem: {e.response.status_code} - {e.response.text}")
            st.session_state['ordens'] = []

    ordens = st.session_state.get('ordens')

    if ordens is None:
        st.info("Clique em 'Calcular ordem' para carregar ordens.")
    elif ordens:
        # mapa id -> fornecedor para apresentar nomes e capacidades
        id_to_fornecedor = {f['id']: f for f in fornecedores}

        produtos = sorted([o['produto'] for o in ordens], key=lambda s: s.lower())
        produto_sel = st.selectbox("Produto", options=produtos, key='produto_sel')

        ordem = next((o for o in ordens if o['produto'] == produto_sel), None)
        if ordem:
            st.write("Lista de agricultores por ordem de inscrição:")
            for idx, fid in enumerate(ordem['fornecedores_ids'], start=1):
                forn = id_to_fornecedor.get(fid)
                if forn:
                    # procurar o produto dentro dos produtos do fornecedor (case-insensitive)
                    capacidade = None
                    for p in forn.get('produtos', []):
                        if p.get('nome', '').lower() == produto_sel.lower():
                            capacidade = p.get('capacidade')
                            break
                    cap_text = f"{capacidade} unidades" if capacidade is not None else "capacidade desconhecida"
                    st.write(f"{idx}. {forn['nome']} — {cap_text}")
                else:
                    st.write(f"{idx}. {fid} — fornecedor não encontrado")
        # Botão para mostrar todas as ordens (cada produto com sua lista de fornecedores e capacidades)
        if st.button("Mostrar todas as ordens"):
            for o in ordens:
                with st.expander(f"{o['produto']} ({len(o.get('fornecedores_ids', []))} fornecedores)"):
                    if not o.get('fornecedores_ids'):
                        st.write("Nenhum fornecedor para este produto.")
                        continue
                    for idx, fid in enumerate(o['fornecedores_ids'], start=1):
                        forn = id_to_fornecedor.get(fid)
                        if forn:
                            capacidade = None
                            for p in forn.get('produtos', []):
                                if p.get('nome', '').lower() == o['produto'].lower():
                                    capacidade = p.get('capacidade')
                                    break
                            cap_text = f"{capacidade} unidades" if capacidade is not None else "capacidade desconhecida"
                            st.write(f"{idx}. {forn['nome']} — {cap_text}")
                        else:
                            st.write(f"{idx}. {fid} — fornecedor não encontrado")
        else:
            st.info("Ordem não encontrada para o produto selecionado.")

        if st.button("Limpar ordens"):
            st.session_state['ordens'] = None
            st.rerun()
    else:
        st.info("Ainda não há ordens calculadas.")
