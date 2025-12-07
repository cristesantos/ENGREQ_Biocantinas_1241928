from typing import List, Dict
from .schemas import Fornecedor, OrdemFornecedor
from .storage import listar_fornecedores, obter_fornecedor, atualizar_fornecedor
from datetime import date, datetime, timedelta
import hashlib
import secrets
import os
from typing import Optional
from jose import jwt, JWTError
from .storage import create_user, get_user_by_username, get_user_by_id
from .schemas import UserCreate

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def aprovar_fornecedor(fid: int, aprovado: bool) -> Fornecedor:
    fornecedor = obter_fornecedor(fid)
    if not fornecedor:
        raise ValueError("Fornecedor não encontrado")
    fornecedor.aprovado = aprovado
    atualizar_fornecedor(fornecedor)
    return fornecedor

def calcular_ordem_por_produto() -> List[OrdemFornecedor]:
    fornecedores = [f for f in listar_fornecedores() if f.aprovado]

    mapa: Dict[str, List[Fornecedor]] = {}

    for f in fornecedores:
        # garantir que a data esteja no formato date
        if isinstance(f.data_inscricao, str):
            f.data_inscricao = date.fromisoformat(f.data_inscricao)

        for p in f.produtos:
            mapa.setdefault(p.nome, []).append(f)

    ordens: List[OrdemFornecedor] = []
    for nome_produto, lista in mapa.items():
        lista_ordenada = sorted(lista, key=lambda f: f.data_inscricao)
        ordens.append(
            OrdemFornecedor(
                produto=nome_produto,
                fornecedores_ids=[f.id for f in lista_ordenada]
            )
        )
    return ordens


# --- Authentication services (simple token-based using DB) ---
def _hash_password(password: str, salt: Optional[str] = None) -> (str, str):
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwd_hash.hex(), salt


def register_user(user: UserCreate) -> dict:
    existing = get_user_by_username(user.username)
    if existing:
        raise ValueError("Usuário já existe")
    pwd_hash, salt = _hash_password(user.password)
    u = create_user(user.username, pwd_hash, salt, user.role.value)
    return u


def authenticate_user(username: str, password: str) -> Optional[dict]:
    u = get_user_by_username(username)
    if not u:
        return None
    stored_hash = u.get('password_hash')
    salt = u.get('salt')
    calc_hash, _ = _hash_password(password, salt)
    if calc_hash != stored_hash:
        return None
    return {"id": u['id'], "username": u['username'], "role": u['role']}


def create_access_token_for_user(user_id: int, expires_minutes: int = 60) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_user_from_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            return None
        user_id = int(sub)
    except JWTError:
        return None
    u = get_user_by_id(user_id)
    if not u:
        return None
    return {"id": u['id'], "username": u['username'], "role": u['role']}