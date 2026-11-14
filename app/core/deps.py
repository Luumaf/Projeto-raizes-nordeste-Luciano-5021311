from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db        
from app.models.usuario import Usuario   
from app.core.config_jwt import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/usuarios/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de autenticação",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Usuario).filter(Usuario.email == username).first()
    if user is None:
        raise credentials_exception
        
    return user


def get_current_manager(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if current_user.perfil != "GERENTE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido somente para gerentes",
        )
    return current_user


oauth2_optional_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/usuarios/login",
    auto_error=False,
)


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_optional_scheme),
    db: Session = Depends(get_db),
) -> Optional[Usuario]:
    if token is None:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None or not user.ativo:
        raise credentials_exception

    return user

def get_current_staff(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if current_user.perfil not in ("ATENDENTE", "GERENTE"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido somente para atendentes e gerentes",
        )
    return current_user