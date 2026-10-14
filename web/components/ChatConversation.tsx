'use client';

import React, { useEffect, useRef } from 'react';
import { ChatMessage } from '@/lib/types';
import { AnswerCard } from './AnswerCard';

interface ChatConversationProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSelectPrompt: (prompt: string) => void;
}

export const ChatConversation: React.FC<ChatConversationProps> = ({
  messages,
  isLoading,
  onSelectPrompt,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const quickPrompts = [
    { label: '📅 Nghỉ phép năm', prompt: 'Tôi có bao nhiêu ngày nghỉ phép?' },
    { label: '🏠 Làm việc tại nhà', prompt: 'Tôi được làm việc tại nhà mấy ngày?' },
    { label: '📋 Duyệt phép', prompt: 'Quy trình phê duyệt nghỉ phép của quản lý như thế nào?' },
    { label: '💼 Chính sách lương', prompt: 'Chính sách lương của tôi là gì?' },
  ];

  return (
    <div className="chat-scroll-area">
      <div className="chat-center-container">
        {messages.length === 0 ? (
          <div className="welcome-box">
            <div className="welcome-icon">🛡️</div>
            <h1 className="welcome-title">Appota Knowledge Guard</h1>
            <p className="welcome-desc">
              Hãy hỏi về những chính sách liên quan đến bạn. Mỗi câu trả lời sẽ kèm đoạn trích
              từ tài liệu phù hợp. Khi chưa đủ thông tin, trợ lý sẽ nói rõ.
            </p>
            <div className="welcome-hint">
              💡 <em>Chọn câu hỏi mẫu bên dưới hoặc nhập câu hỏi để bắt đầu:</em>
            </div>

            <div className="quick-chips-row">
              {quickPrompts.map((item, idx) => (
                <button
                  key={idx}
                  className="quick-chip"
                  onClick={() => onSelectPrompt(item.prompt)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <React.Fragment key={msg.id}>
                {msg.role === 'user' ? (
                  <div className="user-msg-row">
                    <div className="user-bubble">{msg.content}</div>
                  </div>
                ) : (
                  <div className="assistant-msg-row">
                    <AnswerCard
                      messageId={msg.id}
                      content={msg.content}
                      status={msg.status}
                      reason={msg.reason}
                      citations={msg.citations}
                    />
                  </div>
                )}
              </React.Fragment>
            ))}

            {isLoading && (
              <div className="assistant-msg-row">
                <div className="assistant-card" style={{ padding: '1rem 1.25rem' }}>
                  <div className="loading-indicator">
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <span className="pulse-dot" />
                      <span className="pulse-dot" />
                      <span className="pulse-dot" />
                    </div>
                    <span>Đang tìm kiếm tài liệu và kiểm tra thẩm quyền...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={bottomRef} style={{ height: 1 }} />
      </div>
    </div>
  );
};
