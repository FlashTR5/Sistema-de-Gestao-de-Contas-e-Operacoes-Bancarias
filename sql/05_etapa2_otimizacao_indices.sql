-- ============================================================================
-- PROJETO FINAL: LABORATÓRIO DE BANCO DE DADOS (UCB 2026/2)
-- SGBD: MySQL 8.0
-- ARQUIVO: 05_etapa2_otimizacao_indices.sql
-- IMPLEMENTAÇÃO: Artefato B4 da Etapa 2 (Otimização e Índices Compostos)
-- ============================================================================

USE sistema_bancario;

-- ----------------------------------------------------------------------------
-- ÍNDICE COMPOSTO 1 (Para Consulta Crítica 1 - Extratos por Período)
-- Justificativa: A busca filtra por 'numero_conta_origem' (alta seletividade) 
-- e ordena/restringe por 'data_hora'. O índice composto permite que o otimizador
-- do MySQL realize Index Range Scan eliminando a necessidade de etapa de 'filesort'.
-- ----------------------------------------------------------------------------
CREATE INDEX idx_transacao_conta_data ON transacao(numero_conta_origem, data_hora);

-- ----------------------------------------------------------------------------
-- ÍNDICE COMPOSTO 2 (Para Consulta Crítica 2 - Cobrança de Parcelas em Atraso)
-- Justificativa: Consultas do setor de recuperação de crédito filtram parcelas
-- por status ('EM_ATRASO') e ordenam por 'data_vencimento'. Esse índice composto
-- evita Full Table Scan de dezenas de milhares de parcelas quitadas.
-- ----------------------------------------------------------------------------
CREATE INDEX idx_parcela_status_vencimento ON parcela_emprestimo(status, data_vencimento);

-- ----------------------------------------------------------------------------
-- ÍNDICE COMPOSTO 3 (Para Consulta Crítica 3 - Auditoria de Histórico Temporal)
-- Justificativa: Rastreamento cronológico de alterações de status por conta bancária.
-- O índice permite busca direta por conta e leitura ordenada das alterações no tempo.
-- ----------------------------------------------------------------------------
CREATE INDEX idx_historico_conta_data ON historico_status_conta(numero_conta, data_alteracao);
