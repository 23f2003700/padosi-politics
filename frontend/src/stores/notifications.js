import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsAPI } from '@/services/api'

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const pagination = ref({
    total: 0,
    pages: 0,
    page: 1,
    per_page: 20
  })

  // Toast notifications
  const toasts = ref([])
  let toastId = 0

  // Getters
  const hasUnread = computed(() => unreadCount.value > 0)

  // Actions
  async function fetchNotifications(params = {}) {
    try {
      loading.value = true
      const response = await notificationsAPI.list({
        page: pagination.value.page,
        per_page: pagination.value.per_page,
        ...params
      })
      notifications.value = response.data.data
      unreadCount.value = response.data.unread_count
      pagination.value = response.data.pagination
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to fetch notifications' }
    } finally {
      loading.value = false
    }
  }

  async function fetchUnreadCount() {
    try {
      const response = await notificationsAPI.getUnreadCount()
      unreadCount.value = response.data.data.unread_count
    } catch (err) {
      console.error('Failed to fetch unread count:', err)
    }
  }

  async function markAsRead(id) {
    try {
      await notificationsAPI.markAsRead(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification && !notification.is_read) {
        notification.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to mark as read' }
    }
  }

  async function markAllAsRead() {
    try {
      await notificationsAPI.markAllAsRead()
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to mark all as read' }
    }
  }

  async function deleteNotification(id) {
    try {
      await notificationsAPI.delete(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification && !notification.is_read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      notifications.value = notifications.value.filter(n => n.id !== id)
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to delete notification' }
    }
  }

  async function clearAll() {
    try {
      await notificationsAPI.clearAll()
      notifications.value = []
      unreadCount.value = 0
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to clear notifications' }
    }
  }

  // Toast management
  function showToast(message, type = 'info', duration = 4000) {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }

  function removeToast(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  function showSuccess(message) {
    return showToast(message, 'success')
  }

  function showError(message) {
    return showToast(message, 'error', 6000)
  }

  function showWarning(message) {
    return showToast(message, 'warning')
  }

  function showInfo(message) {
    return showToast(message, 'info')
  }

  return {
    // State
    notifications,
    unreadCount,
    loading,
    pagination,
    toasts,
    // Getters
    hasUnread,
    // Actions
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
    showToast,
    removeToast,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
})
