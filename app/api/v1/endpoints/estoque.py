from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_manager, get_current_user
from app.db.session import get_db
from app.models.estoque import Estoque
from app.models.pratos import Prato
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from app.schemas.estoque import EstoqueResponse, MovimentacaoEstoque

router = APIRouter(prefix="/unidades", tags=["Estoque"])


@router.get(
    "/{id_unidade}/pratos/{id_prato}/estoque",
    response_model=EstoqueResponse,
)
def consultar_estoque(
    id_unidade: int,    
    id_prato: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    estoque = db.query(Estoque).filter(
        Estoque.id_unidade == id_unidade,
        Estoque.id_prato == id_prato,
    ).first()

    if estoque is None:
        raise HTTPException(status_code=404, detail="Estoque não encontrado")

    return estoque


@router.post(
    "/{id_unidade}/pratos/{id_prato}/estoque/movimentacoes",
    response_model=EstoqueResponse,
)
def movimentar_estoque(
    id_unidade: int,
    id_prato: int,
    movimentacao: MovimentacaoEstoque,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_manager),
):
    if db.query(Unidade).filter(Unidade.id == id_unidade).first() is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")

    if db.query(Prato).filter(Prato.id == id_prato).first() is None:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    estoque = db.query(Estoque).filter(
        Estoque.id_unidade == id_unidade,
        Estoque.id_prato == id_prato,
    ).first()

    if movimentacao.tipo == "saida" and (
        estoque is None or estoque.quantidade < movimentacao.quantidade
    ):
        raise HTTPException(status_code=409, detail="Estoque insuficiente")

    if estoque is None:
        estoque = Estoque(
            id_unidade=id_unidade,
            id_prato=id_prato,
            quantidade=0,
        )
        db.add(estoque)

    if movimentacao.tipo == "entrada":
        estoque.quantidade += movimentacao.quantidade
    else:
        estoque.quantidade -= movimentacao.quantidade

    db.commit()
    db.refresh(estoque)
    return estoque