import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.roles?.includes('admin'))
  const isSecretary = computed(() => user.value?.roles?.includes('secretary') || isAdmin.value)
  const isCommittee = computed(() => user.value?.roles?.includes('committee_member') || isSecretary.value)
  const karmaScore = computed(() => user.value?.karma_score || 0)
  const society = computed(() => user.value?.society || null)

  // Actions
  async function initializeAuth() {
    if (token.value) {
      try {
        loading.value = true
        const response = await authAPI.getProfile()
        user.value = response.data.data
      } catch (err) {
        // Token invalid, clear it
        logout()
      } finally {
        loading.value = false
      }
    }
  }

  async function login(credentials) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authAPI.login(credentials)
      const { access_token, refresh_token, user: userData, society: societyData } = response.data.data
      
      // Store token
      localStorage.setItem('access_token', access_token)
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token)
      }
      
      token.value = access_token
      user.value = { ...userData, society: societyData }
      
      // Redirect to dashboard or intended page
      const redirect = router.currentRoute.value.query.redirect || '/dashboard'
      router.push(redirect)
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authAPI.register(userData)
      const { access_token, refresh_token, user: newUser } = response.data.data
      
      // Store token
      localStorage.setItem('access_token', access_token)
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token)
      }
      
      token.value = access_token
      user.value = newUser
      
      router.push('/dashboard')
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  function logout() {
    // Clear tokens
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    // Clear state
    token.value = null
    user.value = null
    error.value = null
    
    // Redirect to login
    router.push('/login')
  }

  async function updateProfile(data) {
    try {
      loading.value = true
      const response = await authAPI.updateProfile(data)
      user.value = { ...user.value, ...response.data.data }
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to update profile'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function refreshProfile() {
    try {
      const response = await authAPI.getProfile()
      user.value = response.data.data
    } catch (err) {
      console.error('Failed to refresh profile:', err)
    }
  }

  function updateKarma(points) {
    if (user.value) {
      user.value.karma_score = (user.value.karma_score || 0) + points
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    isSecretary,
    isCommittee,
    karmaScore,
    society,
    // Actions
    initializeAuth,
    login,
    register,
    logout,
    updateProfile,
    refreshProfile,
    updateKarma
  }
})
