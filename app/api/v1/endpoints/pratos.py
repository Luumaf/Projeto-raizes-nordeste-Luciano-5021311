from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.pratos import Prato
from app.schemas.pratos import PratoCreate, PratoResponse
from app.core.deps import get_current_manager
from app.models.usuario import Usuario

router = APIRouter()

@router.get("/", response_model=List[PratoResponse])
def listar_pratos(db: Session = Depends(get_db)):
    return db.query(Prato).all()

@router.post("/", response_model=PratoResponse, status_code=status.HTTP_201_CREATED)
def criar_prato(
    prato: PratoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_manager),
):
    novo_prato = Prato(
        nome=prato.nome,
        descricao=prato.descricao,
        preco=prato.preco,
        disponivel=prato.disponivel
    )
    db.add(novo_prato)
    db.commit()
    db.refresh(novo_prato)
    return novo_prato

@router.put("/{prato_id}", response_model=PratoResponse)
def atualizar_prato(
    prato_id: int, 
    prato_data: PratoCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_manager),
):
    prato = db.query(Prato).filter(Prato.id == prato_id).first()
    if not prato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prato não encontrado")
    
    prato.nome = prato_data.nome
    prato.descricao = prato_data.descricao
    prato.preco = prato_data.preco
    prato.disponivel = prato_data.disponivel
    
    db.commit()
    db.refresh(prato)
    return prato

@router.delete("/{prato_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_prato(
    prato_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_manager),
):
    prato = db.query(Prato).filter(Prato.id == prato_id).first()
    if not prato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prato não encontrado")
    
    db.delete(prato)
    db.commit()
    return None
