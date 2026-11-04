from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

# Chave secreta super importante (em produção, isso ficaria no arquivo .env)
SECRET_KEY = "sua_chave_secreta_super_segura_aqui_mude_depois"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # O token expira em 30 minutos

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt