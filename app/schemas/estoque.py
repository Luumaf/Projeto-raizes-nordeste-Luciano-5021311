from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class EstoqueAtualizar(BaseModel):
    quantidade: int = Field(ge=0)

class EstoqueResponse(BaseModel):
    id_unidade: int
    id_prato: int
    quantidade: int
    model_config = ConfigDict(from_attributes=True)

class MovimentacaoEstoque(BaseModel):
    tipo: Literal["entrada", "saida"]
    quantidade: int = Field(gt=0)