'use client';

import React, { useState, useRef, useEffect } from 'react';

interface QuestionComposerProps {
  onSend: (question: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export const QuestionComposer: React.FC<QuestionComposerProps> = ({
  onSend,
  isLoading,
  disabled = false,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const clean = input.trim();
    if (!clean || isLoading || disabled) return;
    onSend(clean);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-adjust height
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  return (
    <div className="composer-area">
      <div className="composer-center">
        <form className="composer-form" onSubmit={handleSubmit}>
          <textarea
            ref={textareaRef}
            id="chat-input-textarea"
            className="composer-textarea"
            placeholder="Hỏi về chính sách dành cho bạn, ví dụ: Tôi có bao nhiêu ngày nghỉ phép?"
            rows={1}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={isLoading || disabled}
          />
          <button
            type="submit"
            id="chat-send-button"
            className="send-btn"
            disabled={!input.trim() || isLoading || disabled}
            aria-label="Gửi câu hỏi"
          >
            {isLoading ? (
              <span className="pulse-dot" style={{ width: 6, height: 6 }} />
            ) : (
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </form>
        <div className="composer-caption">
          Dữ liệu thử nghiệm nội bộ · Quyền truy cập được kiểm soát tự động theo bối cảnh người hỏi
        </div>
      </div>
    </div>
  );
};
