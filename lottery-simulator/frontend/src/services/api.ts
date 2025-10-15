import axios, { AxiosInstance, AxiosResponse } from 'axios';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // 使用事件通知而不是直接跳转，避免页面刷新
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
    return Promise.reject(error);
  }
);

// 认证API
export const authAPI = {
  login: (credentials: { username: string; password: string }) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    return api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  
  register: (userData: {
    username: string;
    email: string;
    password: string;
    phone?: string;
  }) => api.post('/api/auth/register', userData),
  
  getCurrentUser: () => api.get('/api/auth/profile'),
  
  refreshToken: () => api.post('/api/auth/refresh'),
  
  logout: () => api.post('/api/auth/logout'),
  
  updateProfile: (profileData: {
    nickname?: string;
    avatar?: string;
    phone?: string;
    email?: string;
  }) => api.put('/api/auth/profile', profileData),
  
  changePassword: (passwordData: {
    old_password: string;
    new_password: string;
  }) => api.put('/api/auth/password', passwordData),
};

// 彩票API
export const lotteryAPI = {
  getCurrentPeriod: () => api.get('/api/lottery/current-period'),
  
  getHistoricalDraws: (limit: number = 50) =>
    api.get(`/api/lottery/historical-draws?limit=${limit}`),
  
  quickPick: () => api.get('/api/lottery/quick-pick'),
  
  purchase: (data: {
    red_balls: number[];
    blue_ball: number;
    multiple: number;
    period?: string;
  }) => api.post('/api/lottery/purchase', data),
  
  batchPurchase: (data: {
    purchases: Array<{
      red_balls: number[];
      blue_ball: number;
      multiple: number;
    }>;
    period?: string;
  }) => api.post('/api/lottery/batch-purchase', data),
  
  getPurchaseHistory: (params: {
    period?: string;
    page?: number;
    size?: number;
  }) => api.get('/api/lottery/purchase-history', { params }),
  
  getPurchaseDetail: (purchaseId: number) =>
    api.get(`/api/lottery/purchase/${purchaseId}`),
  
  checkWinning: (purchaseId: number) =>
    api.get(`/api/lottery/check-winning/${purchaseId}`),
  
  getPurchaseStatistics: () => api.get('/api/lottery/purchase-statistics'),
  
  getPrizeLevels: () => api.get('/api/lottery/prize-levels'),
};

// 账户API
export const accountAPI = {
  getBalance: () => api.get('/api/account/balance'),
  
  recharge: (data: { amount: number; payment_method: string }) =>
    api.post('/api/account/recharge', data),
  
  withdraw: (data: { amount: number; payment_method: string }) =>
    api.post('/api/account/withdraw', data),
  
  getTransactionHistory: (params: {
    transaction_type?: string;
    page?: number;
    size?: number;
    start_date?: string;
    end_date?: string;
  }) => api.get('/api/account/transactions', { params }),
  
  getAccountStatistics: () => api.get('/api/account/statistics'),
  
  setAccountLimits: (data: {
    daily_limit?: number;
    monthly_limit?: number;
  }) => api.put('/api/account/limits', data),
  
  getBalanceHistory: (days: number = 30) =>
    api.get(`/api/account/balance-history?days=${days}`),
};

// 分析API
export const analysisAPI = {
  getRecommendations: (params?: {
    analysis_type?: string;
    period_count?: number;
  }) => api.get('/api/analysis/recommendations', { params }),
  
  getMarkovAnalysis: (params?: { period_count?: number }) =>
    api.get('/api/analysis/markov-analysis', { params }),
  
  getFrequencyAnalysis: (params?: { period_count?: number }) =>
    api.get('/api/analysis/frequency-analysis', { params }),
  
  getTrendAnalysis: (params?: { period_count?: number }) =>
    api.get('/api/analysis/trend-analysis', { params }),
  
  getHotColdAnalysis: (params?: { period_count?: number }) =>
    api.get('/api/analysis/hot-cold-analysis', { params }),
  
  getPatternAnalysis: (params?: { period_count?: number }) =>
    api.get('/api/analysis/pattern-analysis', { params }),
  
  getCorrelationAnalysis: (params?: { period_count?: number }) =>
    api.get('/api/analysis/correlation-analysis', { params }),
  
  getPredictionAccuracy: () => api.get('/api/analysis/prediction-accuracy'),
  
  getModelComparison: () => api.get('/api/analysis/model-comparison'),
  
  getCustomAnalysis: (data: {
    analysis_type: string;
    parameters: Record<string, any>;
  }) => api.post('/api/analysis/custom-analysis', data),
  
  getAnalysisStatistics: () => api.get('/api/analysis/statistics'),
  
  saveAnalysis: (data: {
    name: string;
    analysis_type: string;
    parameters: Record<string, any>;
    results: Record<string, any>;
  }) => api.post('/api/analysis/save-analysis', data),
  
  getMyAnalyses: (params?: { page?: number; size?: number }) =>
    api.get('/api/analysis/my-analyses', { params }),
};

export default api;