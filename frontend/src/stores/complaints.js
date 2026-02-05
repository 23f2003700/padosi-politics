import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { complaintsAPI, votesAPI, commentsAPI } from '@/services/api'

export const useComplaintsStore = defineStore('complaints', () => {
  // State
  const complaints = ref([])
  const currentComplaint = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    total: 0,
    pages: 0,
    page: 1,
    per_page: 10
  })
  const filters = ref({
    status: '',
    category: '',
    priority: '',
    search: '',
    sort_by: 'created_at',
    sort_order: 'desc'
  })

  // Categories and statuses cache
  const categories = ref([])
  const statuses = ref([])
  const priorities = ref([])

  // Getters
  const openComplaintsCount = computed(() => 
    complaints.value.filter(c => ['open', 'acknowledged', 'in_progress', 'escalated'].includes(c.status)).length
  )

  // Actions
  async function fetchComplaints(params = {}) {
    try {
      loading.value = true
      error.value = null
      
      const queryParams = {
        page: pagination.value.page,
        per_page: pagination.value.per_page,
        ...filters.value,
        ...params
      }
      
      // Remove empty filters
      Object.keys(queryParams).forEach(key => {
        if (!queryParams[key]) delete queryParams[key]
      })
      
      const response = await complaintsAPI.list(queryParams)
      complaints.value = response.data.data
      pagination.value = response.data.pagination
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch complaints'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function fetchComplaint(id) {
    try {
      loading.value = true
      error.value = null
      
      const response = await complaintsAPI.get(id)
      currentComplaint.value = response.data.data
      
      return { success: true, data: currentComplaint.value }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch complaint'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function createComplaint(data) {
    try {
      loading.value = true
      error.value = null
      
      const response = await complaintsAPI.create(data)
      
      // Add to list
      complaints.value.unshift(response.data.data)
      
      return { success: true, data: response.data.data }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to create complaint'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function updateComplaint(id, data) {
    try {
      loading.value = true
      error.value = null
      
      const response = await complaintsAPI.update(id, data)
      
      // Update in list
      const index = complaints.value.findIndex(c => c.id === id)
      if (index !== -1) {
        complaints.value[index] = response.data.data
      }
      
      // Update current if viewing
      if (currentComplaint.value?.id === id) {
        currentComplaint.value = response.data.data
      }
      
      return { success: true, data: response.data.data }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to update complaint'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function deleteComplaint(id) {
    try {
      loading.value = true
      error.value = null
      
      await complaintsAPI.delete(id)
      
      // Remove from list
      complaints.value = complaints.value.filter(c => c.id !== id)
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to delete complaint'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(id, status, resolutionNote = null) {
    try {
      loading.value = true
      error.value = null
      
      const data = { status }
      if (resolutionNote) data.resolution_note = resolutionNote
      
      const response = await complaintsAPI.updateStatus(id, data)
      
      // Update in list and current
      const index = complaints.value.findIndex(c => c.id === id)
      if (index !== -1) {
        complaints.value[index] = response.data.data
      }
      if (currentComplaint.value?.id === id) {
        currentComplaint.value = response.data.data
      }
      
      return { success: true, data: response.data.data }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to update status'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function vote(complaintId, voteType, isAnonymous = true) {
    try {
      const response = await votesAPI.vote(complaintId, { vote_type: voteType, is_anonymous: isAnonymous })
      
      // Update counts in list and current
      const updateCounts = (complaint) => {
        complaint.support_count = response.data.data.support_count
        complaint.oppose_count = response.data.data.oppose_count
        complaint.user_vote = voteType
      }
      
      const index = complaints.value.findIndex(c => c.id === complaintId)
      if (index !== -1) updateCounts(complaints.value[index])
      if (currentComplaint.value?.id === complaintId) updateCounts(currentComplaint.value)
      
      return { success: true, data: response.data.data }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to vote' }
    }
  }

  async function removeVote(complaintId) {
    try {
      const response = await votesAPI.removeVote(complaintId)
      
      // Update counts
      const updateCounts = (complaint) => {
        complaint.support_count = response.data.data.support_count
        complaint.oppose_count = response.data.data.oppose_count
        complaint.user_vote = null
      }
      
      const index = complaints.value.findIndex(c => c.id === complaintId)
      if (index !== -1) updateCounts(complaints.value[index])
      if (currentComplaint.value?.id === complaintId) updateCounts(currentComplaint.value)
      
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to remove vote' }
    }
  }

  async function addComment(complaintId, text, isAnonymous = false) {
    try {
      const response = await commentsAPI.add(complaintId, { comment_text: text, is_anonymous: isAnonymous })
      
      // Add to current complaint's comments
      if (currentComplaint.value?.id === complaintId) {
        if (!currentComplaint.value.comments) {
          currentComplaint.value.comments = []
        }
        currentComplaint.value.comments.unshift(response.data.data)
        currentComplaint.value.comments_count = (currentComplaint.value.comments_count || 0) + 1
      }
      
      return { success: true, data: response.data.data }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to add comment' }
    }
  }

  async function deleteComment(commentId) {
    try {
      await commentsAPI.delete(commentId)
      
      // Remove from current complaint's comments
      if (currentComplaint.value?.comments) {
        currentComplaint.value.comments = currentComplaint.value.comments.filter(c => c.id !== commentId)
        currentComplaint.value.comments_count = Math.max(0, (currentComplaint.value.comments_count || 0) - 1)
      }
      
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to delete comment' }
    }
  }

  async function loadCategories() {
    if (categories.value.length === 0) {
      try {
        const response = await complaintsAPI.getCategories()
        categories.value = response.data.data
      } catch (err) {
        console.error('Failed to load categories:', err)
      }
    }
    return categories.value
  }

  async function loadStatuses() {
    if (statuses.value.length === 0) {
      try {
        const response = await complaintsAPI.getStatuses()
        statuses.value = response.data.data
      } catch (err) {
        console.error('Failed to load statuses:', err)
      }
    }
    return statuses.value
  }

  async function loadPriorities() {
    if (priorities.value.length === 0) {
      try {
        const response = await complaintsAPI.getPriorities()
        priorities.value = response.data.data
      } catch (err) {
        console.error('Failed to load priorities:', err)
      }
    }
    return priorities.value
  }

  function setFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.page = 1 // Reset to first page
  }

  function setPage(page) {
    pagination.value.page = page
  }

  function clearCurrentComplaint() {
    currentComplaint.value = null
  }

  return {
    // State
    complaints,
    currentComplaint,
    loading,
    error,
    pagination,
    filters,
    categories,
    statuses,
    priorities,
    // Getters
    openComplaintsCount,
    // Actions
    fetchComplaints,
    fetchComplaint,
    createComplaint,
    updateComplaint,
    deleteComplaint,
    updateStatus,
    vote,
    removeVote,
    addComment,
    deleteComment,
    loadCategories,
    loadStatuses,
    loadPriorities,
    setFilters,
    setPage,
    clearCurrentComplaint
  }
})
