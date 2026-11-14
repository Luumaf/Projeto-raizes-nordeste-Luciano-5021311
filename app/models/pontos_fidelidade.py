from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class PontosFidelidade(Base):
    __tablename__ = "pontos_fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    pedido_id = Column(Integer,ForeignKey("pedidos.id"),nullable=False,unique=True,)
    pontos = Column(Integer, nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())
    usuario = relationship("Usuario")
    pedido = relationship("Pedido")
