'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { DemoUser, ChatMessage, AnswerResponse } from '@/lib/types';
import { UserSelector } from '@/components/UserSelector';
import { ChatConversation } from '@/components/ChatConversation';
import { QuestionComposer } from '@/components/QuestionComposer';

export default function ChatPage() {
  const [users, setUsers] = useState<DemoUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<DemoUser | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [historyTitles, setHistoryTitles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingUsers, setLoadingUsers] = useState<boolean>(true);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);

  // Fetch demo users on load
  useEffect(() => {
    async function fetchUsers() {
      try {
        const res = await fetch('/api/users');
        if (res.ok) {
          const data: DemoUser[] = await res.json();
          setUsers(data);
          if (data.length > 0) {
            setSelectedUser(data[0]);
          }
        }
      } catch (err) {
        console.error('Failed to load demo users:', err);
      } finally {
        setLoadingUsers(false);
      }
    }
    fetchUsers();
  }, []);

  // Reset conversation
  const handleResetChat = useCallback(() => {
    setMessages([]);
    setHistoryTitles([]);
  }, []);

  // Handle user change - strictly clears conversation to prevent context leakage
  const handleSelectUser = useCallback((user: DemoUser) => {
    setSelectedUser(user);
    setMessages([]);
    setHistoryTitles([]);
  }, []);

  // Send question
  const handleSendMessage = useCallback(
    async (questionText: string) => {
      const clean = questionText.trim();
      if (!clean || !selectedUser || isLoading) return;

      // Close mobile sidebar if open
      setMobileSidebarOpen(false);

      // Track short title for current session history
      const shortTitle = clean.length <= 32 ? clean : `${clean.slice(0, 30)}...`;
      setHistoryTitles((prev) => (prev.includes(shortTitle) ? prev : [...prev, shortTitle]));

      const userMsgId = `user-${Date.now()}`;
      const assistantMsgId = `assistant-${Date.now()}`;

      // Append user query
      setMessages((prev) => [
        ...prev,
        {
          id: userMsgId,
          role: 'user',
          content: clean,
          timestamp: Date.now(),
        },
      ]);

      setIsLoading(true);

      try {
        const res = await fetch('/api/answer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: selectedUser.user_id,
            question: clean,
          }),
        });

        if (res.ok) {
          const data: AnswerResponse = await res.json();
          setMessages((prev) => [
            ...prev,
            {
              id: assistantMsgId,
              role: 'assistant',
              content: data.answer,
              status: data.status,
              reason: data.reason,
              citations: data.citations,
              timestamp: Date.now(),
            },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            {
              id: assistantMsgId,
              role: 'assistant',
              content: 'Hiện chưa thể trả lời câu hỏi này. Vui lòng thử lại sau.',
              status: 'ERROR',
              reason: 'service_error',
              citations: [],
              timestamp: Date.now(),
            },
          ]);
        }
      } catch (error) {
        console.error('Request failed:', error);
        setMessages((prev) => [
          ...prev,
          {
            id: assistantMsgId,
            role: 'assistant',
            content: 'Không thể kết nối đến máy chủ xử lý. Vui lòng thử lại sau.',
            status: 'ERROR',
            reason: 'network_error',
            citations: [],
            timestamp: Date.now(),
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [selectedUser, isLoading]
  );

  const presetQuestions = [
    { title: 'Tôi có bao nhiêu ngày nghỉ phép?', query: 'Tôi có bao nhiêu ngày nghỉ phép?' },
    { title: 'Tôi được làm việc tại nhà mấy ngày?', query: 'Tôi được làm việc tại nhà mấy ngày?' },
    { title: 'Tôi có được làm việc tại nhà thứ Sáu?', query: 'Tôi có được làm việc tại nhà thứ Sáu không?' },
    { title: 'Chính sách lương của tôi là gì?', query: 'Chính sách lương của tôi là gì?' },
    { title: 'Ai duyệt đơn nghỉ phép?', query: 'Quy trình phê duyệt nghỉ phép của quản lý như thế nào?' },
  ];

  return (
    <div className="app-container">
      {/* Left Sidebar */}
      <aside className={`sidebar ${mobileSidebarOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-header">
          <div className="brand-row">
            <div className="brand-icon">🛡️</div>
            <div>
              <div className="brand-title">Knowledge Guard</div>
              <div className="brand-subtitle">Trợ lý tra cứu chính sách</div>
            </div>
          </div>

          <button
            id="new-chat-btn"
            className="new-chat-btn"
            onClick={handleResetChat}
            type="button"
          >
            <span>➕</span>
            <span>Cuộc trò chuyện mới</span>
          </button>
        </div>

        <div className="sidebar-content">
          {historyTitles.length > 0 && (
            <div>
              <div className="sidebar-section-title">Hội thoại phiên này</div>
              {historyTitles.slice(-5).map((t, idx) => (
                <div key={idx} className="history-item active">
                  💬 {t}
                </div>
              ))}
            </div>
          )}

          <div>
            <div className="sidebar-section-title">Người đang hỏi</div>
            {loadingUsers ? (
              <div style={{ fontSize: '0.82rem', color: '#9CA3AF' }}>Đang tải danh sách...</div>
            ) : (
              <UserSelector
                users={users}
                selectedUser={selectedUser}
                onSelectUser={handleSelectUser}
              />
            )}
          </div>

          <div>
            <div className="sidebar-section-title">Câu hỏi gợi ý</div>
            <div className="preset-btn-list">
              {presetQuestions.map((p, idx) => (
                <button
                  key={idx}
                  className="preset-btn"
                  onClick={() => handleSendMessage(p.query)}
                  disabled={isLoading || !selectedUser}
                >
                  {p.title}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          Bản thử nghiệm dùng dữ liệu giả lập.
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="main-wrapper">
        <header className="main-topbar">
          <div className="topbar-left">
            <button
              className="mobile-menu-toggle"
              onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
              aria-label="Mở menu"
            >
              ☰
            </button>
            <div>
              <div className="topbar-title">Knowledge Guard</div>
              <div className="topbar-subtitle">Hỏi đáp chính sách dành cho bạn</div>
            </div>
          </div>

          {selectedUser && (
            <div className="profile-pill">
              <span className="status-indicator" />
              <span>
                <strong>{selectedUser.name}</strong> · {selectedUser.company}
              </span>
            </div>
          )}
        </header>

        <ChatConversation
          messages={messages}
          isLoading={isLoading}
          onSelectPrompt={handleSendMessage}
        />

        <QuestionComposer
          onSend={handleSendMessage}
          isLoading={isLoading}
          disabled={!selectedUser}
        />
      </main>
    </div>
  );
}
