import os
import mysql.connector
from mysql.connector import Error, errorcode
from dotenv import load_dotenv

# Carrega credenciais do arquivo .env (Obrigatório fora do código)
load_dotenv()

def get_connection(user=None, password=None):
    """
    Retorna uma conexão direta com o MySQL 8.0.
    Permite passar usuário e senha para simulação dos perfis B5 (admin, atendente, auditor).
    """
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_name = os.getenv("DB_NAME", "sistema_bancario")
    db_user = user or os.getenv("DB_USER", "root")
    db_pass = password or os.getenv("DB_PASSWORD", "banco_secret")

    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_pass,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
        autocommit=False
    )
    # Garante que NOW(), CURRENT_TIMESTAMP e transações operem no fuso de Brasília (-03:00)
    try:
        cur = conn.cursor()
        cur.execute("SET time_zone = '-03:00';")
        cur.close()
    except Exception:
        pass
    return conn

def traduzir_erro_banco(err: Error) -> str:
    """
    Traduz códigos de erro do MySQL para mensagens amigáveis ao usuário final (Requisito B1).
    Evita exibir stack trace bruta do driver.
    """
    if err.errno == errorcode.ER_DUP_ENTRY:
        msg = str(err)
        if "uq_cliente_cpf_cnpj" in msg:
            return "Erro de Validação: O CPF ou CNPJ informado já está cadastrado no sistema."
        if "uq_cliente_email" in msg:
            return "Erro de Validação: O endereço de e-mail informado já pertence a outro cliente."
        if "pk_cliente_conta" in msg:
            return "Erro de Validação: Este cliente já está vinculado a esta conta bancária."
        return "Erro de Validação: Já existe um registro com os mesmos dados únicos."

    elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
        msg = str(err)
        if "fk_conta_agencia" in msg:
            return "Erro de Integridade: A agência informada não existe no cadastro."
        if "fk_trans_origem" in msg:
            return "Erro de Integridade: A conta de origem informada não existe."
        if "fk_trans_destino" in msg:
            return "Erro de Integridade: A conta de destino informada não existe."
        if "fk_cartao_conta" in msg:
            return "Erro de Integridade: A conta bancária para emissão do cartão não existe."
        return "Erro de Integridade: Um dos registros associados não foi encontrado no banco de dados."

    elif err.errno == errorcode.ER_ROW_IS_REFERENCED_2:
        return "Restrição de Integridade: Este registro não pode ser excluído pois possui movimentações ou vínculos financeiros ativos."

    elif err.errno == 3819:  # ER_CHECK_CONSTRAINT_VIOLATED
        msg = str(err)
        if "ck_trans_valor" in msg:
            return "Regra de Negócio Violada: O valor da transação deve ser estritamente positivo (maior que zero)."
        if "ck_conta_modalidade" in msg:
            return "Regra de Negócio Violada: A modalidade da conta deve ser 'CORRENTE' ou 'POUPANCA'."
        if "ck_conta_status" in msg:
            return "Regra de Negócio Violada: O status da conta deve ser 'ATIVA', 'BLOQUEADA' ou 'ENCERRADA'."
        if "ck_func_cargo" in msg:
            return "Regra de Negócio Violada: O cargo informado não faz parte do plano de cargos bancários permitido."
        if "ck_cc_tipo_titular" in msg:
            return "Regra de Negócio Violada: O tipo de titular deve ser 'TITULAR', 'CO-TITULAR' ou 'AUTORIZADO'."
        return "Regra de Negócio Violada: Uma restrição de validação (CHECK) do banco de dados impediu esta operação."

    elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        return "Controle de Acesso (Segurança): O perfil atual não possui permissão para executar esta operação no banco de dados."

    return f"Erro no Banco de Dados: {err.msg} (Código: {err.errno})"

def execute_query(sql: str, params: tuple = None, fetch_all: bool = True, user: str = None, password: str = None):
    """
    Executa consulta SELECT exclusivamente parametrizada (Prepared Statement).
    """
    conn = None
    try:
        conn = get_connection(user, password)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        result = cursor.fetchall() if fetch_all else cursor.fetchone()
        cursor.close()
        return result, None
    except Error as e:
        return None, traduzir_erro_banco(e)
    finally:
        if conn and conn.is_connected():
            conn.close()

def execute_dml(sql: str, params: tuple = None, user: str = None, password: str = None):
    """
    Executa comando DML (INSERT, UPDATE, DELETE) com Prepared Statement e COMMIT.
    """
    conn = None
    try:
        conn = get_connection(user, password)
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return True, last_id, None
    except Error as e:
        if conn:
            conn.rollback()
        return False, None, traduzir_erro_banco(e)
    finally:
        if conn and conn.is_connected():
            conn.close()

def executar_transferencia_transacional(conta_origem: str, conta_destino: str, valor: float, simular_falha: bool = False):
    """
    Operação de Negócio Multitabela em Única Transação (Item Central B1 e B3).
    Passo 1: Bloqueia e consulta saldo da conta de origem (SELECT ... FOR UPDATE).
    Passo 2: Debita saldo da conta de origem.
    Passo 3: Credita saldo na conta de destino.
    Passo 4: Se simular_falha=True, provoca erro proposital no meio da transação.
    Passo 5: Registra na tabela 'transacao'.
    Passo 6: COMMIT ou ROLLBACK.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Inicia transação explícita
        cursor.execute("START TRANSACTION;")
        
        # 1. Verifica e bloqueia conta de origem
        cursor.execute("SELECT saldo, status FROM conta_bancaria WHERE numero_conta = %s FOR UPDATE;", (conta_origem,))
        origem = cursor.fetchone()
        if not origem:
            conn.rollback()
            return False, "Conta de origem não encontrada."
        if origem['status'] != 'ATIVA':
            conn.rollback()
            return False, f"Conta de origem não está ativa (Status: {origem['status']})."
        if float(origem['saldo']) < valor:
            conn.rollback()
            return False, f"Saldo insuficiente na conta de origem (Saldo atual: R$ {origem['saldo']:.2f}, Valor solicitado: R$ {valor:.2f})."

        # 2. Verifica conta de destino
        cursor.execute("SELECT status FROM conta_bancaria WHERE numero_conta = %s FOR UPDATE;", (conta_destino,))
        destino = cursor.fetchone()
        if not destino:
            conn.rollback()
            return False, "Conta de destino não encontrada."
        if destino['status'] != 'ATIVA':
            conn.rollback()
            return False, f"Conta de destino não está ativa (Status: {destino['status']})."

        # 3. Debita origem
        cursor.execute("UPDATE conta_bancaria SET saldo = saldo - %s WHERE numero_conta = %s;", (valor, conta_origem))

        # 4. Credita destino
        cursor.execute("UPDATE conta_bancaria SET saldo = saldo + %s WHERE numero_conta = %s;", (valor, conta_destino))

        # 5. Cenário de Falha Forçada (Se acionado pelo botão da banca)
        if simular_falha:
            # Simula violação proposital ou interrupção antes de registrar o log da transação
            raise Error("SIMULAÇÃO DE FALHA PROVOCADA: Falha catastrófica de rede no meio da transação antes do COMMIT!")

        # 6. Registra histórico da transação
        cursor.execute(
            "INSERT INTO transacao (numero_conta_origem, numero_conta_destino, tipo, valor, data_hora) VALUES (%s, %s, 'TRANSFERENCIA', %s, NOW());",
            (conta_origem, conta_destino, valor)
        )

        # 7. Confirmação
        conn.commit()
        cursor.close()
        return True, "Transferência realizada com sucesso! Transação confirmada (COMMIT) em ambas as contas."

    except Error as e:
        if conn:
            conn.rollback()
        return False, f"Transação CANCELADA (ROLLBACK executado): {e}"
    finally:
        if conn and conn.is_connected():
            conn.close()
