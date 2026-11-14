from enum import Enum as PythonEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class ResultadoPagamento(str, PythonEnum):
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id"),
        nullable=False,
        unique=True,
    )
    resultado = Column(Enum(ResultadoPagamento), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    pedido = relationship("Pedido")