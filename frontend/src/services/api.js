import axios from 'axios'
import { getToken, logout } from './auth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      logout()
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData)
}

// User API
export const userAPI = {
  getLots: () => api.get('/user/lots'),
  bookSpot: (lotId) => api.post('/user/book', { lot_id: lotId }),
  leaveSpot: (reservationId) => api.post('/user/leave', { reservation_id: reservationId }),
  getMyReservations: () => api.get('/user/my_reservations'),
  triggerExport: () => api.post('/user/export/trigger'),
  getExportStatus: () => api.get('/user/export/status'),
  downloadExport: (jobId) => api.get(`/user/export/download/${jobId}`, { responseType: 'blob' })
}

// Admin API
export const adminAPI = {
  getDashboardStats: () => api.get('/admin/dashboard/stats'),
  getLots: () => api.get('/admin/lots'),
  getLot: (lotId) => api.get(`/admin/lots/${lotId}`),
  createLot: (lotData) => api.post('/admin/lots', lotData),
  updateLot: (lotId, lotData) => api.put(`/admin/lots/${lotId}`, lotData),
  deleteLot: (lotId) => api.delete(`/admin/lots/${lotId}`),
  getLotSpots: (lotId) => api.get(`/admin/lots/${lotId}/spots`)
}

// Cache clearing
export const cacheAPI = {
  clearCache: () => api.post('/cache/clear')
}

export default api