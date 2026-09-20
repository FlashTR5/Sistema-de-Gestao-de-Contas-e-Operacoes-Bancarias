USE sistema_bancario;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE beneficiario;
TRUNCATE TABLE cartao;
TRUNCATE TABLE parcela_emprestimo;
TRUNCATE TABLE emprestimo_pessoal;
TRUNCATE TABLE financiamento;
TRUNCATE TABLE emprestimo_consignado;
TRUNCATE TABLE emprestimo;
TRUNCATE TABLE transacao;
TRUNCATE TABLE historico_status_conta;
TRUNCATE TABLE cliente_conta;
TRUNCATE TABLE conta_bancaria;
TRUNCATE TABLE funcionario_setor;
TRUNCATE TABLE funcionario;
TRUNCATE TABLE setor;
TRUNCATE TABLE agencia;
TRUNCATE TABLE cliente;
SET FOREIGN_KEY_CHECKS = 1;


-- 1. CARGA DE CLIENTES
INSERT INTO cliente (cpf_cnpj, nome, telefone, email) VALUES
('111.222.333-04', 'Carlos Eduardo Silva', '(61) 98888-1111', 'carlos.silva@email.com'),
('222.333.444-05', 'Mariana Santos Rocha', '(61) 97777-2222', 'mariana.rocha@email.com'),
('333.444.555-06', 'Lucas Fernandes Lima', '(61) 96666-3333', 'lucas.lima@email.com'),
('12.345.678/0001-90', 'Tech Solutions LTDA', '(61) 3333-4444', 'contato@techsolutions.com');

-- 2. CARGA DE AGÊNCIAS
INSERT INTO agencia (nome, endereco) VALUES
('Agência Central Brasília', 'SBN Quadra 2 Bloco J, Brasília - DF'),
('Agência Taguatinga', 'C12 Bloco A, Taguatinga Centro - DF');

-- 3. CARGA DE SETORES
INSERT INTO setor (codigo_agencia, nome) VALUES
(1, 'Diretoria Geral'),
(1, 'Crédito e Empréstimos'),
(1, 'Cartões e Atendimento'),
(2, 'Gerência Geral'),
(2, 'Atendimento ao Cliente');


-- 4. CARGA DE FUNCIONÁRIOS E AUTORRELACIONAMENTO (HIERARQUIA)
-- Gerente Geral da Agência 1 (Sem supervisor)
INSERT INTO funcionario (codigo_agencia, id_supervisor, nome, cargo, role_user) VALUES
(1, NULL, 'Roberto Alves', 'Gerente Geral', 'ROLE_GERENTE_GERAL');

-- Líderes e Atendentes da Agência 1 (Supervisionados por Roberto Alves - ID 1)
INSERT INTO funcionario (codigo_agencia, id_supervisor, nome, cargo, role_user) VALUES
(1, 1, 'Fernanda Costa', 'Líder de Setor', 'ROLE_LIDER'),
(1, 1, 'Beatriz Souza', 'Atendente', 'ROLE_ATENDENTE');

-- Gerente Geral da Agência 2 (Sem supervisor)
INSERT INTO funcionario (codigo_agencia, id_supervisor, nome, cargo, role_user) VALUES
(2, NULL, 'Ricardo Mendes', 'Gerente Geral', 'ROLE_GERENTE_GERAL');



-- 5. HISTÓRICO DE FUNCIONÁRIO E SETOR (N:N)
INSERT INTO funcionario_setor (id_funcionario, id_setor, data_inicio, data_fim, papel_desempenhado) VALUES
(1, 1, '2020-01-15', NULL, 'Gestor Geral da Agência'),
(2, 2, '2021-03-01', NULL, 'Supervisora de Crédito'),
(3, 3, '2022-06-10', NULL, 'Atendimento ao Público'),
(4, 4, '2019-11-01', NULL, 'Gestor Geral da Agência');


-- 6. CARGA DE CONTAS BANCÁRIAS
INSERT INTO conta_bancaria (numero_conta, codigo_agencia, modalidade, data_abertura, status) VALUES
('1001-0', 1, 'CORRENTE', '2021-02-10', 'ATIVA'),
('1002-8', 1, 'POUPANCA', '2021-05-20', 'ATIVA'),
('2001-5', 2, 'CORRENTE', '2022-01-15', 'ATIVA'),
('2002-3', 2, 'CORRENTE', '2023-03-10', 'BLOQUEADA');


-- 7. VÍNCULO CLIENTE E CONTA (N:N)
INSERT INTO cliente_conta (id_cliente, numero_conta, tipo_titular, data_vinculo) VALUES
(1, '1001-0', 'TITULAR', '2021-02-10'),
(1, '1002-8', 'TITULAR', '2021-05-20'),
(2, '2001-5', 'TITULAR', '2022-01-15'),
(3, '2001-5', 'COTITULAR', '2022-02-01'),
(4, '2002-3', 'TITULAR', '2023-03-10');


-- 8. HISTÓRICO DE STATUS DAS CONTAS
INSERT INTO historico_status_conta (numero_conta, status_anterior, status_novo, data_alteracao, motivo) VALUES
('2002-3', 'ATIVA', 'BLOQUEADA', '2026-08-15 14:30:00', 'Suspeita de fraude / Documentação pendente');


-- 9. CARGA DE TRANSAÇÕES
INSERT INTO transacao (numero_conta_origem, numero_conta_destino, tipo, valor, data_hora) VALUES
('1001-0', NULL, 'DEPOSITO', 5000.00, '2026-09-01 10:15:00'),
('1001-0', '2001-5', 'TRANSFERENCIA', 1200.00, '2026-09-02 11:30:00'),
('2001-5', NULL, 'SAQUE', 300.00, '2026-09-05 16:45:00');


-- 10. ESPECIALIZAÇÃO DE EMPRÉSTIMOS E PARCELAS
-- Contrato 1: Consignado (Carlos Eduardo)
INSERT INTO emprestimo (id_cliente, tipo_modalidade, valor_total, data_contratacao, status) VALUES
(1, 'Consignado', 15000.00, '2026-01-10', 'ATIVO');

INSERT INTO emprestimo_consignado (id_emprestimo, orgao_emissor, margem_consignavel) VALUES
(1, 'Ministério da Educação', 30.00);

INSERT INTO parcela_emprestimo (id_emprestimo, numero_parcela, valor, data_vencimento, data_pagamento, status) VALUES
(1, 1, 1250.00, '2026-02-10', '2026-02-08', 'PAGO'),
(1, 2, 1250.00, '2026-03-10', '2026-03-10', 'PAGO'),
(1, 3, 1250.00, '2026-04-10', NULL, 'PENDENTE');

-- Contrato 2: Financiamento (Mariana Santos)
INSERT INTO emprestimo (id_cliente, tipo_modalidade, valor_total, data_contratacao, status) VALUES
(2, 'Financiamento', 80000.00, '2026-05-20', 'ATIVO');

INSERT INTO financiamento (id_emprestimo, tipo_bem, valor_entrada) VALUES
(2, 'Veiculo', 20000.00);

INSERT INTO parcela_emprestimo (id_emprestimo, numero_parcela, valor, data_vencimento, data_pagamento, status) VALUES
(2, 1, 1800.00, '2026-06-20', '2026-06-19', 'PAGO'),
(2, 2, 1800.00, '2026-07-20', NULL, 'EM_ATRASO');

-- Contrato 3: Pessoal (Carlos Eduardo)
INSERT INTO emprestimo (id_cliente, tipo_modalidade, valor_total, data_contratacao, status) VALUES
(1, 'Pessoal', 5000.00, '2026-07-01', 'ATIVO');

INSERT INTO emprestimo_pessoal (id_emprestimo, finalidade, taxa_juros_mensal) VALUES
(3, 'Viagem e Lazer', 2.50);

INSERT INTO parcela_emprestimo (id_emprestimo, numero_parcela, valor, data_vencimento, data_pagamento, status) VALUES
(3, 1, 1000.00, '2026-08-01', '2026-08-01', 'PAGO');


-- 11. CARGA DE CARTÕES E BENEFICIÁRIOS
INSERT INTO cartao (numero_cartao, numero_conta, tipo, status) VALUES
('4532111122223333', '1001-0', 'MULTIPLO', 'ATIVO'),
('5412888899990000', '2001-5', 'DEBITO', 'ATIVO'),
('4012333344445555', '2002-3', 'CREDITO', 'BLOQUEADO');

INSERT INTO beneficiario (numero_conta_origem, nome, documento, banco, agencia, conta) VALUES
('1001-0', 'João Pereira', '444.555.666-07', 'Banco Itaú', '0123', '98765-4'),
('2001-5', 'Maria de Fatima', '555.666.777-08', 'Banco do Brasil', '1234', '11223-3');