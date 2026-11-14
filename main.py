from fastapi import FastAPI
from app.api.v1.endpoints import estoque, pedidos, pratos, unidades, usuarios
from app.db.session import engine, Base
from app.models.estoque import Estoque
from app.models.pratos import Prato
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from app.models.pedido import ItemPedido, Pedido
from app.models.pagamento import Pagamento
from app.models.historico_status_pedido import HistoricoStatusPedido
from app.models.pontos_fidelidade import PontosFidelidade


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raízes do Nordeste API de Luciano",
    description="API desenvolvida para o projeto acadêmico da Uninter de Luciano Gomes Martines Filho.",
    version="1.0.0",
)

# Inclui as rotas de usuarios na aplicacao principal
app.include_router(usuarios.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(pratos.router, prefix="/api/v1", tags=["Pratos"])
app.include_router(unidades.router, prefix="/api/v1")
app.include_router(estoque.router, prefix="/api/v1")
app.include_router(pedidos.router, prefix="/api/v1")


@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo à API Raízes do Nordeste de Luciano!"}