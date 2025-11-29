from pydantic import BaseModel
from datetime import date
from typing import List, Optional

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
