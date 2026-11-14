from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from app.models.pagamento import ResultadoPagamento
from pydantic import BaseModel, ConfigDict, Field
from app.models.pedido import CanalPedido, StatusPedido



class ItemPedidoCreate(BaseModel):
    prato_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class PedidoCreate(BaseModel):
    unidade_id: int = Field(gt=0)
    canal_pedido: CanalPedido
    itens: List[ItemPedidoCreate] = Field(min_length=1)
    usuario_id: Optional[int] = Field(default=None, gt=0)


class ItemPedidoResponse(BaseModel):
    id: int
    prato_id: int
    quantidade: int
    preco_unitario: Decimal

    model_config = ConfigDict(from_attributes=True)

class HistoricoStatusResponse(BaseModel):
    status: StatusPedido
    alterado_por_id: Optional[int]
    alterado_em: datetime

    model_config = ConfigDict(from_attributes=True)

class PedidoResponse(BaseModel):
    id: int
    unidade_id: int
    usuario_id: Optional[int]
    canal_pedido: CanalPedido
    status: StatusPedido
    total: Decimal
    criado_em: datetime
    itens: List[ItemPedidoResponse]
    historico_status: List[HistoricoStatusResponse]

    model_config = ConfigDict(from_attributes=True)


class AtualizarStatusPedido(BaseModel):
    status: StatusPedido


class PagamentoMockRequest(BaseModel):
    resultado: ResultadoPagamento


class PagamentoResponse(BaseModel):
    id: int
    pedido_id: int
    resultado: ResultadoPagamento
    valor: Decimal
    pedido_status: StatusPedido
    criado_em: datetime
    pontos_creditados: int = 0
