<template>
  <div>
    <!-- Page Header -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Society Complaints</h1>
          <p class="text-gray-500 mt-1">Browse, search, and track all community issues</p>
        </div>
        <router-link to="/complaints/new" class="btn btn-primary shadow-lg shadow-primary-500/25">
          <PlusIcon class="w-5 h-5 mr-2" />
          New Complaint
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-6">
      <div class="space-y-4">
        <!-- Search - Full Width on Mobile -->
        <div class="w-full">
          <div class="relative">
            <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              v-model="filters.search"
              type="text"
              placeholder="Search complaints..."
              class="input pl-10 w-full"
              @input="debouncedSearch"
            />
          </div>
        </div>
        
        <!-- Filter Dropdowns - Grid on Mobile -->
        <div class="grid grid-cols-2 sm:flex sm:flex-wrap gap-3">
          <!-- Category Filter -->
          <select v-model="filters.category" class="input text-sm" @change="fetchComplaints">
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat" :value="cat">
              {{ formatCategory(cat) }}
            </option>
          </select>
          
          <!-- Status Filter -->
          <select v-model="filters.status" class="input text-sm" @change="fetchComplaints">
            <option value="">All Status</option>
            <option v-for="stat in statuses" :key="stat" :value="stat">
              {{ formatStatus(stat) }}
            </option>
          </select>
          
          <!-- Priority Filter -->
          <select v-model="filters.priority" class="input text-sm" @change="fetchComplaints">
            <option value="">All Priorities</option>
            <option v-for="pri in priorities" :key="pri" :value="pri">
              {{ pri.charAt(0).toUpperCase() + pri.slice(1) }}
            </option>
          </select>
          
          <!-- Sort -->
          <select v-model="filters.sort" class="input text-sm" @change="fetchComplaints">
            <option value="-created_at">Newest</option>
            <option value="created_at">Oldest</option>
            <option value="-vote_count">Most Voted</option>
            <option value="-comment_count">Most Discussed</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="complaints.length === 0" class="card p-12 text-center">
      <ClipboardDocumentListIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No complaints found</h3>
      <p class="text-gray-500 mb-4">Try adjusting your filters or be the first to file a complaint!</p>
      <router-link to="/complaints/new" class="btn btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        File Complaint
      </router-link>
    </div>
    
    <!-- Complaints List -->
    <div v-else class="space-y-4">
      <div 
        v-for="complaint in complaints"
        :key="complaint.id"
        class="card hover:shadow-lg transition-shadow"
      >
        <div class="p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div class="flex-1 min-w-0">
              <!-- Badges -->
              <div class="flex flex-wrap items-center gap-2 mb-2">
                <span :class="categoryClass(complaint.category)" class="badge text-xs">
                  {{ formatCategory(complaint.category) }}
                </span>
                <span :class="statusClass(complaint.status)" class="badge text-xs">
                  {{ formatStatus(complaint.status) }}
                </span>
                <span :class="priorityClass(complaint.priority)" class="badge text-xs">
                  {{ complaint.priority }}
                </span>
                <span v-if="complaint.is_anonymous" class="badge badge-secondary text-xs">
                  Anonymous
                </span>
              </div>
              
              <!-- Title -->
              <router-link 
                :to="`/complaints/${complaint.id}`"
                class="text-base sm:text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors line-clamp-2"
              >
                {{ complaint.title }}
              </router-link>
              
              <!-- Description Preview -->
              <p class="text-gray-600 mt-2 text-sm line-clamp-2">
                {{ complaint.description }}
              </p>
              
              <!-- Meta -->
              <div class="flex flex-wrap items-center text-xs sm:text-sm text-gray-500 mt-3 gap-x-3 gap-y-1">
                <span>
                  {{ complaint.is_anonymous ? 'Anonymous' : complaint.author?.username }}
                </span>
                <span class="hidden sm:inline">•</span>
                <span>{{ formatDate(complaint.created_at) }}</span>
                <span v-if="complaint.location" class="hidden sm:inline">•</span>
                <span v-if="complaint.location" class="hidden sm:flex items-center">
                  <MapPinIcon class="w-4 h-4 mr-1" />
                  {{ complaint.location }}
                </span>
              </div>
            </div>
            
            <!-- Vote Section - Horizontal on mobile -->
            <div class="flex sm:flex-col items-center sm:items-center gap-3 sm:gap-0 sm:ml-4">
              <button 
                @click.prevent="handleVote(complaint)"
                class="p-2 rounded-lg transition-colors"
                :class="complaint.user_vote ? 'bg-primary-100 text-primary-600' : 'hover:bg-gray-100 text-gray-400'"
              >
                <HandThumbUpIcon class="w-5 h-5 sm:w-6 sm:h-6" />
              </button>
              <div class="flex sm:flex-col items-center sm:items-center gap-1 sm:gap-0">
                <span class="font-semibold text-gray-900">{{ complaint.support_count || 0 }}</span>
                <span class="text-xs text-gray-500">votes</span>
              </div>
            </div>
          </div>
          
          <!-- Footer -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mt-4 pt-4 border-t gap-3">
            <div class="flex items-center space-x-4 text-sm text-gray-500">
              <span class="flex items-center">
                <ChatBubbleLeftIcon class="w-4 h-4 mr-1" />
                {{ complaint.comment_count || 0 }} comments
              </span>
              <span v-if="complaint.evidence_count" class="flex items-center">
                <PhotoIcon class="w-4 h-4 mr-1" />
                {{ complaint.evidence_count }} files
              </span>
            </div>
            <router-link 
              :to="`/complaints/${complaint.id}`"
              class="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              View Details →
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Pagination -->
    <div v-if="pagination.total_pages > 1" class="flex justify-center mt-8">
      <nav class="flex items-center space-x-2">
        <button 
          @click="changePage(pagination.current_page - 1)"
          :disabled="pagination.current_page === 1"
          class="btn btn-secondary"
          :class="{ 'opacity-50 cursor-not-allowed': pagination.current_page === 1 }"
        >
          Previous
        </button>
        
        <span class="px-4 text-sm text-gray-600">
          Page {{ pagination.current_page }} of {{ pagination.total_pages }}
        </span>
        
        <button 
          @click="changePage(pagination.current_page + 1)"
          :disabled="pagination.current_page === pagination.total_pages"
          class="btn btn-secondary"
          :class="{ 'opacity-50 cursor-not-allowed': pagination.current_page === pagination.total_pages }"
        >
          Next
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useComplaintsStore } from '@/stores/complaints'
import { useNotificationsStore } from '@/stores/notifications'
import {
  MagnifyingGlassIcon,
  ClipboardDocumentListIcon,
  PlusIcon,
  HandThumbUpIcon,
  ChatBubbleLeftIcon,
  PhotoIcon,
  MapPinIcon
} from '@heroicons/vue/24/outline'

const complaintsStore = useComplaintsStore()
const notificationsStore = useNotificationsStore()

const loading = ref(true)
const complaints = ref([])
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_items: 0
})

const filters = reactive({
  search: '',
  category: '',
  status: '',
  priority: '',
  sort: '-created_at'
})

const categories = [
  'maintenance', 'security', 'noise', 'parking', 
  'cleanliness', 'amenities', 'safety', 'other'
]

const statuses = ['pending', 'in_progress', 'resolved', 'escalated', 'rejected']
const priorities = ['low', 'medium', 'high', 'critical']

let searchTimeout = null

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

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchComplaints()
  }, 300)
}

const fetchComplaints = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      per_page: 10,
      sort: filters.sort
    }
    
    if (filters.search) params.search = filters.search
    if (filters.category) params.category = filters.category
    if (filters.status) params.status = filters.status
    if (filters.priority) params.priority = filters.priority
    
    await complaintsStore.fetchComplaints(params)
    complaints.value = complaintsStore.complaints
    pagination.value = complaintsStore.pagination
  } catch (error) {
    notificationsStore.showError('Failed to fetch complaints')
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchComplaints(page)
  }
}

const handleVote = async (complaint) => {
  try {
    if (complaint.user_vote) {
      const result = await complaintsStore.removeVote(complaint.id)
      if (!result.success) {
        notificationsStore.showError(result.error || 'Failed to remove vote')
        return
      }
    } else {
      const result = await complaintsStore.vote(complaint.id, 'support')
      if (!result.success) {
        notificationsStore.showError(result.error || 'Failed to vote')
        return
      }
    }
  } catch (error) {
    notificationsStore.showError('Failed to vote')
  }
}

onMounted(() => {
  fetchComplaints()
})
</script>
