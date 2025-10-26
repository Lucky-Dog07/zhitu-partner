import api from './api';

export interface StartSessionRequest {
  learning_path_id: number;
}

export interface ContinueConversationRequest {
  session_id: number;
  answer: string;
}

export interface EndSessionRequest {
  session_id: number;
}

export interface Message {
  role: 'interviewer' | 'candidate' | 'system';
  content: string;
  timestamp: string;
}

export interface Evaluation {
  overall_score: number;
  dimension_scores: {
    technical_depth: number;
    expression: number;
    problem_solving: number;
    experience: number;
  };
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  summary: string;
}

export interface InterviewSession {
  id: number;
  position: string;
  status: string;
  conversation: Message[];
  evaluation?: Evaluation;
  duration_minutes: number;
}

export const interviewSimulatorAPI = {
  async start(learning_path_id: number) {
    const response = await api.post('/interview-simulator/start', {
      learning_path_id
    });
    return response.data;
  },

  async continue(session_id: number, answer: string) {
    const response = await api.post('/interview-simulator/continue', {
      session_id,
      answer
    });
    return response.data;
  },

  async end(session_id: number) {
    const response = await api.post('/interview-simulator/end', {
      session_id
    });
    return response.data;
  },

  async getHistory(limit: number = 10) {
    const response = await api.get(`/interview-simulator/history?limit=${limit}`);
    return response.data;
  },

  async getSession(session_id: number): Promise<InterviewSession> {
    const response = await api.get(`/interview-simulator/session/${session_id}`);
    return response.data;
  }
};

