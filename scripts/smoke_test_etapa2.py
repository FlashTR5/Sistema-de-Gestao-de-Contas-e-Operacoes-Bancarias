#!/usr/bin/env python3
"""Dez verificações reais da Etapa 2. Requer o banco povoado e .env do projeto.

Usa contas temporárias identificadas por UUID para COMMIT/ROLLBACK e auditoria.
Remove somente os registros do próprio teste ao finalizar; nunca debita contas reais.
Não substitui a demonstração completa dos CRUDs nem os estudos de EXPLAIN.
"""
import argparse
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from auth import hash_senha, verificar_senha
from db import get_connection, execute_query, executar_transferencia_transacional
from mysql.connector import Error, errorcode


def exigir(condicao, mensagem):
    if not condicao:
        raise RuntimeError(mensagem)


@contextmanager
def conexao(user=None, password=None):
    conn = get_connection(user, password)
    try:
        yield conn
    finally:
        try:
            conn.rollback()
        finally:
            conn.close()


def consultar(sql, params=()):
    resultado, erro = execute_query(sql, params)
    exigir(erro is None and resultado is not None, erro or 'Consulta sem resultado.')
    return resultado


@contextmanager
def contas_de_teste():
    """Fixture persistida para permitir que a função real abra outra conexão."""
    prefixo = 'SM' + uuid4().hex[:12]
    contas = (prefixo + '-O', prefixo + '-D')
    with conexao() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute('SELECT codigo_agencia FROM agencia ORDER BY codigo_agencia LIMIT 1')
                agencia = cursor.fetchone()
                exigir(agencia is not None, 'É necessário ao menos uma agência cadastrada.')
                for conta in contas:
                    cursor.execute(
                        "INSERT INTO conta_bancaria (numero_conta, codigo_agencia, modalidade, saldo, data_abertura, status) VALUES (%s, %s, 'CORRENTE', %s, CURDATE(), 'ATIVA')",
                        (conta, agencia[0], Decimal('100.00')))
                conn.commit()
                yield contas
            finally:
                conn.rollback()
                # Identificadores exclusivos: nenhuma limpeza global ou por faixa.
                cursor.execute('DELETE FROM transacao WHERE numero_conta_origem IN (%s, %s) OR numero_conta_destino IN (%s, %s)', contas + contas)
                cursor.execute("DELETE FROM tb_auditoria_sistema WHERE tabela_afetada = 'conta_bancaria' AND registro_id IN (%s, %s)", contas)
                cursor.execute('DELETE FROM conta_bancaria WHERE numero_conta IN (%s, %s)', contas)
                conn.commit()


def verificar_conexao():
    banco = consultar('SELECT DATABASE() AS banco')[0]['banco']
    exigir(banco == 'sistema_bancario', 'A conexão deve apontar para sistema_bancario.')
    return f'Conectado a {banco}.'


def verificar_volume():
    volume = consultar('SELECT (SELECT COUNT(*) FROM transacao) AS transacoes, (SELECT COUNT(*) FROM parcela_emprestimo) AS parcelas, (SELECT COUNT(*) FROM historico_status_conta) AS historicos')[0]
    exigir(volume['transacoes'] > 10000, f"Massa insuficiente: {volume['transacoes']} transações (exigido > 10.000).")
    return f"{volume['transacoes']:,} transações; {volume['parcelas']:,} parcelas; {volume['historicos']:,} históricos."


def verificar_prepared_statements():
    payload = "' OR '1'='1; DROP TABLE cliente; --"
    retorno = consultar('SELECT %s AS literal', (payload,))
    exigir(retorno[0]['literal'] == payload, 'A camada de dados alterou o literal parametrizado.')
    clientes = consultar('SELECT id_cliente FROM cliente WHERE email = %s', (payload,))
    exigir(not clientes, 'Payload SQLi retornou clientes indevidamente.')
    with conexao() as conn:
        with conn.cursor(prepared=True) as cursor:
            cursor.execute('SELECT %s = %s', (payload, payload))
            exigir(cursor.fetchone()[0] == 1, 'Prepared Statement nativo falhou.')
    return 'Parâmetros preservados como literais; SQLi bloqueada; prepare nativo verificado.'


def verificar_cruds():
    consultas = (
        ('cliente', 'SELECT id_cliente, nome FROM cliente LIMIT 1'),
        ('conta_bancaria', 'SELECT numero_conta, saldo FROM conta_bancaria LIMIT 1'),
        ('cartao', 'SELECT numero_cartao FROM cartao LIMIT 1'),
        ('beneficiario', 'SELECT id_beneficiario, nome FROM beneficiario LIMIT 1'),
    )
    for tabela, sql in consultas:
        exigir(bool(consultar(sql)), f'CRUD {tabela}: tabela vazia.')
    return 'SELECTs básicos de cliente, conta, cartão e beneficiário executados.'


def verificar_consultas_parametrizadas():
    conta = consultar('SELECT numero_conta FROM conta_bancaria ORDER BY numero_conta LIMIT 1')[0]['numero_conta']
    extrato = consultar('''
        SELECT t.tipo, COUNT(*) AS quantidade, COALESCE(SUM(t.valor), 0) AS volume
        FROM transacao t INNER JOIN conta_bancaria cb ON cb.numero_conta = t.numero_conta_origem
        WHERE (t.numero_conta_origem = %s OR t.numero_conta_destino = %s)
          AND t.data_hora BETWEEN %s AND %s GROUP BY t.tipo
        ''', (conta, conta, date(2000, 1, 1), date(2100, 1, 1)))
    credito = consultar('''
        SELECT c.id_cliente, e.id_emprestimo, COUNT(p.numero_parcela) AS parcelas,
               COALESCE(SUM(p.valor), 0) AS total
        FROM cliente c INNER JOIN emprestimo e ON c.id_cliente = e.id_cliente
        LEFT JOIN parcela_emprestimo p ON e.id_emprestimo = p.id_emprestimo
        WHERE e.status = %s GROUP BY c.id_cliente, e.id_emprestimo
        ''', ('ATIVO',))
    return f'Extrato: {len(extrato)} grupos; crédito: {len(credito)} contratos (filtros parametrizados).'


def verificar_view():
    linhas = consultar('SELECT codigo_agencia, quantidade_transacoes FROM vw_relatorio_consolidado_agencias')
    exigir(bool(linhas), 'VIEW consolidada vazia.')
    return f'VIEW consolidada consultada: {len(linhas)} agências.'


def estado_transferencia(contas):
    saldos = consultar('SELECT numero_conta, saldo FROM conta_bancaria WHERE numero_conta IN (%s, %s) ORDER BY numero_conta', contas)
    registros = consultar('SELECT COUNT(*) AS total FROM transacao WHERE numero_conta_origem = %s AND numero_conta_destino = %s', contas)[0]['total']
    auditoria = consultar("SELECT COUNT(*) AS total FROM tb_auditoria_sistema WHERE tabela_afetada = 'conta_bancaria' AND registro_id IN (%s, %s)", contas)[0]['total']
    return {linha['numero_conta']: linha['saldo'] for linha in saldos}, registros, auditoria


def verificar_transacao():
    with contas_de_teste() as contas:
        sucesso, mensagem = executar_transferencia_transacional(*contas, Decimal('10.00'))
        exigir(sucesso, mensagem)
        depois_commit = estado_transferencia(contas)
        exigir(depois_commit[0] == {contas[0]: Decimal('90.00'), contas[1]: Decimal('110.00')}, 'COMMIT não confirmou os dois saldos esperados.')
        exigir(depois_commit[1] == 1, 'COMMIT não gerou o registro em transacao.')
        exigir(depois_commit[2] == 2, 'COMMIT não registrou a auditoria dos dois saldos.')
        sucesso, mensagem = executar_transferencia_transacional(*contas, Decimal('5.00'), simular_falha=True)
        exigir(not sucesso and 'ROLLBACK' in mensagem, 'Falha forçada não provocou ROLLBACK.')
        exigir(estado_transferencia(contas) == depois_commit, 'ROLLBACK não restaurou saldos, transações e auditoria.')
    return 'Função real: COMMIT confirmado e falha forçada revertida nas duas contas e nos históricos.'


def verificar_perfis():
    perfis = (
        ('user_admin', 'DB_ADMIN_PASSWORD', 'SELECT id_cliente FROM cliente LIMIT 1'),
        ('user_atendente', 'DB_ATENDENTE_PASSWORD', 'SELECT id_cliente FROM cliente LIMIT 1'),
        ('user_auditor', 'DB_AUDITOR_PASSWORD', 'SELECT id_auditoria FROM tb_auditoria_sistema LIMIT 1'),
    )
    for usuario, variavel, sql in perfis:
        senha = os.getenv(variavel)
        exigir(bool(senha), f"Configure {variavel} no .env ou no ambiente para testar {usuario}.")
        with conexao(usuario, senha) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT CURRENT_USER()')
                exigir(cursor.fetchone()[0].split('@')[0] == usuario, f'Login efetivo incorreto para {usuario}.')
                cursor.execute(sql)
                cursor.fetchall()
                if usuario == 'user_admin':
                    cursor.execute('DELETE FROM agencia WHERE codigo_agencia = -1')
                else:
                    proibido = 'DELETE FROM cliente WHERE 1 = 0' if usuario == 'user_atendente' else 'UPDATE cliente SET nome = nome WHERE 1 = 0'
                    try:
                        cursor.execute(proibido)
                    except Error as erro:
                        exigir(erro.errno == errorcode.ER_TABLEACCESS_DENIED_ERROR, f'{usuario}: erro inesperado no teste de privilégios ({erro.errno}).')
                    else:
                        raise RuntimeError(f'{usuario}: privilégio proibido concedido.')
    return 'Três logins reais; leitura autorizada e escritas proibidas recusadas.'


def verificar_trigger():
    with contas_de_teste() as contas:
        with conexao() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT COALESCE(MAX(id_auditoria), 0) AS ultimo FROM tb_auditoria_sistema')
                ultimo = cursor.fetchone()['ultimo']
                cursor.execute('UPDATE conta_bancaria SET saldo = saldo + %s WHERE numero_conta = %s', (Decimal('1.00'), contas[0]))
                cursor.execute("SELECT operacao, usuario_responsavel, data_hora, valores_anteriores, valores_novos FROM tb_auditoria_sistema WHERE id_auditoria > %s AND tabela_afetada = 'conta_bancaria' AND registro_id = %s", (ultimo, contas[0]))
                linhas = cursor.fetchall()
                exigir(len(linhas) == 1, 'Trigger não gerou exatamente um registro de auditoria.')
                registro = linhas[0]
                exigir(registro['operacao'] == 'UPDATE' and registro['usuario_responsavel'] and registro['data_hora'], 'Auditoria incompleta: operação, autor ou data ausentes.')
                antes = json.loads(registro['valores_anteriores'])
                depois = json.loads(registro['valores_novos'])
                exigir(Decimal(str(antes['saldo'])) == Decimal('100.00') and Decimal(str(depois['saldo'])) == Decimal('101.00'), 'Valores anterior e posterior incorretos na auditoria.')
                # O contexto reverte alteração e log após comprovar o disparo.
    return 'Trigger disparado: autor, data, operação e valores anterior/posterior validados.'


def verificar_bcrypt():
    senha = 'MinhaSenha#2026'
    primeiro, segundo = hash_senha(senha), hash_senha(senha)
    exigir(len(primeiro) == 60 and primeiro.startswith('$2b$'), 'Formato bcrypt inesperado.')
    exigir(primeiro != segundo, 'O sal deve ser aleatório a cada geração.')
    exigir(verificar_senha(senha, primeiro), 'Senha correta rejeitada.')
    exigir(not verificar_senha('senha-incorreta', primeiro), 'Senha incorreta aceita.')
    return 'bcrypt: 60 caracteres, sal aleatório, senha correta aceita e incorreta recusada.'


def executar_verificacoes(verificacoes, saida=sys.stdout, color=False):
    falhas = 0
    for indice, (titulo, verificar) in enumerate(verificacoes, 1):
        try:
            detalhe = verificar()
            status, cor = 'PASS', '\033[32m'
        except Exception as erro:
            falhas += 1
            detalhe = str(erro).replace('\n', ' ')
            status, cor = 'FAIL', '\033[31m'
        marcador = f'[{status}]'
        if color:
            marcador = f'{cor}{marcador}\033[0m'
        print(f'{marcador} {indice:02d}. {titulo} — {detalhe}', file=saida)
    print(f'\nResultado: {len(verificacoes) - falhas}/{len(verificacoes)} verificações aprovadas.', file=saida)
    return 1 if falhas else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-color', action='store_true', help='Desativa cores ANSI.')
    args = parser.parse_args(argv)
    verificacoes = [
        ('Conexão com sistema_bancario', verificar_conexao),
        ('Massa de dados > 10.000 transações', verificar_volume),
        ('Prepared Statements e SQL Injection', verificar_prepared_statements),
        ('Quatro CRUDs (SELECTs básicos)', verificar_cruds),
        ('Duas consultas parametrizadas', verificar_consultas_parametrizadas),
        ('VIEW de relatório consolidado', verificar_view),
        ('Transação multitabela: COMMIT e ROLLBACK', verificar_transacao),
        ('Três perfis MySQL e menor privilégio', verificar_perfis),
        ('Trigger e registro de auditoria', verificar_trigger),
        ('Hash e autenticação bcrypt', verificar_bcrypt),
    ]
    return executar_verificacoes(verificacoes, color=sys.stdout.isatty() and not args.no_color and 'NO_COLOR' not in os.environ)


if __name__ == '__main__':
    sys.exit(main())
