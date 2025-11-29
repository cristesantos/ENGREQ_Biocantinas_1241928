from fastapi import FastAPI, HTTPException
from typing import List
from . import schemas, storage, services

app = FastAPI(title="BioCantinas - Fornecedores")

@app.post("/fornecedores", response_model=schemas.Fornecedor)
def criar_fornecedor(fornecedor: schemas.FornecedorCreate):
    return storage.criar_fornecedor(fornecedor)

@app.get("/fornecedores", response_model=List[schemas.Fornecedor])
def listar_fornecedores():
    return storage.listar_fornecedores()

@app.get("/fornecedores/{fid}", response_model=schemas.Fornecedor)
def obter_fornecedor(fid: int):
    f = storage.obter_fornecedor(fid)
    if not f:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return f

@app.patch("/fornecedores/{fid}/aprovacao", response_model=schemas.Fornecedor)
def aprovar_fornecedor(fid: int, body: schemas.FornecedorUpdateAprovacao):
    try:
        return services.aprovar_fornecedor(fid, body.aprovado)
    except ValueError:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

@app.get("/fornecedores/ordem", response_model=List[schemas.OrdemFornecedor])
def obter_ordem_por_produto():
    return services.calcular_ordem_por_produto()
