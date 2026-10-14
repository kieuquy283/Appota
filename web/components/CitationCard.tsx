'use client';

import React from 'react';
import { Citation } from '@/lib/types';

interface CitationCardProps {
  citation: Citation;
  index: number;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation, index }) => {
  return (
    <div className="citation-card" id={`citation-card-${index}`}>
      <div className="citation-badge">[{index}]</div>
      <div className="citation-body">
        <div className="citation-title">{citation.title}</div>
        {citation.section && (
          <div className="citation-meta">
            <span>Phần: {citation.section}</span>
          </div>
        )}
        {citation.excerpt && (
          <blockquote className="citation-excerpt">
            “{citation.excerpt}”
          </blockquote>
        )}
      </div>
    </div>
  );
};
