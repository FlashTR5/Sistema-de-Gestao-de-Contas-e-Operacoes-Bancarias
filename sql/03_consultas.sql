-- ============================================================================
-- PROJETO FINAL: LABORATÓRIO DE BANCO DE DADOS (UCB 2026/2)
-- SGBD: MySQL 8.0
-- ARQUIVO: 03_consultas.sql (15 Consultas Obrigatórias - Atende Devolutiva C4)
-- ============================================================================

USE sistema_bancario;

-- ============================================================================
-- CATEGORIA 1: CONSULTAS BÁSICAS (5 CONSULTAS)
-- Requisitos: Projeção, seleção com WHERE, ordenação, LIKE, BETWEEN, IN e NULL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CONSULTA 1 (Básica com LIKE e ORDER BY)
-- Pergunta de Negócio: Quais clientes possuem o sobrenome 'Silva' ou 'Souza',
-- exibindo nome completo e e-mail em ordem alfabética?
-- ----------------------------------------------------------------------------
SELECT 
    id_cliente,
    nome,
    cpf_cnpj,
    email
FROM cliente
WHERE nome LIKE '%Silva%' OR nome LIKE '%Souza%'
ORDER BY nome ASC;

-- ----------------------------------------------------------------------------
-- CONSULTA 2 (Básica com BETWEEN e ORDER BY DESC)
-- Pergunta de Negócio: Quais transações financeiras com valor entre R$ 1.000,00 
-- e R$ 5.000,00 foram realizadas no sistema, ordenadas da mais recente para a mais antiga?
-- ----------------------------------------------------------------------------
SELECT 
    id_transacao,
    numero_conta_origem,
    numero_conta_destino,
    tipo,
    valor,
    data_hora
FROM transacao
WHERE valor BETWEEN 1000.00 AND 5000.00
ORDER BY data_hora DESC;

-- ----------------------------------------------------------------------------
-- CONSULTA 3 (Básica com operador IN)
-- Pergunta de Negócio: Quais contas bancárias encontram-se em situação especial 
-- (bloqueadas ou encerradas) que necessitam de intervenção da gerência?
-- ----------------------------------------------------------------------------
SELECT 
    numero_conta,
    codigo_agencia,
    modalidade,
    saldo,
    status
FROM conta_bancaria
WHERE status IN ('BLOQUEADA', 'ENCERRADA')
ORDER BY status, numero_conta;

-- ----------------------------------------------------------------------------
-- CONSULTA 4 (Básica com IS NULL / IS NOT NULL)
-- Pergunta de Negócio: Quais funcionários ocupam posições de topo na agência 
-- (sem supervisor atribuído) e quais clientes possuem cadastro com telefone opcional pendente?
-- ----------------------------------------------------------------------------
SELECT 
    id_funcionario,
    nome,
    cargo,
    codigo_agencia
FROM funcionario
WHERE id_supervisor IS NULL;

-- ----------------------------------------------------------------------------
-- CONSULTA 5 (Básica com projeção formatada e filtros múltiplos)
-- Pergunta de Negócio: Quais cartões de crédito encontram-se com status ativo 
-- emitidos para contas correntes?
-- ----------------------------------------------------------------------------
SELECT 
    c.numero_cartao,
    c.numero_conta,
    c.tipo AS tipo_cartao,
    c.status AS status_cartao
FROM cartao c
WHERE c.tipo = 'CREDITO' AND c.status = 'ATIVO'
ORDER BY c.numero_conta;


-- ============================================================================
-- CATEGORIA 2: JUNÇÕES E AGREGAÇÕES (5 CONSULTAS)
-- Requisitos: Ao menos uma com 3 tabelas, uma com LEFT JOIN, uma com GROUP BY e HAVING
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CONSULTA 6 (Junção Tripla: 3 Tabelas)
-- Pergunta de Negócio: Qual é a lista consolidada de titulares, contendo nome do cliente, 
-- CPF, número da conta bancária, modalidade da conta e o nome da agência onde a conta foi aberta?
-- ----------------------------------------------------------------------------
SELECT 
    c.nome AS nome_cliente,
    c.cpf_cnpj,
    cb.numero_conta,
    cb.modalidade AS modalidade_conta,
    cb.saldo,
    a.nome AS nome_agencia
FROM cliente c
INNER JOIN cliente_conta cc ON c.id_cliente = cc.id_cliente
INNER JOIN conta_bancaria cb ON cc.numero_conta = cb.numero_conta
INNER JOIN agencia a ON cb.codigo_agencia = a.codigo_agencia
WHERE cc.tipo_titular = 'TITULAR'
ORDER BY a.nome, cb.numero_conta;

-- ----------------------------------------------------------------------------
-- CONSULTA 7 (LEFT JOIN)
-- Pergunta de Negócio: Quais clientes cadastrados ainda não realizaram nenhuma 
-- movimentação financeira de saída (origem) no sistema?
-- ----------------------------------------------------------------------------
SELECT 
    c.id_cliente,
    c.nome AS nome_cliente,
    cb.numero_conta,
    t.id_transacao
FROM cliente c
INNER JOIN cliente_conta cc ON c.id_cliente = cc.id_cliente
INNER JOIN conta_bancaria cb ON cc.numero_conta = cb.numero_conta
LEFT JOIN transacao t ON cb.numero_conta = t.numero_conta_origem
WHERE t.id_transacao IS NULL;

-- ----------------------------------------------------------------------------
-- CONSULTA 8 (GROUP BY e Agregações: COUNT, SUM, AVG)
-- Pergunta de Negócio: Qual o volume financeiro total transacionado, a quantidade 
-- de transações e o ticket médio movimentado por tipo de operação (PIX, TED, etc.)?
-- ----------------------------------------------------------------------------
SELECT 
    tipo AS tipo_transacao,
    COUNT(*) AS total_operacoes,
    SUM(valor) AS volume_total,
    ROUND(AVG(valor), 2) AS ticket_medio
FROM transacao
GROUP BY tipo
ORDER BY volume_total DESC;

-- ----------------------------------------------------------------------------
-- CONSULTA 9 (GROUP BY com HAVING)
-- Pergunta de Negócio: Quais agências bancárias movimentaram um volume total 
-- superior a R$ 30.000,00 em transações de saída de seus correntistas?
-- ----------------------------------------------------------------------------
SELECT 
    a.codigo_agencia,
    a.nome AS nome_agencia,
    COUNT(t.id_transacao) AS total_transacoes,
    SUM(t.valor) AS volume_movimentado
FROM agencia a
INNER JOIN conta_bancaria cb ON a.codigo_agencia = cb.codigo_agencia
INNER JOIN transacao t ON cb.numero_conta = t.numero_conta_origem
GROUP BY a.codigo_agencia, a.nome
HAVING SUM(t.valor) > 30000.00
ORDER BY volume_movimentado DESC;

-- ----------------------------------------------------------------------------
-- CONSULTA 10 (Junção de Herança: Superclasse + Subclasses com Coalesce)
-- Pergunta de Negócio: Qual a visão detalhada de todos os contratos de crédito, 
-- exibindo os dados específicos conforme cada modalidade (consignado, financiamento ou pessoal)?
-- ----------------------------------------------------------------------------
SELECT 
    e.id_emprestimo,
    c.nome AS cliente,
    e.tipo_modalidade,
    e.valor_total,
    e.status,
    COALESCE(ec.orgao_emissor, 'N/A') AS orgao_consignado,
    COALESCE(f.tipo_bem, 'N/A') AS bem_financiado,
    COALESCE(ep.finalidade, 'N/A') AS finalidade_pessoal
FROM emprestimo e
INNER JOIN cliente c ON e.id_cliente = c.id_cliente
LEFT JOIN emprestimo_consignado ec ON e.id_emprestimo = ec.id_emprestimo
LEFT JOIN financiamento f ON e.id_emprestimo = f.id_emprestimo
LEFT JOIN emprestimo_pessoal ep ON e.id_emprestimo = ep.id_emprestimo
ORDER BY e.id_emprestimo;


-- ============================================================================
-- CATEGORIA 3: CONSULTAS AVANÇADAS (5 CONSULTAS)
-- Requisitos: Ao menos uma correlacionada, uma com EXISTS e pergunta de negócio não trivial
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CONSULTA 11 (Subconsulta Correlacionada)
-- Pergunta de Negócio: Quais transações individuais possuem valor estritamente 
-- superior à média de todas as transações realizadas pela própria conta de origem?
-- ----------------------------------------------------------------------------
SELECT 
    t1.id_transacao,
    t1.numero_conta_origem,
    t1.tipo,
    t1.valor,
    t1.data_hora
FROM transacao t1
WHERE t1.valor > (
    SELECT AVG(t2.valor)
    FROM transacao t2
    WHERE t2.numero_conta_origem = t1.numero_conta_origem
)
ORDER BY t1.numero_conta_origem, t1.valor DESC;

-- ----------------------------------------------------------------------------
-- CONSULTA 12 (Subconsulta com EXISTS)
-- Pergunta de Negócio: Quais clientes possuem contratos de empréstimo ativos que 
-- apresentam pelo menos uma parcela atualmente com status 'EM_ATRASO'?
-- ----------------------------------------------------------------------------
SELECT 
    c.id_cliente,
    c.nome AS cliente_inadimplente,
    c.cpf_cnpj,
    c.telefone
FROM cliente c
WHERE EXISTS (
    SELECT 1 
    FROM emprestimo e
    INNER JOIN parcela_emprestimo p ON e.id_emprestimo = p.id_emprestimo
    WHERE e.id_cliente = c.id_cliente 
      AND p.status = 'EM_ATRASO'
);

-- ----------------------------------------------------------------------------
-- CONSULTA 13 (Subconsulta com NOT EXISTS)
-- Pergunta de Negócio: Quais contas bancárias ativas e regulares nunca sofreram 
-- nenhuma alteração ou bloqueio registrado no histórico de status?
-- ----------------------------------------------------------------------------
SELECT 
    cb.numero_conta,
    cb.codigo_agencia,
    cb.modalidade,
    cb.data_abertura,
    cb.saldo
FROM conta_bancaria cb
WHERE cb.status = 'ATIVA'
  AND NOT EXISTS (
    SELECT 1 
    FROM historico_status_conta h
    WHERE h.numero_conta = cb.numero_conta
      AND h.status_novo IN ('BLOQUEADA', 'ENCERRADA')
);

-- ----------------------------------------------------------------------------
-- CONSULTA 14 (Subconsulta Escalar com Window/Agregação)
-- Pergunta de Negócio: Qual o percentual que o saldo de cada conta representa 
-- em relação ao saldo total depositado em sua respectiva agência bancária?
-- ----------------------------------------------------------------------------
SELECT 
    cb.numero_conta,
    cb.codigo_agencia,
    cb.saldo AS saldo_conta,
    (SELECT SUM(cb2.saldo) FROM conta_bancaria cb2 WHERE cb2.codigo_agencia = cb.codigo_agencia) AS saldo_total_agencia,
    ROUND((cb.saldo / (SELECT SUM(cb2.saldo) FROM conta_bancaria cb2 WHERE cb2.codigo_agencia = cb.codigo_agencia)) * 100, 2) AS percentual_agencia
FROM conta_bancaria cb
ORDER BY cb.codigo_agencia, percentual_agencia DESC;

-- ----------------------------------------------------------------------------
-- CONSULTA 15 (Consulta Analítica Complexa de Risco de Crédito)
-- Pergunta de Negócio: Qual é o montante total de crédito concedido, o valor já 
-- amortizado (pago) e a taxa de recuperação financeira por cliente tomador?
-- ----------------------------------------------------------------------------
SELECT 
    c.id_cliente,
    c.nome AS cliente,
    COUNT(DISTINCT e.id_emprestimo) AS total_contratos,
    SUM(e.valor_total) AS total_tomado,
    COALESCE(SUM(CASE WHEN p.status = 'PAGO' THEN p.valor ELSE 0 END), 0.00) AS total_pago,
    COALESCE(SUM(CASE WHEN p.status = 'EM_ATRASO' THEN p.valor ELSE 0 END), 0.00) AS total_atraso,
    ROUND((COALESCE(SUM(CASE WHEN p.status = 'PAGO' THEN p.valor ELSE 0 END), 0.00) / SUM(e.valor_total)) * 100, 2) AS taxa_liquidacao_pct
FROM cliente c
INNER JOIN emprestimo e ON c.id_cliente = e.id_cliente
LEFT JOIN parcela_emprestimo p ON e.id_emprestimo = p.id_emprestimo
GROUP BY c.id_cliente, c.nome
HAVING SUM(e.valor_total) > 0
ORDER BY total_tomado DESC;