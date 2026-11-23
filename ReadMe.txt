-- Requisitos

Python 3.11
FastAPI e Uvicorn
SQLAlchemy
Pydantic
SQLite para execução local
Dependências Python listadas em "requirements.txt"



-- Como configurar as variáveos de ambiente

Na raiz do projeto, criar um arquivo .env com a URL do banco SQLite:

```env
DATABASE_URL=sqlite:///./raizes_nordeste.db



-- Como instalar as dependências

na pasta raiz do projeto, tem que criar o ambiente virtual e instalar as dependências:

py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt



--Banco de dados e dados iniciais

 Ao iniciar a aplicação, o SQLAlchemy cria as tabelas que ainda não existem.  Os dados necessários para os testes tem que ser preparados previamente pelo fluxo disponível na API



-- Como iniciar a API
python -m uvicorn main:app --reload

A API ficará disponível em http://127.0.0.1:8000



-- Como acessar a Documentação Swagger/OpenAPI

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
Especificação OpenAPI em JSON: http://127.0.0.1:8000/openapi.json



-- Como rodar os testes

os testes podem ser feitos manualmente pelo Swagger em http://127.0.0.1:8000/docs , utilizando dados de teste e registrando as requisições, respostas e resultados obtidos.


