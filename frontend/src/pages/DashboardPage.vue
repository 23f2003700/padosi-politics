<template>
  <div class="animate-fade-in">
    <!-- Welcome Banner -->
    <div class="card bg-gradient-to-r from-primary-600 via-primary-700 to-indigo-700 text-white p-4 sm:p-6 mb-6 sm:mb-8 relative overflow-hidden">
      <div class="absolute top-0 right-0 w-48 sm:w-64 h-48 sm:h-64 bg-white/5 rounded-full transform translate-x-20 -translate-y-20"></div>
      <div class="absolute bottom-0 left-1/2 w-32 sm:w-48 h-32 sm:h-48 bg-white/5 rounded-full transform -translate-x-1/2 translate-y-20"></div>
      <div class="relative z-10">
        <h2 class="text-xl sm:text-2xl font-bold mb-2">Welcome back, {{ authStore.user?.full_name?.split(' ')[0] || 'Resident' }}! 👋</h2>
        <p class="text-primary-100 text-sm sm:text-base max-w-lg">Track complaints, engage with your community, and help make your society a better place to live.</p>
      </div>
    </div>
    
    <!-- Stats Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
      <div class="stat-card group hover:shadow-lg transition-all duration-300">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between">
          <div class="order-2 sm:order-1">
            <p class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Total Complaints</p>
            <p class="text-2xl sm:text-3xl font-bold text-gray-900">{{ stats.total_complaints || 0 }}</p>
          </div>
          <div class="order-1 sm:order-2 w-10 h-10 sm:w-14 sm:h-14 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl sm:rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform mb-2 sm:mb-0">
            <ClipboardDocumentListIcon class="w-5 h-5 sm:w-7 sm:h-7 text-primary-600" />
          </div>
        </div>
        <div class="mt-2 sm:mt-4 flex items-center text-xs sm:text-sm">
          <span class="text-success-600 font-medium">↑ 12%</span>
          <span class="text-gray-400 ml-2 hidden sm:inline">from last month</span>
        </div>
      </div>
      
      <div class="stat-card group hover:shadow-lg transition-all duration-300">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between">
          <div class="order-2 sm:order-1">
            <p class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Pending</p>
            <p class="text-2xl sm:text-3xl font-bold text-warning-600">{{ stats.pending_complaints || 0 }}</p>
          </div>
          <div class="order-1 sm:order-2 w-10 h-10 sm:w-14 sm:h-14 bg-gradient-to-br from-warning-100 to-amber-200 rounded-xl sm:rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform mb-2 sm:mb-0">
            <ClockIcon class="w-5 h-5 sm:w-7 sm:h-7 text-warning-600" />
          </div>
        </div>
        <div class="mt-2 sm:mt-4 flex items-center text-xs sm:text-sm">
          <span class="text-warning-600 font-medium">{{ stats.pending_complaints || 0 }} <span class="hidden sm:inline">need attention</span></span>
        </div>
      </div>
      
      <div class="stat-card group hover:shadow-lg transition-all duration-300">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between">
          <div class="order-2 sm:order-1">
            <p class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Resolved</p>
            <p class="text-2xl sm:text-3xl font-bold text-success-600">{{ stats.resolved_complaints || 0 }}</p>
          </div>
          <div class="order-1 sm:order-2 w-10 h-10 sm:w-14 sm:h-14 bg-gradient-to-br from-success-100 to-emerald-200 rounded-xl sm:rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform mb-2 sm:mb-0">
            <CheckCircleIcon class="w-5 h-5 sm:w-7 sm:h-7 text-success-600" />
          </div>
        </div>
        <div class="mt-2 sm:mt-4 flex items-center text-xs sm:text-sm">
          <span class="text-success-600 font-medium">Great progress!</span>
        </div>
      </div>
      
      <div class="stat-card group hover:shadow-lg transition-all duration-300">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between">
          <div class="order-2 sm:order-1">
            <p class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Escalated</p>
            <p class="text-2xl sm:text-3xl font-bold text-danger-600">{{ stats.escalated_complaints || 0 }}</p>
          </div>
          <div class="order-1 sm:order-2 w-10 h-10 sm:w-14 sm:h-14 bg-gradient-to-br from-danger-100 to-red-200 rounded-xl sm:rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform mb-2 sm:mb-0">
            <ExclamationTriangleIcon class="w-5 h-5 sm:w-7 sm:h-7 text-danger-600" />
          </div>
        </div>
        <div class="mt-2 sm:mt-4 flex items-center text-xs sm:text-sm">
          <span class="text-danger-600 font-medium">{{ stats.escalated_complaints || 0 }} <span class="hidden sm:inline">urgent</span></span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
      <!-- Recent Complaints -->
      <div class="lg:col-span-2">
        <div class="card">
          <div class="p-6 border-b">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold text-gray-900">Recent Complaints</h2>
              <router-link to="/complaints" class="text-sm text-primary-600 hover:text-primary-700">
                View all →
              </router-link>
            </div>
          </div>
          
          <div v-if="loading" class="p-8 text-center">
            <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
          </div>
          
          <div v-else-if="recentComplaints.length === 0" class="p-8 text-center text-gray-500">
            No complaints yet. Be the first to file one!
          </div>
          
          <div v-else class="divide-y">
            <router-link 
              v-for="complaint in recentComplaints"
              :key="complaint.id"
              :to="`/complaints/${complaint.id}`"
              class="block p-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2 mb-1">
                    <span :class="categoryClass(complaint.category)" class="badge">
                      {{ formatCategory(complaint.category) }}
                    </span>
                    <span :class="statusClass(complaint.status)" class="badge">
                      {{ formatStatus(complaint.status) }}
                    </span>
                    <span :class="priorityClass(complaint.priority)" class="badge">
                      {{ complaint.priority }}
                    </span>
                  </div>
                  <h3 class="font-medium text-gray-900 truncate">{{ complaint.title }}</h3>
                  <p class="text-sm text-gray-500 mt-1">
                    by {{ complaint.author?.username }} • {{ formatDate(complaint.created_at) }}
                  </p>
                </div>
                <div class="flex items-center space-x-4 text-sm text-gray-500 ml-4">
                  <span class="flex items-center">
                    <HandThumbUpIcon class="w-4 h-4 mr-1" />
                    {{ complaint.vote_count || 0 }}
                  </span>
                  <span class="flex items-center">
                    <ChatBubbleLeftIcon class="w-4 h-4 mr-1" />
                    {{ complaint.comment_count || 0 }}
                  </span>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Quick Actions -->
        <div class="card p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-3">
            <router-link to="/complaints/new" class="btn btn-primary w-full">
              <PlusIcon class="w-5 h-5 mr-2" />
              New Complaint
            </router-link>
            <router-link to="/my-complaints" class="btn btn-secondary w-full">
              <DocumentTextIcon class="w-5 h-5 mr-2" />
              My Complaints
            </router-link>
          </div>
        </div>
        
        <!-- My Karma -->
        <div class="card p-6">
          <h3 class="font-semibold text-gray-900 mb-4">My Karma</h3>
          <div class="text-center">
            <div class="w-20 h-20 bg-gradient-to-br from-success-400 to-success-600 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-2xl font-bold text-white">{{ authStore.user?.karma_points || 0 }}</span>
            </div>
            <p class="text-sm text-gray-500">Keep contributing to earn more!</p>
          </div>
          <router-link to="/leaderboard" class="btn btn-ghost w-full mt-4">
            View Leaderboard →
          </router-link>
        </div>
        
        <!-- Top Contributors -->
        <div class="card p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Top Contributors</h3>
          <div class="space-y-3">
            <div 
              v-for="(user, index) in topContributors"
              :key="user.id"
              class="flex items-center"
            >
              <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                :class="{
                  'bg-yellow-100 text-yellow-700': index === 0,
                  'bg-gray-100 text-gray-700': index === 1,
                  'bg-orange-100 text-orange-700': index === 2,
                  'bg-gray-50 text-gray-500': index > 2
                }"
              >
                {{ index + 1 }}
              </span>
              <div class="ml-3 flex-1">
                <p class="text-sm font-medium text-gray-900">{{ user.username }}</p>
              </div>
              <span class="text-sm font-semibold text-success-600">{{ user.karma_points }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dashboardService, karmaService } from '@/services/api'
import {
  ClipboardDocumentListIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  HandThumbUpIcon,
  ChatBubbleLeftIcon,
  PlusIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const loading = ref(true)
const stats = ref({})
const recentComplaints = ref([])
const topContributors = ref([])

const formatCategory = (category) => {
  return category?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || category
}

const formatStatus = (status) => {
  return status?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || status
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const categoryClass = (category) => ({
  'badge-primary': ['maintenance', 'security'].includes(category),
  'badge-warning': ['noise', 'parking'].includes(category),
  'badge-danger': ['safety', 'emergency'].includes(category),
  'badge-success': ['cleanliness', 'amenities'].includes(category),
})

const statusClass = (status) => ({
  'badge-warning': status === 'pending',
  'badge-primary': status === 'in_progress',
  'badge-success': status === 'resolved',
  'badge-danger': status === 'escalated',
  'badge-secondary': status === 'rejected',
})

const priorityClass = (priority) => ({
  'badge-secondary': priority === 'low',
  'badge-primary': priority === 'medium',
  'badge-warning': priority === 'high',
  'badge-danger': priority === 'critical',
})

onMounted(async () => {
  try {
    // Fetch dashboard data
    const [dashboardRes, leaderboardRes] = await Promise.all([
      dashboardService.getStats(),
      karmaService.getLeaderboard({ limit: 5 })
    ])
    
    stats.value = dashboardRes.data.data?.stats || {}
    recentComplaints.value = dashboardRes.data.data?.recent_complaints || []
    topContributors.value = leaderboardRes.data.data?.leaderboard || []
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>
