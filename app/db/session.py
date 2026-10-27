from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Ajuste para o SQLite aceitar requisições do FastAPI corretamente
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args) # Cria o motor de conexao com o banco de dados usando a URL do .env / 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Fabrica de sessoes para interagir com o banco / Cada requisicao que chegar na API precisara de uma sessao propria para fazer consultas ou salvamentos... essa fabrica cria e gerencia essas sessoes.

Base = declarative_base() # Base declarativa para as tabelas herdarem


# Funcao utilitaria para injetar a sessao do banco nas rotas da API / gerenciador de contexto (usar Depends no FastAPI) para garantir que a sessao do banco seja sempre aberta para a requisicao e fechada logo em seguida, evitando vazamentos de memória.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()