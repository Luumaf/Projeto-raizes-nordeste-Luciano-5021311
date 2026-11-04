import bcrypt

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Verifica se a palavra-passe digitada confere com o hash salvo no banco."""
    # Converte para bytes e corta estritamente nos primeiros 72 bytes exigidos pelo bcrypt
    senha_bytes = senha_pura.encode('utf-8')[:72]
    return bcrypt.checkpw(senha_bytes, senha_hash.encode('utf-8'))

def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro a partir de uma palavra-passe pura."""
    senha_bytes = senha.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    return hash_bytes.decode('utf-8')