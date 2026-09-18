# 🏦 Sistema de Gestão de Contas e Operações Bancárias

> **SGBD Utilizado:** MySQL 8.0  
> **Linguagem / Padrão:** SQL (DDL ANSI Standard)  

---

## 📌 Visão Geral do Projeto

Este projeto consiste na modelagem e implementação do banco de dados relacional para um **Sistema de Gestão de Contas e Operações Bancárias**. 

A solução foi projetada para atender aos requisitos de um ambiente bancário dinâmico, garantindo rastreabilidade de dados, integridade referencial rigorosa e suporte a operações financeiras complexas, tais como:

- **Gerenciamento de Clientes e Contas:** Controle de titulares, modalidades de conta (Corrente e Poupança) e histórico de alterações de status.
- **Estrutura Organizacional:** Alocação de funcionários em setores de agências, hierarquia de supervisão e papéis desempenhados[cite: 2].
- **Operações Financeiras e Cartões:** Emissão de cartões de débito/crédito, cadastro de beneficiários e registro auditável de transações entre contas[cite: 2].
- **Módulo de Empréstimos e Financiamentos:** Mapeamento especializado de modalidades de crédito e gestão de parcelamentos (entidades fracas)[cite: 2].

---

## 🎯 Tema e Escopo

* **Tema:** Sistema Bancário e Operações de Crédito.
* **Escopo da Etapa 1:**
  - Modelagem Conceitual e Lógica do Banco de Dados.
  - Mapeamento Relacional e Normalização (até a 3ª Forma Normal - 3FN).
  - Implementação do Script DDL (`01_ddl.sql`) com Constraints, Checks e Ações de Integridade Referencial (`ON DELETE` / `ON UPDATE`).
  - Elaboração dos Artefatos de Documentação (Dicionário de Dados, Justificativas de Mapeamento e Prova de Normalização).

---

## 👥 Integrantes do Grupo

| **Gabriel Almeida Silva Netto**  
| **Gabriel Reis** 
| **Gabriel Lima Leite** 
| **Celiandro Borges Mazarro** 
| **Eduardo** 

---

## 🛠️ Destaques da Modelagem Relacional

O esquema de banco de dados implementa os seguintes conceitos avançados de modelagem relacional[cite: 2]:

1. **Generalização / Especialização:** Mapeamento da superclasse `emprestimo` com as subclasses `emprestimo_consignado` e `financiamento` via abordagem *Tabela por Classe*[cite: 2].
2. **Entidade Temporal (Histórico Datado):** Tabela `historico_status_conta` para auditoria e rastreamento temporal das mudanças de estado das contas bancárias[cite: 2].
3. **Relacionamentos N:N com Atributos Próprios:**
   - `cliente_conta`: Armazena o tipo de titularidade e a data de vínculo[cite: 2].
   - `funcionario_setor`: Registra a vigência (datas de início/fim) e o papel desempenhado pelo colaborador[cite: 2].
4. **Autorrelacionamento (1:N):** Tabela `funcionario` com suporte à hierarquia de supervisores (`id_supervisor`)[cite: 2].
5. **Entidade Fraca:** Tabela `parcela_emprestimo` identificada compostamente por `(id_emprestimo, numero_parcela)`[cite: 2].

