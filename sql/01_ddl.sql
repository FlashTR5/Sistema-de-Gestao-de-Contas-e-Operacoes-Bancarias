CREATE DATABASE IF NOT EXISTS sistema_bancario
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE sistema_bancario;

-- 1. TABELAS BASE (INDEPENDENTES)
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

CREATE TABLE agencia (
    codigo_agencia INT AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    CONSTRAINT pk_agencia PRIMARY KEY (codigo_agencia)
);

-- 2. ESTRUTURA DE SETOR E FUNCIONÁRIOS
CREATE TABLE setor (
    id_setor INT AUTO_INCREMENT,
    codigo_agencia INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    CONSTRAINT pk_setor PRIMARY KEY (id_setor),
    CONSTRAINT fk_setor_agencia FOREIGN KEY (codigo_agencia) 
        REFERENCES agencia(codigo_agencia) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE funcionario (
    id_funcionario INT AUTO_INCREMENT,
    codigo_agencia INT NOT NULL,
    id_supervisor INT,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    role_user VARCHAR(50) NOT NULL,
    CONSTRAINT pk_funcionario PRIMARY KEY (id_funcionario),
    CONSTRAINT fk_func_agencia FOREIGN KEY (codigo_agencia) 
        REFERENCES agencia(codigo_agencia) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_func_supervisor FOREIGN KEY (id_supervisor) 
        REFERENCES funcionario(id_funcionario) ON DELETE SET NULL ON UPDATE CASCADE
);

-- RELACIONAMENTO N:N COM ATRIBUTO PRÓPRIO #1 (Funcionário x Setor - Histórico)
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

-- 3. CONTAS E HISTÓRICO TEMPORAL
CREATE TABLE conta_bancaria (
    numero_conta VARCHAR(20),
    codigo_agencia INT NOT NULL,
    modalidade VARCHAR(20) NOT NULL,
    data_abertura DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVA',
    CONSTRAINT pk_conta_bancaria PRIMARY KEY (numero_conta),
    CONSTRAINT fk_conta_agencia FOREIGN KEY (codigo_agencia) 
        REFERENCES agencia(codigo_agencia) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_conta_modalidade CHECK (modalidade IN ('CORRENTE', 'POUPANCA')),
    CONSTRAINT ck_conta_status CHECK (status IN ('ATIVA', 'BLOQUEADA', 'ENCERRADA'))
);

-- RELACIONAMENTO N:N COM ATRIBUTO PRÓPRIO #2 (Cliente x Conta)
CREATE TABLE cliente_conta (
    id_cliente INT NOT NULL,
    numero_conta VARCHAR(20) NOT NULL,
    tipo_titular VARCHAR(20) NOT NULL DEFAULT 'TITULAR',
    data_vinculo DATE NOT NULL,
    CONSTRAINT pk_cliente_conta PRIMARY KEY (id_cliente, numero_conta),
    CONSTRAINT fk_cc_cliente FOREIGN KEY (id_cliente) 
        REFERENCES cliente(id_cliente) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cc_conta FOREIGN KEY (numero_conta) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE CASCADE ON UPDATE CASCADE
);

-- HISTÓRICO DATADO (ENTIDADE TEMPORAL)
CREATE TABLE historico_status_conta (
    id_historico INT AUTO_INCREMENT,
    numero_conta VARCHAR(20) NOT NULL,
    status_anterior VARCHAR(20) NOT NULL,
    status_novo VARCHAR(20) NOT NULL,
    data_alteracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(255),
    CONSTRAINT pk_historico_status PRIMARY KEY (id_historico),
    CONSTRAINT fk_hist_conta FOREIGN KEY (numero_conta) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 4. TRANSAÇÕES E OPERAÇÕES
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
    CONSTRAINT ck_trans_valor CHECK (valor > 0)
);

-- 5. ESPECIALIZAÇÃO / GENERALIZAÇÃO (EMPRÉSTIMOS)
-- SUPERCLASSE
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
    CONSTRAINT ck_emp_status CHECK (status IN ('EM_ANALISE', 'ATIVO', 'QUITADO', 'INADIMPLENTE', 'CANCELADO'))
);

-- SUBCLASSE 1: Consignado
CREATE TABLE emprestimo_consignado (
    id_emprestimo INT NOT NULL,
    orgao_emissor VARCHAR(100) NOT NULL,
    margem_consignavel DECIMAL(5, 2) NOT NULL,
    CONSTRAINT pk_emp_consignado PRIMARY KEY (id_emprestimo),
    CONSTRAINT fk_sub_consignado FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- SUBCLASSE 2: Financiamento
CREATE TABLE financiamento (
    id_emprestimo INT NOT NULL,
    tipo_bem VARCHAR(50) NOT NULL,
    valor_entrada DECIMAL(15, 2) NOT NULL,
    CONSTRAINT pk_financiamento PRIMARY KEY (id_emprestimo),
    CONSTRAINT fk_sub_financiamento FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- SUBCLASSE 3: Empréstimo Pessoal (Mantém o alinhamento com a RN20 do A1)
CREATE TABLE emprestimo_pessoal (
    id_emprestimo INT NOT NULL,
    finalidade VARCHAR(100) NOT NULL,
    taxa_juros_mensal DECIMAL(5, 2) NOT NULL,
    CONSTRAINT pk_emp_pessoal PRIMARY KEY (id_emprestimo),
    CONSTRAINT fk_sub_pessoal FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ENTIDADE FRACA (Chave Composta PK/FK)
CREATE TABLE parcela_emprestimo (
    id_emprestimo INT NOT NULL,
    numero_parcela INT NOT NULL,
    valor DECIMAL(15, 2) NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    CONSTRAINT pk_parcela PRIMARY KEY (id_emprestimo, numero_parcela),
    CONSTRAINT fk_parc_emprestimo FOREIGN KEY (id_emprestimo) 
        REFERENCES emprestimo(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_parc_status CHECK (status IN ('PENDENTE', 'PAGO', 'EM_ATRASO'))
);

-- 6. CARTÕES E BENEFICIÁRIOS
CREATE TABLE cartao (
    numero_cartao VARCHAR(16),
    numero_conta VARCHAR(20) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    status VARCHAR(22) NOT NULL DEFAULT 'AGUARDANDO_DESBLOQUEIO',
    CONSTRAINT pk_cartao PRIMARY KEY (numero_cartao),
    CONSTRAINT fk_cartao_conta FOREIGN KEY (numero_conta) 
        REFERENCES conta_bancaria(numero_conta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_cartao_tipo CHECK (tipo IN ('DEBITO', 'CREDITO', 'MULTIPLO')),
    CONSTRAINT ck_cartao_status CHECK (status IN ('ATIVO', 'BLOQUEADO', 'CANCELADO', 'AGUARDANDO_DESBLOQUEIO'))
);

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
