from sqlalchemy import Column, ForeignKey, Integer
from app.db.session import Base


class Estoque(Base):
    __tablename__ = "estoque"

    id_unidade = Column(Integer, ForeignKey("unidade.id"), primary_key=True)
    id_prato = Column(Integer, ForeignKey("pratos.id"), primary_key=True)
    quantidade = Column(Integer, nullable=False, default=0)