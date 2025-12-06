import streamlit as st
import requests
from datetime import date
import threading
import uvicorn
import sys
import os
from pathlib import Path


def _resolve_api_url():
    """Resolve a API URL com precedência: st.secrets -> ENV -> localhost."""
    url = None
    # 1) st.secrets (Streamlit Cloud or local .streamlit/secrets.toml)
    try:
        url = st.secrets.get("API_URL") if hasattr(st, "secrets") else None
    except Exception:
        url = None

    # 2) variável de ambiente
    if not url:
        url = os.getenv("API_URL")

    # 3) fallback
    if not url:
        url = "http://127.0.0.1:8000"

    return url


API_URL = _resolve_api_url()

st.set_page_config(page_title="BioCantinas - Fornecedores")
st.info(f"API_URL em uso: {API_URL}")

# Tentar importar o app FastAPI localmente; se falhar, desativar servidor embebido
fastapi_app = None
try:
    from biocantinas.backend.app.main import app as fastapi_app
except ImportError:
    # Em ambiente de deploy (ex: Streamlit Cloud), a estrutura é diferente
    # Tentar adicionar o path pai ao sys.path e reimportar
    try:
        backend_path = Path(__file__).parent.parent / "backend"
        if backend_path.exists():
            sys.path.insert(0, str(backend_path.parent))
            from biocantinas.backend.app.main import app as fastapi_app
    except ImportError:
        st.warning("⚠️ Servidor FastAPI embebido não disponível. Certifique-se que a API está a correr em http://127.0.0.1:8000")
        fastapi_app = None

# Start FastAPI server once per Streamlit session (apenas se disponível localmente)
def _start_api():
    if fastapi_app:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")

if fastapi_app and "api_thread_started" not in st.session_state:
    st.session_state.api_thread = threading.Thread(target=_start_api, daemon=True)
    st.session_state.api_thread.start()
    st.session_state.api_thread_started = True
    st.info("FastAPI iniciado em background na porta 8000")


st.sidebar.title("BioCantinas")
pagina = st.sidebar.radio("Perfil", ["Página inicial", "Gestor", "Produtor"])

# Página inicial
if pagina == "Página inicial":
    st.header("Bem-vindo ao BioCantinas!")
    st.write("Selecione uma opção na barra lateral.")

# Importar páginas separadas
elif pagina == "Gestor":
    from pagina_gestor import pagina_gestor
    pagina_gestor(API_URL)
elif pagina == "Produtor":
    from pagina_produtor import pagina_produtor
    pagina_produtor(API_URL)