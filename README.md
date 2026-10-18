# 🏦 Sistema de Gestão de Contas e Operações Bancárias

> **Instituição:** Universidade Católica de Brasília (UCB)  
> **Curso:** Bacharelado em Engenharia de Software  
> **Disciplina:** Laboratório de Banco de Dados — GPE17M40083  
> **Professor:** Samuel Novais Moura Júnior  
> **Semestre:** 2026/2  
> **SGBD Utilizado:** MySQL 8.0 (Containerizado via Docker)  
> **Interface da Aplicação:** Python 3 + Streamlit  

---

## 👥 Integrantes da Equipe
- **Gabriel Almeida Silva Netto**
- **Gabriel Reis**
- **Gabriel Lima Leite**
- **Celiandro Borges Mazarro**
- **Caio Gasparin**
- **Eduardo**

---

## 📌 Visão Geral do Projeto
Este repositório contém a entrega completa e integrada da disciplina, contemplando:
1. **Etapa 1 Revisada (Devolutivas C1 a C5)**:
   - **MER Conceitual** unificado em notação Crow's Foot com cardinalidades mín/máx explícitas, herança (`d/t`) e entidade fraca `historico_status_conta`.
   - **Modelo Lógico** com chaves PK/FK sublinhadas/marcadas, justificativas de mapeamento e prova formal da 3FN baseada em Dependências Funcionais.
   - **DDL (`sql/01_ddl.sql`)**: 100% autoral, sem `CASCADE` destrutivo no domínio financeiro (`ON DELETE RESTRICT`), constraints `CHECK` e nomenclatura padronizada (`pk_`, `fk_`, `ck_`, `uq_`, `idx_`).
   - **Cargas (`sql/02_Cargas.sql`)**: 40+ linhas nas tabelas principais, 100+ transações e casos de contorno.
   - **Consultas (`sql/03_consultas.sql`)**: 15 consultas com perguntas de negócio (5 básicas, 5 junções/agregações, 5 avançadas/correlacionadas).
2. **Etapa 2 (N2 - Operação, Interface e Desempenho)**:
   - **B1**: Aplicação funcional web (Streamlit) com 4 CRUDs, 2 consultas parametrizadas, relatório consolidado via VIEW e operação transacional atômica com simulação de falha (Rollback).
   - **B2**: Camada de dados escrita pela equipe (`app/db.py`) com 100% Prepared Statements (zero concatenação), credenciais fora do Git e teste de SQL Injection.
   - **B3**: Transações ACID com bloqueio de linha (`SELECT ... FOR UPDATE`), experimento de concorrência com 2 sessões e modo didático de Deadlock (erro 1213).
   - **B4**: Otimização com `EXPLAIN ANALYZE` sobre massa comprovada de **10.123 transações**, com 92% de ganho de tempo após índices compostos.
   - **B5**: Segurança com 3 perfis nativos MySQL (`user_admin`, `user_atendente`, `user_auditor`), VIEW de mascaramento LGPD e senhas com hash e sal (`bcrypt`).
   - **B6**: Trilha de auditoria em tabela dedicada (`tb_auditoria_sistema`) com 2 gatilhos capturando estados `OLD` e `NEW` em formato JSON.
   - **B7**: Projeto físico com tipos de dados revisados, projeção de crescimento para 2 anos (~15,4 GB), plano de backup 3-2-1 e proposta de particionamento anual.
   - **B8**: Relatório final consolidado em PDF (`docs/relatorio_etapa2.pdf`), declaração de IA e roteiro da demonstração ao vivo de 15 minutos.

---

## 📂 Estrutura do Repositório

```text
banco/
├── app/
│   ├── app.py                      # Aplicação Web Streamlit (Interface dos entregáveis B1 a B6)
│   ├── db.py                       # Camada de dados (Prepared Statements + tratamento de erros MySQL)
│   ├── auth.py                     # Algoritmo de hash com sal aleatório (bcrypt, 12 rounds)
│   ├── theme.py                    # Design System semântico (escala 4px/8px, sem cores hardcoded)
│   ├── ui_components.py            # Componentes reutilizáveis (KPIs, Callouts, Badges, Pickers)
│   └── validators.py               # Validações estritas de entrada (CPF, busca numérica, e-mail)
├── docs/
│   ├── modelo_er.md                # MER Conceitual revisado (Crow's Foot e cardinalidades)
│   ├── modelo_logico.md            # Esquema lógico (PK/FK), justificativas e prova formal 3FN
│   ├── dicionario_dados.md         # Dicionário de dados conforme Anexo A do edital
│   ├── plano_etapa2.md             # Plano de implementação da Etapa 2
│   ├── relatorio_etapa2.md         # Relatório técnico final consolidado em Markdown
│   └── relatorio_etapa2.pdf        # Relatório técnico oficial compilado e paginado para entrega
├── scripts/
│   ├── smoke_test_etapa2.py        # Suíte de smoke test automatizado (10 checagens de integridade)
│   ├── experimento_concorrencia.py # Experimento de concorrência (Row-level lock e --deadlock)
│   ├── gerador_carga_alta.py       # Gerador da carga massiva de 10.000+ transações
│   ├── gerar_cargas_completas.py   # Gerador da carga base com casos de contorno
│   └── gerar_pdf_relatorio.py      # Compilador do relatório técnico para PDF (ReportLab)
├── sql/
│   ├── 01_ddl.sql                  # Script físico DDL revisado (100% autoral, sem CASCADE financeiro)
│   ├── 02_Cargas.sql               # Script de carga inicial com casos de contorno
│   ├── 03_consultas.sql            # 15 consultas SQL obrigatórias com perguntas de negócio
│   ├── 04_etapa2_seguranca_auditoria.sql # Auditoria, 2 triggers JSON, 2 views e 3 perfis MySQL
│   └── 05_etapa2_otimizacao_indices.sql  # 3 índices compostos para o benchmark de desempenho
├── tests/
│   ├── test_validators.py          # 19 testes unitários dos validadores de regex e formato
│   └── test_etapa2.py              # Testes unitários das melhorias e componentes da Etapa 2
├── docker-compose.yml              # Orquestração do MySQL 8.0 oficial em container
├── requirements.txt                # Dependências Python do projeto
├── .env.example                    # Modelo seguro de variáveis de ambiente
├── .gitignore                      # Proteção contra vazamento de credenciais e venv
└── README.md                       # Documentação completa de uso e operação
```

---

## 🚀 Como Executar em Máquina Limpa

### 1. Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.10+](https://www.python.org/)

### 2. Inicialização do Banco de Dados (MySQL 8.0)
```bash
# 1. Clone o repositório oficial
git clone https://github.com/guilhermebarcelos06/Trabalho-de-banco-de-dados.git
cd Trabalho-de-banco-de-dados

# 2. Configure o arquivo de variáveis de ambiente
cp .env.example .env

# 3. Suba o container do MySQL 8.0
docker compose up -d

# 4. Aguarde cerca de 10 segundos para inicialização do MySQL e execute os scripts na ordem:
docker exec -i mysql-banco mysql -uroot -pbanco_secret sistema_bancario < sql/01_ddl.sql
docker exec -i mysql-banco mysql -uroot -pbanco_secret sistema_bancario < sql/02_Cargas.sql
docker exec -i mysql-banco mysql -uroot -pbanco_secret sistema_bancario < sql/04_etapa2_seguranca_auditoria.sql
docker exec -i mysql-banco mysql -uroot -pbanco_secret sistema_bancario < sql/05_etapa2_otimizacao_indices.sql
```

### 3. Configuração do Ambiente Python e Execução da Aplicação
```bash
# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate   # No Windows: .venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Inicie a aplicação web Streamlit
streamlit run app/app.py
```
Acesse no seu navegador: **`http://localhost:8501`**

---

## 🧭 Guia de Uso da Interface (Passo a Passo dos 7 Menus)

A aplicação está dividida em 7 módulos no menu lateral, cada um correspondendo aos requisitos do edital:

### 1. `1. CRUD de 4 Entidades (B1)`
- **Objetivo**: Gerenciar de ponta a ponta as entidades **Cliente**, **Conta Bancária**, **Cartão** e **Beneficiário**.
- **Como Usar**:
  - Selecione a entidade desejada no selectbox do topo.
  - **Consultar**: Utilize o campo de filtro com busca dinâmica por nome ou documento.
  - **Novo Cadastro**: Preencha o formulário. O sistema bloqueia letras em campos numéricos (CPF, número da conta) e valida formatos.
  - **Atualizar / Remover**: Digite o ID ou CPF numérico (o sistema bloqueia letras e prioriza o ID exato no ranking instantâneo). Edite os campos e clique em Salvar ou Excluir. Mensagens amigáveis são exibidas se houver violação de chave estrangeira ou duplicidade.

### 2. `2. Consultas Parametrizadas (B1)`
- **Objetivo**: Executar consultas analíticas com junções e agregações alimentadas por filtros dinâmicos.
- **Telas Disponíveis**:
  - **Extrato Parametrizado por Período**: Selecione a conta e o intervalo de datas. O sistema exibe a tabela de transações, o total de entradas/saídas e o volume transacionado via Prepared Statements.
  - **Painel da Carteira de Crédito**: Filtre contratos de empréstimo por status (`ATIVO`, `QUITADO`, `EM_ATRASO`) com cálculo consolidado do valor total tomado e parcelas pendentes.

### 3. `3. Relatório Consolidado - VIEW (B1)`
- **Objetivo**: Exibir relatório executivo alimentado diretamente pela visão `vw_relatorio_consolidado_agencias`.
- **Destaques**:
  - Três cartões de KPI no topo: Total de Contas Ativas, Custódia Global e Volume Movimentado.
  - Tabela consolidada por agência.
  - **Gráfico horizontal em Altair**: Exibe o volume transacionado por agência sem textos verticais truncados.

### 4. `4. Transação Multitabela & Rollback (B1/B3)`
- **Objetivo**: Demonstrar atomicidade financeira e resiliência a falhas operacionais.
- **Como Testar**:
  1. **Transferência com Sucesso (COMMIT)**: Selecione conta de origem e destino, informe um valor (ex: R$ 300,00) e clique no botão verde. Os saldos são atualizados atomicamente, uma linha é gravada em `transacao` e dois registros são inseridos em `tb_auditoria_sistema`.
  2. **Validação de Saldo Insuficiente**: Tente transferir um valor superior ao saldo da conta de origem. O sistema intercepta com um callout amigável de erro antes de onerar o banco.
  3. **Falha Forçada (ROLLBACK)**: Clique no botão vermelho. O sistema debita a origem e força uma exceção no meio do processo. O bloco `try/except` executa `conn.rollback()` e comprova na tela que os saldos de ambas as contas permaneceram intactos.

### 5. `5. Segurança & SQL Injection (B2/B5)`
- **Abas Disponíveis**:
  - **🧪 Teste de SQL Injection**: Digite o payload `' OR '1'='1`. O sistema demonstra que a consulta trata a entrada como literal puro via Prepared Statement, resultando em zero vazamento de dados.
  - **👥 Perfis MySQL & Privilégios**: Teste comandos de escrita com credenciais reais de `user_admin`, `user_atendente` e `user_auditor`. Comprove que o atendente e o auditor têm comandos de exclusão/alteração rejeitados pelo SGBD (`Access denied`).
  - **🔒 Proteção LGPD**: Visualização da VIEW `vw_cliente_atendimento`, na qual os dígitos centrais do CPF aparecem mascarados (`***.456.789-**`).
  - **🔑 Senhas com Hash e Sal (bcrypt)**: Digite qualquer senha (ex: `SenhaForte#2026`) e clique em "Gerar Hash com Sal". O sistema gera o hash de 60 caracteres com sal aleatório (`$2b$12$...`) e permite testar a verificação de autenticação com senhas corretas e incorretas.

### 6. `6. Otimização & EXPLAIN (B4)`
- **Objetivo**: Avaliar o plano de execução (`EXPLAIN`) das 3 consultas críticas do sistema sobre massa de dados real.
- **Destaques**:
  - Três cartões de KPI no topo comprovando a volumetria real do banco (**10.123 transações**, **84 parcelas** e **40 históricos**).
  - Escolha entre as 3 consultas e clique em "Executar EXPLAIN" para inspecionar o plano de execução do MySQL com Index Range Scan.

### 7. `7. Gatilhos de Auditoria (B6)`
- **Objetivo**: Inspecionar em tempo real os eventos capturados pelos triggers `AFTER UPDATE`.
- **Como Testar**: Altere o saldo ou status de qualquer conta no Menu 1 ou execute uma transferência no Menu 4. Em seguida, acerte este menu para visualizar os registros gravados com autor, data/hora e o payload JSON contendo o estado anterior (`OLD`) e posterior (`NEW`).

---

## 🧪 Testes Automatizados e Concorrência

### 1. Suíte de Testes Unitários (23 Testes)
```bash
.venv/bin/python3 -m unittest discover tests -v
```
Testa validadores de entrada, regex estrita para busca numérica, bloqueio de injeção, geração de hash bcrypt e componentes da aplicação.

### 2. Smoke Test de Ponta a Ponta (10/10 Checagens)
```bash
.venv/bin/python3 scripts/smoke_test_etapa2.py
```
Executa dez verificações reais no MySQL 8.0:
1. Conexão com `sistema_bancario`.
2. Massa de dados comprovada (> 10.000 transações).
3. Prepared Statements e blindagem contra SQLi.
4. SELECTs básicos dos 4 CRUDs.
5. Execução das 2 consultas parametrizadas.
6. Consulta à VIEW de relatório consolidado.
7. Transação multitabela com teste real de COMMIT e ROLLBACK forçado.
8. Três logins reais nos perfis MySQL (`user_admin`, `user_atendente`, `user_auditor`).
9. Disparo de Trigger e validação do payload JSON em `tb_auditoria_sistema`.
10. Geração e validação do algoritmo `bcrypt` (60 caracteres com sal aleatório).

### 3. Experimento de Concorrência com 2 Sessões (B3)
```bash
# Modo Padrão: Bloqueio em Nível de Linha (Row-Level Lock) sob REPEATABLE READ
.venv/bin/python3 scripts/experimento_concorrencia.py

# Modo Deadlock Didático: Demonstra ciclo de espera e rollback automático da vítima
.venv/bin/python3 scripts/experimento_concorrencia.py --deadlock
```

---

## ⏱️ Roteiro da Demonstração ao Vivo (Tópico 6.2 — 15 Minutos)

| Momento | Duração | O que Demonstrar ao Vivo |
|---|---|---|
| **1. Contexto** | 2 min | Apresentar o domínio bancário, as 11 entidades, as 2 tabelas associativas e as correções da Etapa 1 (MER unificado e entidade fraca). |
| **2. CRUD e Consultas** | 4 min | Cadastrar um novo cliente, emitir um cartão, executar a consulta parametrizada com filtro de datas e abrir o relatório consolidado da VIEW. |
| **3. Transação Multitabela** | 3 min | Executar uma transferência com sucesso (COMMIT); em seguida, acionar o botão de falha proposital no meio da transação e mostrar que os saldos permaneceram intactos (ROLLBACK). |
| **4. Restrições em Ação** | 2 min | Tentar cadastrar um cliente com CPF duplicado ou transferir valor acima do saldo na interface, demonstrando a mensagem amigável tratada pelo sistema. |
| **5. Desempenho e Acesso** | 3 min | Exibir o plano `EXPLAIN` antes e depois do índice composto com o tempo reduzido para 1.5ms; testar o login do perfil `user_atendente` tentando excluir um registro e recebendo erro de permissão. |
| **6. Arguição** | 1 min | Respostas da equipe às perguntas técnicas do professor. |

---

## 📋 Checklist Oficial da Etapa 2 (Anexo C)
- [x] A aplicação sobe em máquina limpa seguindo as instruções do README.
- [x] Os quatro CRUDs, as duas consultas parametrizadas e o relatório funcionam.
- [x] Nenhuma consulta é montada por concatenação de string.
- [x] As credenciais do banco não estão versionadas.
- [x] A operação transacional foi testada nos dois desfechos: sucesso e falha.
- [x] O experimento de concorrência está documentado com o que foi observado.
- [x] Os três estudos de EXPLAIN trazem plano antes, índice, plano depois e tempo.
- [x] Os três perfis de acesso foram criados e testados com login real.
- [x] As senhas da aplicação estão armazenadas com hash e sal.
- [x] Os dois gatilhos de auditoria registram autor, data e valores.
- [x] O plano de backup está descrito com frequência e estratégia de retenção.
- [x] As correções apontadas na devolutiva da Etapa 1 foram incorporadas.
- [x] O ambiente de demonstração está preparado: banco povoado e duas sessões abertas.
- [x] A seção de declaração de uso de IA está preenchida.

---

## 📄 Licença e Uso Acadêmico
Projeto desenvolvido para fins estritamente acadêmicos no curso de Engenharia de Software da Universidade Católica de Brasília (UCB).
