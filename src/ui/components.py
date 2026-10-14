"""UI Components for Appota Knowledge Guard."""

from __future__ import annotations

import html
import streamlit as st


def render_topbar(user: dict | None):
    """Render compact top navigation bar (64-72px) replacing the oversized hero."""
    user_pill_html = ""
    if user:
        user_name = html.escape(user.get("name", "User"))
        user_co = html.escape(user.get("company", ""))
        user_pill_html = (
            f'<div class="kg-profile-pill">'
            f'<span class="kg-status-indicator"></span>'
            f'<span><strong>{user_name}</strong> · {user_co}</span>'
            f'</div>'
        )

    raw_html = (
        f'<div class="kg-topbar">'
        f'<div class="kg-brand-lockup">'
        f'<div class="kg-brand-icon">🛡️</div>'
        f'<div class="kg-brand-text">'
        f'<span class="kg-brand-title">Knowledge Guard</span>'
        f'<span class="kg-brand-subtitle">Secure Enterprise Knowledge · Authorized Retrieval Only</span>'
        f'</div>'
        f'</div>'
        f'{user_pill_html}'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)


def render_compact_profile(user: dict):
    """Render a compact user profile card with badges instead of tall tabular rows."""
    name = html.escape(user.get("name", "Unknown"))
    user_id = html.escape(user.get("user_id", ""))
    company = html.escape(user.get("company", ""))
    department = html.escape(user.get("department", ""))
    team = html.escape(user.get("team", "") or department)
    role = html.escape(user.get("role", "EMPLOYEE"))
    level = user.get("level", 1)
    emp_type = html.escape(user.get("employment_type", "FULL_TIME"))

    raw_html = (
        f'<div class="kg-user-card">'
        f'<div class="kg-user-header">'
        f'<span class="kg-user-name">🛡️ {name}</span>'
        f'<span class="kg-user-id">{user_id}</span>'
        f'</div>'
        f'<div class="kg-user-role-line">{role} · {team}</div>'
        f'<div class="kg-chip-row">'
        f'<span class="kg-chip kg-chip-company">{company}</span>'
        f'<span class="kg-chip kg-chip-level">L{level}</span>'
        f'<span class="kg-chip kg-chip-type">{emp_type}</span>'
        f'</div>'
        f'</div>'
        f'<div style="font-size:0.7rem; color:#6B7280; padding:0 0.2rem 0.6rem 0.2rem; line-height:1.3;">'
        f'🔒 <em>Demo identity — Production identity is verified by backend authentication.</em>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)


def render_user_bubble(message: dict):
    """Render user query as a right-aligned bubble on muted dark surface."""
    content = html.escape(message.get("content", ""))
    raw_html = (
        f'<div class="kg-user-msg-container">'
        f'<div class="kg-user-bubble">{content}</div>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)


def render_status_badge(status: str, reason: str | None = None) -> tuple[str, str]:
    """Return status badge HTML and calm security explanatory text."""
    if status == "ANSWER":
        badge = '<span class="kg-verified-badge kg-badge-verified">✓ Verified</span>'
        desc = "Câu trả lời được trích xuất từ tài liệu hợp lệ trong phạm vi thẩm quyền của bạn."
    elif status == "ABSTAIN":
        badge = '<span class="kg-verified-badge kg-badge-abstain">🔒 Giới hạn truy cập / Thiếu căn cứ</span>'
        if reason == "missing_evidence":
            desc = "Tài liệu hiện có chưa đủ căn cứ xác thực để trả lời câu hỏi này."
        else:
            desc = "Hồ sơ hiện tại không có thẩm quyền truy cập thông tin yêu cầu. Nội dung hạn chế đã bị loại trừ trước khi sinh câu trả lời."
    elif status == "CONFLICT":
        badge = '<span class="kg-verified-badge kg-badge-conflict">⛔ Mâu thuẫn chính sách</span>'
        desc = "Phát hiện nhiều văn bản chính sách có cùng cấp thẩm quyền nhưng mâu thuẫn về nội dung."
    else:
        badge = '<span class="kg-verified-badge kg-badge-error">⚠️ Lỗi xử lý</span>'
        desc = "Không thể hoàn thành tra cứu. Vui lòng thử lại với câu hỏi khác."
    return badge, desc


def render_citation_cards(citations: list):
    """Render citation cards directly beneath assistant response."""
    if not citations:
        return

    cards_html = []
    for idx, c in enumerate(citations, start=1):
        doc_id = getattr(c, "document_id", c.get("document_id") if isinstance(c, dict) else "")
        title = getattr(c, "title", c.get("title") if isinstance(c, dict) else "")
        ver = getattr(c, "version", c.get("version") if isinstance(c, dict) else "")
        sec = getattr(c, "section", c.get("section") if isinstance(c, dict) else "")
        excerpt = getattr(c, "excerpt", c.get("excerpt") if isinstance(c, dict) else "")

        sec_part = f"<span>· Mục: <em>{html.escape(sec)}</em></span>" if sec else ""
        excerpt_part = (
            f'<blockquote class="kg-citation-excerpt">“{html.escape(excerpt)}”</blockquote>'
            if excerpt else ""
        )
        card_item = (
            f'<div class="kg-citation-card">'
            f'<div class="kg-citation-num">[{idx}]</div>'
            f'<div class="kg-citation-main">'
            f'<div class="kg-citation-title">{html.escape(title)}</div>'
            f'<div class="kg-citation-meta">'
            f'<span class="kg-citation-code">{html.escape(doc_id)}</span>'
            f'<span>· Phiên bản: <strong>{html.escape(ver)}</strong></span>'
            f'{sec_part}'
            f'</div>'
            f'{excerpt_part}'
            f'</div>'
            f'</div>'
        )
        cards_html.append(card_item)

    joined_cards = "".join(cards_html)
    raw_html = (
        f'<div class="kg-citations-container">'
        f'<div class="kg-citations-header">📚 Nguồn tham khảo ({len(citations)})</div>'
        f'<div class="kg-citation-cards">{joined_cards}</div>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)


def render_assistant_card(message: dict):
    """Render assistant response on a neutral dark surface with verified badge & citations."""
    status = message.get("status", "ANSWER")
    answer = message.get("content", "")
    reason = message.get("reason")
    citations = message.get("citations", [])

    badge_html, desc_text = render_status_badge(status, reason)

    raw_html = (
        f'<div class="kg-assistant-card">'
        f'<div class="kg-assistant-header">'
        f'<div class="kg-assistant-identity"><span>🛡️ Trợ lý Chính sách</span></div>'
        f'{badge_html}'
        f'</div>'
        f'<div class="kg-answer-body">{html.escape(answer)}</div>'
        f'<div class="kg-security-subtext"><span>🛡️</span><span>{html.escape(desc_text)}</span></div>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)

    # Citations directly below
    if citations:
        render_citation_cards(citations)

    # Deep trace in sleek expander
    if message.get("trace"):
        render_audit_trace_expander(message["trace"])


def render_audit_trace_expander(trace: dict):
    """Render guard pipeline and audit trace in an expandable container."""
    if not trace:
        return

    with st.expander("🔍 Guard Pipeline & Chi tiết kiểm soát truy cập", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tổng tài liệu hệ thống", trace.get("total_document_count", 0))
        with col2:
            st.metric(
                "Được quyền đọc",
                trace.get("readable_document_count", 0),
                delta=f"-{trace.get('access_rejected_count', 0)} chặn",
                delta_color="inverse",
            )
        with col3:
            st.metric(
                "Áp dụng",
                trace.get("applicable_document_count", 0),
                delta=f"-{trace.get('applicability_rejected_count', 0)} loại",
                delta_color="inverse",
            )
        with col4:
            st.metric(
                "Phiên bản hợp lệ",
                trace.get("current_version_count", 0),
                delta=f"-{trace.get('version_excluded_count', 0)} cũ/nháp",
                delta_color="inverse",
            )

        st.caption(
            f"Topic: **{trace.get('topic', 'N/A')}** | "
            f"Quyết định thẩm quyền: **{trace.get('resolver_decision', 'N/A')}** | "
            f"Thời gian: **{trace.get('latency_ms', 0)} ms**"
        )


def render_welcome_box():
    """Render clean, enterprise welcome screen when no messages exist."""
    raw_html = (
        f'<div class="kg-welcome-box">'
        f'<div class="kg-welcome-icon">🛡️</div>'
        f'<div class="kg-welcome-title">Appota Knowledge Guard</div>'
        f'<div class="kg-welcome-desc">'
        f'Hệ thống hỏi đáp chính sách doanh nghiệp phân quyền thông minh. '
        f'Câu trả lời được trích xuất hoàn toàn dựa trên thẩm quyền của bạn. '
        f'Tài liệu không được phép truy cập <strong>tuyệt đối không bao giờ đi vào ngữ cảnh LLM</strong>.'
        f'</div>'
        f'<div style="font-size:0.8rem; color:#9CA3AF;">'
        f'💡 <em>Chọn câu hỏi mẫu bên thanh trái hoặc nhập câu hỏi bên dưới để bắt đầu.</em>'
        f'</div>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)
