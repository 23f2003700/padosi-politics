<template>
  <div class="max-w-2xl mx-auto">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">My Profile</h1>
      <p class="text-gray-500 mt-1">Manage your account settings and preferences</p>
    </div>

    <!-- Profile Card -->
    <div class="card overflow-hidden">
      <div class="p-4 sm:p-6 bg-gradient-to-r from-primary-600 via-primary-700 to-indigo-700 text-white relative overflow-hidden">
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full transform translate-x-10 -translate-y-10"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full transform -translate-x-10 translate-y-10"></div>
        <div class="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left relative z-10">
          <div class="w-20 h-20 sm:w-24 sm:h-24 bg-white/20 backdrop-blur rounded-full flex items-center justify-center p-3 sm:p-4 ring-4 ring-white/30 flex-shrink-0">
            <img 
              :src="authStore.user?.roles?.[0] === 'admin' ? '/admin-avatar.svg' : (authStore.user?.roles?.[0] === 'resident' ? '/resident-avatar.svg' : '/user-avatar.svg')" 
              alt="User Avatar" 
              class="w-full h-full" 
            />
          </div>
          <div class="mt-4 sm:mt-0 sm:ml-6">
            <h1 class="text-xl sm:text-2xl font-bold">{{ authStore.user?.username }}</h1>
            <p class="text-primary-100 text-sm sm:text-base break-all">{{ authStore.user?.email }}</p>
            <div class="flex flex-wrap items-center justify-center sm:justify-start mt-3 gap-2">
              <span class="badge bg-white/20 text-white backdrop-blur px-3 py-1">
                {{ formatRole(authStore.user?.roles?.[0]) }}
              </span>
              <span class="flex items-center bg-success-500/20 px-3 py-1 rounded-full">
                <StarIcon class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 text-yellow-300" />
                <span class="font-semibold">{{ authStore.user?.karma_points || 0 }}</span>
                <span class="text-primary-100 ml-1 text-sm">karma</span>
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <UserCircleIcon class="w-5 h-5 mr-2 text-primary-500" />
          Profile Information
        </h2>
        
        <form @submit.prevent="updateProfile" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input 
              v-model="form.username"
              type="text"
              required
              class="input"
              :disabled="!editing"
            />
          </div>
          
          <!-- Email (Read-only) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input 
              :value="authStore.user?.email"
              type="email"
              class="input bg-gray-50"
              disabled
            />
            <p class="text-xs text-gray-500 mt-1">Email cannot be changed</p>
          </div>
          
          <!-- Flat Number -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Flat Number</label>
            <input 
              v-model="form.flat_number"
              type="text"
              class="input"
              :disabled="!editing"
            />
          </div>
          
          <!-- Society -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Society</label>
            <input 
              :value="authStore.user?.society?.name"
              type="text"
              class="input bg-gray-50"
              disabled
            />
          </div>
          
          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4">
            <template v-if="editing">
              <button 
                type="button"
                @click="cancelEdit"
                class="btn btn-secondary"
              >
                Cancel
              </button>
              <button 
                type="submit"
                class="btn btn-primary"
                :disabled="loading"
              >
                {{ loading ? 'Saving...' : 'Save Changes' }}
              </button>
            </template>
            <button 
              v-else
              type="button"
              @click="editing = true"
              class="btn btn-primary"
            >
              <PencilIcon class="w-4 h-4 mr-2" />
              Edit Profile
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Change Password -->
    <div class="card mt-6 overflow-hidden">
      <div class="p-6 bg-gray-50 border-b">
        <h2 class="text-lg font-semibold text-gray-900 flex items-center">
          <KeyIcon class="w-5 h-5 mr-2 text-primary-500" />
          Change Password
        </h2>
      </div>
      
      <div class="p-6">
        <form @submit.prevent="changePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
            <input 
              v-model="passwordForm.current_password"
              type="password"
              required
              class="input"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
            <input 
              v-model="passwordForm.new_password"
              type="password"
              required
              minlength="6"
              class="input"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
            <input 
              v-model="passwordForm.confirm_password"
              type="password"
              required
              class="input"
            />
          </div>
          
          <div v-if="passwordError" class="p-3 bg-danger-50 text-danger-700 rounded-lg text-sm">
            {{ passwordError }}
          </div>
          
          <div class="flex justify-end">
            <button 
              type="submit"
              class="btn btn-primary"
              :disabled="passwordLoading"
            >
              {{ passwordLoading ? 'Changing...' : 'Change Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Karma History -->
    <div class="card mt-6 overflow-hidden">
      <div class="p-6 bg-gray-50 border-b">
        <h2 class="text-lg font-semibold text-gray-900 flex items-center">
          <SparklesIcon class="w-5 h-5 mr-2 text-yellow-500" />
          Karma History
        </h2>
      </div>
      
      <div v-if="karmaHistory.length === 0" class="p-8 text-center text-gray-500">
        <SparklesIcon class="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p>No karma history yet</p>
        <p class="text-sm mt-1">Start contributing to earn karma points!</p>
      </div>
      
      <div v-else class="divide-y">
        <div 
          v-for="log in karmaHistory"
          :key="log.id"
          class="flex items-center justify-between p-4 hover:bg-gray-50"
        >
          <div>
            <p class="font-medium text-gray-900">{{ log.description }}</p>
            <p class="text-sm text-gray-500">{{ formatDate(log.created_at) }}</p>
          </div>
          <span 
            class="font-bold"
            :class="log.points > 0 ? 'text-success-600' : 'text-danger-600'"
          >
            {{ log.points > 0 ? '+' : '' }}{{ log.points }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- Danger Zone -->
    <div class="card mt-6 border-danger-200">
      <div class="p-6">
        <h2 class="text-lg font-semibold text-danger-600 mb-2">Danger Zone</h2>
        <p class="text-sm text-gray-500 mb-4">Once you delete your account, there is no going back.</p>
        <button 
          @click="confirmDelete"
          class="btn bg-danger-600 hover:bg-danger-700 text-white"
        >
          Delete Account
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { karmaService, authService } from '@/services/api'
import { StarIcon, PencilIcon, UserCircleIcon, KeyIcon, ShieldExclamationIcon, SparklesIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const editing = ref(false)
const loading = ref(false)
const passwordLoading = ref(false)
const passwordError = ref('')
const karmaHistory = ref([])

const form = reactive({
  username: authStore.user?.username || '',
  flat_number: authStore.user?.flat_number || ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const formatRole = (role) => {
  const roleMap = {
    admin: 'Administrator',
    secretary: 'Secretary',
    committee_member: 'Committee Member',
    resident: 'Resident'
  }
  return roleMap[role] || role || 'User'
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const cancelEdit = () => {
  editing.value = false
  form.username = authStore.user?.username || ''
  form.flat_number = authStore.user?.flat_number || ''
}

const updateProfile = async () => {
  loading.value = true
  try {
    await authStore.updateProfile(form)
    editing.value = false
    notificationsStore.showSuccess('Profile updated successfully')
  } catch (error) {
    notificationsStore.showError('Failed to update profile')
  } finally {
    loading.value = false
  }
}

const changePassword = async () => {
  passwordError.value = ''
  
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = 'Passwords do not match'
    return
  }
  
  passwordLoading.value = true
  try {
    await authService.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password
    })
    
    // Reset form
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    
    notificationsStore.showSuccess('Password changed successfully')
  } catch (error) {
    passwordError.value = error.response?.data?.message || 'Failed to change password'
  } finally {
    passwordLoading.value = false
  }
}

const confirmDelete = () => {
  if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    deleteAccount()
  }
}

const deleteAccount = async () => {
  try {
    await authService.deleteAccount()
    authStore.logout()
    router.push('/login')
    notificationsStore.showSuccess('Account deleted successfully')
  } catch (error) {
    notificationsStore.showError('Failed to delete account')
  }
}

onMounted(async () => {
  try {
    const res = await karmaService.getMyHistory()
    karmaHistory.value = res.data.data || []
  } catch (error) {
    console.error('Failed to fetch karma history:', error)
  }
})
</script>
