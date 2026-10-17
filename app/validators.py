"""
Módulo de Validações e Formatações
Governança via component-builder e a11y-auditor
"""
import re

def limpar_digitos(valor: str) -> str:
    """Remove todos os caracteres que não sejam dígitos numéricos."""
    if not valor:
        return ""
    return re.sub(r"\D", "", valor)


def validar_cpf(cpf: str) -> tuple[bool, str]:
    """
    Valida CPF pelo algoritmo oficial dos dois dígitos verificadores (Módulo 11).
    Rejeita tamanhos inválidos e sequências com todos os dígitos iguais.
    """
    digitos = limpar_digitos(cpf)
    
    if len(digitos) != 11:
        return False, f"CPF deve conter exatamente 11 dígitos numéricos (informado: {len(digitos)})."
    
    # Rejeita CPFs com todos os dígitos iguais (ex: 111.111.111-11)
    if digitos == digitos[0] * 11:
        return False, "CPF inválido (sequência com dígitos repetidos não é aceita pela Receita Federal)."
    
    # 1º Dígito Verificador
    soma_1 = sum(int(digitos[i]) * (10 - i) for i in range(9))
    resto_1 = soma_1 % 11
    d1 = 0 if resto_1 < 2 else 11 - resto_1
    
    if int(digitos[9]) != d1:
        return False, "CPF inválido (primeiro dígito verificador incorreto)."
    
    # 2º Dígito Verificador
    soma_2 = sum(int(digitos[i]) * (11 - i) for i in range(10))
    resto_2 = soma_2 % 11
    d2 = 0 if resto_2 < 2 else 11 - resto_2
    
    if int(digitos[10]) != d2:
        return False, "CPF inválido (segundo dígito verificador incorreto)."
    
    return True, "CPF válido."


def validar_cnpj(cnpj: str) -> tuple[bool, str]:
    """
    Valida CNPJ pelo algoritmo oficial dos dois dígitos verificadores (Módulo 11).
    """
    digitos = limpar_digitos(cnpj)
    
    if len(digitos) != 14:
        return False, f"CNPJ deve conter exatamente 14 dígitos numéricos (informado: {len(digitos)})."
    
    if digitos == digitos[0] * 14:
        return False, "CNPJ inválido (sequência repetida)."
    
    # 1º Dígito Verificador
    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma_1 = sum(int(digitos[i]) * pesos_1[i] for i in range(12))
    resto_1 = soma_1 % 11
    d1 = 0 if resto_1 < 2 else 11 - resto_1
    
    if int(digitos[12]) != d1:
        return False, "CNPJ inválido (primeiro dígito verificador incorreto)."
    
    # 2º Dígito Verificador
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma_2 = sum(int(digitos[i]) * pesos_2[i] for i in range(13))
    resto_2 = soma_2 % 11
    d2 = 0 if resto_2 < 2 else 11 - resto_2
    
    if int(digitos[13]) != d2:
        return False, "CNPJ inválido (segundo dígito verificador incorreto)."
    
    return True, "CNPJ válido."


def validar_cpf_cnpj(doc: str) -> tuple[bool, str]:
    """
    Roteia automaticamente a validação conforme a quantidade de dígitos (11 = CPF, 14 = CNPJ).
    """
    digitos = limpar_digitos(doc)
    if len(digitos) == 11:
        return validar_cpf(digitos)
    elif len(digitos) == 14:
        return validar_cnpj(digitos)
    else:
        return False, f"Documento deve possuir 11 dígitos (CPF) ou 14 dígitos (CNPJ). Informado: {len(digitos)} dígitos."


def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida se o formato do e-mail atende aos padrões estabelecidos pela RFC 5322.
    """
    if not email or not email.strip():
        return False, "O endereço de e-mail não pode ser vazio."
    
    email_limpo = email.strip()
    padrao = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    
    if not re.match(padrao, email_limpo):
        return False, "Formato de e-mail inválido. Exemplo esperado: usuario@dominio.com."
    
    if len(email_limpo) > 100:
        return False, "O endereço de e-mail excede o limite de 100 caracteres permitido."
    
    return True, "E-mail válido."


def validar_telefone(tel: str) -> tuple[bool, str]:
    """
    Valida telefone brasileiro (fixo: DDD + 8 dígitos ou celular: DDD + 9 dígitos).
    Campo opcional: se vazio, retorna True.
    """
    if not tel or not tel.strip():
        return True, "Telefone opcional não informado."
    
    digitos = limpar_digitos(tel)
    
    if len(digitos) not in [10, 11]:
        return False, f"Telefone brasileiro deve conter DDD + 8 dígitos (fixo) ou 9 dígitos (celular). Informado: {len(digitos)} dígitos."
    
    ddd = int(digitos[:2])
    if ddd < 11 or ddd > 99:
        return False, f"DDD '{ddd}' inválido. Deve estar entre 11 e 99."
    
    if len(digitos) == 11 and digitos[2] != '9':
        return False, "Celulares de 11 dígitos devem iniciar com o dígito 9 após o DDD."
    
    return True, "Telefone válido."


def formatar_moeda(val: float) -> str:
    """Formata valor float para moeda brasileira (ex: R$ 1.500,50)."""
    if val is None:
        return "R$ 0,00"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def validar_numero_conta(num_conta: str) -> tuple[bool, str]:
    """
    Valida o número da conta bancária.
    Deve seguir o formato padrão da agência: 4 a 6 dígitos seguidos de hífen e dígito (ex: 10001-X, 10099-0).
    Bloqueia estritamente inserção de letras aleatórias como 'aasdad'.
    """
    if not num_conta or not num_conta.strip():
        return False, "O número da conta não pode ser vazio."
    
    conta_limpa = num_conta.strip().upper()
    padrao = r"^\d{4,6}-[0-9X]$"
    
    if not re.match(padrao, conta_limpa):
        return False, f"Número de conta '{num_conta}' inválido. O formato obrigatório é números seguidos de hífen e dígito verificador (ex: 10001-X ou 10023-0). Letras avulsas não são permitidas."
    
    return True, "Número de conta válido."


def validar_numero_cartao(n_cartao: str) -> tuple[bool, str]:
    """
    Valida o número do cartão bancário.
    Deve conter exatamente 16 dígitos numéricos. Bloqueia letras e caracteres não numéricos.
    """
    if not n_cartao or not n_cartao.strip():
        return False, "O número do cartão não pode ser vazio."
    
    cartao_limpo = limpar_digitos(n_cartao)
    
    # Se continha letras antes de limpar
    if re.search(r"[a-zA-Z]", n_cartao):
        return False, "O número do cartão não pode conter letras. Apenas 16 dígitos numéricos são aceitos."
    
    if len(cartao_limpo) != 16:
        return False, f"O número do cartão deve conter exatamente 16 dígitos numéricos (informado: {len(cartao_limpo)} dígitos)."
    
    return True, "Número de cartão válido."



def validar_busca_id_cpf(termo: str) -> tuple[bool, str]:
    """Aceita somente dígitos ASCII para a busca incremental por ID ou CPF/CNPJ."""
    if re.search(r"[a-zA-Z]", termo):
        return False, "O campo de busca por ID/CPF aceita exclusivamente dígitos numéricos (0-9). Letras não são permitidas."
    if not re.fullmatch(r"[0-9]+", termo):
        return False, "O campo de busca por ID/CPF aceita exclusivamente dígitos numéricos (0-9)."
    return True, "Busca por ID/CPF válida."


def validar_codigo_agencia(agencia: str) -> tuple[bool, str]:
    """Exige código de agência com 1 a 5 dígitos ASCII, sem letras ou símbolos."""
    if not re.fullmatch(r"[0-9]{1,5}", agencia):
        return False, "O código da agência deve conter de 1 a 5 dígitos numéricos (0-9). Letras não são permitidas."
    return True, "Código da agência válido."
