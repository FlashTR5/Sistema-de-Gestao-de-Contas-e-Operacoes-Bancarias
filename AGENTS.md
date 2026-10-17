# Diretrizes Gerais de Engenharia de Agentes e Design de Interfaces

Este documento define as regras de governança, padrões arquiteturais e a orquestração automática do pacote de **Design Skills** para qualquer agente de IA que atue neste workspace.

---

## 🎯 Orquestração Automática de Design Skills

Sempre que a sua tarefa envolver concepção, estilização, refatoração ou auditoria de interfaces visuais (Web, Mobile, Desktop ou Terminal), você **DEVE consultar e aplicar** as diretrizes das seguintes skills especializadas localizadas em `.agent/skills/` (e instaladas globalmente em `~/.gemini/config/skills/`):

| Skill | Gatilhos de Contexto (Triggers Automáticos) | Objetivo Primário |
| :--- | :--- | :--- |
| **`design-system-architect`** | Criação ou alteração de cores, tipografia, espaçamentos, temas claro/escuro, variáveis CSS ou classes Tailwind. | Garantir arquitetura de tokens em 3 camadas, escala 4px/8px e **zero valores hardcoded** (proibição de `#hex` e pixels arbitrários em componentes). |
| **`ui-polish`** | Criação ou polimento de telas, botões, cards, transições, layouts genéricos. | **Eliminar "AI slop"** (gradientes roxo/neon, sombras borradas excessivas, card-ception) e elevar o acabamento para o nível de produtos como Linear, Vercel, Stripe e Raycast. Implementar a **matriz de 8 estados de UI** (skeleton, empty, error, etc.). |
| **`component-builder`** | Criação de novos componentes reutilizáveis, modais, formulários, dropdowns, tabelas interativas. | Separar lógica de comportamento (headless) da apresentação visual. Utilizar variantes tipadas (CVA / Tailwind Variants), padrão de componentes compostos e acessibilidade nativa. |
| **`a11y-auditor`** | Adição de interações com usuário, formulários, botões, modais, paletas de cores, auditoria de HTML. | Conformidade estrita com **WCAG 2.2 AA/AAA**, navegação completa por teclado, anéis de foco (`:focus-visible`) nítidos, rótulos acessíveis, suporte a `prefers-reduced-motion` e contraste mínimo de 4.5:1. |
| **`ascii-wireframer`** | Fase inicial de planejamento de telas, discussão de layout, alinhamento de requisitos com o usuário antes de codificar. | Prototipar wireframes monospaçados limpos usando caracteres Unicode box-drawing (`┌─┐│└┘├┤`), apresentando visões comparativas Desktop (80 colunas) e Mobile (36 colunas) com fluxo de navegação. |
| **`tui-designer`** | Criação ou evolução de ferramentas de linha de comando (CLI) e interfaces de texto de terminal (TUI). | Desenvolver interfaces de terminal ergonômicas com painéis divididos, barra de status permanente com atalhos mnemônicos (`[q] Sair`, `[Tab] Navegar`), suporte a `NO_COLOR` e saídas encadeáveis (pipes/JSON). |

---

## 🛡️ Regras de Ouro Inegociáveis no Desenvolvimento de Interfaces

1. **Zero Hardcoded Values:**
   - Proibido inserir cores hexadecimais soltas (`#1e40af`) ou valores arbitrários de pixel (`padding: 13px`) no corpo de componentes. Sempre referencie variáveis semânticas (`var(--primary)`, `var(--space-4)`).
2. **Combate ao AI Slop:**
   - Proibidos gradientes neon (rosa/roxo/azul) decorativos em botões e fundos.
   - Proibidas sombras pretas difusas gigantescas que cobrem o conteúdo.
   - Proibido aninhamento excessivo de caixas e cartões.
3. **Completude de Estados:**
   - Nenhuma tela ou componente pode ser entregue exibindo apenas o estado ideal (*Happy Path*). Devem ser previstos estados de *Carregamento (Skeleton)*, *Vazio (Empty State)* e *Erro com Recuperação*.
4. **Preservação de Foco e Acessibilidade:**
   - Proibido remover o foco padrão com `outline: none` sem fornecer indicador visual substituto de alto contraste.
   - Todo campo interativo deve ser acessível por teclado (`Tab`, `Enter`, `Space`, `Esc`).
