import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api'
})

// Request interceptor to add token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't logout on auth endpoints
      const isAuthEndpoint = error.config.url?.includes('/auth/login') || 
                            error.config.url?.includes('/auth/register')
      if (!isAuthEndpoint) {
        console.log('Unauthorized - token may be invalid')
      }
    }
    return Promise.reject(error)
  }
)

export default api
