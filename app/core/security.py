import bcrypt

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Projeto_de_Faculdade_Luciano1995"""
    senha_bytes = senha_pura.encode('utf-8')[:72]
    return bcrypt.checkpw(senha_bytes, senha_hash.encode('utf-8'))

def gerar_hash_senha(senha: str) -> str:
    """Projeto_de_Faculdade_Luciano1995"""
    senha_bytes = senha.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    return hash_bytes.decode('utf-8')