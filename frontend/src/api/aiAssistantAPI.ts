/**
 * AI助手API
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/ai-assistant';

// 类型定义
export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant' | 'system';
  message: string;
  created_at: string;
}

export interface ChatResponse {
  success: boolean;
  message: string;
  error?: string;
}

export interface QuickAction {
  id: string;
  title: string;
  description: string;
  prompt: string;
  icon: string;
}

// 获取token
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

/**
 * 发送消息
 */
export const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/chat`,
      { message },
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error: any) {
    console.error('发送消息失败:', error);
    throw error;
  }
};

/**
 * 获取对话历史
 */
export const getHistory = async (limit: number = 50): Promise<ChatMessage[]> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/history`,
      {
        params: { limit },
        headers: getAuthHeaders()
      }
    );
    return response.data;
  } catch (error: any) {
    console.error('获取历史失败:', error);
    throw error;
  }
};

/**
 * 清空对话历史
 */
export const clearHistory = async (): Promise<void> => {
  try {
    await axios.delete(
      `${API_BASE_URL}/history`,
      { headers: getAuthHeaders() }
    );
  } catch (error: any) {
    console.error('清空历史失败:', error);
    throw error;
  }
};

/**
 * 获取快捷功能列表
 */
export const getQuickActions = async (): Promise<QuickAction[]> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/quick-actions`,
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error: any) {
    console.error('获取快捷功能失败:', error);
    throw error;
  }
};

