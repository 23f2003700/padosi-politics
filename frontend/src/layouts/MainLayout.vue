<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Sidebar -->
    <aside 
      class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 lg:translate-x-0 border-r border-gray-100"
      :class="{ '-translate-x-full': !sidebarOpen }"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center px-4 border-b border-gray-100 bg-gradient-to-r from-primary-50 to-white">
        <AppLogo size="md" variant="dark" :showText="true" />
      </div>
      
      <!-- Navigation -->
      <nav class="p-4 space-y-1">
        <router-link 
          v-for="item in navigationItems" 
          :key="item.to"
          :to="item.to"
          class="nav-item group"
          active-class="nav-item-active"
        >
          <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-gray-100 group-hover:bg-primary-100 transition-colors mr-3"
               :class="{ 'bg-primary-100': $route.path === item.to }">
            <component :is="item.icon" class="w-5 h-5 text-gray-500 group-hover:text-primary-600 transition-colors"
                       :class="{ 'text-primary-600': $route.path === item.to }" />
          </div>
          {{ item.label }}
        </router-link>
        
        <!-- Admin Section -->
        <template v-if="authStore.isAdmin || authStore.isSecretary">
          <div class="pt-4 mt-4 border-t border-gray-100">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">Management</p>
            <router-link 
              to="/admin"
              class="nav-item group"
              active-class="nav-item-active"
            >
              <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-gray-100 group-hover:bg-primary-100 transition-colors mr-3"
                   :class="{ 'bg-primary-100': $route.path === '/admin' }">
                <ShieldCheckIcon class="w-5 h-5 text-gray-500 group-hover:text-primary-600 transition-colors"
                                 :class="{ 'text-primary-600': $route.path === '/admin' }" />
              </div>
              Admin Panel
            </router-link>
          </div>
        </template>
      </nav>
      
      <!-- User Info -->
      <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100 bg-gradient-to-r from-gray-50 to-white">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center shadow-md">
            <span class="text-white font-semibold text-sm">
              {{ authStore.user?.full_name?.charAt(0).toUpperCase() || 'U' }}
            </span>
          </div>
          <div class="ml-3 flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">
              {{ authStore.user?.full_name || 'User' }}
            </p>
            <p class="text-xs text-gray-500 truncate flex items-center">
              <span class="w-2 h-2 bg-success-400 rounded-full mr-1.5"></span>
              {{ formatRole(authStore.user?.roles?.[0]) }}
            </p>
          </div>
          <button @click="handleLogout" class="p-2 text-gray-400 hover:text-danger-500 hover:bg-danger-50 rounded-lg transition-all">
            <ArrowRightOnRectangleIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </aside>
    
    <!-- Mobile Overlay -->
    <div 
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
      @click="sidebarOpen = false"
    ></div>
    
    <!-- Main Content -->
    <div class="lg:ml-64">
      <!-- Header -->
      <header class="h-16 bg-white/80 backdrop-blur-md shadow-sm flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30 border-b border-gray-100">
        <div class="flex items-center">
          <button 
            @click="sidebarOpen = true"
            class="lg:hidden p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Bars3Icon class="w-6 h-6" />
          </button>
          <h1 class="text-xl font-semibold text-gray-900 ml-2 lg:ml-0">
            {{ currentPageTitle }}
          </h1>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- Karma Display -->
          <div class="hidden sm:flex items-center space-x-2 bg-gradient-to-r from-success-50 to-emerald-50 px-4 py-2 rounded-full border border-success-100">
            <div class="w-6 h-6 bg-success-500 rounded-full flex items-center justify-center">
              <StarIcon class="w-4 h-4 text-white" />
            </div>
            <span class="font-bold text-success-700">{{ authStore.user?.karma_score || 0 }}</span>
            <span class="text-success-600 text-sm hidden md:inline">Karma</span>
          </div>
          
          <!-- Notifications -->
          <router-link 
            to="/notifications"
            class="relative p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all"
          >
            <BellIcon class="w-6 h-6" />
            <span 
              v-if="notificationsStore.unreadCount > 0"
              class="absolute -top-1 -right-1 w-5 h-5 bg-danger-500 text-white text-xs font-bold rounded-full flex items-center justify-center shadow-md animate-pulse"
            >
              {{ notificationsStore.unreadCount > 9 ? '9+' : notificationsStore.unreadCount }}
            </span>
          </router-link>
          
          <!-- Profile -->
          <router-link 
            to="/profile"
            class="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all"
          >
            <UserCircleIcon class="w-6 h-6" />
          </router-link>
        </div>
      </header>
      
      <!-- Page Content -->
      <main class="p-4 lg:p-8">
        <router-view />
      </main>
      
      <!-- Footer -->
      <footer class="p-4 lg:p-8 text-center text-gray-400 text-sm border-t border-gray-100 bg-white/50">
        <p>© 2026 Padosi Politics • Built by Aaryan (23F2003700) for IIT Madras BS Program</p>
      </footer>
    </div>
    
    <!-- Toast Notifications -->
    <Teleport to="#toast-container">
      <TransitionGroup name="toast" tag="div" class="space-y-3">
        <div 
          v-for="toast in notificationsStore.toasts"
          :key="toast.id"
          class="toast pointer-events-auto"
          :class="toastClass(toast.type)"
        >
          <component :is="toastIcon(toast.type)" class="w-5 h-5 mr-3 flex-shrink-0" />
          <p class="flex-1 text-sm font-medium">{{ toast.message }}</p>
          <button 
            @click="notificationsStore.removeToast(toast.id)" 
            class="ml-3 p-1 rounded-full hover:bg-black/10 transition-colors cursor-pointer"
          >
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import AppLogo from '@/components/common/AppLogo.vue'
import {
  HomeIcon,
  ClipboardDocumentListIcon,
  PlusCircleIcon,
  DocumentTextIcon,
  TrophyIcon,
  ShieldCheckIcon,
  Bars3Icon,
  BellIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  StarIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const sidebarOpen = ref(false)

const navigationItems = [
  { to: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { to: '/complaints', label: 'All Complaints', icon: ClipboardDocumentListIcon },
  { to: '/complaints/new', label: 'New Complaint', icon: PlusCircleIcon },
  { to: '/my-complaints', label: 'My Complaints', icon: DocumentTextIcon },
  { to: '/leaderboard', label: 'Leaderboard', icon: TrophyIcon },
]

const currentPageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/complaints': 'All Complaints',
    '/complaints/new': 'New Complaint',
    '/my-complaints': 'My Complaints',
    '/leaderboard': 'Karma Leaderboard',
    '/profile': 'My Profile',
    '/notifications': 'Notifications',
    '/admin': 'Admin Panel',
  }
  return titles[route.path] || 'Padosi Politics'
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

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const toastClass = (type) => ({
  'toast-success': type === 'success',
  'toast-error': type === 'error',
  'toast-warning': type === 'warning',
  'toast-info': type === 'info',
})

const toastIcon = (type) => {
  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationTriangleIcon,
    info: InformationCircleIcon
  }
  return icons[type] || InformationCircleIcon
}

onMounted(() => {
  // Fetch notifications on mount
  notificationsStore.fetchNotifications()
})
</script>

<style scoped>
.nav-item {
  @apply flex items-center px-3 py-2.5 text-gray-600 rounded-lg transition-colors hover:bg-gray-100;
}

.nav-item-active {
  @apply bg-primary-50 text-primary-600 font-medium;
}

.toast {
  @apply flex items-center p-4 rounded-lg shadow-lg border;
}

.toast-success {
  @apply bg-success-50 text-success-700 border-success-200;
}

.toast-error {
  @apply bg-danger-50 text-danger-700 border-danger-200;
}

.toast-warning {
  @apply bg-warning-50 text-warning-700 border-warning-200;
}

.toast-info {
  @apply bg-primary-50 text-primary-700 border-primary-200;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
