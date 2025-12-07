from fastapi import FastAPI, HTTPException, Request, Depends, status
from typing import List
from . import schemas, storage, services

from fastapi.responses import JSONResponse

app = FastAPI(title="BioCantinas - Fornecedores")


def _get_current_user(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = parts[1]
    user = services.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


def require_roles(*allowed_roles):
    def _checker(current_user: dict = Depends(_get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted for your role")
        return current_user
    return _checker


@app.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate):
    try:
        u = services.register_user(user)
        return JSONResponse(status_code=201, content={"id": u['id'], "username": u['username'], "role": u['role']})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=schemas.Token)
def login(body: schemas.LoginRequest):
    u = services.authenticate_user(body.username, body.password)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = services.create_access_token_for_user(u['id'])
    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.User)
def me(current_user: dict = Depends(_get_current_user)):
    return {"id": current_user['id'], "username": current_user['username'], "role": current_user['role']}

@app.post("/fornecedores", response_model=schemas.Fornecedor)
def criar_fornecedor(fornecedor: schemas.FornecedorCreate):
    return storage.criar_fornecedor(fornecedor)


@app.get("/gestor")
def gestor_page(current_user: dict = Depends(require_roles("gestor"))):
    return {"message": f"Olá {current_user['username']}, bem-vindo à área de Gestor."}


@app.get("/fornecedor")
def fornecedor_page(current_user: dict = Depends(require_roles("produtor", "fornecedor"))):
    # aceita tanto role 'produtor' quanto 'fornecedor' se houver confusão de nomes
    return {"message": f"Olá {current_user['username']}, área do fornecedor."}

@app.get("/fornecedores", response_model=List[schemas.Fornecedor])
def listar_fornecedores():
    return storage.listar_fornecedores()

# Rota fixa deve vir antes da dinâmica!
@app.get("/fornecedores/ordem_fornecedor", response_model=List[schemas.OrdemFornecedor])
def obter_ordem_por_produto():
    return services.calcular_ordem_por_produto()

@app.get("/fornecedores/{fid}", response_model=schemas.Fornecedor)
def obter_fornecedor(fid: int):
    f = storage.obter_fornecedor(fid)
    if not f:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return f

@app.patch("/fornecedores/{fid}/aprovacao", response_model=schemas.Fornecedor)
def aprovar_fornecedor(fid: int, body: schemas.FornecedorUpdateAprovacao, current_user: dict = Depends(require_roles("gestor"))):
    try:
        return services.aprovar_fornecedor(fid, body.aprovado)
    except ValueError:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
