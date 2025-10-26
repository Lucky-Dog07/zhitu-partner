export enum DifficultyLevel {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard'
}

export enum QuestionStatus {
  NOT_SEEN = 'not_seen',
  MASTERED = 'mastered',
  NOT_MASTERED = 'not_mastered'
}

export interface InterviewQuestion {
  id: number;
  learning_path_id: number;
  question: string;
  answer: string;
  category: string | null;
  difficulty: DifficultyLevel;
  knowledge_points: string[] | null;
  created_at: string;
  user_status: QuestionStatus | null;
  review_count: number;
  last_reviewed_at: string | null;
}

export interface InterviewStatistics {
  total: number;
  not_seen: number;
  mastered: number;
  not_mastered: number;
  mastery_rate: number;
  weak_categories: Array<{ category: string; count: number }>;
  weak_knowledge_points: Array<{ point: string; count: number }>;
}

export interface InterviewQuestionsListResponse {
  questions: InterviewQuestion[];
  statistics: InterviewStatistics;
  total: number;
  has_more: boolean;
}

export interface GenerateQuestionsRequest {
  learning_path_id: number;
  count?: number;
  category?: string;
  based_on_weak_points?: boolean;
}

export interface GenerateQuestionsResponse {
  success: boolean;
  message: string;
  questions: InterviewQuestion[];
  count: number;
}

export interface UpdateStatusRequest {
  question_id: number;
  status: QuestionStatus;
}

