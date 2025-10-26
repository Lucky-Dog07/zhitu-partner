import axios from 'axios';
import type { Notebook, NotebookCreate, NotebookUpdate } from '../types/note';

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

export const notebookAPI = {
  /**
   * 获取笔记本列表
   */
  async list(): Promise<Notebook[]> {
    const response = await api.get<Notebook[]>('/notebooks/');
    return response.data;
  },

  /**
   * 创建笔记本
   */
  async create(data: NotebookCreate): Promise<Notebook> {
    const response = await api.post<Notebook>('/notebooks/', data);
    return response.data;
  },

  /**
   * 更新笔记本
   */
  async update(id: number, data: NotebookUpdate): Promise<Notebook> {
    const response = await api.put<Notebook>(`/notebooks/${id}/`, data);
    return response.data;
  },

  /**
   * 删除笔记本
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/notebooks/${id}/`);
  },
};

