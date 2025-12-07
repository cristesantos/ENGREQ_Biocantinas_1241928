
import sqlite3
from typing import List, Optional
from .schemas import Fornecedor, FornecedorCreate, ProdutoFornecedor
from datetime import date

DB_PATH = "biocantinas.db"

def _init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_inscricao TEXT NOT NULL,
        aprovado INTEGER NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fornecedor_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        intervalo_producao_inicio TEXT NOT NULL,
        intervalo_producao_fim TEXT NOT NULL,
        capacidade INTEGER NOT NULL,
        FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
    )
    """)
    conn.commit()
    conn.close()

_init_db()

# --- Users and tokens tables ---
def _init_auth_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn.commit()
    conn.close()


_init_auth_tables()

def criar_fornecedor(data: FornecedorCreate) -> Fornecedor:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO fornecedores (nome, data_inscricao, aprovado) VALUES (?, ?, ?)",
        (data.nome, str(data.data_inscricao), 0)
    )
    fornecedor_id = c.lastrowid
    for prod in data.produtos:
        c.execute(
            "INSERT INTO produtos (fornecedor_id, nome, intervalo_producao_inicio, intervalo_producao_fim, capacidade) VALUES (?, ?, ?, ?, ?)",
            (fornecedor_id, prod.nome, str(prod.intervalo_producao_inicio), str(prod.intervalo_producao_fim), prod.capacidade)
        )
    conn.commit()
    conn.close()
    return obter_fornecedor(fornecedor_id)

def listar_fornecedores() -> List[Fornecedor]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nome, data_inscricao, aprovado FROM fornecedores")
    fornecedores = []
    for row in c.fetchall():
        fid, nome, data_inscricao, aprovado = row
        c.execute("SELECT nome, intervalo_producao_inicio, intervalo_producao_fim, capacidade FROM produtos WHERE fornecedor_id=?", (fid,))
        produtos = [
            ProdutoFornecedor(
                nome=p[0],
                intervalo_producao_inicio=date.fromisoformat(p[1]),
                intervalo_producao_fim=date.fromisoformat(p[2]),
                capacidade=p[3]
            ) for p in c.fetchall()
        ]
        fornecedores.append(
            Fornecedor(
                id=fid,
                nome=nome,
                data_inscricao=date.fromisoformat(data_inscricao),
                aprovado=bool(aprovado),
                produtos=produtos
            )
        )
    conn.close()
    return fornecedores

def obter_fornecedor(fid: int) -> Optional[Fornecedor]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nome, data_inscricao, aprovado FROM fornecedores WHERE id=?", (fid,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    fid, nome, data_inscricao, aprovado = row
    c.execute("SELECT nome, intervalo_producao_inicio, intervalo_producao_fim, capacidade FROM produtos WHERE fornecedor_id=?", (fid,))
    produtos = [
        ProdutoFornecedor(
            nome=p[0],
            intervalo_producao_inicio=date.fromisoformat(p[1]),
            intervalo_producao_fim=date.fromisoformat(p[2]),
            capacidade=p[3]
        ) for p in c.fetchall()
    ]
    conn.close()
    return Fornecedor(
        id=fid,
        nome=nome,
        data_inscricao=date.fromisoformat(data_inscricao),
        aprovado=bool(aprovado),
        produtos=produtos
    )

def atualizar_fornecedor(f: Fornecedor) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE fornecedores SET nome=?, data_inscricao=?, aprovado=? WHERE id=?", (f.nome, str(f.data_inscricao), int(f.aprovado), f.id))
    conn.commit()
    conn.close()


# --- Authentication storage helpers ---
def create_user(username: str, password_hash: str, salt: str, role: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)", (username, password_hash, salt, role))
    uid = c.lastrowid
    conn.commit()
    conn.close()
    return {"id": uid, "username": username, "role": role}


def get_user_by_username(username: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, salt, role FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    uid, uname, password_hash, salt, role = row
    return {"id": uid, "username": uname, "password_hash": password_hash, "salt": salt, "role": role}


def get_user_by_id(uid: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users WHERE id=?", (uid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "username": row[1], "role": row[2]}


def create_token(token: str, user_id: int, expires_at: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO tokens (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires_at))
    conn.commit()
    conn.close()


def get_user_by_token(token: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, expires_at FROM tokens WHERE token=?", (token,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    user_id, expires_at = row
    c.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    conn.close()
    if not u:
        return None
    return {"id": u[0], "username": u[1], "role": u[2], "expires_at": expires_at}


def delete_token(token: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM tokens WHERE token=?", (token,))
    conn.commit()
    conn.close()
