// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  role?: string;  // "user" | "admin"
  is_active?: boolean;
  created_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 学习路线类型
export interface LearningPath {
  id: number;
  user_id: number;
  position: string;
  job_description?: string;
  generated_content?: any;
  created_at: string;
}

export interface LearningPathCreate {
  position: string;
  job_description: string;
  content_types?: string[];
}

// 资源类型
export interface Course {
  id: string;
  title: string;
  provider: string;
  url: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  rating: number;
  description: string;
  tags: string[];
  relevance_score?: number;
}

export interface Book {
  id: string;
  title: string;
  author: string;
  url: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  rating: number;
  description: string;
  tags: string[];
  relevance_score?: number;
}

export interface Certification {
  id: string;
  title: string;
  provider: string;
  url: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  rating: number;
  description: string;
  tags: string[];
  relevance_score?: number;
}

// 内容生成请求
export interface ContentGenerationRequest {
  content_type: string;
}

export interface ContentGenerationResponse {
  success: boolean;
  message: string;
  content: any;
  from_cache: boolean;
}

// 学习进度类型
export interface LearningProgress {
  id: number;
  user_id: number;
  learning_path_id: number;
  content_id: string;
  content_type: string;
  mastered: boolean;
  needs_review: boolean;
}

export interface ProgressUpdate {
  learning_path_id: number;
  content_id: string;
  content_type: string;
  mastered?: boolean;
  needs_review?: boolean;
}

export interface ProgressStats {
  total_items: number;
  mastered_items: number;
  review_items: number;
  mastery_rate: number;
}

// 笔记类型
export interface Note {
  id: number;
  user_id: number;
  title?: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at?: string;
}

export interface NoteCreate {
  title?: string;
  content: string;
  tags?: string[];
}

export interface NoteUpdate {
  title?: string;
  content?: string;
  tags?: string[];
}

// 聊天类型
export interface ChatMessage {
  role: string;
  message: string;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  context?: string;
}

