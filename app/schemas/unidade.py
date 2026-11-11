from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UnidadeCreate(BaseModel):
    nome: str = Field(min_length=1)
    endereco: Optional[str] = None


class UnidadeResponse(UnidadeCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
