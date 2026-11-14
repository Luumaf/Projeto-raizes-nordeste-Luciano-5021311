from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, func

from app.db.session import Base
from app.models.pedido import StatusPedido


class HistoricoStatusPedido(Base):
    __tablename__ = "historico_status_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    status = Column(Enum(StatusPedido), nullable=False)
    alterado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    alterado_em = Column(DateTime, nullable=False, server_default=func.now())