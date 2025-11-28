import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      return Promise.reject(error.response.data);
    } else if (error.request) {
      return Promise.reject({ message: '网络请求失败，请检查服务器连接' });
    } else {
      return Promise.reject({ message: error.message });
    }
  },
);

// 报表相关API
export const reportApi = {
  // 获取报表列表
  listReports: () => api.get('/api/reports'),
  
  // 获取报表详情
  getReport: (reportId) => api.get(`/api/reports/${reportId}`),
  
  // 创建报表
  createReport: (data) => api.post('/api/reports', data),
  
  // 更新报表
  updateReport: (reportId, data) => api.put(`/api/reports/${reportId}`, data),
  
  // 删除报表
  deleteReport: (reportId) => api.delete(`/api/reports/${reportId}`),
  
  // 执行报表查询
  executeReport: (queryConfig) => api.post('/api/reports/execute', { query_config: queryConfig }),
};

export default api;

