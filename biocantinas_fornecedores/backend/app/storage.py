from typing import List
from .schemas import Fornecedor, FornecedorCreate
from datetime import date

# “BD” em memória
_fornecedores: List[Fornecedor] = []
_next_id = 1

def criar_fornecedor(data: FornecedorCreate) -> Fornecedor:
    global _next_id
    fornecedor = Fornecedor(
        id=_next_id,
        aprovado=False,
        **data.dict()
    )
    _fornecedores.append(fornecedor)
    _next_id += 1
    return fornecedor

def listar_fornecedores() -> List[Fornecedor]:
    return _fornecedores

def obter_fornecedor(fid: int) -> Fornecedor | None:
    return next((f for f in _fornecedores if f.id == fid), None)

def atualizar_fornecedor(f: Fornecedor) -> None:
    for i, atual in enumerate(_fornecedores):
        if atual.id == f.id:
            _fornecedores[i] = f
            break
