from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Unidade(Base):
    __tablename__ = "unidade"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    endereco = Column(String, nullable=True)
