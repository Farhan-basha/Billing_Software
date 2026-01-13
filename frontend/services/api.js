/**
 * Centralized API service for all backend communication
 * Handles authentication, error handling, and request/response transformation
 */

import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  async (error) => {
    console.error('API Error:', error.response?.status, error.config?.url, error.response?.data);
    const originalRequest = error.config;

    // If access token expired, try to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = Cookies.get('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}/token/refresh/`,
            { refresh: refreshToken }
          );

          const { access } = response.data;
          Cookies.set('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Refresh failed, clear tokens and redirect to login
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
};

// Customer APIs
export const customerAPI = {
  getAll: (params) => api.get('/customers/', { params }),
  getById: (id) => api.get(`/customers/${id}/`),
  create: (data) => api.post('/customers/', data),
  update: (id, data) => api.patch(`/customers/${id}/`, data),
  delete: (id) => api.delete(`/customers/${id}/`),
  search: (query) => api.get('/customers/search/', { params: { search: query } }),
  getStats: (id) => api.get(`/customers/${id}/stats/`),
};

// Invoice APIs
export const invoiceAPI = {
  getAll: (params) => api.get('/invoices/', { params }),
  getById: (id) => api.get(`/invoices/${id}/`),
  create: (data) => api.post('/invoices/', data),
  update: (id, data) => api.patch(`/invoices/${id}/`, data),
  delete: (id) => api.delete(`/invoices/${id}/`),
  getPrint: (id) => api.get(`/invoices/${id}/print/`),
  updateStatus: (id, status) => api.post(`/invoices/${id}/status/`, { status }),
  getDashboard: () => api.get('/invoices/dashboard/'),
};

// Settings APIs
export const settingsAPI = {
  getCompany: () => api.get('/settings/company/'),
  updateCompany: (data) => api.put('/settings/company/', data),
};

// Helper functions for auth
export const setAuthTokens = (access, refresh) => {
  Cookies.set('access_token', access, { expires: 1 }); // 1 day
  Cookies.set('refresh_token', refresh, { expires: 7 }); // 7 days
};

export const clearAuthTokens = () => {
  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
};

export const getAccessToken = () => {
  return Cookies.get('access_token');
};

export const isAuthenticated = () => {
  return !!getAccessToken();
};

export default api;
