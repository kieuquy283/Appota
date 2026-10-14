export interface DemoUser {
  user_id: string;
  name: string;
  company: string;
  department: string;
  team?: string | null;
  role: string;
  employment_type: string;
}

export interface Citation {
  title: string;
  section?: string | null;
  excerpt?: string | null;
}

export type AnswerStatus = 'ANSWER' | 'ABSTAIN' | 'CONFLICT' | 'ERROR';

export interface AnswerResponse {
  status: AnswerStatus;
  answer: string;
  reason?: string | null;
  citations: Citation[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status?: AnswerStatus;
  reason?: string | null;
  citations?: Citation[];
  timestamp?: number;
}
