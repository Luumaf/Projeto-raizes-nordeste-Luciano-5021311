from datetime import datetime
from decimal import Decimal
from enum import Enum as PythonEnum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class CanalPedido(str, PythonEnum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"


class StatusPedido(str, PythonEnum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGAMENTO_RECUSADO = "PAGAMENTO_RECUSADO"
    PAGO = "PAGO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidade.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    canal_pedido = Column(Enum(CanalPedido), nullable=False)
    status = Column(
        Enum(StatusPedido),
        nullable=False,
        default=StatusPedido.AGUARDANDO_PAGAMENTO,)
    total = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    criado_em = Column(DateTime, nullable=False, server_default=func.now())
    unidade = relationship("Unidade")
    usuario = relationship("Usuario")
    itens = relationship(
        "ItemPedido",
        back_populates="pedido",
        cascade="all, delete-orphan",)

    historico_status = relationship("HistoricoStatusPedido",order_by="HistoricoStatusPedido.id",cascade="all, delete-orphan",)


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    prato_id = Column(Integer, ForeignKey("pratos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    pedido = relationship("Pedido", back_populates="itens")
    prato = relationship("Prato")