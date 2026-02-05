<template>
  <div class="max-w-2xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Notifications</h1>
        <p class="text-gray-500 text-sm sm:text-base mt-1">Stay updated with your society activity</p>
      </div>
      <button 
        v-if="notifications.length > 0"
        @click="markAllAsRead"
        class="btn btn-secondary text-sm w-full sm:w-auto"
      >
        <CheckIcon class="w-4 h-4 mr-2" />
        Mark all as read
      </button>
    </div>
    
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="notifications.length === 0" class="card p-8 sm:p-12 text-center">
      <div class="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <BellIcon class="w-8 h-8 sm:w-10 sm:h-10 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
      <p class="text-gray-500">You're all caught up! 🎉</p>
    </div>
    
    <!-- Notifications List -->
    <div v-else class="space-y-3">
      <div 
        v-for="notification in notifications"
        :key="notification.id"
        class="card p-3 sm:p-4 cursor-pointer transition-all hover:shadow-md border-l-4"
        :class="[
          notification.is_read ? 'border-l-transparent' : 'border-l-primary-500 bg-primary-50/50',
          { 'border-primary-200': !notification.is_read }
        ]"
        @click="handleNotificationClick(notification)"
      >
        <div class="flex items-start">
          <div 
            class="w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center flex-shrink-0"
            :class="notificationIconClass(notification.type)"
          >
            <component :is="notificationIcon(notification.type)" class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div class="ml-3 sm:ml-4 flex-1 min-w-0">
            <p 
              class="text-sm sm:text-base text-gray-900 line-clamp-2"
              :class="{ 'font-semibold': !notification.is_read }"
            >
              {{ notification.title }}
            </p>
            <p class="text-xs sm:text-sm text-gray-600 mt-1 line-clamp-2">{{ notification.message }}</p>
            <p class="text-xs text-gray-400 mt-2 flex items-center">
              <ClockIcon class="w-3 h-3 mr-1" />
              {{ formatDate(notification.created_at) }}
            </p>
          </div>
          <button 
            v-if="!notification.is_read"
            @click.stop="markAsRead(notification.id)"
            class="w-2.5 h-2.5 sm:w-3 sm:h-3 bg-primary-500 rounded-full flex-shrink-0 animate-pulse ml-2"
            title="Mark as read"
          ></button>
        </div>
      </div>
    </div>
    
    <!-- Load More -->
    <div v-if="hasMore" class="text-center mt-6">
      <button 
        @click="loadMore"
        class="btn btn-secondary"
        :disabled="loadingMore"
      >
        {{ loadingMore ? 'Loading...' : 'Load More' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import {
  BellIcon,
  ChatBubbleLeftIcon,
  HandThumbUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  MegaphoneIcon,
  CheckIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const notificationsStore = useNotificationsStore()

const loading = ref(true)
const loadingMore = ref(false)
const notifications = ref([])
const hasMore = ref(false)
const page = ref(1)

const formatDate = (date) => {
  if (!date) return ''
  const now = new Date()
  const d = new Date(date)
  const diff = now - d
  
  // Less than a minute
  if (diff < 60000) return 'Just now'
  // Less than an hour
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  // Less than a day
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  // Less than a week
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`
  
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

const notificationIcon = (type) => {
  const icons = {
    comment: ChatBubbleLeftIcon,
    vote: HandThumbUpIcon,
    status_change: CheckCircleIcon,
    escalation: ExclamationTriangleIcon,
    announcement: MegaphoneIcon,
    default: InformationCircleIcon
  }
  return icons[type] || icons.default
}

const notificationIconClass = (type) => {
  const classes = {
    comment: 'bg-primary-100 text-primary-600',
    vote: 'bg-success-100 text-success-600',
    status_change: 'bg-success-100 text-success-600',
    escalation: 'bg-danger-100 text-danger-600',
    announcement: 'bg-warning-100 text-warning-600',
    default: 'bg-gray-100 text-gray-600'
  }
  return classes[type] || classes.default
}

const handleNotificationClick = async (notification) => {
  // Mark as read
  if (!notification.is_read) {
    await markAsRead(notification.id)
  }
  
  // Navigate if there's a related complaint
  if (notification.complaint_id) {
    router.push(`/complaints/${notification.complaint_id}`)
  }
}

const markAsRead = async (id) => {
  await notificationsStore.markAsRead(id)
  const notification = notifications.value.find(n => n.id === id)
  if (notification) {
    notification.is_read = true
  }
}

const markAllAsRead = async () => {
  await notificationsStore.markAllAsRead()
  notifications.value.forEach(n => n.is_read = true)
}

const loadMore = async () => {
  loadingMore.value = true
  page.value++
  
  try {
    await notificationsStore.fetchNotifications(page.value)
    notifications.value = [...notifications.value, ...notificationsStore.notifications]
    hasMore.value = notificationsStore.pagination?.current_page < notificationsStore.pagination?.total_pages
  } finally {
    loadingMore.value = false
  }
}

onMounted(async () => {
  try {
    await notificationsStore.fetchNotifications()
    notifications.value = notificationsStore.notifications
    hasMore.value = notificationsStore.pagination?.current_page < notificationsStore.pagination?.total_pages
  } finally {
    loading.value = false
  }
})
</script>
