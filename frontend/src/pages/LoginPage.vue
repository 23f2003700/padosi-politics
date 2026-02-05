<template>
  <div>
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-gray-900">Welcome Back</h2>
      <p class="text-gray-500 mt-2">Sign in to your account to continue</p>
    </div>
    
    <form @submit.prevent="handleLogin" class="space-y-5">
      <!-- Email -->
      <div class="form-group">
        <label class="form-label">Email Address</label>
        <div class="relative">
          <input 
            v-model="form.email"
            type="email"
            required
            placeholder="your@email.com"
            class="input pl-11"
            :disabled="loading"
          />
          <EnvelopeIcon class="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
        </div>
      </div>
      
      <!-- Password -->
      <div class="form-group">
        <label class="form-label">Password</label>
        <div class="relative">
          <input 
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            required
            placeholder="••••••••"
            class="input pl-11 pr-11"
            :disabled="loading"
          />
          <LockClosedIcon class="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
          <button 
            type="button"
            @click="showPassword = !showPassword"
            class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
          >
            <EyeIcon v-if="!showPassword" class="w-5 h-5" />
            <EyeSlashIcon v-else class="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <!-- Remember Me & Forgot Password -->
      <div class="flex items-center justify-between text-sm">
        <label class="flex items-center cursor-pointer">
          <input type="checkbox" class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
          <span class="ml-2 text-gray-600">Remember me</span>
        </label>
        <a href="#" class="text-primary-600 hover:text-primary-700 font-medium">Forgot password?</a>
      </div>
      
      <!-- Error Message -->
      <div v-if="error" class="flex items-center gap-3 p-4 bg-red-50 border border-red-100 text-red-700 rounded-xl text-sm">
        <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0" />
        <span>{{ error }}</span>
      </div>
      
      <!-- Submit Button -->
      <button 
        type="submit"
        class="btn btn-primary w-full py-3"
        :disabled="loading"
      >
        <span v-if="loading" class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Signing in...
        </span>
        <span v-else class="flex items-center justify-center">
          Sign In
          <ArrowRightIcon class="w-5 h-5 ml-2" />
        </span>
      </button>
    </form>
    
    <!-- Divider -->
    <div class="relative my-8">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-200"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-4 bg-white text-gray-500">New to PadosiPolitics?</span>
      </div>
    </div>
    
    <!-- Register Link -->
    <router-link to="/register" class="btn btn-outline w-full py-3">
      Create an Account
    </router-link>
    
    <!-- Demo Credentials -->
    <div class="mt-8 p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200">
      <div class="flex items-center gap-2 mb-3">
        <BeakerIcon class="w-4 h-4 text-primary-600" />
        <p class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Demo Accounts</p>
      </div>
      <div class="space-y-2">
        <button 
          @click="fillDemo('admin@padosipolitics.com')"
          class="w-full flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-sm transition-all text-left group"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
              <ShieldCheckIcon class="w-4 h-4 text-amber-600" />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900 group-hover:text-primary-600">Admin</p>
              <p class="text-xs text-gray-500">admin@padosipolitics.com</p>
            </div>
          </div>
          <ChevronRightIcon class="w-4 h-4 text-gray-400 group-hover:text-primary-600" />
        </button>
        <button 
          @click="fillDemo('secretary@greenvalley.com')"
          class="w-full flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-sm transition-all text-left group"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <ClipboardDocumentIcon class="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900 group-hover:text-primary-600">Secretary</p>
              <p class="text-xs text-gray-500">secretary@greenvalley.com</p>
            </div>
          </div>
          <ChevronRightIcon class="w-4 h-4 text-gray-400 group-hover:text-primary-600" />
        </button>
        <button 
          @click="fillDemo('resident1@greenvalley.com')"
          class="w-full flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-sm transition-all text-left group"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <UserIcon class="w-4 h-4 text-green-600" />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900 group-hover:text-primary-600">Resident</p>
              <p class="text-xs text-gray-500">resident1@greenvalley.com</p>
            </div>
          </div>
          <ChevronRightIcon class="w-4 h-4 text-gray-400 group-hover:text-primary-600" />
        </button>
      </div>
    </div>
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
  EnvelopeIcon, 
  LockClosedIcon, 
  ArrowRightIcon,
  ExclamationCircleIcon,
  ShieldCheckIcon,
  ClipboardDocumentIcon,
  UserIcon,
  BeakerIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const form = reactive({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const fillDemo = (email) => {
  form.email = email
  form.password = 'password123'
}

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  const credentials = { 
    email: form.email.trim(), 
    password: form.password 
  }
  console.log('Login attempt with:', credentials.email) // Debug
  
  try {
    const result = await authStore.login(credentials)
    if (result.success) {
      notificationsStore.showSuccess('Welcome back!')
    } else {
      error.value = result.error || 'Login failed. Please try again.'
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
