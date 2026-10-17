#!/usr/bin/env python3
"""
Gerador de Cargas Realistas para o Sistema Bancário (Meta da Devolutiva C4)
- 45 Clientes (PF e PJ)
- 5 Agências
- 10 Setores
- 15 Funcionários
- 45 Contas Bancárias (Corrente e Poupança, saldos realistas)
- 48 Vínculos Cliente-Conta (inclui co-titulares e autorizados)
- 45 Cartões (Débito, Crédito, Múltiplo)
- 40 Históricos de Status de Conta
- 42 Empréstimos (Consignados, Financiamentos e Pessoais)
- 85 Parcelas (Pagas, Pendentes e Em Atraso)
- 120 Transações Financeiras (PIX, TED, DOC, Depósito, Saque, Boleto)
- 30 Beneficiários
"""

import random
from datetime import datetime, timedelta

def main():
    sql = []
    sql.append("-- ============================================================================")
    sql.append("-- PROJETO FINAL: LABORATÓRIO DE BANCO DE DADOS (UCB 2026/2)")
    sql.append("-- ARQUIVO: 02_Cargas.sql (Carga Realista Completa - Atende Devolutiva C4)")
    sql.append("-- Metas: 40+ linhas nas tabelas principais e 100+ na tabela transacao")
    sql.append("-- ============================================================================\n")
    sql.append("USE sistema_bancario;\n")
    sql.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql.append("TRUNCATE TABLE beneficiario;")
    sql.append("TRUNCATE TABLE cartao;")
    sql.append("TRUNCATE TABLE parcela_emprestimo;")
    sql.append("TRUNCATE TABLE emprestimo_pessoal;")
    sql.append("TRUNCATE TABLE financiamento;")
    sql.append("TRUNCATE TABLE emprestimo_consignado;")
    sql.append("TRUNCATE TABLE emprestimo;")
    sql.append("TRUNCATE TABLE transacao;")
    sql.append("TRUNCATE TABLE historico_status_conta;")
    sql.append("TRUNCATE TABLE cliente_conta;")
    sql.append("TRUNCATE TABLE conta_bancaria;")
    sql.append("TRUNCATE TABLE funcionario_setor;")
    sql.append("TRUNCATE TABLE funcionario;")
    sql.append("TRUNCATE TABLE setor;")
    sql.append("TRUNCATE TABLE agencia;")
    sql.append("TRUNCATE TABLE cliente;")
    sql.append("SET FOREIGN_KEY_CHECKS = 1;\n")

    # 1. CLIENTES (45)
    nomes_pf = [
        "Carlos Eduardo Silva", "Mariana Santos Rocha", "Lucas Fernandes Lima", "Beatriz Alves Moreira",
        "Rafael Souza Carvalho", "Juliana Mendes Nogueira", "Fernando Henrique Castro", "Aline Barbosa Dias",
        "Rodrigo Pires Guimaraes", "Camila Duarte Martins", "Thiago Ribeiro Farias", "Patricia Gomes Silveira",
        "Marcelo Ramos Teixeira", "Fernanda Cardoso Lopes", "Gustavo Henrique Borges", "Bruna Vieira Antunes",
        "Diego Nascimento Correa", "Larissa Azevedo Pinto", "Bruno Cesar Magalhaes", "Renata Figueiredo Morais",
        "Leonardo Bastos Cunha", "Vanessa Toledo Peixoto", "Eduardo Paiva Rezende", "Jessica Meireles Prado",
        "Felipe Santana Teles", "Sabrina Esteves Frota", "Alexandre Neves Macedo", "Daniela Vasconcelos",
        "Marcos Vinicius Porto", "Debora Barreto Miranda", "Caio Castro Alencar", "Tatiane Viana Brandao",
        "Igor Siqueira Pacheco", "Monique Tavares Maia", "Leandro Fontes Dorneles", "Leticia Albuquerque",
        "Henrique Salgado Muniz", "Flavia Chaves Goulart", "Andre Luiz Pimentel", "Gisele Medeiros Bicalho"
    ]
    nomes_pj = [
        "Tech Solutions LTDA", "Comercio de Alimentos Brasilia SA", "Inovacao Digital Consultoria ME",
        "Alpha Servicos de Engenharia EIRELI", "Logistica & Transportes Centro-Oeste LTDA"
    ]

    sql.append("-- 1. CARGA DE CLIENTES (45 registros: 40 PF e 5 PJ - Casos de contorno com telefones opcionais)")
    sql.append("INSERT INTO cliente (id_cliente, cpf_cnpj, nome, telefone, email) VALUES")
    cli_rows = []
    
    # 40 PF
    for i, nome in enumerate(nomes_pf, 1):
        cpf = f"{i:03d}.{((i*7)%900)+100:03d}.{((i*13)%900)+100:03d}-{(i*3)%89 + 10:02d}"
        tel = f"'(61) 9{random.randint(8000,9999)}-{random.randint(1000,9999)}'" if i % 5 != 0 else "NULL"
        email = f"'{nome.lower().replace(' ', '.')}@email.com'"
        cli_rows.append(f"({i}, '{cpf}', '{nome}', {tel}, {email})")
    
    # 5 PJ
    for j, nome in enumerate(nomes_pj, 41):
        cnpj = f"{j:02d}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}"
        tel = f"'(61) 3{random.randint(100,999)}-{random.randint(1000,9999)}'"
        email = f"'contato@{nome.split()[0].lower()}.com.br'"
        cli_rows.append(f"({j}, '{cnpj}', '{nome}', {tel}, {email})")
    sql.append(",\n".join(cli_rows) + ";\n")

    # 2. AGÊNCIAS (5)
    sql.append("-- 2. CARGA DE AGÊNCIAS (5 agências)")
    sql.append("INSERT INTO agencia (codigo_agencia, nome, endereco) VALUES")
    agencias = [
        "(1, 'Agência Central Brasília', 'SBN Quadra 2 Bloco J, Asa Norte, Brasília - DF')",
        "(2, 'Agência Taguatinga Centro', 'C12 Bloco A, Taguatinga Centro, Taguatinga - DF')",
        "(3, 'Agência Águas Claras', 'Rua das Figueiras Lote 5, Águas Claras - DF')",
        "(4, 'Agência Asa Sul', 'CLS 204 Bloco B, Asa Sul, Brasília - DF')",
        "(5, 'Agência Ceilândia Norte', 'CNN 1 Bloco F, Ceilândia Norte - DF')"
    ]
    sql.append(",\n".join(agencias) + ";\n")

    # 3. SETORES (10)
    sql.append("-- 3. CARGA DE SETORES (10 setores)")
    sql.append("INSERT INTO setor (id_setor, codigo_agencia, nome) VALUES")
    setores = [
        "(1, 1, 'Diretoria Geral')", "(2, 1, 'Crédito e Empréstimos')", "(3, 1, 'Atendimento Geral')",
        "(4, 2, 'Gerência Geral')", "(5, 2, 'Atendimento ao Cliente')", "(6, 3, 'Operações de Câmbio')",
        "(7, 3, 'Contas e Cartões')", "(8, 4, 'Investimentos Private')", "(9, 4, 'Crédito Imobiliário')",
        "(10, 5, 'Caixa e Retaguarda')"
    ]
    sql.append(",\n".join(setores) + ";\n")

    # 4. FUNCIONÁRIOS (15 com hierarquia)
    sql.append("-- 4. CARGA DE FUNCIONÁRIOS E HIERARQUIA (15 registros com autorrelacionamento)")
    sql.append("INSERT INTO funcionario (id_funcionario, codigo_agencia, id_supervisor, nome, cargo, role_user) VALUES")
    funcs = [
        "(1, 1, NULL, 'Roberto Alves Moreira', 'Gerente Geral', 'ROLE_GERENTE_GERAL')",
        "(2, 1, 1, 'Fernanda Costa Toledo', 'Líder de Setor', 'ROLE_LIDER')",
        "(3, 1, 1, 'Beatriz Souza Silveira', 'Analista de Crédito', 'ROLE_ANALISTA')",
        "(4, 1, 2, 'Lucas Marinho Dantas', 'Atendente', 'ROLE_ATENDENTE')",
        "(5, 1, 2, 'Priscila Ramos Lima', 'Caixa', 'ROLE_CAIXA')",
        "(6, 2, NULL, 'Ricardo Mendes Barreto', 'Gerente Geral', 'ROLE_GERENTE_GERAL')",
        "(7, 2, 6, 'Sergio Murilo Farias', 'Líder de Setor', 'ROLE_LIDER')",
        "(8, 2, 7, 'Claudia Valente Porto', 'Atendente', 'ROLE_ATENDENTE')",
        "(9, 3, NULL, 'Helena Guimaraes Prado', 'Gerente Geral', 'ROLE_GERENTE_GERAL')",
        "(10, 3, 9, 'Tiago Alcantara Dias', 'Gerente de Contas', 'ROLE_GERENTE_CONTAS')",
        "(11, 3, 10, 'Milena Queiroz Melo', 'Atendente', 'ROLE_ATENDENTE')",
        "(12, 4, NULL, 'Arthur Fontenele Castro', 'Gerente Geral', 'ROLE_GERENTE_GERAL')",
        "(13, 4, 12, 'Monica Saraiva Bezerra', 'Gerente de Contas', 'ROLE_GERENTE_CONTAS')",
        "(14, 5, NULL, 'Fabio Junqueira Pinto', 'Gerente Geral', 'ROLE_GERENTE_GERAL')",
        "(15, 5, 14, 'Eliane Correa Vilela', 'Caixa', 'ROLE_CAIXA')"
    ]
    sql.append(",\n".join(funcs) + ";\n")

    # 5. FUNCIONÁRIO_SETOR (15)
    sql.append("-- 5. FUNCIONÁRIO SETOR (15 registros)")
    sql.append("INSERT INTO funcionario_setor (id_funcionario, id_setor, data_inicio, data_fim, papel_desempenhado) VALUES")
    fs_rows = []
    for fid in range(1, 16):
        setor_id = ((fid - 1) % 10) + 1
        data_ini = f"2023-{(fid % 12) + 1:02d}-01"
        data_fim = "NULL" if fid % 4 != 0 else f"'2024-{(fid % 12) + 1:02d}-28'"
        papel = "Gestor" if fid in (1, 6, 9, 12, 14) else "Operacional"
        fs_rows.append(f"({fid}, {setor_id}, '{data_ini}', {data_fim}, '{papel}')")
    sql.append(",\n".join(fs_rows) + ";\n")

    # 6. CONTAS BANCÁRIAS (45)
    sql.append("-- 6. CARGA DE CONTAS BANCÁRIAS (45 registros - atende C4 e inclui status BLOQUEADA/ENCERRADA)")
    sql.append("INSERT INTO conta_bancaria (numero_conta, codigo_agencia, modalidade, saldo, data_abertura, status) VALUES")
    contas = []
    for c in range(1, 46):
        num = f"100{c:02d}-X"
        ag = ((c - 1) % 5) + 1
        mod = "CORRENTE" if c % 3 != 0 else "POUPANCA"
        saldo = round(random.uniform(500.0, 55000.0), 2)
        status = "ATIVA"
        if c == 13: status = "BLOQUEADA"
        if c == 27: status = "ENCERRADA"; saldo = 0.00
        if c == 40: status = "BLOQUEADA"
        data_ab = f"2022-{(c % 11) + 1:02d}-{(c % 25) + 1:02d}"
        contas.append(f"('{num}', {ag}, '{mod}', {saldo:.2f}, '{data_ab}', '{status}')")
    sql.append(",\n".join(contas) + ";\n")

    # 7. CLIENTE_CONTA (48 vínculos)
    sql.append("-- 7. CLIENTE CONTA (48 vínculos N:N - Casos com Co-titular e Autorizado)")
    sql.append("INSERT INTO cliente_conta (id_cliente, numero_conta, tipo_titular, data_vinculo) VALUES")
    cc_rows = []
    for c in range(1, 46):
        cc_rows.append(f"({c}, '100{c:02d}-X', 'TITULAR', '2023-01-15')")
    # Casos de Co-titularidade
    cc_rows.append("(2, '10001-X', 'CO-TITULAR', '2023-02-10')")
    cc_rows.append("(4, '10003-X', 'CO-TITULAR', '2023-03-01')")
    cc_rows.append("(6, '10005-X', 'AUTORIZADO', '2023-04-12')")
    sql.append(",\n".join(cc_rows) + ";\n")

    # 8. HISTÓRICO STATUS CONTA (40 registros)
    sql.append("-- 8. HISTÓRICO DE STATUS (40 registros - auditoria temporal)")
    sql.append("INSERT INTO historico_status_conta (numero_conta, status_anterior, status_novo, data_alteracao, motivo) VALUES")
    hist_rows = []
    motivos = ["Abertura e ativação da conta", "Suspeita de fraude preventiva", "Regularização cadastral", "Solicitação do cliente", "Encerramento formal de conta"]
    for h in range(1, 41):
        cnum = f"100{h:02d}-X"
        santerior = "EM_ANALISE" if h <= 35 else "ATIVA"
        snovo = "ATIVA" if h <= 35 else ("BLOQUEADA" if h % 2 == 0 else "ENCERRADA")
        dt = f"2024-{(h % 9) + 1:02d}-{(h % 27) + 1:02d} 14:30:00"
        mot = random.choice(motivos)
        hist_rows.append(f"('{cnum}', '{santerior}', '{snovo}', '{dt}', '{mot}')")
    sql.append(",\n".join(hist_rows) + ";\n")

    # 9. CARTÕES (45 registros)
    sql.append("-- 9. CARGA DE CARTÕES (45 registros)")
    sql.append("INSERT INTO cartao (numero_cartao, numero_conta, tipo, status) VALUES")
    cartao_rows = []
    tipos = ["DEBITO", "CREDITO", "MULTIPLO"]
    status_cartao = ["ATIVO", "ATIVO", "ATIVO", "BLOQUEADO", "AGUARDANDO_DESBLOQUEIO"]
    for k in range(1, 46):
        num_c = f"4532{k:04d}9876{random.randint(1000,9999)}"[:16]
        cnum = f"100{k:02d}-X"
        tipo = tipos[k % 3]
        st = status_cartao[k % 5]
        cartao_rows.append(f"('{num_c}', '{cnum}', '{tipo}', '{st}')")
    sql.append(",\n".join(cartao_rows) + ";\n")

    # 10. BENEFICIÁRIOS (30)
    sql.append("-- 10. CARGA DE BENEFICIÁRIOS (30 registros)")
    sql.append("INSERT INTO beneficiario (numero_conta_origem, nome, documento, banco, agencia, conta) VALUES")
    ben_rows = []
    bancos = ["001 - Banco do Brasil", "104 - Caixa Economica", "237 - Bradesco", "341 - Itau Unibanco", "260 - Nu Pagamentos"]
    for b in range(1, 31):
        c_origem = f"100{((b - 1) % 45) + 1:02d}-X"
        nome_ben = f"Favorecido {b} Silva"
        doc = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
        bco = bancos[b % 5]
        ag = f"0{random.randint(100,999)}"
        cta = f"{random.randint(10000,99999)}-{random.randint(0,9)}"
        ben_rows.append(f"('{c_origem}', '{nome_ben}', '{doc}', '{bco}', '{ag}', '{cta}')")
    sql.append(",\n".join(ben_rows) + ";\n")

    # 11. EMPRÉSTIMOS (42 superclasse e subclasses)
    sql.append("-- 11. EMPRÉSTIMOS E SUBCLASSES (42 registros: Consignado, Financiamento, Pessoal)")
    sql.append("INSERT INTO emprestimo (id_emprestimo, id_cliente, tipo_modalidade, valor_total, data_contratacao, status) VALUES")
    emp_rows = []
    consignados = []
    financiamentos = []
    pessoais = []
    
    for e in range(1, 43):
        cli_id = ((e - 1) % 40) + 1
        modalidades = ["CONSIGNADO", "FINANCIAMENTO", "PESSOAL"]
        mod = modalidades[e % 3]
        val = round(random.uniform(5000.0, 150000.0), 2)
        st = "ATIVO" if e <= 35 else ("QUITADO" if e <= 39 else "INADIMPLENTE")
        dt = f"2024-{(e % 8) + 1:02d}-{(e % 25) + 1:02d}"
        emp_rows.append(f"({e}, {cli_id}, '{mod}', {val:.2f}, '{dt}', '{st}')")
        
        if mod == "CONSIGNADO":
            consignados.append(f"({e}, 'Governo do Distrito Federal', {random.choice([30.0, 35.0, 40.0]):.2f})")
        elif mod == "FINANCIAMENTO":
            tipo_bem = "Veiculo Automotor" if e % 2 == 0 else "Imovel Residencial"
            entrada = round(val * 0.2, 2)
            financiamentos.append(f"({e}, '{tipo_bem}', {entrada:.2f})")
        else:
            pessoais.append(f"({e}, 'Capital de Giro / Pessoal', {random.choice([1.89, 2.45, 3.10]):.2f})")
            
    sql.append(",\n".join(emp_rows) + ";\n")
    
    sql.append("INSERT INTO emprestimo_consignado (id_emprestimo, orgao_emissor, margem_consignavel) VALUES")
    sql.append(",\n".join(consignados) + ";\n")
    
    sql.append("INSERT INTO financiamento (id_emprestimo, tipo_bem, valor_entrada) VALUES")
    sql.append(",\n".join(financiamentos) + ";\n")
    
    sql.append("INSERT INTO emprestimo_pessoal (id_emprestimo, finalidade, taxa_juros_mensal) VALUES")
    sql.append(",\n".join(pessoais) + ";\n")

    # 12. PARCELAS DE EMPRÉSTIMO (85 registros)
    sql.append("-- 12. PARCELAS DE EMPRÉSTIMO (85 registros - Casos de contorno: pagas, pendentes e em atraso)")
    sql.append("INSERT INTO parcela_emprestimo (id_emprestimo, numero_parcela, valor, data_vencimento, data_pagamento, status) VALUES")
    parc_rows = []
    pid_count = 0
    for e in range(1, 43):
        # 2 parcelas para cada emprestimo
        for num_p in (1, 2):
            pid_count += 1
            if pid_count > 85: break
            vlr_p = round(random.uniform(400.0, 3200.0), 2)
            if num_p == 1 and e <= 30:
                dt_venc = "2024-05-10"
                dt_pag = "'2024-05-08'"
                st_p = "PAGO"
            elif e > 38:
                dt_venc = "2024-07-10"
                dt_pag = "NULL"
                st_p = "EM_ATRASO"
            else:
                dt_venc = "2024-12-10"
                dt_pag = "NULL"
                st_p = "PENDENTE"
            parc_rows.append(f"({e}, {num_p}, {vlr_p:.2f}, '{dt_venc}', {dt_pag}, '{st_p}')")
    sql.append(",\n".join(parc_rows) + ";\n")

    # 13. TRANSAÇÕES FINANCEIRAS (120 registros - META OFICIAL DE 100+)
    sql.append("-- 13. TRANSAÇÕES FINANCEIRAS (120 registros: PIX, TED, DOC, DEPOSITO, SAQUE, BOLETO, TRANSFERENCIA)")
    sql.append("INSERT INTO transacao (id_transacao, numero_conta_origem, numero_conta_destino, tipo, valor, data_hora) VALUES")
    tx_rows = []
    tipos_tx = ["PIX", "TED", "TRANSFERENCIA", "PAGAMENTO_BOLETO", "SAQUE", "DEPOSITO"]
    
    start_date = datetime(2024, 1, 1, 8, 0, 0)
    for t in range(1, 121):
        c_origem = f"100{((t - 1) % 45) + 1:02d}-X"
        tipo = tipos_tx[t % len(tipos_tx)]
        vlr = round(random.uniform(15.0, 8500.0), 2)
        
        if tipo in ("SAQUE", "PAGAMENTO_BOLETO"):
            c_destino = "NULL"
        else:
            dest_idx = ((t * 7) % 45) + 1
            if dest_idx == ((t - 1) % 45) + 1:
                dest_idx = (dest_idx % 45) + 1
            c_destino = f"'100{dest_idx:02d}-X'"
            
        cur_date = start_date + timedelta(days=t * 2, hours=(t * 3) % 12, minutes=(t * 17) % 60)
        dt_str = cur_date.strftime("%Y-%m-%d %H:%M:%S")
        
        tx_rows.append(f"({t}, '{c_origem}', {c_destino}, '{tipo}', {vlr:.2f}, '{dt_str}')")
    sql.append(",\n".join(tx_rows) + ";\n")

    with open("/home/guilherme-barcelos/Documentos/facu/banco/sql/02_Cargas.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(sql))
    print("02_Cargas.sql gerado com sucesso!")

if __name__ == "__main__":
    main()
