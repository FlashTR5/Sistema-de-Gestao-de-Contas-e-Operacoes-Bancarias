"""
Módulo de Componentes de Interface Reutilizáveis
Governança via component-builder, ui-polish e a11y-auditor
"""
import streamlit as st

def render_header(title: str, subtitle: str, badge_text: str = None, badge_type: str = "primary", icon: str = "🏦"):
    """
    Renderiza um cabeçalho elegante com hierarquia tipográfica, respiro e badge contextual.
    """
    badge_html = f'<span class="badge badge-{badge_type}">{badge_text}</span>' if badge_text else ""
    html = f"""
    <div class="header-banner">
        <div>
            <h1 class="header-info-title">
                <span>{icon}</span> {title}
            </h1>
            <p class="header-info-subtitle">{subtitle}</p>
        </div>
        <div>
            {badge_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi(col, title: str, value: str, caption: str = "", badge_text: str = None, badge_type: str = "neutral"):
    """
    Renderiza um cartão de KPI estilo Linear/Stripe com alinhamento óptico e badge.
    """
    badge_html = f'<span class="badge badge-{badge_type}">{badge_text}</span>' if badge_text else ""
    caption_html = f'<div class="kpi-caption">{caption}</div>' if caption else ""
    html = f"""
    <div class="kpi-card">
        <div class="kpi-title">
            <span>{title}</span>
            {badge_html}
        </div>
        <div class="kpi-value">{value}</div>
        {caption_html}
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)


def render_empty_state(title: str, description: str, icon: str = "🔍", action_hint: str = None):
    """
    Implementa o estado Vazio (Empty State) da Matriz de UI de 8 estados.
    """
    hint_html = f'<div style="margin-top: 12px; font-size: 0.8125rem; color: var(--primary-brand); font-weight: 500;">💡 {action_hint}</div>' if action_hint else ""
    html = f"""
    <div class="empty-state-box">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-desc">{description}</div>
        {hint_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """
    Retorna a string HTML de um badge acessível conforme o status (a11y: cor + ícone + texto).
    """
    st_upper = str(status).upper()
    if st_upper in ["ATIVA", "ATIVO", "QUITADO", "PAGO", "SUCESSO"]:
        return f'<span class="badge badge-success">● {status}</span>'
    elif st_upper in ["BLOQUEADA", "BLOQUEADO", "EM_ATRASO", "FALHA"]:
        return f'<span class="badge badge-warning">▲ {status}</span>'
    elif st_upper in ["ENCERRADA", "CANCELADO", "INADIMPLENTE"]:
        return f'<span class="badge badge-error">✕ {status}</span>'
    else:
        return f'<span class="badge badge-neutral">○ {status}</span>'


def render_callout(title: str, message: str, callout_type: str = "info", icon: str = "ℹ️"):
    """
    Renderiza um painel de destaque com feedback semântico.
    """
    border_color = {
        "info": "rgba(6, 182, 212, 0.3)",
        "success": "rgba(16, 185, 129, 0.3)",
        "warning": "rgba(245, 158, 11, 0.3)",
        "error": "rgba(239, 68, 68, 0.3)"
    }.get(callout_type, "var(--border-subtle)")

    bg_color = {
        "info": "rgba(6, 182, 212, 0.07)",
        "success": "rgba(16, 185, 129, 0.07)",
        "warning": "rgba(245, 158, 11, 0.07)",
        "error": "rgba(239, 68, 68, 0.07)"
    }.get(callout_type, "var(--surface-subtle)")

    html = f"""
    <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: var(--radius-md); padding: 14px 18px; margin: 12px 0;">
        <div style="font-weight: 600; font-size: 0.9375rem; color: var(--foreground-primary); margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
            <span>{icon}</span> {title}
        </div>
        <div style="font-size: 0.875rem; color: var(--foreground-muted); line-height: 1.5;">
            {message}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_searchable_account_picker(key_prefix: str, label: str = "Selecione a Conta Bancária:", filtro_status: str = None, help_text: str = None):
    """
    Renderiza um seletor pesquisável de contas no padrão rico solicitado pelo usuário (Print 5).
    Permite pesquisar dinamicamente por número da conta (ex: 10001), nome do titular ou CPF.
    Retorna uma tupla (numero_conta, dados_completos_conta).
    """
    from db import execute_query
    
    termo = st.text_input(
        "🔍 Buscar conta (por número, titular ou CPF):",
        placeholder="Digite o número (ex: 10001), titular ou CPF...",
        key=f"search_{key_prefix}"
    )
    
    where_clauses = []
    params = []
    
    if termo.strip():
        where_clauses.append("(cb.numero_conta LIKE %s OR c.nome LIKE %s OR c.cpf_cnpj LIKE %s)")
        t = f"%{termo.strip()}%"
        params.extend([t, t, t])
        
    if filtro_status:
        where_clauses.append("cb.status = %s")
        params.append(filtro_status)
        
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    sql = f"""
    SELECT 
        cb.numero_conta, 
        cb.codigo_agencia,
        cb.modalidade, 
        cb.saldo, 
        cb.status, 
        c.nome AS titular, 
        c.cpf_cnpj
    FROM conta_bancaria cb
    INNER JOIN cliente_conta cc ON cb.numero_conta = cc.numero_conta AND cc.tipo_titular = 'TITULAR'
    INNER JOIN cliente c ON cc.id_cliente = c.id_cliente
    {where_sql}
    ORDER BY cb.numero_conta ASC 
    LIMIT 45;
    """
    res, err = execute_query(sql, tuple(params) if params else None)
    
    if err:
        st.error(err)
        return None, None
        
    if not res:
        render_callout(
            "Nenhuma Conta Localizada",
            f"Nenhuma conta bancária cadastrada corresponde ao termo de busca '{termo}'.",
            callout_type="warning",
            icon="⚠️"
        )
        return None, None
        
    def format_opt(acc):
        num = acc['numero_conta']
        titular = acc['titular']
        saldo = float(acc['saldo'])
        st_val = acc['status']
        doc = acc['cpf_cnpj']
        doc_mask = f"{doc[:3]}.***-**" if len(doc) >= 11 else doc
        return f"🏦 {num} · {titular} (Doc: {doc_mask} | Saldo: R$ {saldo:,.2f} | {st_val})"
        
    opcoes = {acc['numero_conta']: acc for acc in res}
    
    sel_key = st.selectbox(
        f"{label} ({len(res)} contas encontradas):",
        options=list(opcoes.keys()),
        format_func=lambda k: format_opt(opcoes[k]),
        key=f"sel_{key_prefix}",
        help=help_text
    )
    
    return sel_key, opcoes[sel_key]

