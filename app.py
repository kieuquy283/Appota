"""Appota Knowledge Guard — Multi-Turn Chat & Citations
Enterprise AI Assistant with Authorization-Aware Retrieval (RBAC) & Provenance Citations.
"""

from __future__ import annotations

import html
import streamlit as st

from src.service import answer_question, list_demo_users
from src.ui.theme import ENTERPRISE_THEME_CSS
from src.ui.components import (
    render_topbar,
    render_compact_profile,
    render_user_bubble,
    render_assistant_card,
    render_status_badge,
    render_citation_cards,
    render_audit_trace_expander,
    render_welcome_box,
)

# Page configuration
st.set_page_config(
    page_title="Appota Knowledge Guard — Enterprise Knowledge Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject design system and enterprise theme
st.markdown(ENTERPRISE_THEME_CSS, unsafe_allow_html=True)


def load_users() -> list[dict]:
    """Load trusted synthetic demo users from backend."""
    try:
        return list_demo_users()
    except Exception as e:
        st.error(f"Lỗi khi tải danh sách người dùng: {e}")
        return []


def format_user_label(user: dict) -> str:
    """Format user label for dropdown selector."""
    return f"{user['user_id']} — {user['name']} ({user['company']} / {user['department']} / {user['role']})"


def init_session_state():
    """Initialize conversation and user tracking in session state."""
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if "current_user_id" not in st.session_state:
        st.session_state["current_user_id"] = None
    if "pending_prompt" not in st.session_state:
        st.session_state["pending_prompt"] = None
    if "session_history_titles" not in st.session_state:
        st.session_state["session_history_titles"] = []


def reset_conversation():
    """Clear message history for current or changed session."""
    st.session_state["chat_messages"] = []
    st.session_state["pending_prompt"] = None
    st.session_state["session_history_titles"] = []


def render_sidebar(users: list[dict]) -> dict | None:
    """Render modern enterprise sidebar with brand, new chat, conversation list, demo user switcher, and test cases."""
    # Top Identity & New Chat
    st.sidebar.markdown(
        """
        <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:1rem; padding-bottom:0.5rem; border-bottom: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size:1.5rem;">🛡️</div>
            <div>
                <div style="font-weight:700; font-size:1.05rem; color:#FFFFFF; line-height:1.2;">Knowledge Guard</div>
                <div style="font-size:0.75rem; color:#9CA3AF;">Enterprise Security AI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("➕ Cuộc trò chuyện mới", use_container_width=True, type="secondary"):
        reset_conversation()
        st.rerun()

    # Conversation History in Session
    titles = st.session_state.get("session_history_titles", [])
    if titles:
        st.sidebar.markdown('<div class="kg-sidebar-section-title">Hội thoại phiên này</div>', unsafe_allow_html=True)
        for t in titles[-4:]:
            st.sidebar.markdown(f'<div class="kg-history-item active">💬 {html.escape(t)}</div>', unsafe_allow_html=True)

    st.sidebar.markdown('<div class="kg-sidebar-section-title">Định danh giả lập (Demo Identity)</div>', unsafe_allow_html=True)

    if not users:
        st.sidebar.warning("Không có dữ liệu người dùng.")
        return None

    # User selector
    user_labels = [format_user_label(u) for u in users]
    default_idx = 0
    if st.session_state.get("current_user_id"):
        for idx, u in enumerate(users):
            if u["user_id"] == st.session_state["current_user_id"]:
                default_idx = idx
                break

    selected_label = st.sidebar.selectbox(
        "Chuyển đổi người dùng:",
        user_labels,
        index=default_idx,
        key="user_selector",
        label_visibility="collapsed",
    )

    selected_user = next((u for u in users if format_user_label(u) == selected_label), users[0])
    selected_id = selected_user["user_id"]

    # Security check: User switch resets conversation history immediately to prevent context leakage
    if st.session_state.get("current_user_id") is not None and st.session_state["current_user_id"] != selected_id:
        reset_conversation()

    st.session_state["current_user_id"] = selected_id

    # Compact profile card
    render_compact_profile(selected_user)

    # Preset / Evaluation Cases
    st.sidebar.markdown('<div class="kg-sidebar-section-title">Trường hợp kiểm thử (Evaluation Cases)</div>', unsafe_allow_html=True)
    st.sidebar.caption("Kiểm chứng hành vi truy xuất theo quyền và tính toán vẹn:")

    preset_questions = [
        ("Nghỉ phép năm (Alice 15 vs Carol 12)", "Tôi có bao nhiêu ngày nghỉ phép?"),
        ("WFH ngày trong tuần (Alice 2 ngày)", "Tôi được WFH mấy ngày?"),
        ("WFH thứ Sáu (Thiếu bằng chứng → ABSTAIN)", "Tôi có được WFH thứ Sáu không?"),
        ("Lương HR (Chặn tài liệu mật → ABSTAIN)", "Chính sách lương của tôi là gì?"),
        ("Phê duyệt phép (Quyền Manager)", "Quy trình phê duyệt nghỉ phép của quản lý như thế nào?"),
    ]

    for title, q_text in preset_questions:
        if st.sidebar.button(title, use_container_width=True, key=f"btn_{title}"):
            st.session_state["pending_prompt"] = q_text
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size:0.72rem; color:#6B7280; text-align:center; line-height:1.4;">
            Appota Knowledge Guard · RBAC Engine<br/>
            Deterministic Guard + Extractive LLM
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected_user


def render_status(message: dict):
    """Backwards-compatible wrapper rendering status, answer, and reason."""
    import textwrap
    status = message.get("status", "ANSWER")
    answer = message.get("content", "")
    reason = message.get("reason")
    badge_html, desc_text = render_status_badge(status, reason)

    raw_html = textwrap.dedent(f"""
<div class="kg-assistant-card">
    <div class="kg-assistant-header">
        <div class="kg-assistant-identity">🛡️ Trợ lý Chính sách</div>
        {badge_html}
    </div>
    <div class="kg-answer-body">{html.escape(answer)}</div>
    <div class="kg-security-subtext">🛡️ {html.escape(desc_text)}</div>
</div>
""").strip()
    st.markdown(raw_html, unsafe_allow_html=True)


def render_citations(citations: list):
    """Render numbered citation cards bound to the specific assistant message."""
    render_citation_cards(citations)


def render_audit_trace(trace: dict):
    """Render guard pipeline and audit trace in an expandable container."""
    render_audit_trace_expander(trace)


def render_user_message(message: dict):
    """Render a user query bubble."""
    render_user_bubble(message)


def render_assistant_message(message: dict):
    """Render an assistant response bubble containing status, inline citations, cards, and audit trace."""
    render_assistant_card(message)


def render_chat_history():
    """Render the full sequence of multi-turn chat messages or the welcome screen."""
    messages = st.session_state.get("chat_messages", [])
    if not messages:
        render_welcome_box()
        return

    for msg in messages:
        if msg.get("role") == "user":
            render_user_message(msg)
        elif msg.get("role") == "assistant":
            render_assistant_message(msg)


def submit_question(question: str, user_id: str):
    """Submit question to backend and record result in session history."""
    clean_q = question.strip()
    if not clean_q:
        return

    # Track in session history titles if not already present
    titles = st.session_state.setdefault("session_history_titles", [])
    short_title = clean_q if len(clean_q) <= 32 else clean_q[:30] + "..."
    if short_title not in titles:
        titles.append(short_title)

    # Append user question
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": clean_q,
    })

    # Execute backend pipeline with security guarantee
    with st.spinner("Đang kiểm tra quyền và tìm tài liệu..."):
        try:
            result = answer_question(user_id, clean_q)
            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": result.answer,
                "status": result.status,
                "citations": result.citations,
                "reason": result.reason,
                "trace": result.trace,
                "request_id": result.trace.get("request_id") if result.trace else None,
            })
        except Exception as e:
            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}",
                "status": "ERROR",
                "citations": [],
                "reason": "internal_error",
                "trace": {},
                "request_id": None,
            })


def render_quick_action_chips():
    """Render quick suggestion action chips above input composer."""
    quick_items = [
        ("📅 Nghỉ phép năm", "Tôi có bao nhiêu ngày nghỉ phép?"),
        ("🏠 Chính sách WFH", "Tôi được WFH mấy ngày?"),
        ("📋 Duyệt phép", "Quy trình phê duyệt nghỉ phép của quản lý như thế nào?"),
    ]
    cols = st.columns(len(quick_items))
    for idx, (label, prompt_text) in enumerate(quick_items):
        with cols[idx]:
            if st.button(label, key=f"quick_{idx}", use_container_width=True):
                st.session_state["pending_prompt"] = prompt_text
                st.rerun()


def main():
    init_session_state()
    users = load_users()
    selected_user = render_sidebar(users)

    # Render compact topbar (replacing the large hero)
    render_topbar(selected_user)

    if not selected_user:
        st.error("Không thể tiếp tục vì chưa chọn người dùng.")
        return

    user_id = selected_user["user_id"]

    # Check for pending prompt triggered by preset or quick button
    pending_prompt = st.session_state.get("pending_prompt")
    if pending_prompt:
        st.session_state["pending_prompt"] = None
        submit_question(pending_prompt, user_id)

    # Render multi-turn conversation
    render_chat_history()

    # Quick prompt actions (when empty or few messages)
    if len(st.session_state.get("chat_messages", [])) == 0:
        render_quick_action_chips()

    # Bottom spacer so persistent chat input never overlaps citations or audit traces
    st.markdown('<div class="kg-bottom-spacer"></div>', unsafe_allow_html=True)

    # Fixed bottom chat input
    user_input = st.chat_input("Nhập câu hỏi về chính sách doanh nghiệp (VD: Tôi có bao nhiêu ngày nghỉ phép?)...")
    if user_input:
        submit_question(user_input, user_id)
        st.rerun()


if __name__ == "__main__":
    main()
