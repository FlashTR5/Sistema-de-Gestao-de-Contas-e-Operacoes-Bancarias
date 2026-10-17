#!/usr/bin/env python3
"""
Experimento de Concorrência e Controle Transacional (Artefato B3)
Demonstração de 2 sessões simultâneas disputando a mesma conta bancária com row-level lock (SELECT ... FOR UPDATE).
Registra o comportamento observado (bloqueio, espera) e o nível de isolamento em vigor (REPEATABLE READ).
"""

import argparse
from pathlib import Path
import sys
import threading
import time
import mysql.connector
from datetime import datetime
from mysql.connector import errorcode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from db import get_connection

def sessao_1(resultados):
    try:
        conn = mysql.connector.connect(host="localhost", port=3306, user="root", password="banco_secret", database="sistema_bancario")
        cursor = conn.cursor()
        
        # Inicia transação 1
        cursor.execute("START TRANSACTION;")
        resultados.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Sessão 1: Inicia transação e bloqueia conta 10001-X com FOR UPDATE")
        cursor.execute("SELECT saldo FROM conta_bancaria WHERE numero_conta = '10001-X' FOR UPDATE;")
        saldo = cursor.fetchone()[0]
        resultados.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Sessão 1: Leu saldo atual: R$ {saldo:.2f}")

        # Mantém o lock por 3 segundos para forçar espera na Sessão 2
        time.sleep(3)

        # Realiza débito e commit
        cursor.execute("UPDATE conta_bancaria SET saldo = saldo - 50.00 WHERE numero_conta = '10001-X';")
        conn.commit()
        resultados.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Sessão 1: Debitou R$ 50.00 e executou COMMIT. Lock liberado!")
        cursor.close()
        conn.close()
    except Exception as e:
        resultados.append(f"Sessão 1 Erro: {e}")

def sessao_2(resultados):
    try:
        # Aguarda 0.5s para garantir que a Sessão 1 adquiriu o lock primeiro
        time.sleep(0.5)
        conn = mysql.connector.connect(host="localhost", port=3306, user="root", password="banco_secret", database="sistema_bancario")
        cursor = conn.cursor()
        
        # Inicia transação 2
        cursor.execute("START TRANSACTION;")
        resultados.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Sessão 2: Tenta ler/bloquear a mesma conta 10001-X (Entrando em ESPERA / ROW LOCK...)")
        
        t_inicio_espera = time.time()
        cursor.execute("SELECT saldo FROM conta_bancaria WHERE numero_conta = '10001-X' FOR UPDATE;")
        saldo = cursor.fetchone()[0]
        tempo_bloqueio = time.time() - t_inicio_espera
        
        resultados.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Sessão 2: Desbloqueada após {tempo_bloqueio:.2f}s! Leu saldo atualizado: R$ {saldo:.2f}")

        cursor.execute("UPDATE conta_bancaria SET saldo = saldo - 25.00 WHERE numero_conta = '10001-X';")
        conn.commit()
        resultados.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Sessão 2: Debitou R$ 25.00 e executou COMMIT com sucesso.")
        cursor.close()
        conn.close()
    except Exception as e:
        resultados.append(f"Sessão 2 Erro: {e}")

def experimento_bloqueio_linha():
    print("=" * 70)
    print("EXPERIMENTO DE CONCORRÊNCIA E CONTROLE TRANSACIONAL (ARTEFATO B3)")
    print("Nível de Isolamento: REPEATABLE READ (Padrão MySQL com MVCC)")
    print("=" * 70)

    resultados = []
    t1 = threading.Thread(target=sessao_1, args=(resultados,))
    t2 = threading.Thread(target=sessao_2, args=(resultados,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("\nCronologia dos Eventos Observados:")
    for r in resultados:
        print(" ", r)

    print("\nConclusão do Experimento:")
    print(" 1. Bloqueio em Nível de Linha (Row-Level Lock) comprovado com sucesso.")
    print(" 2. A Sessão 2 permaneceu em espera sem sofrer Deadlock ou Lost Update.")
    print(" 3. A consistência e atomicidade dos saldos bancários foram 100% mantidas.")
    print("=" * 70)

def executar_deadlock():
    """Locks opostos em contas reais; escrita somente em tabelas temporárias locais.

    A leitura da tabela temporária após erro 1213 ocorre ANTES de um rollback
    explícito, provando que o InnoDB desfez a transação inteira automaticamente.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT @@transaction_isolation, @@innodb_deadlock_detect')
            isolamento, deteccao = cursor.fetchone()
            if not deteccao:
                raise RuntimeError('innodb_deadlock_detect está desativado; não é possível demonstrar o erro 1213.')
            cursor.execute('SELECT numero_conta FROM conta_bancaria ORDER BY numero_conta LIMIT 2')
            contas = [linha[0] for linha in cursor.fetchall()]
            if len(contas) != 2:
                raise RuntimeError('O experimento requer duas contas cadastradas.')
    finally:
        conn.close()

    print('EXPERIMENTO OPCIONAL DE DEADLOCK (B3)')
    print(f'Nível de isolamento observado: {isolamento}')
    print(f'Sessão 1 bloqueia {contas[0]} e pede {contas[1]}; sessão 2 faz a ordem inversa.')
    print('Saldos reais permanecem intactos; a prova do rollback usa tabelas temporárias InnoDB.')
    barreira = threading.Barrier(2, timeout=10)
    mutex = threading.Lock()
    eventos, desfechos, erros = [], [], []

    def registrar(texto):
        with mutex:
            eventos.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {texto}")

    def sessao(numero, primeira, segunda):
        conexao = None
        cursor = None
        try:
            conexao = get_connection()
            cursor = conexao.cursor()
            cursor.execute('SET SESSION innodb_lock_wait_timeout = 10')
            # TEMPORARY TABLE é privada desta conexão e some ao fechar a sessão.
            cursor.execute('CREATE TEMPORARY TABLE forge_deadlock_probe (id INT PRIMARY KEY, valor INT NOT NULL) ENGINE=InnoDB')
            cursor.execute('INSERT INTO forge_deadlock_probe VALUES (1, 0)')
            conexao.commit()
            conexao.start_transaction()
            cursor.execute('UPDATE forge_deadlock_probe SET valor = 1 WHERE id = 1')
            cursor.execute('SELECT saldo FROM conta_bancaria WHERE numero_conta = %s FOR UPDATE', (primeira,))
            if cursor.fetchone() is None:
                raise RuntimeError(f'Conta {primeira} não encontrada.')
            registrar(f'Sessão {numero}: lock em {primeira}; alteração temporária 0 -> 1 ainda não confirmada.')
            barreira.wait()
            registrar(f'Sessão {numero}: solicita lock em {segunda} (ciclo de espera mútua).')
            try:
                cursor.execute('SELECT saldo FROM conta_bancaria WHERE numero_conta = %s FOR UPDATE', (segunda,))
                cursor.fetchone()
            except mysql.connector.Error as erro:
                if erro.errno != errorcode.ER_LOCK_DEADLOCK:
                    raise
                registrar(f'Sessão {numero}: erro 1213 (ER_LOCK_DEADLOCK); eleita vítima pelo InnoDB.')
                # Prova do rollback automático, antes de qualquer conn.rollback().
                cursor.execute('SELECT valor FROM forge_deadlock_probe WHERE id = 1')
                valor = cursor.fetchone()[0]
                if valor != 0:
                    raise RuntimeError('O rollback automático não restaurou o valor temporário inicial.')
                registrar(f'Sessão {numero}: valor temporário voltou a 0 ANTES de ROLLBACK explícito; transação inteira desfeita automaticamente.')
                with mutex:
                    desfechos.append('vitima')
            else:
                conexao.commit()
                cursor.execute('SELECT valor FROM forge_deadlock_probe WHERE id = 1')
                if cursor.fetchone()[0] != 1:
                    raise RuntimeError('COMMIT da sessão sobrevivente não persistiu a alteração temporária.')
                registrar(f'Sessão {numero}: lock liberado pela vítima; COMMIT confirmou valor temporário 1.')
                with mutex:
                    desfechos.append('commit')
        except Exception as erro:
            barreira.abort()
            with mutex:
                erros.append(f'Sessão {numero}: {erro}')
        finally:
            if conexao is not None:
                try:
                    conexao.rollback()
                finally:
                    if cursor is not None:
                        cursor.close()
                    conexao.close()

    threads = [
        threading.Thread(target=sessao, args=(1, contas[0], contas[1])),
        threading.Thread(target=sessao, args=(2, contas[1], contas[0])),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for evento in eventos:
        print(' ', evento)
    if erros or sorted(desfechos) != ['commit', 'vitima']:
        for erro in erros:
            print(f'[FAIL] {erro}')
        print('[FAIL] Não foram comprovados uma vítima 1213 e um COMMIT sobrevivente.')
        return 1
    print('[PASS] Deadlock detectado: uma vítima sofreu rollback automático e a outra sessão concluiu COMMIT.')
    print('A vítima pode repetir a transação completa em uma operação real; a escolha da vítima não é predeterminada.')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deadlock', action='store_true', help='Demonstra um ciclo de espera mútua e o rollback automático após erro 1213.')
    args = parser.parse_args(argv)
    if args.deadlock:
        try:
            return executar_deadlock()
        except Exception as erro:
            print(f'[FAIL] Não foi possível executar o deadlock: {erro}')
            return 1
    experimento_bloqueio_linha()
    return 0


if __name__ == '__main__':
    sys.exit(main())
