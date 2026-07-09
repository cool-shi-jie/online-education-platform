import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    access: localStorage.getItem('access') || '',
    refresh: localStorage.getItem('refresh') || ''
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.access || state.refresh),
    role: (state) => state.user?.role
  },
  actions: {
    syncFromStorage() {
      this.access = localStorage.getItem('access') || ''
      this.refresh = localStorage.getItem('refresh') || ''
      this.user = JSON.parse(localStorage.getItem('user') || 'null')
    },
    async login(payload) {
      const { data } = await http.post('/auth/login/', payload)
      this.access = data.access
      this.refresh = data.refresh
      this.user = data.user
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
    },
    async register(payload) {
      await http.post('/auth/register/', payload)
    },
    async fetchMe() {
      const { data } = await http.get('/auth/me/')
      this.access = localStorage.getItem('access') || this.access
      this.refresh = localStorage.getItem('refresh') || this.refresh
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    },
    async updateProfile(payload) {
      const { data } = await http.patch('/auth/me/', payload)
      this.access = localStorage.getItem('access') || this.access
      this.refresh = localStorage.getItem('refresh') || this.refresh
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    },
    async changePassword(payload) {
      await http.post('/auth/change-password/', payload)
    },
    logout() {
      this.user = null
      this.access = ''
      this.refresh = ''
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('user')
    }
  }
})
