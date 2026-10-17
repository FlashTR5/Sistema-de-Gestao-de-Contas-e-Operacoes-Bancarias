"""
Módulo de Tema e Tokens Semânticos de Design
Governança via design-system-architect e ui-polish
"""
import streamlit as st

def apply_custom_theme():
    """
    Injeta tokens semânticos e regras CSS avançadas para elevar o acabamento
    da aplicação para o padrão Linear/Vercel/Stripe, eliminando AI slop e
    garantindo acessibilidade WCAG 2.2 AA.
    """
    custom_css = """
    <style>
    /* ==========================================================================
       1. Tokens Semânticos de Design (design-system-architect)
       ========================================================================== */
    :root {
        /* Superfícies */
        --surface-base: #0b0f19;
        --surface-subtle: #111827;
        --surface-raised: #1f2937;
        --surface-card: rgba(31, 41, 55, 0.7);
        --surface-card-hover: rgba(55, 65, 81, 0.5);

        /* Tipografia e Cores de Frente */
        --foreground-primary: #f9fafb;
        --foreground-muted: #9ca3af;
        --foreground-subtle: #6b7280;

        /* Destaques e Ação */
        --primary-brand: #3b82f6;
        --primary-brand-hover: #60a5fa;
        --primary-brand-active: #2563eb;
        --primary-surface: rgba(59, 130, 246, 0.12);

        /* Feedback Semântico */
        --success-base: #10b981;
        --success-surface: rgba(16, 185, 129, 0.12);
        --warning-base: #f59e0b;
        --warning-surface: rgba(245, 158, 11, 0.12);
        --error-base: #ef4444;
        --error-surface: rgba(239, 68, 68, 0.12);
        --info-base: #06b6d4;
        --info-surface: rgba(6, 182, 212, 0.12);

        /* Bordas e Divisores (Opacidade sutil para evitar poluição visual) */
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-focus: rgba(96, 165, 250, 0.6);
        --border-strong: rgba(255, 255, 255, 0.18);

        /* Raios de Borda e Sombras */
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        --shadow-glow: 0 0 15px -3px rgba(59, 130, 246, 0.15);

        /* Transições Rápidas e Orgânicas */
        --transition-snappy: all 180ms cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* ==========================================================================
       2. Tipografia Global e Alinhamento Óptico (ui-polish)
       ========================================================================== */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        letter-spacing: -0.012em;
    }

    /* Redução de Padding Excessivo do Topo do Streamlit */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px !important;
    }

    /* Cabeçalhos refinados */
    h1, h2, h3, h4 {
        letter-spacing: -0.025em !important;
        font-weight: 600 !important;
    }

    /* ==========================================================================
       3. Barra Lateral (Sidebar) com Acabamento Premium
       ========================================================================== */
    [data-testid="stSidebar"] {
        background-color: var(--surface-subtle) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--foreground-primary) !important;
    }

    /* ==========================================================================
       4. Cards de Métricas e KPIs Customizados
       ========================================================================== */
    .kpi-card {
        background: var(--surface-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 18px 20px;
        box-shadow: var(--shadow-card);
        backdrop-filter: blur(8px);
        transition: var(--transition-snappy);
        margin-bottom: 12px;
    }

    .kpi-card:hover {
        border-color: var(--border-strong);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }

    .kpi-title {
        font-size: 0.8125rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--foreground-muted);
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .kpi-value {
        font-size: 1.625rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--foreground-primary);
        line-height: 1.2;
    }

    .kpi-caption {
        font-size: 0.8125rem;
        color: var(--foreground-subtle);
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* ==========================================================================
       5. Badges e Indicadores de Estado Acessíveis (a11y-auditor)
       ========================================================================== */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 9999px;
        line-height: 1.2;
        letter-spacing: 0.02em;
    }

    .badge-primary {
        background: var(--primary-surface);
        color: var(--primary-brand-hover);
        border: 1px solid rgba(59, 130, 246, 0.25);
    }

    .badge-success {
        background: var(--success-surface);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .badge-warning {
        background: var(--warning-surface);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }

    .badge-error {
        background: var(--error-surface);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }

    .badge-neutral {
        background: rgba(255, 255, 255, 0.06);
        color: var(--foreground-muted);
        border: 1px solid var(--border-subtle);
    }

    /* ==========================================================================
       6. Empty States Elegantes (ui-polish & component-builder)
       ========================================================================== */
    .empty-state-box {
        text-align: center;
        padding: 42px 24px;
        background: var(--surface-subtle);
        border: 1px dashed var(--border-strong);
        border-radius: var(--radius-lg);
        margin: 20px 0;
    }

    .empty-state-icon {
        font-size: 2.2rem;
        margin-bottom: 12px;
        opacity: 0.85;
    }

    .empty-state-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--foreground-primary);
        margin-bottom: 6px;
    }

    .empty-state-desc {
        font-size: 0.875rem;
        color: var(--foreground-muted);
        max-width: 440px;
        margin: 0 auto;
    }

    /* ==========================================================================
       7. Hero Header e Banners de Seção
       ========================================================================== */
    .header-banner {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-card);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }

    .header-info-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--foreground-primary);
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .header-info-subtitle {
        font-size: 0.875rem;
        color: var(--foreground-muted);
        margin: 0;
    }

    /* ==========================================================================
       8. Inputs, Botões e Focus Visible (a11y-auditor)
       ========================================================================== */
    div[data-baseweb="input"] {
        border-radius: var(--radius-sm) !important;
        border-color: var(--border-subtle) !important;
        transition: var(--transition-snappy) !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
    }

    button[kind="primary"] {
        background-color: var(--primary-brand) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        transition: var(--transition-snappy) !important;
    }

    button[kind="primary"]:hover {
        background-color: var(--primary-brand-hover) !important;
        transform: translateY(-1px);
    }

    button[kind="primary"]:active {
        transform: scale(0.98);
    }

    /* Abas Modernizadas */
    div[data-testid="stTabs"] button[role="tab"] {
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: var(--transition-snappy) !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }

    /* Tabelas e Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        overflow: hidden;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
