<template>
  <div>
    <!-- Page Header -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">My Complaints</h1>
          <p class="text-gray-500 mt-1">Track and manage the complaints you've filed</p>
        </div>
        <router-link to="/complaints/new" class="btn btn-primary shadow-lg shadow-primary-500/25">
          <PlusIcon class="w-5 h-5 mr-2" />
          New Complaint
        </router-link>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6">
      <div class="card p-3 sm:p-4 border-l-4 border-gray-400">
        <p class="text-xs sm:text-sm text-gray-500">Total Filed</p>
        <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ stats.total }}</p>
      </div>
      <div class="card p-3 sm:p-4 border-l-4 border-warning-400">
        <p class="text-xs sm:text-sm text-gray-500">Pending</p>
        <p class="text-xl sm:text-2xl font-bold text-warning-600">{{ stats.pending }}</p>
      </div>
      <div class="card p-3 sm:p-4 border-l-4 border-primary-400">
        <p class="text-xs sm:text-sm text-gray-500">In Progress</p>
        <p class="text-xl sm:text-2xl font-bold text-primary-600">{{ stats.in_progress }}</p>
      </div>
      <div class="card p-3 sm:p-4 border-l-4 border-success-400">
        <p class="text-xs sm:text-sm text-gray-500">Resolved</p>
        <p class="text-xl sm:text-2xl font-bold text-success-600">{{ stats.resolved }}</p>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="complaints.length === 0" class="card p-12 text-center">
      <DocumentTextIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No complaints yet</h3>
      <p class="text-gray-500 mb-4">Start contributing to your society by filing complaints!</p>
      <router-link to="/complaints/new" class="btn btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        File Your First Complaint
      </router-link>
    </div>
    
    <!-- Complaints List -->
    <div v-else class="space-y-4">
      <div 
        v-for="complaint in complaints"
        :key="complaint.id"
        class="card hover:shadow-lg transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <!-- Badges -->
              <div class="flex flex-wrap items-center gap-2 mb-2">
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
              
              <!-- Title -->
              <router-link 
                :to="`/complaints/${complaint.id}`"
                class="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors"
              >
                {{ complaint.title }}
              </router-link>
              
              <!-- Meta -->
              <div class="flex items-center text-sm text-gray-500 mt-2 space-x-4">
                <span>{{ formatDate(complaint.created_at) }}</span>
                <span v-if="complaint.location">•</span>
                <span v-if="complaint.location" class="flex items-center">
                  <MapPinIcon class="w-4 h-4 mr-1" />
                  {{ complaint.location }}
                </span>
              </div>
            </div>
            <!-- Stats -->
            <div class="ml-6 flex items-center space-x-4 text-sm text-gray-500">
              <span class="flex items-center">
                <HandThumbUpIcon class="w-5 h-5 mr-1" />
                {{ complaint.vote_count || 0 }}
              </span>
              <span class="flex items-center">
                <ChatBubbleLeftIcon class="w-5 h-5 mr-1" />
                {{ complaint.comment_count || 0 }}
              </span>
            </div>
          </div>
          
          <!-- Progress Bar for Status -->
          <div class="mt-4 pt-4 border-t">
            <div class="flex items-center justify-between text-xs text-gray-500 mb-2">
              <span>Progress</span>
              <span>{{ getStatusProgress(complaint.status) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all"
                :class="getProgressColor(complaint.status)"
                :style="{ width: `${getStatusProgress(complaint.status)}%` }"
              ></div>
            </div>
          </div>
          
          <!-- Actions -->
          <div class="flex items-center justify-end mt-4 space-x-2">
            <router-link 
              :to="`/complaints/${complaint.id}`"
              class="btn btn-sm btn-secondary"
            >
              View Details
            </router-link>
            <button 
              v-if="complaint.status === 'pending'"
              @click="editComplaint(complaint.id)"
              class="btn btn-sm btn-ghost"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { complaintsService } from '@/services/api'
import { useNotificationsStore } from '@/stores/notifications'
import {
  DocumentTextIcon,
  PlusIcon,
  MapPinIcon,
  HandThumbUpIcon,
  ChatBubbleLeftIcon,
  PencilIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const notificationsStore = useNotificationsStore()

const loading = ref(true)
const complaints = ref([])
const stats = reactive({
  total: 0,
  pending: 0,
  in_progress: 0,
  resolved: 0
})

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
    year: 'numeric'
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

const getStatusProgress = (status) => {
  const progress = {
    pending: 25,
    in_progress: 50,
    escalated: 60,
    resolved: 100,
    rejected: 100
  }
  return progress[status] || 0
}

const getProgressColor = (status) => {
  const colors = {
    pending: 'bg-warning-500',
    in_progress: 'bg-primary-500',
    escalated: 'bg-danger-500',
    resolved: 'bg-success-500',
    rejected: 'bg-gray-500'
  }
  return colors[status] || 'bg-gray-500'
}

const editComplaint = (id) => {
  router.push(`/complaints/${id}/edit`)
}

onMounted(async () => {
  try {
    const res = await complaintsService.getMine()
    complaints.value = res.data.data || []
    
    // Calculate stats
    stats.total = complaints.value.length
    stats.pending = complaints.value.filter(c => c.status === 'pending').length
    stats.in_progress = complaints.value.filter(c => c.status === 'in_progress').length
    stats.resolved = complaints.value.filter(c => c.status === 'resolved').length
  } catch (error) {
    notificationsStore.showError('Failed to fetch your complaints')
  } finally {
    loading.value = false
  }
})
</script>
