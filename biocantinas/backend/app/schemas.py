from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from enum import Enum


class Role(str, Enum):
    gestor = "gestor"
    produtor = "produtor"
    outro = "outro"


class ProdutoFornecedor(BaseModel):
    nome: str
    intervalo_producao_inicio: date
    intervalo_producao_fim: date
    capacidade: int

class FornecedorCreate(BaseModel):
    nome: str
    data_inscricao: date
    produtos: List[ProdutoFornecedor]

class Fornecedor(FornecedorCreate):
    id: int
    aprovado: bool

class FornecedorUpdateAprovacao(BaseModel):
    aprovado: bool

class OrdemFornecedor(BaseModel):
    produto: str
    fornecedores_ids: List[int]


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role


class User(BaseModel):
    id: int
    username: str
    role: Role


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
