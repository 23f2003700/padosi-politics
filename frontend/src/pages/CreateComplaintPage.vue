<template>
  <div class="max-w-2xl mx-auto">
    <!-- Page Header -->
    <div class="mb-6">
      <router-link to="/complaints" class="inline-flex items-center text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeftIcon class="w-4 h-4 mr-2" />
        Back to Complaints
      </router-link>
    </div>
    
    <div class="card overflow-hidden">
      <div class="p-6 bg-gradient-to-r from-primary-600 to-indigo-600 text-white">
        <h2 class="text-xl font-bold">File a New Complaint</h2>
        <p class="text-primary-100 mt-1">Help improve our society by reporting issues</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Title <span class="text-danger-500">*</span>
          </label>
          <input 
            v-model="form.title"
            type="text"
            required
            maxlength="200"
            placeholder="Brief description of the issue"
            class="input"
            :disabled="loading"
          />
          <p class="text-xs text-gray-500 mt-1">{{ form.title.length }}/200</p>
        </div>
        
        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Category <span class="text-danger-500">*</span>
          </label>
          <select v-model="form.category" required class="input" :disabled="loading">
            <option value="">Select a category</option>
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">
              {{ cat.label }}
            </option>
          </select>
        </div>
        
        <!-- Priority -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Priority <span class="text-danger-500">*</span>
          </label>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
            <button 
              type="button"
              @click="form.priority = 'low'"
              class="p-2 sm:p-3 rounded-xl border-2 transition-all text-center"
              :class="form.priority === 'low' 
                ? 'border-slate-400 bg-slate-50 text-slate-700 shadow-sm'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
            >
              <span class="text-xs sm:text-sm font-medium">Low</span>
            </button>
            <button 
              type="button"
              @click="form.priority = 'medium'"
              class="p-2 sm:p-3 rounded-xl border-2 transition-all text-center"
              :class="form.priority === 'medium' 
                ? 'border-primary-400 bg-primary-50 text-primary-700 shadow-sm'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
            >
              <span class="text-xs sm:text-sm font-medium">Medium</span>
            </button>
            <button 
              type="button"
              @click="form.priority = 'high'"
              class="p-2 sm:p-3 rounded-xl border-2 transition-all text-center"
              :class="form.priority === 'high' 
                ? 'border-warning-400 bg-warning-50 text-warning-700 shadow-sm'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
            >
              <span class="text-xs sm:text-sm font-medium">High</span>
            </button>
            <button 
              type="button"
              @click="form.priority = 'critical'"
              class="p-2 sm:p-3 rounded-xl border-2 transition-all text-center"
              :class="form.priority === 'critical' 
                ? 'border-danger-400 bg-danger-50 text-danger-700 shadow-sm'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
            >
              <span class="text-xs sm:text-sm font-medium">Critical</span>
            </button>
          </div>
        </div>
        
        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description <span class="text-danger-500">*</span>
          </label>
          <textarea 
            v-model="form.description"
            rows="5"
            required
            minlength="20"
            placeholder="Provide detailed information about the issue..."
            class="input resize-none"
            :disabled="loading"
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">Minimum 20 characters</p>
        </div>
        
        <!-- Location -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <input 
            v-model="form.location"
            type="text"
            placeholder="e.g., Building A, 3rd Floor, Near Lift"
            class="input"
            :disabled="loading"
          />
        </div>
        
        <!-- Evidence Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Evidence (Optional)
          </label>
          <div 
            class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors cursor-pointer"
            @click="$refs.fileInput.click()"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <input 
              ref="fileInput"
              type="file"
              multiple
              accept="image/*,.pdf,.doc,.docx"
              class="hidden"
              @change="handleFileSelect"
            />
            <CloudArrowUpIcon class="w-10 h-10 text-gray-400 mx-auto mb-2" />
            <p class="text-sm text-gray-600">
              <span class="text-primary-600 font-medium">Click to upload</span> or drag and drop
            </p>
            <p class="text-xs text-gray-500 mt-1">Images, PDF, DOC (Max 5MB each)</p>
          </div>
          
          <!-- File Previews -->
          <div v-if="files.length > 0" class="mt-4 space-y-2">
            <div 
              v-for="(file, index) in files"
              :key="index"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center">
                <PhotoIcon v-if="file.type.startsWith('image')" class="w-5 h-5 text-primary-500 mr-3" />
                <DocumentIcon v-else class="w-5 h-5 text-gray-500 mr-3" />
                <span class="text-sm text-gray-700 truncate max-w-[200px]">{{ file.name }}</span>
                <span class="text-xs text-gray-500 ml-2">({{ formatFileSize(file.size) }})</span>
              </div>
              <button 
                type="button"
                @click="removeFile(index)"
                class="text-gray-400 hover:text-danger-500"
              >
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
        
        <!-- Anonymous Toggle -->
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p class="font-medium text-gray-900">Post Anonymously</p>
            <p class="text-sm text-gray-500">Your identity will be hidden from other residents</p>
          </div>
          <button 
            type="button"
            @click="form.is_anonymous = !form.is_anonymous"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
            :class="form.is_anonymous ? 'bg-primary-600' : 'bg-gray-200'"
          >
            <span 
              class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
              :class="form.is_anonymous ? 'translate-x-6' : 'translate-x-1'"
            ></span>
          </button>
        </div>
        
        <!-- Validation Messages -->
        <div v-if="!isFormValid && (form.title || form.description)" class="p-3 bg-warning-50 text-warning-700 rounded-lg text-sm">
          <p v-if="form.title.length < 5">• Title must be at least 5 characters</p>
          <p v-if="!form.category">• Please select a category</p>
          <p v-if="form.description.length < 20">• Description must be at least 20 characters ({{ form.description.length }}/20)</p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-danger-50 text-danger-700 rounded-lg text-sm">
          {{ error }}
        </div>
        
        <!-- Submit Buttons -->
        <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 sm:space-x-4">
          <router-link to="/complaints" class="btn btn-secondary w-full sm:w-auto text-center">
            Cancel
          </router-link>
          <button 
            type="submit"
            class="btn btn-primary w-full sm:w-auto"
            :disabled="loading || !isFormValid"
          >
            <span v-if="loading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting...
            </span>
            <span v-else>Submit Complaint</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import { complaintsService } from '@/services/api'
import {
  CloudArrowUpIcon,
  PhotoIcon,
  DocumentIcon,
  XMarkIcon,
  ArrowLeftIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const notificationsStore = useNotificationsStore()

const form = reactive({
  title: '',
  category: '',
  priority: 'medium',
  description: '',
  location: '',
  is_anonymous: false
})

const files = ref([])
const loading = ref(false)
const error = ref('')

const categories = [
  { value: 'noise', label: '🔊 Noise' },
  { value: 'parking', label: '🚗 Parking' },
  { value: 'pet', label: '🐕 Pet Related' },
  { value: 'maintenance', label: '🔧 Maintenance' },
  { value: 'cleanliness', label: '🧹 Cleanliness' },
  { value: 'security', label: '🔒 Security' },
  { value: 'water', label: '💧 Water' },
  { value: 'electricity', label: '⚡ Electricity' },
  { value: 'harassment', label: '⚠️ Harassment' },
  { value: 'other', label: '📝 Other' }
]

const priorities = [
  { value: 'low', label: 'Low', color: 'gray' },
  { value: 'medium', label: 'Medium', color: 'primary' },
  { value: 'high', label: 'High', color: 'warning' },
  { value: 'critical', label: 'Critical', color: 'danger' }
]

const isFormValid = computed(() => {
  return form.title.trim().length >= 5 && 
         form.category && 
         form.priority && 
         form.description.trim().length >= 20
})

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

const handleDrop = (event) => {
  const droppedFiles = Array.from(event.dataTransfer.files)
  addFiles(droppedFiles)
}

const addFiles = (newFiles) => {
  const maxSize = 5 * 1024 * 1024 // 5MB
  
  for (const file of newFiles) {
    if (file.size > maxSize) {
      notificationsStore.showWarning(`${file.name} is too large (max 5MB)`)
      continue
    }
    
    if (files.value.length >= 5) {
      notificationsStore.showWarning('Maximum 5 files allowed')
      break
    }
    
    files.value.push(file)
  }
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    // Use JSON if no files, FormData if files attached
    let requestData
    
    if (files.value.length > 0) {
      // Create FormData for file upload
      requestData = new FormData()
      requestData.append('title', form.title.trim())
      requestData.append('category', form.category)
      requestData.append('priority', form.priority)
      requestData.append('description', form.description.trim())
      requestData.append('is_anonymous', form.is_anonymous)
      
      // Append files
      for (const file of files.value) {
        requestData.append('evidence', file)
      }
    } else {
      // Use JSON for simpler requests without files
      requestData = {
        title: form.title.trim(),
        category: form.category,
        priority: form.priority,
        description: form.description.trim(),
        is_anonymous: form.is_anonymous
      }
    }
    
    const res = await complaintsService.create(requestData)
    
    notificationsStore.showSuccess('Complaint submitted successfully!')
    router.push(`/complaints/${res.data.data.id}`)
  } catch (err) {
    console.error('Submit error:', err)
    const errorData = err.response?.data
    if (errorData?.errors) {
      // Show specific validation errors
      const errorMessages = Object.entries(errorData.errors)
        .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
        .join('; ')
      error.value = errorMessages || errorData.error || 'Validation failed'
    } else {
      error.value = errorData?.message || errorData?.error || 'Failed to submit complaint'
    }
  } finally {
    loading.value = false
  }
}
</script>
