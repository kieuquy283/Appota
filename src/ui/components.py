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
        f'<span class="kg-brand-subtitle">Hỏi đáp chính sách dành cho bạn</span>'
        f'</div>'
        f'</div>'
        f'{user_pill_html}'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)


def render_compact_profile(user: dict):
    """Render a compact user profile card with badges instead of tall tabular rows."""
    name = html.escape(user.get("name", "Người dùng"))
    company = html.escape(user.get("company", ""))
    department = html.escape(user.get("department", ""))
    team = html.escape(user.get("team", "") or department)
    role_labels = {"PEOPLE_MANAGER": "Quản lý", "MANAGER": "Quản lý",
                   "HR": "Nhân sự", "EMPLOYEE": "Nhân viên"}
    role = role_labels.get(user.get("role"), "Nhân viên")
    employment_labels = {
        "FULL_TIME": "Toàn thời gian", "PART_TIME": "Bán thời gian",
        "INTERN": "Thực tập", "CONTRACTOR": "Hợp đồng",
    }
    emp_type = html.escape(employment_labels.get(user.get("employment_type"), "Nhân sự"))
    team_part = f" · {team}" if team != department else ""

    raw_html = (
        f'<div class="kg-user-card">'
        f'<div class="kg-user-header">'
        f'<span class="kg-user-name">{name}</span>'
        f'</div>'
        f'<div class="kg-user-role-line">{role} · {department}{team_part}</div>'
        f'<div class="kg-chip-row">'
        f'<span class="kg-chip kg-chip-company">{company}</span>'
        f'<span class="kg-chip kg-chip-type">{emp_type}</span>'
        f'</div>'
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
        badge = '<span class="kg-verified-badge kg-badge-verified">✓ Đã tìm thấy thông tin</span>'
        desc = "Câu trả lời dựa trên tài liệu bạn có thể xem."
    elif status == "ABSTAIN":
        badge = '<span class="kg-verified-badge kg-badge-abstain">Chưa đủ thông tin</span>'
        if reason == "missing_evidence":
            desc = "Tài liệu hiện có chưa đủ thông tin để trả lời câu hỏi này."
        else:
            desc = "Chưa có thông tin phù hợp để trả lời câu hỏi này."
    elif status == "CONFLICT":
        badge = '<span class="kg-verified-badge kg-badge-conflict">Thông tin chưa thống nhất</span>'
        desc = "Các tài liệu hiện có đưa ra thông tin khác nhau. Vui lòng hỏi bộ phận phụ trách."
    else:
        badge = '<span class="kg-verified-badge kg-badge-error">Tạm thời chưa trả lời được</span>'
        desc = "Vui lòng thử lại sau."
    return badge, desc


def render_citation_cards(citations: list):
    """Render citation cards directly beneath assistant response."""
    if not citations:
        return

    cards_html = []
    for idx, c in enumerate(citations, start=1):
        title = getattr(c, "title", c.get("title") if isinstance(c, dict) else "")
        sec = getattr(c, "section", c.get("section") if isinstance(c, dict) else "")
        excerpt = getattr(c, "excerpt", c.get("excerpt") if isinstance(c, dict) else "")

        sec_part = f"<span>Phần: {html.escape(sec)}</span>" if sec else ""
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
        f'<div class="kg-citations-header">📚 Đoạn trích từ tài liệu</div>'
        f'<div class="kg-citation-cards">{joined_cards}</div>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)


def render_assistant_card(message: dict):
    """Render assistant response on a neutral dark surface with verified badge & citations."""
    status = message.get("status", "ANSWER")
    answer = message.get("content", "")
    if status == "ABSTAIN":
        answer = "Mình chưa tìm thấy đủ thông tin phù hợp để trả lời câu hỏi này."
    elif status == "CONFLICT":
        answer = "Các tài liệu hiện có đưa ra thông tin khác nhau. Vui lòng hỏi bộ phận phụ trách để xác nhận."
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
        f'<div class="kg-security-subtext"><span>{html.escape(desc_text)}</span></div>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)

    # Citations directly below
    if citations:
        render_citation_cards(citations)

def render_welcome_box():
    """Render clean, enterprise welcome screen when no messages exist."""
    raw_html = (
        f'<div class="kg-welcome-box">'
        f'<div class="kg-welcome-icon">🛡️</div>'
        f'<div class="kg-welcome-title">Appota Knowledge Guard</div>'
        f'<div class="kg-welcome-desc">'
        f'Hãy hỏi về những chính sách liên quan đến bạn. '
        f'Mỗi câu trả lời sẽ kèm đoạn trích từ tài liệu phù hợp. '
        f'Khi chưa đủ thông tin, trợ lý sẽ nói rõ.'
        f'</div>'
        f'<div style="font-size:0.8rem; color:#9CA3AF;">'
        f'💡 <em>Chọn câu hỏi mẫu bên thanh trái hoặc nhập câu hỏi bên dưới để bắt đầu.</em>'
        f'</div>'
        f'</div>'
    )
    st.markdown(raw_html, unsafe_allow_html=True)
