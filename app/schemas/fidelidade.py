from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PontosFidelidadeResponse(BaseModel):
    id: int
    pedido_id: int
    pontos: int
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class FidelidadeResponse(BaseModel):
    saldo_pontos: int
    historico: list[PontosFidelidadeResponse]
