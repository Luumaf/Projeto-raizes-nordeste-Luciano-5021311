from pydantic import BaseModel, ConfigDict
from typing import Optional

class PratoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    disponivel: Optional[bool] = True

class PratoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    disponivel: bool

    model_config = ConfigDict(from_attributes=True)