import bcrypt

def hash_senha(senha_plana: str) -> str:
    """
    Gera um hash seguro com Salt aleatório utilizando bcrypt (Requisito B5).
    Nunca armazena senhas em texto claro.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(senha_plana.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verificar_senha(senha_plana: str, hash_armazenado: str) -> bool:
    """
    Verifica se a senha plana corresponde ao hash armazenado com sal.
    """
    try:
        return bcrypt.checkpw(senha_plana.encode('utf-8'), hash_armazenado.encode('utf-8'))
    except Exception:
        return False
