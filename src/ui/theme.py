"""Enterprise Design System and CSS for Appota Knowledge Guard."""

ENTERPRISE_THEME_CSS = """
<style>
/* Enterprise Font and Core Reset */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --kg-bg: #0E1117;
    --kg-surface: #161B22;
    --kg-surface-elevated: #1D2430;
    --kg-surface-hover: #212936;
    --kg-border: rgba(255, 255, 255, 0.08);
    --kg-border-subtle: rgba(255, 255, 255, 0.04);
    --kg-primary: #3B82F6;
    --kg-primary-glow: rgba(59, 130, 246, 0.15);
    --kg-text-primary: #F3F4F6;
    --kg-text-secondary: #9CA3AF;
    --kg-text-muted: #6B7280;
    --kg-success: #10B981;
    --kg-success-bg: rgba(16, 185, 129, 0.12);
    --kg-warning: #F59E0B;
    --kg-warning-bg: rgba(245, 158, 11, 0.12);
    --kg-danger: #EF4444;
    --kg-danger-bg: rgba(239, 68, 68, 0.12);
    --kg-radius-sm: 6px;
    --kg-radius-md: 10px;
    --kg-radius-lg: 14px;
}

/* Base typography */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--kg-text-primary);
}

/* Center main content & limit width to ~1060px */
.block-container {
    max-width: 1060px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 2rem !important;
    margin: 0 auto !important;
}

/* Compact Top Navigation Bar (replaces giant hero) */
.kg-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.25rem;
    background: var(--kg-surface);
    border: 1px solid var(--kg-border);
    border-radius: var(--kg-radius-md);
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.kg-brand-lockup {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.kg-brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: var(--kg-primary-glow);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: var(--kg-radius-sm);
    font-size: 1.2rem;
}

.kg-brand-text {
    display: flex;
    flex-direction: column;
}

.kg-brand-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.01em;
    line-height: 1.2;
}

.kg-brand-subtitle {
    font-size: 0.78rem;
    color: var(--kg-text-secondary);
    letter-spacing: 0.01em;
}

.kg-profile-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.85rem;
    background: var(--kg-surface-elevated);
    border: 1px solid var(--kg-border);
    border-radius: 9999px;
    font-size: 0.82rem;
    color: var(--kg-text-primary);
}

.kg-status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--kg-success);
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0A0D12 !important;
    border-right: 1px solid var(--kg-border) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

.kg-sidebar-section-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--kg-text-muted);
    margin: 1.2rem 0 0.5rem 0;
}

/* Compact User Card */
.kg-user-card {
    background: var(--kg-surface);
    border: 1px solid var(--kg-border);
    border-radius: var(--kg-radius-md);
    padding: 0.85rem 1rem;
    margin-top: 0.4rem;
    margin-bottom: 0.6rem;
}

.kg-user-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}

.kg-user-name {
    font-weight: 700;
    font-size: 0.95rem;
    color: #FFFFFF;
}

.kg-user-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--kg-text-muted);
    background: rgba(255, 255, 255, 0.05);
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
}

.kg-user-role-line {
    font-size: 0.82rem;
    color: var(--kg-text-secondary);
    margin-bottom: 0.55rem;
}

.kg-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}

.kg-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.18rem 0.5rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.kg-chip-company {
    background: rgba(59, 130, 246, 0.15);
    color: #93C5FD;
    border: 1px solid rgba(59, 130, 246, 0.25);
}

.kg-chip-level {
    background: rgba(255, 255, 255, 0.06);
    color: var(--kg-text-primary);
    border: 1px solid var(--kg-border);
}

.kg-chip-type {
    background: rgba(16, 185, 129, 0.12);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Chat History List */
.kg-history-group {
    margin-bottom: 0.85rem;
}

.kg-history-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--kg-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
}

.kg-history-item {
    padding: 0.45rem 0.65rem;
    border-radius: var(--kg-radius-sm);
    font-size: 0.82rem;
    color: var(--kg-text-secondary);
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
    border-left: 2px solid transparent;
}

.kg-history-item:hover {
    background: var(--kg-surface-hover);
    color: var(--kg-text-primary);
}

.kg-history-item.active {
    background: var(--kg-surface-elevated);
    color: #FFFFFF;
    border-left: 2px solid var(--kg-primary);
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 0.85rem 0 !important;
    gap: 0.9rem !important;
}

/* User Message Bubble — Sleek, right-aligned, muted dark surface */
.kg-user-msg-container {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    margin: 0.4rem 0;
}

.kg-user-bubble {
    background: var(--kg-surface-elevated);
    border: 1px solid var(--kg-border);
    border-radius: 14px 14px 2px 14px;
    padding: 0.75rem 1.15rem;
    max-width: 78%;
    color: #F8FAFC;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
    word-break: break-word;
}

/* Assistant Message Surface — Neutral enterprise look (NO GIANT GREEN CARD) */
.kg-assistant-card {
    background: var(--kg-surface);
    border: 1px solid var(--kg-border);
    border-radius: var(--kg-radius-lg);
    padding: 1.15rem 1.35rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    margin: 0.4rem 0 0.85rem 0;
    width: 100%;
}

.kg-assistant-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.85rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--kg-border-subtle);
}

.kg-assistant-identity {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #FFFFFF;
}

/* Verified Badge (Reserved strictly for authorized source backing) */
.kg-verified-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.kg-badge-verified {
    background: var(--kg-success-bg);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.25);
}

.kg-badge-abstain {
    background: var(--kg-warning-bg);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.25);
}

.kg-badge-conflict {
    background: var(--kg-danger-bg);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

.kg-badge-error {
    background: var(--kg-danger-bg);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

/* Answer Body */
.kg-answer-body {
    font-size: 0.98rem;
    line-height: 1.6;
    color: var(--kg-text-primary);
    margin-bottom: 0.65rem;
}

.kg-answer-body strong {
    color: #FFFFFF;
}

.kg-security-subtext {
    font-size: 0.8rem;
    color: var(--kg-text-secondary);
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-top: 0.4rem;
}

/* Citations Section */
.kg-citations-container {
    margin-top: 1rem;
    padding-top: 0.85rem;
    border-top: 1px solid var(--kg-border-subtle);
}

.kg-citations-header {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--kg-text-secondary);
    margin-bottom: 0.65rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.kg-citation-cards {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.kg-citation-card {
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    background: var(--kg-surface-elevated);
    border: 1px solid var(--kg-border);
    border-radius: var(--kg-radius-md);
    padding: 0.75rem 1rem;
    transition: all 0.2s ease;
}

.kg-citation-card:hover {
    background: var(--kg-surface-hover);
    border-color: rgba(59, 130, 246, 0.35);
}

.kg-citation-num {
    background: var(--kg-primary);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.75rem;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    flex-shrink: 0;
    margin-top: 0.1rem;
}

.kg-citation-main {
    flex: 1;
    min-width: 0;
}

.kg-citation-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1.35;
    word-break: break-word;
}

.kg-citation-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem;
    margin-top: 0.35rem;
    font-size: 0.75rem;
    color: var(--kg-text-secondary);
}

.kg-citation-code {
    font-family: 'JetBrains Mono', monospace;
    background: rgba(255, 255, 255, 0.06);
    color: #93C5FD;
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
}

.kg-citation-excerpt {
    margin: 0.7rem 0 0;
    padding: 0.55rem 0.8rem;
    border-left: 3px solid var(--kg-primary);
    background: rgba(59, 130, 246, 0.08);
    border-radius: 0 6px 6px 0;
    color: var(--kg-text-primary);
    font-size: 0.84rem;
    line-height: 1.55;
    white-space: pre-line;
}

/* Quick Actions Chips Container */
.kg-quick-actions-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

/* Bottom Spacer to ensure composer NEVER obscures citations */
.kg-bottom-spacer {
    height: 120px;
    width: 100%;
}

/* Welcome Empty State */
.kg-welcome-box {
    background: var(--kg-surface);
    border: 1px solid var(--kg-border);
    border-radius: var(--kg-radius-lg);
    padding: 2.25rem 2rem;
    text-align: center;
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.kg-welcome-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
}

.kg-welcome-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.5rem;
}

.kg-welcome-desc {
    font-size: 0.92rem;
    color: var(--kg-text-secondary);
    max-width: 620px;
    margin: 0 auto 1.5rem auto;
    line-height: 1.6;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .kg-topbar {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
    }
    .kg-user-bubble {
        max-width: 90%;
    }
    .kg-citation-card {
        flex-direction: column;
        gap: 0.4rem;
    }
}
</style>
"""
