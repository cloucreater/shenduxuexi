import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export interface User {
  id: number
  username: string
  email?: string | null
  phone?: string | null
  avatar?: string | null
  role: 'user' | 'admin'
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const userLoaded = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username: string, password: string, captcha: string) {
    console.log('[AUTH STORE] login called with:', { username, password, captcha })
    const response = await api.post<{ token: string; user: User }>('/auth/login', {
      username,
      password,
      captcha
    })
    console.log('[AUTH STORE] login response:', response.data)
    
    token.value = response.data.token
    user.value = response.data.user
    userLoaded.value = true
    localStorage.setItem('token', response.data.token)
    
    console.log('[AUTH STORE] token saved to localStorage:', localStorage.getItem('token'))
    console.log('[AUTH STORE] authStore.token:', token.value)
    console.log('[AUTH STORE] authStore.user:', user.value)
    
    return response.data
  }

  async function register(username: string, password: string, email?: string, phone?: string) {
    const response = await api.post<{ token: string; user: User }>('/auth/register', {
      username,
      password,
      email,
      phone
    })
    token.value = response.data.token
    user.value = response.data.user
    localStorage.setItem('token', response.data.token)
    return response.data
  }

  async function fetchCurrentUser() {
    if (!token.value) return
    try {
      const response = await api.get<User>('/auth/me')
      user.value = response.data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    userLoaded.value = false
    localStorage.removeItem('token')
  }

  // 初始化时尝试获取用户信息
  async function initAuth() {
    if (token.value && !user.value) {
      try {
        await fetchCurrentUser()
      } catch {
        // ignore
      }
    }
  }

  async function updatePassword(oldPassword: string, newPassword: string) {
    await api.put('/auth/password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }

  async function updateProfile(data: { email?: string; phone?: string }) {
    const response = await api.put<User>('/auth/profile', data)
    user.value = response.data
    return response.data
  }

  return {
    token,
    user,
    userLoaded,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    fetchCurrentUser,
    initAuth,
    updatePassword,
    updateProfile
  }
})