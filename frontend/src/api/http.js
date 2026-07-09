import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  timeout: 15000
})

let refreshPromise = null

function clearAuthStorage() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('user')
  window.dispatchEvent(new Event('auth-storage-cleared'))
}

function isTokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1] || ''))
    return payload.exp && payload.exp * 1000 <= Date.now()
  } catch {
    return true
  }
}

function isPublicGetRequest(config) {
  const method = (config.method || 'get').toLowerCase()
  const url = config.url || ''
  return method === 'get' && (url.startsWith('/courses/') || url === '/courses')
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem('refresh')
  if (!refresh || isTokenExpired(refresh)) return ''

  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${http.defaults.baseURL}/auth/refresh/`, { refresh })
      .then(({ data }) => {
        localStorage.setItem('access', data.access)
        return data.access
      })
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token && !isTokenExpired(token)) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const originalRequest = error.config || {}
      if (!originalRequest.__retriedWithRefresh) {
        originalRequest.__retriedWithRefresh = true
        try {
          const access = await refreshAccessToken()
          if (access) {
            originalRequest.headers = originalRequest.headers || {}
            originalRequest.headers.Authorization = `Bearer ${access}`
            return http(originalRequest)
          }
        } catch {
          clearAuthStorage()
        }
      }
      clearAuthStorage()
      if (isPublicGetRequest(originalRequest) && !originalRequest.__retriedWithoutAuth) {
        originalRequest.__retriedWithoutAuth = true
        if (originalRequest.headers) {
          delete originalRequest.headers.Authorization
        }
        return http(originalRequest)
      }
    }
    const message = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default http
