# Guia de Engenharia: Como Usar o Pacote de Design Skills

Este guia documenta como o pacote profissional de **6 Design Skills** foi aplicado no **Sistema de Gestão de Contas e Operações Bancárias** e ensina como você pode invocar e aproveitar cada uma delas em qualquer projeto futuro.

---

## 🎨 1. Como as Skills Transformaram a Aplicação do Trabalho

A interface padrão do Streamlit foi elevada para o padrão estético e ergonômico de referências mundiais de produto (**Linear, Vercel, Stripe e Mercury**), orquestrando 5 skills em harmonia:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ARQUITETURA DE DESIGN DA APLICAÇÃO                   │
├──────────────────────────┬─────────────────────────────────────────────┤
│ design-system-architect  │ Tokens semânticos (:root CSS), escala 4px/  │
│                          │ 8px, cores com opacidade e tipografia fluida│
├──────────────────────────┼─────────────────────────────────────────────┤
│ ui-polish                │ Eliminação de AI slop, bordas sutis 1px,    │
│                          │ microinterações (180ms ease-out) e 8 estados│
├──────────────────────────┼─────────────────────────────────────────────┤
│ component-builder        │ Módulo app/ui_components.py desacoplado     │
│                          │ com render_header, render_kpi, empty_states │
├──────────────────────────┼─────────────────────────────────────────────┤
│ a11y-auditor             │ Contraste WCAG AA (4.5:1), focus-visible    │
│                          │ nítido e badges com reforço semiótico duplo │
├──────────────────────────┼─────────────────────────────────────────────┤
│ ascii-wireframer         │ Prototipação em blocos Unicode box-drawing  │
│                          │ antes da implementação de layouts           │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### O que mudou na prática:
1. **Zero Cores Hardcoded:** Todas as cores agora derivam de variáveis semânticas (`--surface-card`, `--foreground-primary`, `--primary-brand`, `--border-subtle`).
2. **Matriz de Estados Completa:** Se uma busca de cliente ou extrato não retorna dados, a aplicação não fica muda nem quebra — ela renderiza um **Empty State** estilizado com ícone vetorial e dica de ação.
3. **Cards de Métricas:** Estatísticas financeiras (custódia global, volume de transações, ticket médio) utilizam o componente `render_kpi()`, com hierarquia clara e badges visuais.
4. **Respiro Visual (Whitespace Intencional):** O espaçamento do topo foi calibrado, evitando que a página pareça comprimida ou afogada.

---

## 🚀 2. Como Usar e Explorar a Nova Interface

Com o servidor rodando em `http://localhost:8501`, explore os novos padrões de design nas abas:

1. **Aba 1 (CRUD com Empty States e Forms Polidos):**
   - Acesse a aba *Consultar Clientes* e digite um termo inexistente no filtro: observe o componente de *Empty State* com ícone e sugestão de ação.
   - Observe os inputs com foco destacado (*focus-visible ring*) em azul cobalto acessível.
2. **Aba 2 (Consultas Parametrizadas & KPI Cards):**
   - Execute a busca de extrato por período: observe os três cartões de KPI (*Transações Encontradas*, *Volume Transacionado* e *Ticket Médio*) com microinteração de hover (elevação de 2px e sombra difusa sutil).
3. **Aba 3 (Relatório Consolidado VIEW):**
   - Gráfico de barras integrado com a paleta do design system e contadores de agências com badges semânticos.
4. **Aba 4 (Transação ACID & Rollback):**
   - Painéis comparativos de saldo de Origem e Destino com badges em tempo real e banner explicativo sobre o mecanismo de segurança financeira.

---

## 🧠 3. Como Invocar Cada Skill no Seu Dia a Dia

Todas as 6 skills estão instaladas tanto no seu workspace (`.agent/skills/`) quanto no escopo global da sua máquina (`~/.gemini/config/skills/`). Você pode acioná-las das seguintes maneiras:

### Opção A: Invocação Automática por Contexto
O arquivo [`AGENTS.md`](file:///home/guilherme-barcelos/Documentos/facu/banco/AGENTS.md) na raiz do projeto instrui qualquer agente de IA a acionar a skill correta automaticamente sempre que você pedir algo relacionado a design, CSS, acessibilidade ou terminal.

### Opção B: Invocação Explícita por Comando / Prompt

#### 1. `design-system-architect`
- **Quando usar:** Ao criar ou mudar temas, cores, escalas de espaçamento ou variáveis CSS.
- **Como pedir no chat:**
  > *"Atue com a skill design-system-architect para criar a paleta de cores e variáveis CSS do meu novo projeto."*
  > *"Use a skill design-system-architect para auditar meus componentes e remover todos os valores hexadecimais hardcoded."*

#### 2. `ui-polish`
- **Quando usar:** Quando uma tela parecer crua, genérica ou com "cara de IA", ou faltar tratamento de estados de erro/loading.
- **Como pedir no chat:**
  > *"Use a skill ui-polish para refinar o visual dessa página. Remova o aspecto genérico de IA, adicione bordas sutis de 1px com transparência e implemente estados de loading e empty state."*

#### 3. `component-builder`
- **Quando usar:** Ao desenvolver novos componentes reutilizáveis, modais, formulários ou tabelas com variantes tipadas.
- **Como pedir no chat:**
  > *"Com a skill component-builder, crie um componente de Card Composto reutilizável com variantes primária, secundária e de perigo usando CVA."*

#### 4. `a11y-auditor`
- **Quando usar:** Para auditar formulários, contraste de cores e suporte a navegação por teclado (WCAG 2.2).
- **Como pedir no chat:**
  > *"Execute a skill a11y-auditor no meu formulário de login para checar contraste mínimo de 4.5:1, etiquetas em todos os inputs e navegação 100% via Tab e Enter."*

#### 5. `ascii-wireframer`
- **Quando usar:** Antes de escrever código frontend, para alinhar a disposição de elementos na tela no próprio terminal.
- **Como pedir no chat:**
  > *"Com a skill ascii-wireframer, esboce um wireframe no terminal usando caracteres box-drawing para a tela de extrato bancário em formato Desktop (80 cols) e Mobile (36 cols)."*

#### 6. `tui-designer`
- **Quando usar:** Ao criar ferramentas CLI interativas ou painéis no terminal (Python Textual, Rich, Go Bubble Tea).
- **Como pedir no chat:**
  > *"Use a skill tui-designer para projetar uma CLI interativa com painéis divididos, barra de status no rodapé com [q] Sair e suporte a NO_COLOR."*
