from fastapi import FastAPI
from app.api import usuarios
from app.db.session import engine, Base

# Cria as tabelas no banco de dados automaticamente ao iniciar (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raízes do Nordeste API de Luciano",
    description="API desenvolvida para o projeto acadêmico da Uninter de Luciano Gomes Martines Filho.",
    version="1.0.0",
)

# Inclui as rotas de usuarios na aplicacao principal
app.include_router(usuarios.router)


@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo à API Raízes do Nordeste de Luciano!"}