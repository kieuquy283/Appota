# UI/UX Refactor Plan — Appota Knowledge Guard

## 1. Executive Summary & Product Objective
**Appota Knowledge Guard** is an enterprise internal knowledge chatbot with strict authorization-aware retrieval (RBAC), multi-turn conversation, and provenance citations. 

The objective of this refactor is to transform the application from a "Streamlit demo/dashboard" appearance into a polished, trustworthy enterprise AI assistant (reminiscent of modern enterprise assistants like Glean, ChatGPT Enterprise, and Microsoft Copilot) while:
1. **Strictly preserving** all backend retrieval, RBAC/governance logic, citation bindings, and session security semantics.
2. **Preserving 100% compatibility** with existing unit tests (`test_core.py` and `test_chat_citation.py`).
3. Resolving critical UX issues (oversized hero, giant green answer cards, chat input obscuring content, sidebar metadata bloat, inconsistent color palette).

---

## 2. Current Architecture & File Breakdown

### Backend & Business Logic (DO NOT MODIFY)
- `src/governance.py`: RBAC rules (`can_read`, `is_applicable`), version governance (`current_versions`), authority resolution (`resolve_authority`).
- `src/retrieval.py`: Intent detection (`detect_intent`), dense/lexical cosine similarity retrieval (`retrieve`).
- `src/llm.py`: Offline extractive generation (`_offline_answer`) and LLM API generation (`generate`), strict citation alignment with retrieved sources.
- `src/models.py`: Data models (`Citation`, `AnswerResult`, `Status`).
- `src/service.py`: Service orchestrator (`answer_question`, `list_demo_users`).
- `src/store.py`: Seed data loader and user lookup.
- `data/seed.json`: Synthetic organizations, users (U01–U06), and documents.

### Frontend (TO REFACTOR & MODULARIZE)
- `app.py`: Current monolithic entrypoint containing CSS injection, session management, sidebar rendering, message rendering, citation cards, audit trace expander, and chat loop.
- Existing tests import `app` directly and test:
  - `app.submit_question(question, user_id)`
  - `app.reset_conversation()`
  - `app.format_user_label(user)`
  - `app.render_sidebar(users)`
  - `app.render_status(message)`
  - `app.st.session_state["chat_messages"]`

To ensure zero breakage of test imports while achieving high modularity, `app.py` will remain the stable API and delegate presentation to modular UI modules in `src/ui/`:
- `src/ui/theme.py`: Enterprise dark theme CSS tokens, typography, layout containers, chat bubble styles, citation cards, and composer styling.
- `src/ui/components.py`: Modular rendering functions for top navigation bar, compact profile badge card, chat bubbles, verified status badges, citations with metadata badges, and audit trace.

---

## 3. Problems Found in Current Implementation

1. **Oversized Hero Block (`.hero-header`)**:
   - Consumes ~160px+ of prime vertical space at the top of the main window with huge text and boilerplate descriptions.
2. **Giant Green Alert Answer Box (`.status-banner.status-answer`)**:
   - The entire assistant response is styled inside a neon-green alert box (`#f0fdf4` / `#86efac`), making it look like a success alert notification rather than an enterprise assistant answer.
3. **Chat Input Overlap & Content Hiding**:
   - Insufficient bottom padding (`~0.5rem`) on the chat container causes citations and the audit trace expander to be partially clipped or hidden behind the persistent `st.chat_input` composer.
4. **Sidebar Profile Card Bloat**:
   - Renders 5 separate stacked rows for Company, Department, Team, Role, Employment Type in large text, dominating the sidebar and pushing conversation controls and evaluation cases down.
5. **Lack of Proper Chat Hierarchy**:
   - User messages render as plain full-width bold text inside default Streamlit boxes.
   - Assistant answers lack clear distinction between status metadata, verified badge, message body, and citations.
6. **Clashing & Saturated Color Palette**:
   - Interface mixes navy (`#0f172a`), neon green (`#22c55e`), bright pastel blue (`#e0f2fe`), deep blue (`#3b82f6`), amber (`#f59e0b`), pink (`#fdf2f8`), and gray.
7. **No Multi-Conversation Support in Sidebar**:
   - Only a single ephemeral list exists in session state; clicking "New Chat" wipes history without a clean conversation thread list.
8. **Security Communication Nuance**:
   - Need clear "Demo Identity" vs "Backend Authentication" notice so evaluators understand identity cannot be forged in production.
   - Need verified status badge clearly explaining that answers are grounded in authorized access scope without fabricating LLM guarantees.

---

## 4. Refactor Sequence & Priority

### Phase P0 (Critical UX & Layout Foundations)
1. **Establish Enterprise Dark / Restrained Palette Design System**:
   - Background: `#0E1117`
   - Surface: `#161B22`
   - Secondary Surface / Chat Bubbles: `#1D2430` (User) & `#161B22` (Assistant)
   - Accent / Brand: `#3B82F6` / `#2563EB` (Appota subtle blue)
   - Border: `rgba(255, 255, 255, 0.08)`
   - Verified Badge: `#10B981` (Green reserved strictly for small verified chip)
   - Access Denied / Danger: `#EF4444` (Red reserved strictly for denial/errors)
   - Text Primary: `#F3F4F6` / `#FFFFFF`, Secondary: `#9CA3AF`
2. **Replace Large Hero with Compact Top Navigation Bar**:
   - Compact header (64–72px) with shield icon, `Knowledge Guard`, subtle tagline `Secure enterprise knowledge`, and current active user avatar pill.
3. **Main Content Width & Padding**:
   - Constrain main conversation container to `max-width: 1040px`, centered, with 120px bottom padding to prevent `st.chat_input` from overlapping content.
4. **Chat Bubble Redesign**:
   - **User message**: Right-aligned, compact muted bubble (`#1E293B` or `#1D2430` with subtle border), no red color.
   - **Assistant message**: Left-aligned neutral surface (`#161B22`), verified badge (`✓ Verified · Authorized Scope`), neutral clean typography.
5. **Citations Redesign**:
   - Compact citation cards directly under assistant message with index badge `[1]`, document title, authority badge, version, section, and metadata chips.
   - Clear visual link to inline markers `[1]`.
6. **Access Denied / ABSTAIN UI**:
   - Calm, non-alarmist security notification stating access limitations without leaking unauthorized document metadata.

### Phase P1 (Sidebar, Profile & Identity Polish)
7. **Sidebar Modernization**:
   - Top: App brand + `[ + Cuộc trò chuyện mới ]`.
   - Conversations thread list (Session-based history with time grouping `Hôm nay`).
   - Demo Identity section: Compact user badge with chips (`[AlphaPay]`, `[Backend]`, `[L3 Full-time]`), clear label `Demo identity (backend authenticated)`.
   - Evaluation cases with clean interactive buttons.
8. **Verification & Audit Trace Polish**:
   - Retain the deep audit pipeline in a sleek, non-distracting collapsible accordion.

### Phase P2 (Interactive Micro-Polish)
9. **Quick Action Prompt Chips**:
   - Subtle chips above composer (e.g. `[Nghỉ phép năm]`, `[Chính sách WFH]`, `[Quy trình quản lý]`).
10. **Responsive Layout Check**:
    - Wrap chips and citation metadata gracefully on narrow screens.

---

## 5. Files to Modify and Not to Modify

### Files to Modify / Create:
- `app.py`: Keep public API intact for unit tests; delegate styling and UI components to modular helpers; integrate new navigation, sidebar, chat bubbles, citations, and conversation history.
- `src/ui/__init__.py`: Package init.
- `src/ui/theme.py`: Design tokens, CSS injection, layout styling.
- `src/ui/components.py`: Component renderers (header, profile card, conversation history, chat bubbles, citations, audit trace).
- `docs/ui_refactor_summary.md`: Final summary documentation.

### Files NOT to Modify:
- `src/governance.py` (Security & RBAC boundaries)
- `src/retrieval.py` (Deterministic & semantic retrieval)
- `src/llm.py` (LLM & extractive citation generation)
- `src/models.py` (Data schemas)
- `src/service.py` (Core pipeline orchestration)
- `src/store.py` (Data loader)
- `data/seed.json` (Seed dataset)
- `tests/test_core.py` (Must pass without changes)
- `tests/test_chat_citation.py` (Must pass without changes)

---

## 6. Risk Areas & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| **Unit tests fail due to missing `app.py` symbols** | Retain all existing functions in `app.py` (`submit_question`, `reset_conversation`, `format_user_label`, `render_sidebar`, `render_status`, `render_citations`, `render_audit_trace`, `st.session_state["chat_messages"]`). |
| **User context leak across sessions** | Retain automatic conversation wipe when `current_user_id` changes. |
| **Sensitive metadata leak on ABSTAIN** | Ensure ABSTAIN displays generic, safe reason text without disclosing unauthorized document titles or internal secrets. |
| **Streamlit chat_input CSS obstruction** | Add dedicated `.chat-bottom-spacer` with height `120px` to guarantee zero overlap. |
| **Brittle CSS breakage** | Use stable HTML containers rendered via `unsafe_allow_html=True` with custom scoped class names (`kg-...`), rather than relying on dynamic Streamlit internal hash classes. |

---

## 7. Acceptance Criteria
1. `python -m unittest discover tests` passes with 0 failures and 0 errors.
2. Large hero is completely removed; compact top bar is present.
3. Giant green answer box is replaced with neutral, modern assistant message + compact `✓ Verified` badge.
4. User messages are right-aligned bubbles in muted dark surface.
5. Citations are clearly rendered with index badges and metadata chips directly below the relevant assistant turn.
6. Bottom padding prevents `chat_input` from overlapping citations or audit trace.
7. Sidebar displays compact profile chips and session conversation threads.
8. Evaluation buttons cleanly populate prompt and execute queries.
9. No backend or authorization semantics modified.
