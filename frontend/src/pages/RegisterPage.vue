<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 text-center mb-2">Create Account</h2>
    <p class="text-center text-gray-500 mb-6">Join your society community today</p>
    
    <form @submit.prevent="handleRegister" class="space-y-4">
      <!-- Username -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          <span class="flex items-center">
            <UserIcon class="w-4 h-4 mr-1.5 text-gray-400" />
            Username
          </span>
        </label>
        <input 
          v-model="form.username"
          type="text"
          required
          placeholder="johndoe"
          class="input"
          :disabled="loading"
        />
      </div>
      
      <!-- Email -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          <span class="flex items-center">
            <EnvelopeIcon class="w-4 h-4 mr-1.5 text-gray-400" />
            Email Address
          </span>
        </label>
        <input 
          v-model="form.email"
          type="email"
          required
          placeholder="your@email.com"
          class="input"
          :disabled="loading"
        />
      </div>
      
      <div class="grid grid-cols-2 gap-4">
        <!-- Flat Number -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            <span class="flex items-center">
              <HomeIcon class="w-4 h-4 mr-1.5 text-gray-400" />
              Flat Number
            </span>
          </label>
          <input 
            v-model="form.flat_number"
            type="text"
            required
            placeholder="A-101"
            class="input"
            :disabled="loading"
          />
        </div>
        
        <!-- Society Code -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            <span class="flex items-center">
              <BuildingOfficeIcon class="w-4 h-4 mr-1.5 text-gray-400" />
              Society Code
            </span>
          </label>
          <input 
            v-model="form.society_code"
            type="text"
            required
            placeholder="SOC123"
            class="input"
            :disabled="loading"
          />
        </div>
      </div>
      <p class="text-xs text-gray-500 -mt-2">Get society code from your society admin or secretary</p>
      
      <!-- Password -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          <span class="flex items-center">
            <LockClosedIcon class="w-4 h-4 mr-1.5 text-gray-400" />
            Password
          </span>
        </label>
        <div class="relative">
          <input 
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            required
            minlength="6"
            placeholder="••••••••"
            class="input pr-10"
            :disabled="loading"
          />
          <button 
            type="button"
            @click="showPassword = !showPassword"
            class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
          >
            <EyeIcon v-if="!showPassword" class="w-5 h-5" />
            <EyeSlashIcon v-else class="w-5 h-5" />
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
      </div>
      
      <!-- Confirm Password -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          <span class="flex items-center">
            <ShieldCheckIcon class="w-4 h-4 mr-1.5 text-gray-400" />
            Confirm Password
          </span>
        </label>
        <input 
          v-model="form.confirm_password"
          :type="showPassword ? 'text' : 'password'"
          required
          placeholder="••••••••"
          class="input"
          :disabled="loading"
        />
      </div>
      
      <!-- Error Message -->
      <div v-if="error" class="flex items-start p-3 bg-danger-50 text-danger-700 rounded-lg text-sm">
        <ExclamationCircleIcon class="w-5 h-5 mr-2 flex-shrink-0" />
        {{ error }}
      </div>
      
      <!-- Terms -->
      <div class="flex items-start">
        <input 
          id="terms" 
          type="checkbox" 
          required
          class="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label for="terms" class="ml-2 text-sm text-gray-600">
          I agree to the <a href="#" class="text-primary-600 hover:underline">Terms of Service</a> and <a href="#" class="text-primary-600 hover:underline">Privacy Policy</a>
        </label>
      </div>
      
      <!-- Submit Button -->
      <button 
        type="submit"
        class="btn btn-primary w-full"
        :disabled="loading"
      >
        <span v-if="loading" class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Creating account...
        </span>
        <span v-else class="flex items-center justify-center">
          <UserPlusIcon class="w-5 h-5 mr-2" />
          Create Account
        </span>
      </button>
    </form>
    
    <!-- Divider -->
    <div class="relative my-6">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-200"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-3 bg-white text-gray-500">Already have an account?</span>
      </div>
    </div>
    
    <!-- Login Link -->
    <router-link 
      to="/login" 
      class="btn w-full border-2 border-primary-200 bg-primary-50 text-primary-700 hover:bg-primary-100"
    >
      <ArrowLeftOnRectangleIcon class="w-5 h-5 mr-2" />
      Sign in to your account
    </router-link>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { 
  EyeIcon, 
  EyeSlashIcon, 
  UserIcon, 
  EnvelopeIcon, 
  HomeIcon, 
  BuildingOfficeIcon, 
  LockClosedIcon, 
  ShieldCheckIcon,
  ExclamationCircleIcon,
  UserPlusIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const form = reactive({
  username: '',
  email: '',
  flat_number: '',
  society_code: '',
  password: '',
  confirm_password: ''
})

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const handleRegister = async () => {
  // Validate passwords match
  if (form.password !== form.confirm_password) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await authStore.register({
      username: form.username,
      email: form.email,
      flat_number: form.flat_number,
      society_code: form.society_code,
      password: form.password
    })
    notificationsStore.showSuccess('Account created successfully!')
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.message || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
