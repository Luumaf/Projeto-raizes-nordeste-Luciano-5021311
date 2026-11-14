from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.db.session import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    perfil = Column(String, nullable=False, default="CLIENTE", server_default="CLIENTE")
    consentimento_fidelidade = Column(Boolean,nullable=False,default=False,server_default="0",)
    consentimento_fidelidade_em = Column(DateTime, nullable=True)
    consentimento_fidelidade_revogado_em = Column(DateTime, nullable=True)