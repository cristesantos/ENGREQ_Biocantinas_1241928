import streamlit as st
import requests
from datetime import date
import threading
import uvicorn
import sys
import os
from pathlib import Path

# ============================================================
#  1. Ajustar sys.path para garantir import do backend
# ============================================================

ROOT = Path(__file__).resolve().parents[1]   # pasta que contém "backend"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ============================================================
#  2. Resolver API_URL (prioridade: secrets → env → local)
# ============================================================

def _resolve_api_url():
    url = None
    try:
        url = st.secrets.get("API_URL") if hasattr(st, "secrets") else None
    except Exception:
        url = None

    if not url:
        url = os.getenv("API_URL")

    if not url:
        url = "http://127.0.0.1:8000"

    return url

API_URL = _resolve_api_url()

st.set_page_config(page_title="BioCantinas - Fornecedores")
st.info(f"API_URL em uso: {API_URL}")


# ============================================================
#  2.5 Inicialização do estado de sessão (autenticação)
# ============================================================

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False


# ============================================================
#  3. Importação robusta da API FastAPI local
# ============================================================

def _import_fastapi():
    """
    Tenta importar a API independentemente da estrutura de pastas.
    Funciona em desenvolvimento local.
    """
    try:
        from backend.app.main import app as api
        return api
    except Exception:
        return None

fastapi_app = _import_fastapi()


# ============================================================
#  4. Função que inicia a API FastAPI embutida
# ============================================================

def _start_api():
    print("=== Iniciando FastAPI embutida ===")
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")


def _is_running_on_cloud():
    """STREAMLIT_RUNTIME só existe no Streamlit Cloud."""
    return "STREAMLIT_RUNTIME" in os.environ


# ============================================================
#  5. Iniciar API somente localmente
# ============================================================

if (
    fastapi_app                              # backend carregado corretamente
    and not _is_running_on_cloud()           # não rodar no Streamlit Cloud
    and "api_thread_started" not in st.session_state
):
    st.session_state.api_thread = threading.Thread(
        target=_start_api,
        daemon=True
    )
    st.session_state.api_thread.start()
    st.session_state.api_thread_started = True
    st.info("FastAPI iniciada localmente na porta 8000")


# ============================================================
#  5.5 Funções de autenticação
# ============================================================

def login(username: str, password: str):
    """Faz login e armazena o token JWT."""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data["access_token"]
            # Busca info do usuário
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            user_resp = requests.get(f"{API_URL}/auth/me", headers=headers)
            if user_resp.status_code == 200:
                st.session_state.user_info = user_resp.json()
            st.success("Login realizado com sucesso!")
            return True
        else:
            st.error(f"Erro no login: {response.json().get('detail', 'Usuário ou senha inválidos')}")
            return False
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return False


def register(username: str, password: str, role: str):
    """Registra um novo usuário."""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"username": username, "password": password, "role": role}
        )
        if response.status_code in [200, 201]:
            st.success("Usuário registrado com sucesso! Faça login agora.")
            st.session_state.show_register = False
            return True
        else:
            st.error(f"Erro no registro: {response.json().get('detail', 'Erro desconhecido')}")
            return False
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return False


def logout():
    """Faz logout."""
    st.session_state.auth_token = None
    st.session_state.user_info = None
    st.success("Logout realizado!")


# ============================================================
#  5.6 Página de login/registro (se não autenticado)
# ============================================================

if not st.session_state.auth_token:
    st.header("BioCantinas - Autenticação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login", use_container_width=True):
            st.session_state.show_register = False
    with col2:
        if st.button("Registrar", use_container_width=True):
            st.session_state.show_register = True
    
    if st.session_state.show_register:
        st.subheader("Criar nova conta")
        reg_username = st.text_input("Usuário (registro)", key="reg_username")
        reg_password = st.text_input("Senha (registro)", type="password", key="reg_password")
        reg_role = st.selectbox("Papel", ["gestor", "produtor", "outro"], key="reg_role")
        if st.button("Criar conta"):
            if reg_username and reg_password:
                register(reg_username, reg_password, reg_role)
            else:
                st.error("Preencha todos os campos!")
    else:
        st.subheader("Fazer login")
        username = st.text_input("Usuário", key="username")
        password = st.text_input("Senha", type="password", key="password")
        if st.button("Entrar"):
            if username and password:
                login(username, password)
            else:
                st.error("Preencha todos os campos!")
    st.stop()


# ============================================================
#  6. Sidebar e navegação (usuário autenticado)
# ============================================================

st.sidebar.title("BioCantinas")
st.sidebar.write(f"👤 Logado como: **{st.session_state.user_info['username']}** ({st.session_state.user_info['role']})")

if st.sidebar.button("Logout"):
    logout()
    st.rerun()

# Filtrar páginas por papel do usuário
user_role = st.session_state.user_info.get("role", "outro")
paginas_disponiveis = ["Página inicial"]

if user_role == "gestor":
    paginas_disponiveis.append("Gestor")
if user_role in ["produtor", "fornecedor"]:
    paginas_disponiveis.append("Produtor")

pagina = st.sidebar.radio("Perfil", paginas_disponiveis)


# ============================================================
#  7. Página inicial
# ============================================================

if pagina == "Página inicial":
    st.header("Bem-vindo ao BioCantinas!")
    st.write(f"Você está logado como **{st.session_state.user_info['username']}** com o papel **{st.session_state.user_info['role']}**")


# ============================================================
#  8. Páginas importadas
# ============================================================

elif pagina == "Gestor" and st.session_state.user_info.get("role") == "gestor":
    from pagina_gestor import pagina_gestor
    pagina_gestor(API_URL, st.session_state.auth_token)

elif pagina == "Produtor" and st.session_state.user_info.get("role") in ["produtor", "fornecedor"]:
    from pagina_produtor import pagina_produtor
    pagina_produtor(API_URL, st.session_state.auth_token)

else:
    st.error("Acesso negado: você não tem permissão para acessar esta página.")
