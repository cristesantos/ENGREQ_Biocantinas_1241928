
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
