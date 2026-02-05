import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Determine API base URL
// In development, Vite proxy handles /api routes
// In production, use the environment variable
const getBaseURL = () => {
  // Check if we're in production (no Vite dev server)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // Default to relative /api for development (proxied by Vite)
  return '/api'
}

// Create axios instance
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    console.log('Request to:', config.url, 'Token exists:', !!token)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response, config } = error
    
    if (response) {
      // Skip auth redirect for login/register endpoints
      const isAuthEndpoint = config.url?.includes('/auth/login') || config.url?.includes('/auth/register')
      
      // Handle specific error codes
      switch (response.status) {
        case 401:
          // Unauthorized - only redirect if NOT on login/register page
          if (!isAuthEndpoint) {
            const authStore = useAuthStore()
            authStore.logout()
            router.push({ name: 'login' })
          }
          break
        case 403:
          // Forbidden
          console.error('Access denied')
          break
        case 404:
          // Not found
          console.error('Resource not found')
          break
        case 429:
          // Rate limited
          console.error('Too many requests')
          break
        case 500:
          // Server error
          console.error('Server error')
          break
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  changePassword: (data) => api.post('/auth/change-password', data)
}

// Societies API
export const societiesAPI = {
  list: (params) => api.get('/societies', { params }),
  get: (id, includeStats = false) => api.get(`/societies/${id}`, { params: { include_stats: includeStats } }),
  getFlats: (id) => api.get(`/societies/${id}/flats`),
  getStats: (id) => api.get(`/societies/${id}/stats`)
}

// Complaints API
export const complaintsAPI = {
  list: (params) => api.get('/complaints', { params }),
  get: (id) => api.get(`/complaints/${id}`),
  create: (data) => api.post('/complaints', data),
  update: (id, data) => api.put(`/complaints/${id}`, data),
  delete: (id) => api.delete(`/complaints/${id}`),
  updateStatus: (id, data) => api.patch(`/complaints/${id}/status`, data),
  getCategories: () => api.get('/complaints/categories'),
  getStatuses: () => api.get('/complaints/statuses'),
  getPriorities: () => api.get('/complaints/priorities')
}

// Evidence API
export const evidenceAPI = {
  upload: (complaintId, formData) => api.post(`/evidence`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getForComplaint: (complaintId) => api.get(`/evidence/complaints/${complaintId}/evidence`),
  delete: (id) => api.delete(`/evidence/${id}`)
}

// Votes API
export const votesAPI = {
  vote: (complaintId, data) => api.post(`/complaints/${complaintId}/vote`, data),
  removeVote: (complaintId) => api.delete(`/complaints/${complaintId}/vote`),
  getMyVote: (complaintId) => api.get(`/complaints/${complaintId}/vote`)
}

// Comments API
export const commentsAPI = {
  list: (complaintId, params) => api.get(`/complaints/${complaintId}/comments`, { params }),
  add: (complaintId, data) => api.post(`/complaints/${complaintId}/comments`, data),
  delete: (id) => api.delete(`/comments/${id}`)
}

// Escalations API
export const escalationsAPI = {
  list: (params) => api.get('/escalations', { params }),
  escalate: (complaintId, data) => api.post(`/escalations/complaints/${complaintId}/escalate`, data),
  acknowledge: (id, data) => api.patch(`/escalations/${id}/acknowledge`, data),
  getForComplaint: (complaintId) => api.get(`/escalations/complaints/${complaintId}/escalations`)
}

// Karma API
export const karmaAPI = {
  getMyKarma: () => api.get('/my-karma'),
  getUserKarma: (userId) => api.get(`/users/${userId}/karma`),
  getLeaderboard: (params) => api.get('/leaderboard', { params }),
  getStats: () => api.get('/karma-stats')
}

// Notifications API
export const notificationsAPI = {
  list: (params) => api.get('/notifications', { params }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markAsRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllAsRead: () => api.patch('/notifications/mark-all-read'),
  delete: (id) => api.delete(`/notifications/${id}`),
  clearAll: () => api.delete('/notifications/clear-all')
}

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getSocietyStats: () => api.get('/dashboard/society-stats'),
  getRecentActivity: (params) => api.get('/dashboard/recent-activity', { params })
}

// Simplified service exports for pages
export const authService = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.patch('/auth/me', data),
  changePassword: (data) => api.post('/auth/change-password', data),
  deleteAccount: () => api.delete('/auth/me')
}

export const complaintsService = {
  getAll: (params) => api.get('/complaints', { params }),
  getById: (id) => api.get(`/complaints/${id}`),
  getMine: () => api.get('/complaints', { params: { my_complaints: true } }),
  create: (data) => api.post('/complaints', data, {
    headers: data instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {}
  }),
  update: (id, data) => api.patch(`/complaints/${id}`, data),
  delete: (id) => api.delete(`/complaints/${id}`),
  updateStatus: (id, data) => api.patch(`/complaints/${id}/status`, data)
}

export const votesService = {
  vote: (complaintId) => api.post(`/complaints/${complaintId}/vote`),
  removeVote: (complaintId) => api.delete(`/complaints/${complaintId}/vote`)
}

export const commentsService = {
  getAll: (complaintId) => api.get(`/complaints/${complaintId}/comments`),
  create: (complaintId, data) => api.post(`/complaints/${complaintId}/comments`, data),
  delete: (complaintId, commentId) => api.delete(`/complaints/${complaintId}/comments/${commentId}`)
}

export const karmaService = {
  getLeaderboard: (params) => api.get('/leaderboard', { params }),
  getMyHistory: () => api.get('/my-karma')
}

export const notificationsService = {
  getAll: (params) => api.get('/notifications', { params }),
  markAsRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllAsRead: () => api.patch('/notifications/mark-all-read'),
  clearAll: () => api.delete('/notifications/clear-all')
}

export const dashboardService = {
  getStats: () => api.get('/dashboard/stats'),
  getAdminStats: () => api.get('/dashboard/admin-stats')
}

export const societiesService = {
  getMembers: () => api.get('/societies/members'),
  updateUserRole: (userId, data) => api.patch(`/societies/users/${userId}/role`, data),
  toggleUserStatus: (userId) => api.patch(`/societies/users/${userId}/toggle-status`),
  getSettings: () => api.get('/societies/settings'),
  updateSettings: (data) => api.patch('/societies/settings', data)
}

export const escalationsService = {
  getAll: () => api.get('/escalations'),
  create: (complaintId, data) => api.post(`/complaints/${complaintId}/escalate`, data),
  resolve: (id) => api.patch(`/escalations/${id}/resolve`)
}

export const tasksService = {
  getStatus: () => api.get('/tasks/status'),
  runEscalation: () => api.post('/tasks/run-escalation'),
  runReminders: () => api.post('/tasks/run-reminders'),
  runCleanup: (days = 30) => api.post(`/tasks/run-cleanup?days=${days}`),
  calculateStats: () => api.post('/tasks/calculate-stats')
}

export default api
