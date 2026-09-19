-- ============================================================================
-- SCRIPT DE CONSULTAS E RELATÓRIOS (03_consultas.sql)
-- SGBD: MySQL 8.0
-- ============================================================================

USE sistema_bancario;

-- ----------------------------------------------------------------------------
-- CONSULTA 1: Listar Contas Bancárias, Seus Titulares e Agência
-- Demostra: Relacionamento N:N (cliente_conta) e 1:N (agencia - conta)
-- ----------------------------------------------------------------------------
SELECT 
    c.nome AS cliente,
    c.cpf_cnpj,
    cc.tipo_titular,
    cb.numero_conta,
    cb.modalidade,
    cb.status AS status_conta,
    a.nome AS agencia
FROM cliente c
INNER JOIN cliente_conta cc ON c.id_cliente = cc.id_cliente
INNER JOIN conta_bancaria cb ON cc.numero_conta = cb.numero_conta
INNER JOIN agencia a ON cb.codigo_agencia = a.codigo_agencia
ORDER BY cb.numero_conta;

-- ----------------------------------------------------------------------------
-- CONSULTA 2: Extrato Detalhado de Transações por Conta
-- Demonstra: Auto-relacionamento de tabelas via JOIN (Origem e Destino)
-- ----------------------------------------------------------------------------
SELECT 
    t.id_transacao,
    t.data_hora,
    t.tipo AS tipo_transacao,
    t.valor,
    t.numero_conta_origem AS conta_origem,
    cli_origem.nome AS titular_origem,
    t.numero_conta_destino AS conta_destino,
    cli_destino.nome AS titular_destino
FROM transacao t
LEFT JOIN conta_bancaria cb_origem ON t.numero_conta_origem = cb_origem.numero_conta
LEFT JOIN cliente_conta cc_origem ON cb_origem.numero_conta = cc_origem.numero_conta AND cc_origem.tipo_titular = 'TITULAR'
LEFT JOIN cliente cli_origem ON cc_origem.id_cliente = cli_origem.id_cliente
LEFT JOIN conta_bancaria cb_destino ON t.numero_conta_destino = cb_destino.numero_conta
LEFT JOIN cliente_conta cc_destino ON cb_destino.numero_conta = cc_destino.numero_conta AND cc_destino.tipo_titular = 'TITULAR'
LEFT JOIN cliente cli_destino ON cc_destino.id_cliente = cli_destino.id_cliente
ORDER BY t.data_hora DESC;

-- ----------------------------------------------------------------------------
-- CONSULTA 3: Relatório da Especialização / Herança de Empréstimos
-- Demonstra: Junção de Superclasse (emprestimo) com Subclasses
-- ----------------------------------------------------------------------------
SELECT 
    e.id_emprestimo,
    c.nome AS cliente,
    e.tipo_modalidade,
    e.valor_total,
    e.status,
    COALESCE(ec.orgao_emissor, 'N/A') AS orgao_emissor,
    COALESCE(f.tipo_bem, 'N/A') AS bem_financiado,
    COALESCE(f.valor_entrada, 0.00) AS valor_entrada
FROM emprestimo e
INNER JOIN cliente c ON e.id_cliente = c.id_cliente
LEFT JOIN emprestimo_consignado ec ON e.id_emprestimo = ec.id_emprestimo
LEFT JOIN financiamento f ON e.id_emprestimo = f.id_emprestimo;

-- ----------------------------------------------------------------------------
-- CONSULTA 4: Resumo de Parcelas Pendentes e Pagas por Empréstimo
-- Demonstra: Entidade Fraca (parcela_emprestimo), GROUP BY e Agregar Valores
-- ----------------------------------------------------------------------------
SELECT 
    e.id_emprestimo,
    c.nome AS cliente,
    COUNT(p.numero_parcela) AS total_parcelas,
    SUM(CASE WHEN p.status = 'PAGO' THEN p.valor ELSE 0 END) AS total_pago,
    SUM(CASE WHEN p.status = 'PENDENTE' THEN p.valor ELSE 0 END) AS total_pendente
FROM emprestimo e
INNER JOIN cliente c ON e.id_cliente = c.id_cliente
INNER JOIN parcela_emprestimo p ON e.id_emprestimo = p.id_emprestimo
GROUP BY e.id_emprestimo, c.nome;

-- ----------------------------------------------------------------------------
-- CONSULTA 5: Hierarquia de Funcionários (Supervisor x Subordinado)
-- Demonstra: Autorrelacionamento 1:N na tabela funcionario
-- ----------------------------------------------------------------------------
SELECT 
    f.id_funcionario,
    f.nome AS funcionario,
    f.cargo,
    a.nome AS agencia,
    COALESCE(sup.nome, 'Sem Supervisor (Gerente Geral)') AS supervisor_direto
FROM funcionario f
INNER JOIN agencia a ON f.codigo_agencia = a.codigo_agencia
LEFT JOIN funcionario sup ON f.id_supervisor = sup.id_funcionario;

-- ----------------------------------------------------------------------------
-- CONSULTA 6: Histórico de Alterações de Status das Contas (Auditoria)
-- Demonstra: Consulta a Entidades Temporais
-- ----------------------------------------------------------------------------
SELECT 
    h.id_historico,
    h.numero_conta,
    h.status_anterior,
    h.status_novo,
    h.data_alteracao,
    h.motivo
FROM historico_status_conta h
ORDER BY h.data_alteracao DESC;