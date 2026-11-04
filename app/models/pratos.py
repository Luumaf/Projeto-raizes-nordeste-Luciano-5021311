from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.session import Base

class Prato(Base):
    __tablename__ = "pratos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(String, nullable=True)
    preco = Column(Float, nullable=False)
    disponivel = Column(Boolean, default=True)