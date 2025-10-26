import axios from 'axios';
import type {
  InterviewQuestionsListResponse,
  GenerateQuestionsRequest,
  GenerateQuestionsResponse,
  UpdateStatusRequest,
  InterviewStatistics
} from '../types/interview';

// 创建axios实例（使用相对路径，依赖Vite代理）
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加token
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

// 响应拦截器：处理401错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // token失效，清除并跳转到登录页
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const interviewAPI = {
  /**
   * 生成面试题
   */
  async generateQuestions(data: GenerateQuestionsRequest): Promise<GenerateQuestionsResponse> {
    const response = await api.post<GenerateQuestionsResponse>('/interview/generate', data);
    return response.data;
  },

  /**
   * 获取面试题列表
   */
  async getQuestions(
    learningPathId: number,
    status?: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<InterviewQuestionsListResponse> {
    const response = await api.get<InterviewQuestionsListResponse>(
      `/interview/questions/${learningPathId}`,
      {
        params: { status, limit, offset }
      }
    );
    return response.data;
  },

  /**
   * 获取所有学习路线的错题
   */
  async getAllMistakes(
    limit: number = 500,
    offset: number = 0
  ): Promise<InterviewQuestionsListResponse> {
    const response = await api.get<InterviewQuestionsListResponse>(
      `/interview/questions/all/mistakes`,
      {
        params: { limit, offset }
      }
    );
    return response.data;
  },

  /**
   * 更新题目状态
   */
  async updateStatus(data: UpdateStatusRequest): Promise<any> {
    const response = await api.post('/interview/status', data);
    return response.data;
  },

  /**
   * 获取统计信息
   */
  async getStatistics(learningPathId: number): Promise<InterviewStatistics> {
    const response = await api.get<InterviewStatistics>(
      `/interview/statistics/${learningPathId}`
    );
    return response.data;
  },

  /**
   * 根据薄弱点生成题目
   */
  async generateWeakPointsQuestions(
    learningPathId: number,
    count: number = 20
  ): Promise<GenerateQuestionsResponse> {
    const response = await api.post<GenerateQuestionsResponse>(
      `/interview/generate-weak-points`,
      null,
      {
        params: { learning_path_id: learningPathId, count }
      }
    );
    return response.data;
  },
};

