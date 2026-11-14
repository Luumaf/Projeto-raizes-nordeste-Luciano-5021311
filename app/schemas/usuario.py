from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UsuarioBase(BaseModel):
    nome: str
    email: str


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    perfil: str
    consentimento_fidelidade: bool
    consentimento_fidelidade_em: Optional[datetime]
    consentimento_fidelidade_revogado_em: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ConsentimentoFidelidadeUpdate(BaseModel):
    consentir: bool