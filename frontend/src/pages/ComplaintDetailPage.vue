<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="card p-12 text-center">
      <ExclamationTriangleIcon class="w-16 h-16 text-danger-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">Failed to load complaint</h3>
      <p class="text-gray-500 mb-4">{{ error }}</p>
      <router-link to="/complaints" class="btn btn-primary">
        Back to Complaints
      </router-link>
    </div>
    
    <!-- Complaint Detail -->
    <div v-else-if="complaint" class="max-w-4xl mx-auto">
      <!-- Back Button -->
      <router-link to="/complaints" class="inline-flex items-center text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeftIcon class="w-4 h-4 mr-2" />
        Back to Complaints
      </router-link>
      
      <!-- Main Card -->
      <div class="card overflow-hidden">
        <!-- Colored Header Bar based on priority -->
        <div 
          class="h-2"
          :class="{
            'bg-slate-400': complaint.priority === 'low',
            'bg-primary-500': complaint.priority === 'medium',
            'bg-warning-500': complaint.priority === 'high',
            'bg-danger-500': complaint.priority === 'critical'
          }"
        ></div>
        
        <div class="p-4 sm:p-6">
          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4 gap-4">
            <div class="flex-1">
              <!-- Badges -->
              <div class="flex flex-wrap items-center gap-2 mb-3">
                <span :class="categoryClass(complaint.category)" class="badge text-xs sm:text-sm">
                  {{ formatCategory(complaint.category) }}
                </span>
                <span :class="statusClass(complaint.status)" class="badge text-xs sm:text-sm">
                  {{ formatStatus(complaint.status) }}
                </span>
                <span :class="priorityClass(complaint.priority)" class="badge text-xs sm:text-sm">
                  {{ complaint.priority }}
                </span>
                <span v-if="complaint.is_anonymous" class="badge badge-secondary text-xs sm:text-sm">
                  🕶️ Anonymous
                </span>
              </div>
              
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900">{{ complaint.title }}</h1>
            </div>
            
            <!-- Vote Section -->
            <div class="flex sm:flex-col items-center sm:ml-6 bg-gray-50 rounded-xl p-3 sm:p-4 self-start">
              <button 
                @click="handleVote"
                class="p-2 sm:p-3 rounded-xl transition-all transform hover:scale-110"
                :class="complaint.user_vote ? 'bg-primary-100 text-primary-600 shadow-lg shadow-primary-500/20' : 'hover:bg-gray-100 text-gray-400'"
              >
                <HandThumbUpIcon class="w-6 h-6 sm:w-8 sm:h-8" />
              </button>
              <div class="flex sm:flex-col items-center ml-3 sm:ml-0 sm:mt-1">
                <span class="text-lg sm:text-xl font-bold text-gray-900">{{ complaint.support_count || 0 }}</span>
                <span class="text-xs text-gray-500 ml-1 sm:ml-0">votes</span>
              </div>
            </div>
          </div>
          
          <!-- Meta Info -->
          <div class="flex flex-wrap items-center text-xs sm:text-sm text-gray-500 gap-2 sm:gap-3 mb-6 pb-6 border-b">
            <span class="flex items-center bg-gray-100 px-2 sm:px-3 py-1 sm:py-1.5 rounded-full">
              <UserCircleIcon class="w-4 h-4 mr-1 sm:mr-1.5" />
              {{ complaint.is_anonymous ? 'Anonymous' : complaint.author?.username }}
            </span>
            <span class="flex items-center bg-gray-100 px-2 sm:px-3 py-1 sm:py-1.5 rounded-full">
              <CalendarIcon class="w-4 h-4 mr-1 sm:mr-1.5" />
              {{ formatDateTime(complaint.created_at) }}
            </span>
            <span v-if="complaint.location" class="flex items-center bg-gray-100 px-2 sm:px-3 py-1 sm:py-1.5 rounded-full">
              <MapPinIcon class="w-4 h-4 mr-1 sm:mr-1.5" />
              {{ complaint.location }}
            </span>
          </div>
          
          <!-- Description -->
          <div class="prose max-w-none mb-6">
            <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Description</h3>
            <p class="text-gray-700 whitespace-pre-wrap leading-relaxed">{{ complaint.description }}</p>
          </div>
          
          <!-- Evidence -->
          <div v-if="complaint.evidence && complaint.evidence.length > 0" class="mb-6">
            <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Attachments</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div 
                v-for="evidence in complaint.evidence"
                :key="evidence.id"
                class="relative group"
              >
                <img 
                  v-if="evidence.file_type?.startsWith('image')"
                  :src="evidence.file_url"
                  :alt="evidence.description"
                  class="w-full h-24 object-cover rounded-lg cursor-pointer"
                  @click="openLightbox(evidence)"
                />
                <a 
                  v-else
                  :href="evidence.file_url"
                  target="_blank"
                  class="flex items-center justify-center w-full h-24 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <DocumentIcon class="w-8 h-8 text-gray-400" />
                </a>
              </div>
            </div>
          </div>
          
          <!-- Actions for Committee/Admin -->
          <div v-if="canUpdateStatus" class="p-4 bg-gray-50 rounded-lg mb-6">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">Update Status</h3>
            <div class="flex flex-wrap gap-2">
              <button 
                v-for="status in availableStatuses"
                :key="status"
                @click="updateStatus(status)"
                class="btn btn-sm"
                :class="complaint.status === status ? 'btn-primary' : 'btn-secondary'"
              >
                {{ formatStatus(status) }}
              </button>
            </div>
          </div>
          
          <!-- Escalation Info -->
          <div v-if="complaint.escalation" class="p-4 bg-danger-50 border border-danger-200 rounded-lg mb-6">
            <div class="flex items-start">
              <ExclamationTriangleIcon class="w-5 h-5 text-danger-500 mr-3 mt-0.5" />
              <div>
                <h3 class="font-semibold text-danger-700">Escalated</h3>
                <p class="text-sm text-danger-600 mt-1">{{ complaint.escalation.reason }}</p>
                <p class="text-xs text-danger-500 mt-2">
                  Escalated on {{ formatDateTime(complaint.escalation.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Comments Section -->
      <div class="card mt-6">
        <div class="p-6 border-b">
          <h2 class="text-lg font-semibold text-gray-900">
            Comments ({{ comments.length }})
          </h2>
        </div>
        
        <!-- Comment Form -->
        <div class="p-6 border-b bg-gray-50">
          <form @submit.prevent="submitComment" class="flex space-x-4">
            <div class="flex-1">
              <textarea 
                v-model="newComment"
                rows="2"
                placeholder="Write a comment..."
                class="input resize-none"
                :disabled="commentLoading"
              ></textarea>
            </div>
            <button 
              type="submit"
              class="btn btn-primary self-end"
              :disabled="!newComment.trim() || commentLoading"
            >
              <PaperAirplaneIcon class="w-5 h-5" />
            </button>
          </form>
        </div>
        
        <!-- Comments List -->
        <div v-if="comments.length === 0" class="p-8 text-center text-gray-500">
          No comments yet. Be the first to comment!
        </div>
        
        <div v-else class="divide-y">
          <div 
            v-for="comment in comments"
            :key="comment.id"
            class="p-6"
          >
            <div class="flex items-start">
              <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-primary-600 font-semibold">
                  {{ comment.author?.username?.charAt(0).toUpperCase() }}
                </span>
              </div>
              <div class="ml-4 flex-1">
                <div class="flex items-center justify-between">
                  <div>
                    <span class="font-medium text-gray-900">{{ comment.author?.username }}</span>
                    <span v-if="comment.is_official" class="ml-2 badge badge-primary">Official</span>
                    <span class="text-sm text-gray-500 ml-2">
                      {{ formatDateTime(comment.created_at) }}
                    </span>
                  </div>
                  <button 
                    v-if="canDeleteComment(comment)"
                    @click="deleteComment(comment.id)"
                    class="text-gray-400 hover:text-danger-500"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
                <p class="text-gray-700 mt-2 whitespace-pre-wrap">{{ comment.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useComplaintsStore } from '@/stores/complaints'
import { useNotificationsStore } from '@/stores/notifications'
import { complaintsService, commentsService } from '@/services/api'
import {
  ArrowLeftIcon,
  HandThumbUpIcon,
  UserCircleIcon,
  CalendarIcon,
  MapPinIcon,
  ExclamationTriangleIcon,
  DocumentIcon,
  PaperAirplaneIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const complaintsStore = useComplaintsStore()
const notificationsStore = useNotificationsStore()

const loading = ref(true)
const error = ref('')
const complaint = ref(null)
const comments = ref([])
const newComment = ref('')
const commentLoading = ref(false)

const availableStatuses = ['pending', 'in_progress', 'resolved', 'rejected']

const canUpdateStatus = computed(() => {
  return authStore.isAdmin || authStore.isSecretary || authStore.isCommittee
})

const formatCategory = (category) => {
  return category?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || category
}

const formatStatus = (status) => {
  return status?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || status
}

const formatDateTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
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

const canDeleteComment = (comment) => {
  return comment.author_id === authStore.user?.id || authStore.isAdmin
}

const fetchComplaint = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const res = await complaintsService.getById(route.params.id)
    complaint.value = res.data.data
    comments.value = complaint.value.comments || []
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load complaint'
  } finally {
    loading.value = false
  }
}

const handleVote = async () => {
  try {
    if (complaint.value.user_vote) {
      const result = await complaintsStore.removeVote(complaint.value.id)
      if (!result.success) {
        notificationsStore.showError(result.error || 'Failed to remove vote')
        return
      }
    } else {
      const result = await complaintsStore.vote(complaint.value.id, 'support')
      if (!result.success) {
        notificationsStore.showError(result.error || 'Failed to vote')
        return
      }
    }
  } catch (err) {
    notificationsStore.showError('Failed to vote')
  }
}

const updateStatus = async (status) => {
  try {
    await complaintsService.updateStatus(complaint.value.id, { status })
    complaint.value.status = status
    notificationsStore.showSuccess('Status updated successfully')
  } catch (err) {
    notificationsStore.showError('Failed to update status')
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  commentLoading.value = true
  
  try {
    const res = await commentsService.create(complaint.value.id, {
      content: newComment.value
    })
    comments.value.unshift(res.data.data)
    newComment.value = ''
    notificationsStore.showSuccess('Comment added')
  } catch (err) {
    notificationsStore.showError('Failed to add comment')
  } finally {
    commentLoading.value = false
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('Are you sure you want to delete this comment?')) return
  
  try {
    await commentsService.delete(complaint.value.id, commentId)
    comments.value = comments.value.filter(c => c.id !== commentId)
    notificationsStore.showSuccess('Comment deleted')
  } catch (err) {
    notificationsStore.showError('Failed to delete comment')
  }
}

const openLightbox = (evidence) => {
  // Simple lightbox - opens in new tab
  window.open(evidence.file_url, '_blank')
}

onMounted(() => {
  fetchComplaint()
})
</script>
