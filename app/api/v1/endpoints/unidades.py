from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_manager
from app.db.session import get_db
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from app.schemas.unidade import UnidadeCreate, UnidadeResponse

router = APIRouter(prefix="/unidades", tags=["Unidades"])


@router.get("/", response_model=List[UnidadeResponse])
def listar_unidades(db: Session = Depends(get_db)):
    return db.query(Unidade).all()


@router.post(
    "/",
    response_model=UnidadeResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_unidade(
    unidade: UnidadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_manager),
):
    nova_unidade = Unidade(
        nome=unidade.nome,
        endereco=unidade.endereco,
    )
    db.add(nova_unidade)
    db.commit()
    db.refresh(nova_unidade)
    return nova_unidade
