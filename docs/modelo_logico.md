# Modelo Lógico Relacional e Normalização — Versão Revisada (C2)

## 1. Esquema Lógico Relacional
Notação: Chaves Primárias sublinhadas (`<u>PK</u>`) e Chaves Estrangeiras indicadas por cardinal (`#FK`).

- **cliente** (<u>id_cliente</u>, cpf_cnpj, nome, telefone, email)
- **agencia** (<u>codigo_agencia</u>, nome, endereco)
- **setor** (<u>id_setor</u>, #codigo_agencia, nome)
- **funcionario** (<u>id_funcionario</u>, #codigo_agencia, #id_supervisor, nome, cargo, role_user)
- **funcionario_setor** (<u>#id_funcionario, #id_setor, data_inicio</u>, data_fim, papel_desempenhado)
- **conta_bancaria** (<u>numero_conta</u>, #codigo_agencia, modalidade, saldo, data_abertura, status)
- **cliente_conta** (<u>#id_cliente, #numero_conta</u>, tipo_titular, data_vinculo)
- **historico_status_conta** (<u>id_historico</u>, #numero_conta, status_anterior, status_novo, data_alteracao, motivo)
- **transacao** (<u>id_transacao</u>, #numero_conta_origem, #numero_conta_destino, tipo, valor, data_hora)
- **emprestimo** (<u>id_emprestimo</u>, #id_cliente, tipo_modalidade, valor_total, data_contratacao, status)
- **emprestimo_consignado** (<u>#id_emprestimo</u>, orgao_emissor, margem_consignavel)
- **financiamento** (<u>#id_emprestimo</u>, tipo_bem, valor_entrada)
- **emprestimo_pessoal** (<u>#id_emprestimo</u>, finalidade, taxa_juros_mensal)
- **parcela_emprestimo** (<u>#id_emprestimo, numero_parcela</u>, valor, data_vencimento, data_pagamento, status)
- **cartao** (<u>numero_cartao</u>, #numero_conta, tipo, status)
- **beneficiario** (<u>id_beneficiario</u>, #numero_conta_origem, nome, documento, banco, agencia, conta)

---

## 2. Justificativas de Mapeamento (Atendimento à Devolutiva C2)

### 2.1 Justificativa da Especialização em Três Tabelas (Tabela por Subclasse)
Optou-se pela abordagem **Tabela por Subclasse (Class Table Inheritance)** para a hierarquia de `emprestimo`:
- **Alternativa Descartada 1 (Tabela Única com Nulos)**: Geraria dezenas de colunas esparsas com valores `NULL` (ex: `orgao_emissor` seria nulo para financiamentos; `tipo_bem` nulo para consignados), violando restrições de integridade `NOT NULL` indispensáveis no domínio financeiro.
- **Alternativa Descartada 2 (Uma Tabela por Subclasse Concreta sem Superclasse)**: Duplicaria colunas comuns (`id_cliente`, `valor_total`, `status`, `data_contratacao`) e impediria a existência de uma chave estrangeira unificada para a entidade fraca `parcela_emprestimo`.
- **Vantagem da Abordagem Escolhida**: Mantém a superclasse `emprestimo` contendo os dados gerais e permitindo que `parcela_emprestimo` aponte para um identificador único de crédito, enquanto cada subclasse armazena estritamente seus atributos obrigatórios com integridade referencial `CASCADE` na PK/FK.

### 2.2 Justificativa de Chaves Naturais vs. Chaves Substitutas (Surrogate Keys)
- **Chaves Naturais Utilizadas**:
  - `conta_bancaria.numero_conta`: O número da conta (ex: `10001-X`) possui padrão bancário regulamentado, é amplamente conhecido pelos correntistas e serve como identificador estável, eliminando junções desnecessárias em extratos.
  - `cartao.numero_cartao`: O identificador físico de 16 dígitos emitido pela bandeira já é intrinsecamente único e global no ecossistema de meios de pagamento.
- **Chaves Substitutas Adotadas**:
  - `cliente.id_cliente`: Embora o `cpf_cnpj` seja único (e protegido por constraint `UNIQUE`), é um dado textual sujeito a formatação e eventuais atualizações de documentação. A chave surrogate numérica inteira otimiza drasticamente o custo de índices nas tabelas associativas e de crédito.
  - `transacao.id_transacao`, `emprestimo.id_emprestimo`, `agencia.codigo_agencia`: Inteiros sequenciais (`AUTO_INCREMENT`) proporcionam indexação compacta em árvore B+ e previnem a sobrecarga de chaves compostas gigantescas em tabelas de alto volume.

### 2.3 Justificativa da PK Composta de `funcionario_setor`
A chave primária é composta por `(id_funcionario, id_setor, data_inicio)`:
- O relacionamento entre funcionário e setor é N:N temporal.
- Um mesmo funcionário pode ter trabalhado no setor de Atendimento em 2023, sido transferido para Crédito em 2024 e retornado ao Atendimento em 2025.
- Portanto, apenas `(id_funcionario, id_setor)` não garantiria a unicidade do histórico caso haja retorno ao mesmo setor. A inclusão de `data_inicio` assegura unicidade temporal perfeita.

---

## 3. Demonstração Formal da Normalização até a 3ª Forma Normal (3FN)

### 3.1 Lista Exaustiva de Dependências Funcionais (DFs)

1. **Relação `cliente`**:
   - `id_cliente -> {cpf_cnpj, nome, telefone, email}` (Chave Primária)
   - `cpf_cnpj -> {id_cliente, nome, telefone, email}` (Chave Alternativa)
   - `email -> {id_cliente, cpf_cnpj, nome, telefone}` (Chave Alternativa)
2. **Relação `conta_bancaria`**:
   - `numero_conta -> {codigo_agencia, modalidade, saldo, data_abertura, status}`
3. **Relação `agencia`**:
   - `codigo_agencia -> {nome, endereco}`
4. **Relação `setor`**:
   - `id_setor -> {codigo_agencia, nome}`
5. **Relação `funcionario`**:
   - `id_funcionario -> {codigo_agencia, id_supervisor, nome, cargo, role_user}`
6. **Relação `funcionario_setor`**:
   - `{id_funcionario, id_setor, data_inicio} -> {data_fim, papel_desempenhado}`
7. **Relação `cliente_conta`**:
   - `{id_cliente, numero_conta} -> {tipo_titular, data_vinculo}`
8. **Relação `transacao`**:
   - `id_transacao -> {numero_conta_origem, numero_conta_destino, tipo, valor, data_hora}`
9. **Relação `emprestimo`**:
   - `id_emprestimo -> {id_cliente, tipo_modalidade, valor_total, data_contratacao, status}`
10. **Relação `parcela_emprestimo`**:
    - `{id_emprestimo, numero_parcela} -> {valor, data_vencimento, data_pagamento, status}`
11. **Relação `cartao`**:
    - `numero_cartao -> {numero_conta, tipo, status}`
12. **Relação `beneficiario`**:
    - `id_beneficiario -> {numero_conta_origem, nome, documento, banco, agencia, conta}`

### 3.2 Prova das Formas Normais
- **1ª Forma Normal (1FN)**:
  - Todos os domínios de atributos contêm exclusivamente valores atômicos e indivisíveis.
  - Não existem tabelas aninhadas, vetores ou atributos multivalorados (ex: telefones múltiplos foram normalizados ou restritos a contato preferencial).
- **2ª Forma Normal (2FN)**:
  - O esquema está na 1FN.
  - Em todas as tabelas com chaves primárias compostas (`cliente_conta`, `funcionario_setor`, `parcela_emprestimo`), **nenhum atributo não-chave depende de parte da chave primária (não há dependências parciais)**:
    - Em `parcela_emprestimo`: `valor`, `data_vencimento` e `status` dependem do conjunto `{id_emprestimo, numero_parcela}` simultaneamente.
    - Em `cliente_conta`: `tipo_titular` e `data_vinculo` dependem do par `{id_cliente, numero_conta}`.
- **3ª Forma Normal (3FN)**:
  - O esquema está na 2FN.
  - **Não existem dependências transitivas**: para toda dependência funcional não-trivial `X -> Y`, ou `X` é uma superchave ou `Y` é parte de uma chave candidata.
  - Nenhum atributo não-chave determina outro atributo não-chave (ex: na tabela `conta_bancaria`, o nome e endereço da agência não estão na conta; estão isolados em `agencia`, evitando anomalias de atualização).
- **Conclusão**: O esquema lógico atende plenamente e comprovadamente à **3ª Forma Normal (3FN)** e à **Forma Normal de Boyce-Codd (FNBC)**.
