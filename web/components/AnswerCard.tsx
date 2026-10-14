'use client';

import React from 'react';
import { AnswerStatus, Citation } from '@/lib/types';
import { CitationCard } from './CitationCard';

interface AnswerCardProps {
  content: string;
  status?: AnswerStatus;
  reason?: string | null;
  citations?: Citation[];
  messageId: string;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({
  content,
  status = 'ANSWER',
  reason,
  citations = [],
  messageId,
}) => {
  let badgeClass = 'badge-verified';
  let badgeText = '✓ Đã tìm thấy thông tin';
  let subtext = 'Câu trả lời dựa trên tài liệu bạn có thể xem.';
  let displayAnswer = content;

  if (status === 'ABSTAIN') {
    badgeClass = 'badge-abstain';
    badgeText = 'Chưa đủ thông tin';
    subtext =
      reason === 'missing_evidence'
        ? 'Tài liệu hiện có chưa đủ thông tin để trả lời câu hỏi này.'
        : 'Chưa có thông tin phù hợp để trả lời câu hỏi này.';
    if (!displayAnswer || displayAnswer === content) {
      displayAnswer = 'Mình chưa tìm thấy đủ thông tin phù hợp để trả lời câu hỏi này.';
    }
  } else if (status === 'CONFLICT') {
    badgeClass = 'badge-conflict';
    badgeText = 'Thông tin chưa thống nhất';
    subtext = 'Các tài liệu hiện có đưa ra thông tin khác nhau. Vui lòng hỏi bộ phận phụ trách.';
    if (!displayAnswer || displayAnswer === content) {
      displayAnswer = 'Các tài liệu hiện có đưa ra thông tin khác nhau. Vui lòng hỏi bộ phận phụ trách để xác nhận.';
    }
  } else if (status === 'ERROR') {
    badgeClass = 'badge-error';
    badgeText = 'Tạm thời chưa trả lời được';
    subtext = 'Vui lòng thử lại sau.';
  }

  return (
    <div className="assistant-card" id={`assistant-card-${messageId}`}>
      <div className="assistant-header">
        <div className="assistant-identity">
          <span>🛡️ Trợ lý Chính sách</span>
        </div>
        <div className={`verified-badge ${badgeClass}`}>
          <span>{badgeText}</span>
        </div>
      </div>

      <div className="answer-body">{displayAnswer}</div>

      <div className="security-subtext">
        <span>{subtext}</span>
      </div>

      {citations.length > 0 && (
        <div className="citations-section">
          <div className="citations-header">📚 Đoạn trích từ tài liệu</div>
          <div className="citation-cards-list">
            {citations.map((c, idx) => (
              <CitationCard key={`${messageId}-cit-${idx}`} citation={c} index={idx + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
