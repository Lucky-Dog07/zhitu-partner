import axios from 'axios';
import type {
  AuthResponse,
  LoginCredentials,
  RegisterData,
  LearningPath,
  LearningPathCreate,
  ProgressUpdate,
  ProgressStats,
  Note,
  NoteCreate,
  NoteUpdate,
  ChatMessage,
  ChatRequest
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加token
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

// 响应拦截器 - 处理401错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const { data } = await api.post<AuthResponse>('/auth/login', credentials);
    return data;
  },
  
  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const { data } = await api.post<AuthResponse>('/auth/register', userData);
    return data;
  }
};

// 学习路线API
export const learningPathAPI = {
  generate: async (pathData: LearningPathCreate): Promise<LearningPath> => {
    const { data } = await api.post<LearningPath>('/learning-paths/generate', pathData);
    return data;
  },
  
  list: async (skip = 0, limit = 20): Promise<{ total: number; items: LearningPath[] }> => {
    const { data } = await api.get('/learning-paths', { params: { skip, limit } });
    return data;
  },
  
  get: async (id: number): Promise<LearningPath> => {
    const { data } = await api.get<LearningPath>(`/learning-paths/${id}`);
    return data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/learning-paths/${id}`);
  },
  
  generateContent: async (pathId: number, contentType: string): Promise<any> => {
    const { data } = await api.post(`/learning-paths/${pathId}/generate-content`, {
      content_type: contentType
    });
    return data;
  }
};

// 学习进度API
export const progressAPI = {
  mark: async (progressData: ProgressUpdate): Promise<void> => {
    await api.post('/progress/mark', progressData);
  },
  
  stats: async (learningPathId?: number): Promise<ProgressStats> => {
    const { data } = await api.get<ProgressStats>('/progress/stats', {
      params: learningPathId ? { learning_path_id: learningPathId } : {}
    });
    return data;
  }
};

// 笔记API
export const noteAPI = {
  create: async (noteData: NoteCreate): Promise<Note> => {
    const { data} = await api.post<Note>('/notes', noteData);
    return data;
  },
  
  list: async (skip = 0, limit = 50, tag?: string): Promise<Note[]> => {
    const { data } = await api.get<Note[]>('/notes', {
      params: { skip, limit, ...(tag && { tag }) }
    });
    return data;
  },
  
  get: async (id: number): Promise<Note> => {
    const { data } = await api.get<Note>(`/notes/${id}`);
    return data;
  },
  
  update: async (id: number, noteData: NoteUpdate): Promise<Note> => {
    const { data } = await api.put<Note>(`/notes/${id}`, noteData);
    return data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/notes/${id}`);
  }
};

// 聊天API
export const chatAPI = {
  send: async (chatData: ChatRequest): Promise<ChatMessage> => {
    const { data } = await api.post<ChatMessage>('/chat', chatData);
    return data;
  },
  
  history: async (skip = 0, limit = 50): Promise<ChatMessage[]> => {
    const { data } = await api.get<ChatMessage[]>('/chat/history', {
      params: { skip, limit }
    });
    return data;
  },
  
  clear: async (): Promise<void> => {
    await api.delete('/chat/history');
  }
};

export default api;

