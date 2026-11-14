from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.usuario import Usuario
from app.models.pontos_fidelidade import PontosFidelidade
from app.schemas.fidelidade import FidelidadeResponse
from app.schemas.usuario import (
    ConsentimentoFidelidadeUpdate,
    UsuarioCreate,
    UsuarioResponse,
)
from app.core.security import gerar_hash_senha, verificar_senha
from app.core.config_jwt import criar_access_token
from app.core.deps import get_current_user


# Instância do roteador para o FastAPI
router = APIRouter(prefix="/usuarios", tags=["Usuários e Autenticação"])

# Schema específico para validar o login (apenas email e senha)
class LoginSchema(BaseModel):
    email: str
    senha: str

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica se o e-mail já existe
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado no sistema."
        )
    
    # Cria o usuário com a senha criptografada (hash)
    senha_criptografada = gerar_hash_senha(usuario.senha)
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_criptografada,  # Usando o campo correto do seu model
        ativo=True
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # O OAuth2PasswordRequestForm lê 'username' (que será o seu email) e 'password'
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = criar_access_token(data={"sub": usuario.email})
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/me", response_model=UsuarioResponse)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna os dados do utilizador atualmente autenticado através do token JWT.
    """
    return current_user


@router.patch("/me/fidelidade/consentimento")
def atualizar_consentimento_fidelidade(
    dados: ConsentimentoFidelidadeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    agora = datetime.now(timezone.utc).replace(tzinfo=None)

    if dados.consentir:
        if not current_user.consentimento_fidelidade:
            current_user.consentimento_fidelidade_em = agora
        current_user.consentimento_fidelidade = True
        current_user.consentimento_fidelidade_revogado_em = None
    else:
        if current_user.consentimento_fidelidade:
            current_user.consentimento_fidelidade_revogado_em = agora
        current_user.consentimento_fidelidade = False

    db.commit()
    db.refresh(current_user)
    return {
        "consentimento_fidelidade": current_user.consentimento_fidelidade,
        "consentimento_fidelidade_em": current_user.consentimento_fidelidade_em,
        "consentimento_fidelidade_revogado_em": (
            current_user.consentimento_fidelidade_revogado_em
        ),
    }


@router.get("/me/fidelidade", response_model=FidelidadeResponse)
def consultar_fidelidade(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    saldo = db.query(func.coalesce(func.sum(PontosFidelidade.pontos), 0)).filter(
        PontosFidelidade.usuario_id == current_user.id
    ).scalar()
    historico = (
        db.query(PontosFidelidade)
        .filter(PontosFidelidade.usuario_id == current_user.id)
        .order_by(PontosFidelidade.criado_em.desc(), PontosFidelidade.id.desc())
        .all()
    )
    return {"saldo_pontos": saldo, "historico": historico}