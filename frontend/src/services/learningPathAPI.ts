import api from './api';

export interface LearningPath {
  id: number;
  position: string;
  description?: string;
  created_at?: string;
}

export interface LearningPathListResponse {
  items: LearningPath[];
  total: number;
}

export const learningPathAPI = {
  // 获取学习路径列表
  async list(): Promise<LearningPathListResponse> {
    const response = await api.get('/learning-paths');
    return response.data;
  },

  // 获取单个学习路径详情
  async get(id: number) {
    const response = await api.get(`/learning-paths/${id}`);
    return response.data;
  }
};

