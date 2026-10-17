-- ============================================================================
-- PROJETO FINAL: LABORATÓRIO DE BANCO DE DADOS (UCB 2026/2)
-- SGBD: MySQL 8.0
-- ARQUIVO: 01_ddl.sql (Script Físico DDL - Versão Revisada com Devolutiva C3)
-- EQUIPE: Gabriel Almeida, Gabriel Reis, Gabriel Lima, Celiandro Borges,
--         Caio Gasparin, Eduardo, Guilherme Barcelos
-- ============================================================================

CREATE DATABASE IF NOT EXISTS sistema_bancario
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE sistema_bancario;

-- Desativa checagem temporariamente para reconstrução limpa
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS tb_auditoria_sistema;
DROP TABLE IF EXISTS beneficiario;
DROP TABLE IF EXISTS cartao;
DROP TABLE IF EXISTS parcela_emprestimo;
DROP TABLE IF EXISTS emprestimo_pessoal;
DROP TABLE IF EXISTS financiamento;
DROP TABLE IF EXISTS emprestimo_consignado;
DROP TABLE IF EXISTS emprestimo;
DROP TABLE IF EXISTS transacao;
DROP TABLE IF EXISTS historico_status_conta;
DROP TABLE IF EXISTS cliente_conta;
DROP TABLE IF EXISTS conta_bancaria;
DROP TABLE IF EXISTS funcionario_setor;
DROP TABLE IF EXISTS funcionario;
DROP TABLE IF EXISTS setor;
DROP TABLE IF EXISTS agencia;
DROP TABLE IF EXISTS cliente;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 1. TABELAS BASE INDEPENDENTES
-- ============================================================================

-- Tabela Cliente (Implementa RN01: Identificação de titular por CPF/CNPJ único)
CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT,
    cpf_cnpj VARCHAR(18) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cliente_cpf_cnpj UNIQUE (cpf_cnpj),
    CONSTRAINT uq_cliente_email UNIQUE (email)
);

-- Tabela Agência (Implementa RN02: Toda agência possui código e endereço físico)
CREATE TABLE agencia (
    codigo_agencia INT AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    CONSTRAINT pk_agencia PRIMARY KEY (codigo_agencia)
);

-- ============================================================================
-- 2. ESTRUTURA ORGANIZACIONAL E FUNCIONÁRIOS
-- ============================================================================

-- Tabela Setor (Implementa RN03: Setor vinculado a uma agência)
CREATE TABLE setor (
    id_setor INT AUTO_INCREMENT,
    codigo_agencia INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    CONSTRAINT pk_setor PRIMARY KEY (id_setor),
    CONSTRAINT fk_setor_agencia FOREIGN KEY (codigo_agencia) 
        REFERENCES agencia(codigo_agencia) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX idx_setor_agencia ON setor(codigo_agencia);

-- Tabela Funcionário (Implementa RN04: Hierarquia de supervisão e alocação)
-- Atende ao C3: CHECK de cargos válidos
CREATE TABLE funcionario (
    id_funcionario INT AUTO_INCREMENT,
    codigo_agencia INT NOT NULL,
    id_supervisor INT,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    role_user VARCHAR(50) NOT NULL DEFAULT 'ROLE_ATENDENTE',
    CONSTRAINT pk_funcionario PRIMARY KEY (id_funcionario),
    CONSTRAINT fk_func_agencia FOREIGN KEY (codigo_agencia) 
        REFERENCES agencia(codigo_agencia) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_func_supervisor FOREIGN KEY (id_supervisor) 
        REFERENCES funcionario(id_funcionario) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_func_cargo CHECK (cargo IN ('Gerente Geral', 'Gerente de Contas', 'Líder de Setor', 'Atendente', 'Analista de Crédito', 'Caixa'))
);
CREATE INDEX idx_func_agencia ON funcionario(codigo_agencia);
CREATE INDEX idx_func_supervisor ON funcionario(id_supervisor);

-- Relacionamento N:N com Atributo Próprio #1: Funcionário x Setor (Vigência)
-- (Implementa RN05: Rastreio de papéis e vigência em setores)
CREATE TABLE funcionario_setor (
    id_funcionario INT NOT NULL,
    id_setor INT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    papel_desempenhado VARCHAR(50) NOT NULL,
    CONSTRAINT pk_func_setor PRIMARY KEY (id_funcionario, id_setor, data_inicio),
    CONSTRAINT fk_fs_funcionario FOREIGN KEY (id_funcionario) 
        REFERENCES funcionario(id_funcionario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_fs_setor FOREIGN KEY (id_setor) 
        REFERENCES setor(id_setor) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX idx_fs_setor ON funcionario_setor(id_setor);

-- ============================================================================
-- 3. CONTAS BANCÁRIAS E HISTÓRICO TEMPORAL
-- ============================================================================

-- Tabela Conta Bancária (Implementa RN06: Contas correntes e poupanças ativas/bloqueadas)
CREATE TABLE conta_bancaria (
    numero_conta VARCHAR(20),
    codigo_agencia INT NOT NULL,
    modalidade VARCHAR(20) NOT NULL,
    saldo DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    data_abertura DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVA',
    CONSTRAINT pk_conta_bancaria PRIMARY KEY (numero_conta),
    CONSTRAINT fk_conta_agencia FOREIGN KEY (codigo_agencia) 
        REFERENCES agencia(codigo_agencia) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_conta_modalidade CHECK (modalidade IN ('CORRENTE', 'POUPANCA')),
    CONSTRAINT ck_conta_status CHECK (status IN ('ATIVA', 'BLOQUEADA', 'ENCERRADA'))
);
CREATE INDEX idx_conta_agencia ON conta_bancaria(codigo_agencia);
CREATE INDEX idx_conta_status ON conta_bancaria(status);

-- Relacionamento N:N com Atributo Próprio #2: Cliente x Conta (Titularidade)
-- (Implementa RN07: Associação de titulares e co-titulares à conta)
-- Atende ao C3: CHECK de tipos de titular
CREATE TABLE cliente_conta (
    id_cliente INT NOT NULL,
    numero_conta VARCHAR(20) NOT NULL,
    tipo_titular VARCHAR(20) NOT NULL DEFAULT 'TITULAR',
    data_vinculo DATE NOT NULL,
    CONSTRAINT pk_cliente_conta PRIMARY KEY (id_cliente, numero_conta),
    CONSTRAINT fk_cc_cliente FOREIGN KEY (id_cliente) 
        REFERENCES cliente(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cc_conta FOREIGN KEY (numero_conta) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_cc_tipo_titular CHECK (tipo_titular IN ('TITULAR', 'CO-TITULAR', 'AUTORIZADO'))
);
CREATE INDEX idx_cc_conta ON cliente_conta(numero_conta);

-- Entidade Fraca / Histórico Datado: Histórico de Status da Conta
-- (Implementa RN08: Auditoria temporal das transições de status)
-- Atende à Devolutiva C1 e C3: Identificação por dependência e RESTRICT para integridade financeira
CREATE TABLE historico_status_conta (
    id_historico INT AUTO_INCREMENT,
    numero_conta VARCHAR(20) NOT NULL,
    status_anterior VARCHAR(20) NOT NULL,
    status_novo VARCHAR(20) NOT NULL,
    data_alteracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(255),
    CONSTRAINT pk_historico_status PRIMARY KEY (id_historico),
    CONSTRAINT fk_hist_conta FOREIGN KEY (numero_conta) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX idx_hist_conta_data ON historico_status_conta(numero_conta, data_alteracao);

-- ============================================================================
-- 4. TRANSAÇÕES FINANCEIRAS (ATENÇÃO CRÍTICA A RESTRICT CONFORME C3)
-- ============================================================================

-- Tabela Transação (Implementa RN09: Rastreabilidade financeira inalterável)
-- Atende ao C3: ON DELETE RESTRICT (proibido CASCADE em transações financeiras) e CHECK de tipo
CREATE TABLE transacao (
    id_transacao INT AUTO_INCREMENT,
    numero_conta_origem VARCHAR(20) NOT NULL,
    numero_conta_destino VARCHAR(20),
    tipo VARCHAR(20) NOT NULL,
    valor DECIMAL(15, 2) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_transacao PRIMARY KEY (id_transacao),
    CONSTRAINT fk_trans_origem FOREIGN KEY (numero_conta_origem) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_trans_destino FOREIGN KEY (numero_conta_destino) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_trans_valor CHECK (valor > 0),
    CONSTRAINT ck_trans_tipo CHECK (tipo IN ('PIX', 'TED', 'DOC', 'DEPOSITO', 'SAQUE', 'PAGAMENTO_BOLETO', 'TRANSFERENCIA'))
);
CREATE INDEX idx_trans_origem_data ON transacao(numero_conta_origem, data_hora);
CREATE INDEX idx_trans_destino ON transacao(numero_conta_destino);
CREATE INDEX idx_trans_tipo ON transacao(tipo);

-- ============================================================================
-- 5. ESPECIALIZAÇÃO / GENERALIZAÇÃO: EMPRÉSTIMOS E CRÉDITO
-- ============================================================================

-- Superclasse Empréstimo (Implementa RN10: Solicitação de crédito)
-- Atende ao C3: CHECK de modalidade
CREATE TABLE emprestimo (
    id_emprestimo INT AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    tipo_modalidade VARCHAR(50) NOT NULL,
    valor_total DECIMAL(15, 2) NOT NULL,
    data_contratacao DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'EM_ANALISE',
    CONSTRAINT pk_emprestimo PRIMARY KEY (id_emprestimo),
    CONSTRAINT fk_emp_cliente FOREIGN KEY (id_cliente) 
        REFERENCES cliente(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_emp_status CHECK (status IN ('EM_ANALISE', 'ATIVO', 'QUITADO', 'INADIMPLENTE', 'CANCELADO')),
    CONSTRAINT ck_emp_modalidade CHECK (tipo_modalidade IN ('CONSIGNADO', 'FINANCIAMENTO', 'PESSOAL'))
);
CREATE INDEX idx_emp_cliente ON emprestimo(id_cliente);
CREATE INDEX idx_emp_status ON emprestimo(status);

-- Subclasse 1: Consignado (Implementa RN11)
CREATE TABLE emprestimo_consignado (
    id_emprestimo INT NOT NULL,
    orgao_emissor VARCHAR(100) NOT NULL,
    margem_consignavel DECIMAL(5, 2) NOT NULL,
    CONSTRAINT pk_emp_consignado PRIMARY KEY (id_emprestimo),
    CONSTRAINT fk_sub_consignado FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Subclasse 2: Financiamento (Implementa RN12)
CREATE TABLE financiamento (
    id_emprestimo INT NOT NULL,
    tipo_bem VARCHAR(50) NOT NULL,
    valor_entrada DECIMAL(15, 2) NOT NULL,
    CONSTRAINT pk_financiamento PRIMARY KEY (id_emprestimo),
    CONSTRAINT fk_sub_financiamento FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Subclasse 3: Empréstimo Pessoal (Implementa RN13)
CREATE TABLE emprestimo_pessoal (
    id_emprestimo INT NOT NULL,
    finalidade VARCHAR(100) NOT NULL,
    taxa_juros_mensal DECIMAL(5, 2) NOT NULL,
    CONSTRAINT pk_emp_pessoal PRIMARY KEY (id_emprestimo),
    CONSTRAINT fk_sub_pessoal FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Entidade Fraca: Parcelas do Empréstimo (Chave composta com o identificador do pai)
-- (Implementa RN14: Parcelamento financeiro)
CREATE TABLE parcela_emprestimo (
    id_emprestimo INT NOT NULL,
    numero_parcela INT NOT NULL,
    valor DECIMAL(15, 2) NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    CONSTRAINT pk_parcela PRIMARY KEY (id_emprestimo, numero_parcela),
    CONSTRAINT fk_parc_emprestimo FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_parc_status CHECK (status IN ('PENDENTE', 'PAGO', 'EM_ATRASO'))
);
CREATE INDEX idx_parc_status_venc ON parcela_emprestimo(status, data_vencimento);

-- ============================================================================
-- 6. CARTÕES E BENEFICIÁRIOS
-- ============================================================================

-- Tabela Cartão (Implementa RN15: Meio de pagamento físico/virtual)
CREATE TABLE cartao (
    numero_cartao VARCHAR(16),
    numero_conta VARCHAR(20) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    status VARCHAR(25) NOT NULL DEFAULT 'AGUARDANDO_DESBLOQUEIO',
    CONSTRAINT pk_cartao PRIMARY KEY (numero_cartao),
    CONSTRAINT fk_cartao_conta FOREIGN KEY (numero_conta) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_cartao_tipo CHECK (tipo IN ('DEBITO', 'CREDITO', 'MULTIPLO')),
    CONSTRAINT ck_cartao_status CHECK (status IN ('ATIVO', 'BLOQUEADO', 'CANCELADO', 'AGUARDANDO_DESBLOQUEIO'))
);
CREATE INDEX idx_cartao_conta ON cartao(numero_conta);

-- Tabela Beneficiário (Implementa RN16: Contatos cadastrados para favorecidos de transferência)
CREATE TABLE beneficiario (
    id_beneficiario INT AUTO_INCREMENT,
    numero_conta_origem VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    documento VARCHAR(18) NOT NULL,
    banco VARCHAR(50) NOT NULL,
    agencia VARCHAR(10) NOT NULL,
    conta VARCHAR(20) NOT NULL,
    CONSTRAINT pk_beneficiario PRIMARY KEY (id_beneficiario),
    CONSTRAINT fk_benef_conta FOREIGN KEY (numero_conta_origem) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX idx_benef_conta ON beneficiario(numero_conta_origem);
