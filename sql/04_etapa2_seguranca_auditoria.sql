-- ============================================================================
-- PROJETO FINAL: LABORATÓRIO DE BANCO DE DADOS (UCB 2026/2)
-- SGBD: MySQL 8.0
-- ARQUIVO: 04_etapa2_seguranca_auditoria.sql
-- IMPLEMENTAÇÃO: Artefatos B1, B5 e B6 da Etapa 2 (N2)
-- ============================================================================

USE sistema_bancario;

-- ============================================================================
-- 1. TABELA DE AUDITORIA DEDICADA (B6)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tb_auditoria_sistema (
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
    tabela_afetada VARCHAR(50) NOT NULL,
    operacao VARCHAR(20) NOT NULL,
    registro_id VARCHAR(50) NOT NULL,
    usuario_responsavel VARCHAR(100) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valores_anteriores JSON,
    valores_novos JSON
);

-- ============================================================================
-- 2. GATILHOS DE AUDITORIA (B6)
-- ============================================================================

-- Gatilho 1: Auditoria de Alterações em Conta Bancária (Status, Saldo e Agência)
DROP TRIGGER IF EXISTS trg_audit_conta_bancaria;
DELIMITER $$
CREATE TRIGGER trg_audit_conta_bancaria
AFTER UPDATE ON conta_bancaria
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status OR OLD.codigo_agencia <> NEW.codigo_agencia OR OLD.saldo <> NEW.saldo THEN
        INSERT INTO tb_auditoria_sistema (
            tabela_afetada,
            operacao,
            registro_id,
            usuario_responsavel,
            data_hora,
            valores_anteriores,
            valores_novos
        ) VALUES (
            'conta_bancaria',
            'UPDATE',
            OLD.numero_conta,
            COALESCE(CURRENT_USER(), 'sistema_app'),
            NOW(),
            JSON_OBJECT('status', OLD.status, 'saldo', OLD.saldo, 'codigo_agencia', OLD.codigo_agencia),
            JSON_OBJECT('status', NEW.status, 'saldo', NEW.saldo, 'codigo_agencia', NEW.codigo_agencia)
        );
    END IF;
END$$
DELIMITER ;

-- Gatilho 2: Auditoria de Quitação e Alteração de Parcelas de Empréstimo
DROP TRIGGER IF EXISTS trg_audit_parcela_emprestimo;
DELIMITER $$
CREATE TRIGGER trg_audit_parcela_emprestimo
AFTER UPDATE ON parcela_emprestimo
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status OR OLD.data_pagamento <> NEW.data_pagamento THEN
        INSERT INTO tb_auditoria_sistema (
            tabela_afetada,
            operacao,
            registro_id,
            usuario_responsavel,
            data_hora,
            valores_anteriores,
            valores_novos
        ) VALUES (
            'parcela_emprestimo',
            'UPDATE',
            CONCAT(OLD.id_emprestimo, '-', OLD.numero_parcela),
            COALESCE(CURRENT_USER(), 'sistema_app'),
            NOW(),
            JSON_OBJECT('status', OLD.status, 'data_pagamento', OLD.data_pagamento, 'valor', OLD.valor),
            JSON_OBJECT('status', NEW.status, 'data_pagamento', NEW.data_pagamento, 'valor', NEW.valor)
        );
    END IF;
END$$
DELIMITER ;

-- ============================================================================
-- 3. VISÃO DE RELATÓRIO CONSOLIDADO (B1)
-- ============================================================================
DROP VIEW IF EXISTS vw_relatorio_consolidado_agencias;
CREATE VIEW vw_relatorio_consolidado_agencias AS
SELECT 
    a.codigo_agencia,
    a.nome AS nome_agencia,
    COUNT(DISTINCT cb.numero_conta) AS total_contas_ativas,
    COALESCE(SUM(cb.saldo), 0.00) AS saldo_total_custodia,
    (
        SELECT COALESCE(SUM(t.valor), 0.00) 
        FROM transacao t 
        INNER JOIN conta_bancaria c_origem ON t.numero_conta_origem = c_origem.numero_conta 
        WHERE c_origem.codigo_agencia = a.codigo_agencia
    ) AS volume_total_transacionado,
    (
        SELECT COUNT(t.id_transacao) 
        FROM transacao t 
        INNER JOIN conta_bancaria c_origem ON t.numero_conta_origem = c_origem.numero_conta 
        WHERE c_origem.codigo_agencia = a.codigo_agencia
    ) AS quantidade_transacoes
FROM agencia a
LEFT JOIN conta_bancaria cb ON a.codigo_agencia = cb.codigo_agencia AND cb.status = 'ATIVA'
GROUP BY a.codigo_agencia, a.nome;

-- ============================================================================
-- 4. VISÃO DE RESTRIÇÃO DE PERFIL COM MASCARAMENTO (B5 - LGPD)
-- ============================================================================
DROP VIEW IF EXISTS vw_cliente_atendimento;
CREATE VIEW vw_cliente_atendimento AS
SELECT 
    c.id_cliente,
    c.nome,
    -- Mascaramento de CPF: exibe apenas os 3 primeiros e 2 últimos dígitos (ex: 123.***.***-45)
    CONCAT(SUBSTRING(c.cpf_cnpj, 1, 3), '.***.***-', SUBSTRING(c.cpf_cnpj, 13, 2)) AS cpf_mascarado,
    c.telefone,
    c.email,
    cb.numero_conta,
    cb.modalidade,
    cb.status AS status_conta,
    a.nome AS agencia_vinculada
FROM cliente c
INNER JOIN cliente_conta cc ON c.id_cliente = cc.id_cliente
INNER JOIN conta_bancaria cb ON cc.numero_conta = cb.numero_conta
INNER JOIN agencia a ON cb.codigo_agencia = a.codigo_agencia
WHERE cb.status <> 'ENCERRADA';

-- ============================================================================
-- 5. PERFIS DE ACESSO COM MENOR PRIVILÉGIO (B5 - GRANT / REVOKE)
-- ============================================================================

-- Usuário Administrador (Acesso Irrestrito)
DROP USER IF EXISTS 'user_admin'@'%';
CREATE USER 'user_admin'@'%' IDENTIFIED BY 'AdminPass#2026';
GRANT ALL PRIVILEGES ON sistema_bancario.* TO 'user_admin'@'%';

-- Usuário Atendente de Agência (Acesso Operacional Restrito - Sem exclusões, sem auditoria)
DROP USER IF EXISTS 'user_atendente'@'%';
CREATE USER 'user_atendente'@'%' IDENTIFIED BY 'AtendPass#2026';
GRANT SELECT, INSERT, UPDATE ON sistema_bancario.cliente TO 'user_atendente'@'%';
GRANT SELECT, INSERT, UPDATE ON sistema_bancario.conta_bancaria TO 'user_atendente'@'%';
GRANT SELECT, INSERT, UPDATE ON sistema_bancario.cartao TO 'user_atendente'@'%';
GRANT SELECT, INSERT, UPDATE ON sistema_bancario.beneficiario TO 'user_atendente'@'%';
GRANT SELECT ON sistema_bancario.vw_cliente_atendimento TO 'user_atendente'@'%';
GRANT SELECT, INSERT ON sistema_bancario.transacao TO 'user_atendente'@'%';

-- Usuário Auditor / Compliance (Apenas leitura em tabelas históricas e auditoria)
DROP USER IF EXISTS 'user_auditor'@'%';
CREATE USER 'user_auditor'@'%' IDENTIFIED BY 'AuditPass#2026';
GRANT SELECT ON sistema_bancario.tb_auditoria_sistema TO 'user_auditor'@'%';
GRANT SELECT ON sistema_bancario.historico_status_conta TO 'user_auditor'@'%';
GRANT SELECT ON sistema_bancario.transacao TO 'user_auditor'@'%';
GRANT SELECT ON sistema_bancario.vw_relatorio_consolidado_agencias TO 'user_auditor'@'%';

FLUSH PRIVILEGES;
