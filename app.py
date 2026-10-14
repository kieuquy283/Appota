import html
import json
from datetime import date
import streamlit as st

from src.service import answer_question, list_demo_users

# Page configuration
st.set_page_config(
    page_title="Appota Knowledge Guard — Multi-Turn Chat & Citations",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for enterprise security UI and responsive chat
CUSTOM_CSS = """
<style>
/* Modern fonts and layout enhancements */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header style */
.hero-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #ffffff;
    padding: 1.35rem 1.75rem;
    border-radius: 12px;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
.hero-header h1 {
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.hero-header p {
    font-size: 0.92rem;
    color: #94a3b8;
    margin: 0.45rem 0 0 0;
    line-height: 1.5;
}

/* Welcome empty state card */
.welcome-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    text-align: center;
    margin: 1.5rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}
.welcome-icon {
    font-size: 2.8rem;
    margin-bottom: 0.75rem;
}
.welcome-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.5rem;
}
.welcome-subtitle {
    font-size: 0.92rem;
    color: #64748b;
    max-width: 600px;
    margin: 0 auto 1.5rem auto;
    line-height: 1.5;
}

/* Badge tags */
.tag-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.025em;
    text-transform: uppercase;
}
.tag-company {
    background: #e0f2fe;
    color: #0369a1;
}
.tag-role {
    background: #f1f5f9;
    color: #334155;
}

/* User Card in Sidebar */
.user-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-top: 0.75rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.user-card-title {
    font-weight: 700;
    font-size: 1.05rem;
    color: #0f172a;
    margin-bottom: 0.4rem;
}
.user-meta-item {
    font-size: 0.85rem;
    color: #475569;
    margin-bottom: 0.35rem;
    display: flex;
    justify-content: space-between;
}
.user-meta-label {
    font-weight: 500;
    color: #64748b;
}
.user-meta-val {
    font-weight: 600;
    color: #0f172a;
}

/* Status Banners */
.status-banner {
    border-radius: 10px;
    padding: 1.15rem 1.35rem;
    margin: 0.5rem 0 0.85rem 0;
    border: 1px solid transparent;
}
.status-answer {
    background: #f0fdf4;
    border-color: #86efac;
    color: #166534;
}
.status-abstain {
    background: #fffbeb;
    border-color: #fde68a;
    color: #92400e;
}
.status-conflict {
    background: #fef2f2;
    border-color: #fecaca;
    color: #991b1b;
}
.status-error {
    background: #fdf2f8;
    border-color: #fbcfe8;
    color: #9d174d;
}

.status-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.28rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}
.pill-answer {
    background: #22c55e;
    color: #ffffff;
}
.pill-abstain {
    background: #f59e0b;
    color: #ffffff;
}
.pill-conflict {
    background: #ef4444;
    color: #ffffff;
}
.pill-error {
    background: #e11d48;
    color: #ffffff;
}

/* Citations block */
.citations-wrapper {
    margin-top: 0.75rem;
    margin-bottom: 0.5rem;
}
.citations-header {
    font-weight: 700;
    font-size: 0.88rem;
    color: #334155;
    margin-bottom: 0.45rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.citation-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.45rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    transition: all 0.2s ease;
}
.citation-card:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    border-left-color: #2563eb;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.citation-idx {
    background: #dbeafe;
    color: #1e40af;
    font-weight: 700;
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    line-height: 1;
    margin-top: 0.15rem;
    flex-shrink: 0;
}
.citation-body {
    flex-grow: 1;
}
.citation-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: #0f172a;
    line-height: 1.35;
}
.citation-meta {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.2rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    align-items: center;
}
.citation-code {
    background: #e2e8f0;
    color: #334155;
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.75rem;
}

/* Pipeline trace cards */
.pipeline-step {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.step-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: #1e293b;
    display: flex;
    justify-content: space-between;
}
.step-detail {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.25rem;
}

/* Synthetic banner warning */
.synthetic-banner {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #64748b;
    margin-bottom: 1rem;
    line-height: 1.45;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .hero-header {
        padding: 1rem;
    }
    .hero-header h1 {
        font-size: 1.35rem;
    }
    .citation-card {
        flex-direction: column;
        gap: 0.4rem;
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def load_users() -> list[dict]:
    """Load trusted synthetic demo users from backend."""
    try:
        return list_demo_users()
    except Exception as e:
        st.error(f"Lỗi khi tải danh sách người dùng giả lập: {e}")
        return []


def format_user_label(user: dict) -> str:
    return f"{user['user_id']} — {user['name']} ({user['company']} / {user['department']} / {user['role']})"


def init_session_state():
    """Initialize conversation and user tracking in session state."""
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if "current_user_id" not in st.session_state:
        st.session_state["current_user_id"] = None
    if "pending_prompt" not in st.session_state:
        st.session_state["pending_prompt"] = None


def reset_conversation():
    """Clear message history for current or changed session."""
    st.session_state["chat_messages"] = []
    st.session_state["pending_prompt"] = None


def render_sidebar(users: list[dict]) -> dict | None:
    """Render sidebar with user switcher, profile card, reset button, and preset cases."""
    st.sidebar.markdown("### 👤 Ngữ cảnh người dùng (Trusted Profile)")
    st.sidebar.caption(
        "Backend tự động xác thực profile dựa trên user_id. UI không truyền role/company tự do nhằm ngăn chặn leo thang đặc quyền."
    )

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
        "Chọn người dùng giả lập:",
        user_labels,
        index=default_idx,
        key="user_selector",
    )

    selected_user = next((u for u in users if format_user_label(u) == selected_label), users[0])
    selected_id = selected_user["user_id"]

    # Security check: User switch resets conversation history
    if st.session_state.get("current_user_id") is not None and st.session_state["current_user_id"] != selected_id:
        reset_conversation()

    st.session_state["current_user_id"] = selected_id

    # Profile card
    st.sidebar.markdown(
        f"""
        <div class="user-card">
            <div class="user-card-title">
                🛡️ {html.escape(selected_user['name'])} 
                <span style="font-size:0.8rem; font-weight:normal; color:#64748b;">({html.escape(selected_user['user_id'])})</span>
            </div>
            <div class="user-meta-item">
                <span class="user-meta-label">Công ty:</span>
                <span class="user-meta-val"><span class="tag-badge tag-company">{html.escape(selected_user['company'])}</span></span>
            </div>
            <div class="user-meta-item">
                <span class="user-meta-label">Phòng ban:</span>
                <span class="user-meta-val">{html.escape(selected_user['department'])}</span>
            </div>
            <div class="user-meta-item">
                <span class="user-meta-label">Bộ phận (Team):</span>
                <span class="user-meta-val">{html.escape(selected_user.get('team', '—'))}</span>
            </div>
            <div class="user-meta-item">
                <span class="user-meta-label">Vai trò:</span>
                <span class="user-meta-val"><span class="tag-badge tag-role">{html.escape(selected_user['role'])} (L{selected_user['level']})</span></span>
            </div>
            <div class="user-meta-item">
                <span class="user-meta-label">Hình thức:</span>
                <span class="user-meta-val">{html.escape(selected_user.get('employment_type', 'FULL_TIME'))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Reset / New Chat Button
    st.sidebar.markdown("")
    if st.sidebar.button("➕ Cuộc trò chuyện mới", use_container_width=True, type="secondary"):
        reset_conversation()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧪 Câu hỏi mẫu (Evaluation Cases)")
    st.sidebar.caption("Chọn nhanh để kiểm chứng hành vi chính sách và bảo mật:")

    preset_questions = [
        ("Phép năm (Alice 15 vs Carol 12)", "Tôi có bao nhiêu ngày nghỉ phép?"),
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
        <div style="font-size:0.75rem; color:#94a3b8; text-align:center;">
            Appota Knowledge Guard — synthetic Mission 2 MVP<br/>
            Engine: Deterministic Guard + Extractive LLM
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected_user


def render_status(message: dict):
    """Render status badge, answer text, and policy reason in response bubble."""
    status = message.get("status", "ANSWER")
    answer = message.get("content", "")
    reason = message.get("reason")

    if status == "ANSWER":
        badge_html = '<span class="status-badge-pill pill-answer">✓ ĐÁP ÁN (ANSWER)</span>'
        status_class = "status-answer"
        explanation = "Đã tìm thấy chính sách hiện hành có hiệu lực và phù hợp với thẩm quyền của bạn."
    elif status == "ABSTAIN":
        badge_html = '<span class="status-badge-pill pill-abstain">⚠️ TỪ CHỐI TRẢ LỜI (ABSTAIN)</span>'
        status_class = "status-abstain"
        reason_text = (
            "Thiếu bằng chứng xác thực trong tài liệu được cấp quyền"
            if reason == "missing_evidence"
            else "Không đủ thẩm quyền truy cập tài liệu mật hoặc không tìm thấy tài liệu phù hợp"
        )
        explanation = f"Lý do từ chối: {reason_text}."
    elif status == "CONFLICT":
        badge_html = '<span class="status-badge-pill pill-conflict">⛔ MÂU THUẪN CHÍNH SÁCH (CONFLICT)</span>'
        status_class = "status-conflict"
        explanation = "Phát hiện có hai hoặc nhiều chính sách hiện hành cùng cấp thẩm quyền nhưng mâu thuẫn về nội dung."
    else:
        badge_html = '<span class="status-badge-pill pill-error">⚠️ LỖI XỬ LÝ (ERROR)</span>'
        status_class = "status-error"
        explanation = "Không thể hoàn thành tra cứu. Vui lòng thử lại câu hỏi khác."

    st.markdown(
        f"""
        <div class="status-banner {status_class}">
            {badge_html}
            <div style="font-size:1.05rem; font-weight:600; margin: 0.4rem 0 0.25rem 0; line-height:1.5;">
                {html.escape(answer)}
            </div>
            <div style="font-size:0.83rem; opacity:0.88; margin-top:0.25rem;">
                {html.escape(explanation)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_citations(citations: list):
    """Render numbered citation cards bound to the specific assistant message."""
    if not citations:
        return

    st.markdown(
        """
        <div class="citations-wrapper">
            <div class="citations-header">📚 Nguồn tham khảo:</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for idx, c in enumerate(citations, start=1):
        # Support both Citation objects and dictionary mappings
        doc_id = getattr(c, "document_id", c.get("document_id") if isinstance(c, dict) else "")
        title = getattr(c, "title", c.get("title") if isinstance(c, dict) else "")
        ver = getattr(c, "version", c.get("version") if isinstance(c, dict) else "")
        sec = getattr(c, "section", c.get("section") if isinstance(c, dict) else "")

        sec_html = f" · <em>{html.escape(sec)}</em>" if sec else ""
        st.markdown(
            f"""
            <div class="citation-card">
                <div class="citation-idx">[{idx}]</div>
                <div class="citation-body">
                    <div class="citation-title">{html.escape(title)}</div>
                    <div class="citation-meta">
                        <span class="citation-code">{html.escape(doc_id)}</span>
                        <span>· Phiên bản: <strong>{html.escape(ver)}</strong></span>
                        {sec_html}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_audit_trace(trace: dict):
    """Render guard pipeline and audit trace in an expandable container."""
    if not trace:
        return

    with st.expander("🔍 Vì sao có câu trả lời này? (Guard Pipeline & Audit Trace)", expanded=False):
        st.markdown(
            """
            <div class="synthetic-banner">
                <strong>🛡️ Cơ chế bảo mật Zero-Leakage:</strong> Mọi tài liệu không thuộc quyền đọc (Access Control), 
                không áp dụng (Applicability), hoặc đã hết hiệu lực / bản nháp (Version Filter) đều bị loại bỏ 
                <strong>hoàn toàn trước khi retrieval và LLM context được xây dựng</strong>.<br/>
                <em>Lưu ý: Số lượng tài liệu bị chặn chỉ hiển thị trong môi trường demo/audit này; hệ thống production sẽ ẩn hoàn toàn.</em>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Overview Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Tổng tài liệu hệ thống",
                trace.get("total_document_count", 0),
            )
        with col2:
            st.metric(
                "Được quyền đọc (Readable)",
                trace.get("readable_document_count", 0),
                delta=f"-{trace.get('access_rejected_count', 0)} bị chặn",
                delta_color="inverse",
            )
        with col3:
            st.metric(
                "Được áp dụng (Applicable)",
                trace.get("applicable_document_count", 0),
                delta=f"-{trace.get('applicability_rejected_count', 0)} loại bỏ",
                delta_color="inverse",
            )
        with col4:
            st.metric(
                "Phiên bản hợp lệ (Current)",
                trace.get("current_version_count", 0),
                delta=f"-{trace.get('version_excluded_count', 0)} cũ/nháp",
                delta_color="inverse",
            )

        st.markdown("#### 🔄 Chi tiết các bước lọc theo quy trình xác định:")

        # Step 1: User Context
        user_ctx = trace.get("user_context", {})
        st.markdown(
            f"""
            <div class="pipeline-step">
                <div class="step-title">
                    <span>1. Xác thực hồ sơ tin cậy (Trusted Profile)</span>
                    <span style="color:#10b981;">✓ Hợp lệ</span>
                </div>
                <div class="step-detail">
                    User ID: <code>{html.escape(str(trace.get('user_id', '—')))}</code> | 
                    Công ty: <strong>{html.escape(str(user_ctx.get('company', '—')))}</strong> | 
                    Phòng ban: <strong>{html.escape(str(user_ctx.get('department', '—')))}</strong> | 
                    Vai trò: <strong>{html.escape(str(user_ctx.get('role', '—')))}</strong> (L{user_ctx.get('level', '—')})
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 2: Access & Applicability Filter
        st.markdown(
            f"""
            <div class="pipeline-step">
                <div class="step-title">
                    <span>2. Kiểm soát truy cập (Access Control) & Phạm vi áp dụng (Applicability)</span>
                    <span style="color:#3b82f6;">ACL: Explicit DENY > Explicit ALLOW > Default DENY</span>
                </div>
                <div class="step-detail">
                    • Tài liệu hợp lệ có thể đọc: <strong>{trace.get('readable_document_count', 0)}</strong> / {trace.get('total_document_count', 0)}<br/>
                    • Tài liệu thực sự áp dụng cho người dùng: <strong>{trace.get('applicable_document_count', 0)}</strong> (loại {trace.get('applicability_rejected_count', 0)} tài liệu của đơn vị khác)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 3: Version Governance
        st.markdown(
            f"""
            <div class="pipeline-step">
                <div class="step-title">
                    <span>3. Quản trị vòng đời chính sách (Version Governance)</span>
                    <span style="color:#3b82f6;">APPROVED & Current Date</span>
                </div>
                <div class="step-detail">
                    • Các phiên bản cũ hết hạn hoặc bản nháp DRAFT bị loại bỏ: <strong>{trace.get('version_excluded_count', 0)}</strong><br/>
                    • Số phiên bản đang có hiệu lực bước vào tập ứng viên: <strong>{trace.get('current_version_count', 0)}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 4: Retrieval & Authority Resolution
        res_decision = trace.get("resolver_decision", "N/A")
        retrieved_ids = trace.get("retrieved_document_ids", [])
        retrieved_ver = trace.get("retrieved_versions", [])

        st.markdown(
            f"""
            <div class="pipeline-step">
                <div class="step-title">
                    <span>4. Truy xuất và Giải quyết Thẩm quyền (Retrieval & Authority Resolution)</span>
                    <span style="font-weight:700; color:{'#10b981' if res_decision == 'SELECTED' else '#f59e0b' if res_decision == 'INSUFFICIENT' else '#ef4444'};">
                        {html.escape(str(res_decision))}
                    </span>
                </div>
                <div class="step-detail">
                    • Topic nhận diện: <code>{html.escape(str(trace.get('topic', 'unknown')))}</code><br/>
                    • Nguồn được truy xuất: <code>{html.escape(', '.join(f"{d} ({v})" for d, v in zip(retrieved_ids, retrieved_ver)) if retrieved_ids else 'Không có')}</code><br/>
                    • Quy tắc ưu tiên: <code>OFFICIAL_POLICY > APPROVED_PROCEDURE > GUIDELINE > FAQ</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 5: Final Context Guard
        llm_docs = trace.get("llm_context_document_ids", [])
        llm_vers = trace.get("llm_context_version_ids", [])
        st.markdown(
            f"""
            <div class="pipeline-step">
                <div class="step-title">
                    <span>5. Chốt chặn Ngữ cảnh Cuối (Final Context Guard & Generation)</span>
                    <span style="color:#10b981;">✓ 100% Chunk Hợp lệ</span>
                </div>
                <div class="step-detail">
                    • Nguồn tài liệu được phép chuyển vào LLM: <code>{html.escape(', '.join(f"{d} ({v})" for d, v in zip(llm_docs, llm_vers)) if llm_docs else 'Không có (Ngăn chặn hoàn toàn)')}</code><br/>
                    • Thời gian phản hồi: <strong>{trace.get('latency_ms', 0)} ms</strong> | Request ID: <code>{html.escape(str(trace.get('request_id', '—')))}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Raw Trace Toggle
        with st.expander("📄 Dữ liệu Trace JSON kỹ thuật chi tiết"):
            st.json(trace)


def render_user_message(message: dict):
    """Render a user query bubble."""
    with st.chat_message("user"):
        st.markdown(f"**{html.escape(message.get('content', ''))}**")


def render_assistant_message(message: dict):
    """Render an assistant response bubble containing status, inline citations, cards, and audit trace."""
    with st.chat_message("assistant", avatar="🛡️"):
        render_status(message)
        render_citations(message.get("citations", []))
        if message.get("trace"):
            render_audit_trace(message["trace"])


def render_chat_history():
    """Render the full sequence of multi-turn chat messages or a welcome prompt."""
    messages = st.session_state.get("chat_messages", [])
    if not messages:
        st.markdown(
            """
            <div class="welcome-card">
                <div class="welcome-icon">🛡️</div>
                <div class="welcome-title">Chào mừng bạn đến với Knowledge Guard</div>
                <div class="welcome-subtitle">
                    Hệ thống hỏi đáp chính sách doanh nghiệp đảm bảo an toàn truy xuất:
                    cùng một câu hỏi sẽ phản hồi chính xác theo thẩm quyền và ngữ cảnh của bạn.
                    Tài liệu không được cấp quyền sẽ <strong>không bao giờ đi vào ngữ cảnh LLM</strong>.
                </div>
                <div style="font-size:0.85rem; color:#64748b;">
                    💡 <em>Hãy nhập câu hỏi bên dưới hoặc chọn một câu hỏi mẫu ở thanh bên trái để bắt đầu!</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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

    # Append user question
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": clean_q,
    })

    # Execute backend pipeline
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


def main():
    init_session_state()
    users = load_users()
    selected_user = render_sidebar(users)

    # Hero Banner
    st.markdown(
        """
        <div class="hero-header">
            <h1>🛡️ Appota Knowledge Guard — Multi-Turn Chat & Citations</h1>
            <p>
                Hệ thống hỏi đáp chính sách doanh nghiệp đảm bảo an toàn truy xuất dữ liệu:
                Cùng một câu hỏi sẽ nhận kết quả khác nhau tùy thuộc vào ngữ cảnh người hỏi, 
                trong khi <strong>tài liệu không được phép truy cập không bao giờ đi vào ngữ cảnh LLM</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not selected_user:
        st.error("Không thể tiếp tục vì chưa chọn người dùng.")
        return

    user_id = selected_user["user_id"]

    # Check for pending prompt triggered by preset button in sidebar
    pending_prompt = st.session_state.get("pending_prompt")
    if pending_prompt:
        st.session_state["pending_prompt"] = None
        submit_question(pending_prompt, user_id)

    # Render multi-turn conversation
    render_chat_history()

    # Fixed bottom chat input
    user_input = st.chat_input("Nhập câu hỏi của bạn về chính sách doanh nghiệp (VD: Tôi có bao nhiêu ngày nghỉ phép?)...")
    if user_input:
        submit_question(user_input, user_id)
        st.rerun()


if __name__ == "__main__":
    main()
