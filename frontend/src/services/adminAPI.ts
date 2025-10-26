import api from './api';

// 类型定义
export interface UserListItem {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  learning_paths_count: number;
  notes_count: number;
}

export interface UserDetail {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  last_login_at: string | null;
  learning_paths_count: number;
  notes_count: number;
  interview_questions_count: number;
}

export interface ConfigItem {
  key: string;
  value: string;
  description: string | null;
  category: string;
}

export interface OverviewData {
  total_users: number;
  today_active_users: number;
  week_new_users: number;
  total_learning_paths: number;
  total_notes: number;
  total_questions: number;
}

// Dashboard类型
export interface DashboardOverview {
  total_users: number;
  active_users_today: number;
  new_users_this_week: number;
  total_learning_paths: number;
  total_notes: number;
  total_interview_questions: number;
  online_users: number;
}

export interface ActivityItem {
  type: string;
  username: string;
  description: string;
  timestamp: string;
}

export interface SystemStatus {
  database_status: string;
  api_status: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  last_check_time: string;
}

export interface QuickStats {
  users_this_week: number;
  users_last_week: number;
  users_growth_rate: number;
  paths_this_week: number;
  paths_last_week: number;
  paths_growth_rate: number;
  logins_this_week: number;
  logins_last_week: number;
  logins_growth_rate: number;
}

export interface PopularPath {
  id: number;
  user_id: number;
  username: string;
  created_at: string;
}

// 新增类型：用户增长数据
export interface UserGrowthItem {
  date: string;
  new_users: number;
  total_users: number;
}

// 新增类型：功能使用数据
export interface FeatureUsageData {
  learning_paths: number;
  notes: number;
  interviews: number;
  login_success: number;
  login_failed: number;
}

// 新增类型：活跃度热力图
export interface ActivityHeatmapItem {
  day: string;
  hour: number;
  count: number;
}

// 操作日志类型
export interface OperationLog {
  id: number;
  admin_id: number;
  username: string;
  action: string;
  target_type: string | null;
  target_id: number | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

// 登录日志类型
export interface LoginLog {
  id: number;
  user_id: number | null;
  username: string;
  ip_address: string | null;
  user_agent: string | null;
  status: string;
  fail_reason: string | null;
  login_time: string;
}

export interface LoginLogStatistics {
  today_logins: number;
  today_success: number;
  today_failed: number;
  success_rate: number;
  unique_users_today: number;
  suspicious_ips: Array<{
    ip_address: string;
    fail_count: number;
  }>;
}

// 用户管理API
export const userManagementAPI = {
  async list(params: {
    skip?: number;
    limit?: number;
    search?: string;
    role?: string;
    is_active?: boolean;
  }) {
    const response = await api.get('/admin/users', { params });
    return response.data;
  },

  async get(userId: number): Promise<UserDetail> {
    const response = await api.get(`/admin/users/${userId}`);
    return response.data;
  },

  async update(userId: number, data: {
    username?: string;
    email?: string;
    role?: string;
  }) {
    const response = await api.put(`/admin/users/${userId}`, data);
    return response.data;
  },

  async updateStatus(userId: number, isActive: boolean) {
    const response = await api.patch(`/admin/users/${userId}/status`, {
      is_active: isActive
    });
    return response.data;
  },

  async delete(userId: number) {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },

  async getStatistics(userId: number) {
    const response = await api.get(`/admin/users/${userId}/statistics`);
    return response.data;
  }
};

// 数据统计API
export const analyticsAPI = {
  async getOverview(): Promise<OverviewData> {
    const response = await api.get('/admin/overview');
    return response.data;
  },

  async getUserGrowth(days: number = 30) {
    const response = await api.get('/admin/users/growth', {
      params: { days }
    });
    return response.data;
  },

  async getFeaturesUsage() {
    const response = await api.get('/admin/features/usage');
    return response.data;
  }
};

// 系统配置API
export const configAPI = {
  async list(category?: string): Promise<ConfigItem[]> {
    const response = await api.get('/admin/configs', {
      params: category ? { category } : {}
    });
    return response.data;
  },

  async get(key: string): Promise<ConfigItem> {
    const response = await api.get(`/admin/configs/${key}`);
    return response.data;
  },

  async update(key: string, value: string) {
    const response = await api.put(`/admin/configs/${key}`, { value });
    return response.data;
  },

  async testConnection(service: 'openai' | 'n8n') {
    const response = await api.post('/admin/configs/test-connection', null, {
      params: { service }
    });
    return response.data;
  }
};

// Dashboard API
export const dashboardAPI = {
  async getOverview(): Promise<DashboardOverview> {
    const response = await api.get('/admin/dashboard/overview');
    return response.data;
  },

  async getRecentActivities(limit: number = 20): Promise<ActivityItem[]> {
    const response = await api.get('/admin/dashboard/recent-activities', {
      params: { limit }
    });
    return response.data;
  },

  async getSystemStatus(): Promise<SystemStatus> {
    const response = await api.get('/admin/dashboard/system-status');
    return response.data;
  },

  async getQuickStats(): Promise<QuickStats> {
    const response = await api.get('/admin/dashboard/quick-stats');
    return response.data;
  },

  async getPopularPaths(limit: number = 5): Promise<PopularPath[]> {
    const response = await api.get('/admin/dashboard/popular-paths', {
      params: { limit }
    });
    return response.data;
  },

  // 新增API方法
  async getUserGrowth(days: number = 30): Promise<UserGrowthItem[]> {
    const response = await api.get('/admin/dashboard/user-growth', {
      params: { days }
    });
    return response.data;
  },

  async getFeatureUsage(): Promise<FeatureUsageData> {
    const response = await api.get('/admin/dashboard/feature-usage');
    return response.data;
  },

  async getActivityHeatmap(): Promise<ActivityHeatmapItem[]> {
    const response = await api.get('/admin/dashboard/activity-heatmap');
    return response.data;
  },

  async export(params: {
    start_date?: string;
    end_date?: string;
    format?: 'csv' | 'xlsx';
  }): Promise<Blob> {
    const response = await api.get('/admin/dashboard/export', {
      params,
      responseType: 'blob'
    });
    return response.data;
  }
};

// 操作日志API
export const operationLogsAPI = {
  async list(params: {
    skip?: number;
    limit?: number;
    action?: string;
    target_type?: string;
    user_id?: number;
    start_date?: string;
    end_date?: string;
  }) {
    const response = await api.get('/admin/logs', { params });
    return response.data;
  },

  async get(logId: number): Promise<OperationLog> {
    const response = await api.get(`/admin/logs/${logId}`);
    return response.data;
  },

  async exportCSV(params?: {
    action?: string;
    target_type?: string;
    user_id?: number;
    start_date?: string;
    end_date?: string;
  }) {
    const response = await api.get('/admin/logs/export/csv', {
      params,
      responseType: 'blob'
    });
    return response.data;
  },

  async getSummary(days: number = 7) {
    const response = await api.get('/admin/logs/stats/summary', {
      params: { days }
    });
    return response.data;
  }
};

// 登录日志API
export const loginLogsAPI = {
  async list(params: {
    skip?: number;
    limit?: number;
    username?: string;
    status?: string;
    ip_address?: string;
    start_date?: string;
    end_date?: string;
  }) {
    const response = await api.get('/admin/login-logs', { params });
    return response.data;
  },

  async getStatistics(): Promise<LoginLogStatistics> {
    const response = await api.get('/admin/login-logs/statistics');
    return response.data;
  },

  async getUserLoginLogs(userId: number, limit: number = 10) {
    const response = await api.get(`/admin/login-logs/user/${userId}`, {
      params: { limit }
    });
    return response.data;
  }
};

