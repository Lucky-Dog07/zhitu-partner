import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * AI 笔记生成选项
 */
export interface NoteGenerationOptions {
  include_weak_points?: boolean;
  include_study_plan?: boolean;
  include_interview_tips?: boolean;
  custom_requirements?: string;
}

/**
 * AI 笔记生成请求
 */
export interface NoteGenerationRequest {
  source_type: 'mistakes' | 'interview' | 'learning_path';
  source_id: number; // learning_path_id
  options?: NoteGenerationOptions;
}

/**
 * 笔记草稿元数据
 */
export interface NoteDraftMetadata {
  source: string;
  learning_path_id: number;
  position: string;
  mistakes_count: number;
  generated_at: string;
}

/**
 * AI 笔记草稿响应
 */
export interface NoteDraft {
  title: string;
  content: string;
  suggested_notebook: string;
  metadata: NoteDraftMetadata;
}

export const aiNoteAPI = {
  /**
   * 生成 AI 笔记草稿
   */
  async generateDraft(request: NoteGenerationRequest): Promise<NoteDraft> {
    const response = await api.post<NoteDraft>('/ai-notes/generate-draft', request);
    return response.data;
  }
};

