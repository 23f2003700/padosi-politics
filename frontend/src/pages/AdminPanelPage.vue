<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Admin Panel</h1>
      <p class="text-gray-500 mt-1">Manage your society, users, and system settings</p>
    </div>

    <!-- Tabs -->
    <div class="card mb-6 overflow-hidden">
      <nav class="flex overflow-x-auto bg-gray-50 border-b scrollbar-hide">
        <button 
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="py-3 sm:py-4 px-4 sm:px-6 font-medium text-sm transition-all border-b-2 -mb-px whitespace-nowrap flex-shrink-0"
          :class="activeTab === tab.id 
            ? 'border-primary-500 text-primary-600 bg-white' 
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-100'"
        >
          <component :is="tab.icon" class="w-5 h-5 inline-block mr-1 sm:mr-2" />
          <span class="hidden sm:inline">{{ tab.label }}</span>
          <span class="sm:hidden">{{ tab.label.split(' ')[0] }}</span>
        </button>
      </nav>
    </div>
    
    <!-- Overview Tab -->
    <div v-if="activeTab === 'overview'">
      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="card p-6 border-l-4 border-primary-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Total Users</p>
              <p class="text-3xl font-bold text-gray-900">{{ stats.total_users || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <UsersIcon class="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>
        <div class="card p-6 border-l-4 border-indigo-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Total Complaints</p>
              <p class="text-3xl font-bold text-gray-900">{{ stats.total_complaints || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
              <ClipboardDocumentListIcon class="w-6 h-6 text-indigo-600" />
            </div>
          </div>
        </div>
        <div class="card p-6 border-l-4 border-warning-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Pending Complaints</p>
              <p class="text-3xl font-bold text-warning-600">{{ stats.pending_complaints || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-warning-100 rounded-xl flex items-center justify-center">
              <ClockIcon class="w-6 h-6 text-warning-600" />
            </div>
          </div>
        </div>
        <div class="card p-6 border-l-4 border-success-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Resolution Rate</p>
              <p class="text-3xl font-bold text-success-600">{{ stats.resolution_rate || 0 }}%</p>
            </div>
            <div class="w-12 h-12 bg-success-100 rounded-xl flex items-center justify-center">
              <CheckCircleIcon class="w-6 h-6 text-success-600" />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="card p-6">
          <h3 class="font-semibold text-gray-900 mb-4 flex items-center">
            <ChartBarIcon class="w-5 h-5 mr-2 text-primary-500" />
            Complaints by Category
          </h3>
          <div class="space-y-3">
            <div v-for="(count, category) in stats.complaints_by_category" :key="category">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-600">{{ formatCategory(category) }}</span>
                <span class="font-medium">{{ count }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-primary-500 h-2 rounded-full"
                  :style="{ width: `${(count / stats.total_complaints) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="card p-6">
          <h3 class="font-semibold text-gray-900 mb-4 flex items-center">
            <ChartPieIcon class="w-5 h-5 mr-2 text-indigo-500" />
            Complaints by Status
          </h3>
          <div class="space-y-3">
            <div v-for="(count, status) in stats.complaints_by_status" :key="status">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-600">{{ formatStatus(status) }}</span>
                <span class="font-medium">{{ count }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  :class="statusBarColor(status)"
                  class="h-2 rounded-full"
                  :style="{ width: `${(count / stats.total_complaints) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Users Tab -->
    <div v-if="activeTab === 'users'">
      <div class="card overflow-hidden">
        <div class="p-4 border-b bg-gray-50 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div class="relative w-full sm:w-auto">
            <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              v-model="userSearch"
              type="text"
              placeholder="Search users..."
              class="input pl-10 w-full sm:max-w-xs"
            />
          </div>
        </div>
        
        <!-- Mobile Card View -->
        <div class="sm:hidden divide-y">
          <div v-for="user in filteredUsers" :key="user.id" class="p-4 space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                  <span class="text-primary-600 font-medium">{{ user.username?.charAt(0).toUpperCase() }}</span>
                </div>
                <div class="ml-3">
                  <p class="font-medium text-gray-900">{{ user.username }}</p>
                  <p class="text-xs text-gray-500">{{ user.email }}</p>
                </div>
              </div>
              <span 
                class="badge"
                :class="user.is_active ? 'badge-success' : 'badge-danger'"
              >
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">Flat: {{ user.flat_number }}</span>
              <span class="font-semibold text-success-600">{{ user.karma_points }} karma</span>
            </div>
            <div class="flex items-center justify-between">
              <select 
                v-model="user.role"
                @change="updateUserRole(user)"
                class="input py-1.5 text-sm flex-1 mr-3"
              >
                <option value="resident">Resident</option>
                <option value="committee_member">Committee</option>
                <option value="secretary">Secretary</option>
                <option value="admin">Admin</option>
              </select>
              <button 
                @click="toggleUserStatus(user)"
                class="btn btn-sm"
                :class="user.is_active ? 'btn-danger' : 'btn-success'"
              >
                {{ user.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Desktop Table View -->
        <div class="hidden sm:block overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Flat</th>
                <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Karma</th>
                <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-gray-50">
                <td class="px-4 lg:px-6 py-4">
                  <div class="flex items-center">
                    <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span class="text-primary-600 font-medium">{{ user.username?.charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="ml-3 min-w-0">
                      <p class="font-medium text-gray-900 truncate">{{ user.username }}</p>
                      <p class="text-sm text-gray-500 truncate hidden lg:block">{{ user.email }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-4 lg:px-6 py-4">
                  <select 
                    v-model="user.role"
                    @change="updateUserRole(user)"
                    class="input py-1 text-sm w-full max-w-[130px]"
                  >
                    <option value="resident">Resident</option>
                    <option value="committee_member">Committee</option>
                    <option value="secretary">Secretary</option>
                    <option value="admin">Admin</option>
                  </select>
                </td>
                <td class="px-4 lg:px-6 py-4 text-gray-500 hidden md:table-cell">{{ user.flat_number }}</td>
                <td class="px-4 lg:px-6 py-4">
                  <span class="font-semibold text-success-600">{{ user.karma_points }}</span>
                </td>
                <td class="px-4 lg:px-6 py-4">
                  <span 
                    class="badge"
                    :class="user.is_active ? 'badge-success' : 'badge-danger'"
                  >
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-4 lg:px-6 py-4">
                  <button 
                    @click="toggleUserStatus(user)"
                    class="text-sm whitespace-nowrap"
                    :class="user.is_active ? 'text-danger-600 hover:text-danger-700' : 'text-success-600 hover:text-success-700'"
                  >
                    {{ user.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Escalations Tab -->
    <div v-if="activeTab === 'escalations'">
      <div v-if="escalations.length === 0" class="card p-12 text-center">
        <ExclamationTriangleIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No escalations</h3>
        <p class="text-gray-500">All complaints are being handled properly!</p>
      </div>
      
      <div v-else class="space-y-4">
        <div 
          v-for="escalation in escalations"
          :key="escalation.id"
          class="card p-6 border-l-4 border-danger-500"
        >
          <div class="flex items-start justify-between">
            <div>
              <router-link 
                :to="`/complaints/${escalation.complaint_id}`"
                class="text-lg font-semibold text-gray-900 hover:text-primary-600"
              >
                {{ escalation.complaint?.title }}
              </router-link>
              <p class="text-sm text-danger-600 mt-1">{{ escalation.reason }}</p>
              <p class="text-xs text-gray-500 mt-2">
                Escalated on {{ formatDate(escalation.created_at) }}
              </p>
            </div>
            <button 
              @click="resolveEscalation(escalation)"
              class="btn btn-sm btn-primary"
            >
              Resolve
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- System Tasks Tab -->
    <div v-if="activeTab === 'tasks'">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Task Cards -->
        <div class="card p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="font-semibold text-gray-900">Auto-Escalate Complaints</h3>
              <p class="text-sm text-gray-500 mt-1">Escalate complaints open for 7+ days without action</p>
            </div>
            <div class="w-10 h-10 bg-warning-100 rounded-lg flex items-center justify-center">
              <ArrowPathIcon class="w-5 h-5 text-warning-600" />
            </div>
          </div>
          <button 
            @click="runTask('escalate')"
            :disabled="taskRunning.escalate"
            class="btn btn-primary w-full"
          >
            <ArrowPathIcon v-if="taskRunning.escalate" class="w-4 h-4 mr-2 animate-spin" />
            {{ taskRunning.escalate ? 'Running...' : 'Run Now' }}
          </button>
          <p v-if="taskResults.escalate" class="text-sm text-success-600 mt-2">
            ✓ {{ taskResults.escalate }}
          </p>
        </div>
        
        <div class="card p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="font-semibold text-gray-900">Send Reminders</h3>
              <p class="text-sm text-gray-500 mt-1">Notify secretaries about stale complaints (3+ days)</p>
            </div>
            <div class="w-10 h-10 bg-info-100 rounded-lg flex items-center justify-center">
              <BellIcon class="w-5 h-5 text-info-600" />
            </div>
          </div>
          <button 
            @click="runTask('reminders')"
            :disabled="taskRunning.reminders"
            class="btn btn-primary w-full"
          >
            <ArrowPathIcon v-if="taskRunning.reminders" class="w-4 h-4 mr-2 animate-spin" />
            {{ taskRunning.reminders ? 'Running...' : 'Run Now' }}
          </button>
          <p v-if="taskResults.reminders" class="text-sm text-success-600 mt-2">
            ✓ {{ taskResults.reminders }}
          </p>
        </div>
        
        <div class="card p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="font-semibold text-gray-900">Cleanup Old Notifications</h3>
              <p class="text-sm text-gray-500 mt-1">Delete read notifications older than 30 days</p>
            </div>
            <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <TrashIcon class="w-5 h-5 text-gray-600" />
            </div>
          </div>
          <button 
            @click="runTask('cleanup')"
            :disabled="taskRunning.cleanup"
            class="btn btn-secondary w-full"
          >
            <ArrowPathIcon v-if="taskRunning.cleanup" class="w-4 h-4 mr-2 animate-spin" />
            {{ taskRunning.cleanup ? 'Running...' : 'Run Now' }}
          </button>
          <p v-if="taskResults.cleanup" class="text-sm text-success-600 mt-2">
            ✓ {{ taskResults.cleanup }}
          </p>
        </div>
        
        <div class="card p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="font-semibold text-gray-900">Recalculate Statistics</h3>
              <p class="text-sm text-gray-500 mt-1">Refresh society dashboard statistics</p>
            </div>
            <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <ChartBarIcon class="w-5 h-5 text-primary-600" />
            </div>
          </div>
          <button 
            @click="runTask('stats')"
            :disabled="taskRunning.stats"
            class="btn btn-secondary w-full"
          >
            <ArrowPathIcon v-if="taskRunning.stats" class="w-4 h-4 mr-2 animate-spin" />
            {{ taskRunning.stats ? 'Running...' : 'Run Now' }}
          </button>
          <p v-if="taskResults.stats" class="text-sm text-success-600 mt-2">
            ✓ {{ taskResults.stats }}
          </p>
        </div>
      </div>
      
      <!-- Task System Info -->
      <div class="card p-6 mt-6">
        <h3 class="font-semibold text-gray-900 mb-4">System Information</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-500">Task Mode</p>
            <p class="font-semibold text-gray-900">{{ taskStatus.task_mode || 'Loading...' }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-500">Celery Status</p>
            <p class="font-semibold" :class="taskStatus.celery_enabled ? 'text-success-600' : 'text-gray-600'">
              {{ taskStatus.celery_enabled ? 'Enabled' : 'Disabled' }}
            </p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-500">Environment</p>
            <p class="font-semibold text-gray-900">{{ taskStatus.serverless_mode ? 'Serverless' : 'Standard' }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Settings Tab -->
    <div v-if="activeTab === 'settings'">
      <div class="card p-6 max-w-2xl">
        <h3 class="font-semibold text-gray-900 mb-4">Society Settings</h3>
        
        <form @submit.prevent="updateSettings" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Society Name</label>
            <input 
              v-model="settings.name"
              type="text"
              class="input"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <textarea 
              v-model="settings.address"
              rows="2"
              class="input"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Auto-escalation Days</label>
            <input 
              v-model.number="settings.auto_escalation_days"
              type="number"
              min="1"
              max="30"
              class="input max-w-xs"
            />
            <p class="text-xs text-gray-500 mt-1">Complaints will be auto-escalated after these many days</p>
          </div>
          
          <div class="flex justify-end pt-4">
            <button type="submit" class="btn btn-primary">
              Save Settings
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, markRaw } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'
import { dashboardService, societiesService, escalationsService, tasksService } from '@/services/api'
import { 
  ExclamationTriangleIcon, 
  UsersIcon, 
  ClipboardDocumentListIcon,
  ClockIcon,
  CheckCircleIcon,
  ChartBarIcon,
  ChartPieIcon,
  MagnifyingGlassIcon,
  Cog6ToothIcon,
  HomeModernIcon,
  ArrowPathIcon,
  BellIcon,
  TrashIcon,
  CpuChipIcon
} from '@heroicons/vue/24/outline'

const notificationsStore = useNotificationsStore()

const activeTab = ref('overview')
const tabs = [
  { id: 'overview', label: 'Overview', icon: markRaw(ChartBarIcon) },
  { id: 'users', label: 'Users', icon: markRaw(UsersIcon) },
  { id: 'escalations', label: 'Escalations', icon: markRaw(ArrowPathIcon) },
  { id: 'tasks', label: 'Tasks', icon: markRaw(CpuChipIcon) },
  { id: 'settings', label: 'Settings', icon: markRaw(Cog6ToothIcon) }
]

const stats = ref({})
const users = ref([])
const escalations = ref([])
const userSearch = ref('')

// Task management
const taskRunning = reactive({
  escalate: false,
  reminders: false,
  cleanup: false,
  stats: false
})

const taskResults = reactive({
  escalate: '',
  reminders: '',
  cleanup: '',
  stats: ''
})

const taskStatus = ref({
  celery_enabled: false,
  serverless_mode: false,
  task_mode: 'threaded'
})

const settings = reactive({
  name: '',
  address: '',
  auto_escalation_days: 7
})

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const search = userSearch.value.toLowerCase()
  return users.value.filter(u => 
    u.username?.toLowerCase().includes(search) ||
    u.email?.toLowerCase().includes(search) ||
    u.flat_number?.toLowerCase().includes(search)
  )
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

const statusBarColor = (status) => ({
  'bg-warning-500': status === 'pending',
  'bg-primary-500': status === 'in_progress',
  'bg-success-500': status === 'resolved',
  'bg-danger-500': status === 'escalated',
  'bg-gray-500': status === 'rejected'
})

const updateUserRole = async (user) => {
  try {
    await societiesService.updateUserRole(user.id, { role: user.role })
    notificationsStore.showSuccess('User role updated')
  } catch (error) {
    notificationsStore.showError('Failed to update role')
  }
}

const toggleUserStatus = async (user) => {
  try {
    await societiesService.toggleUserStatus(user.id)
    user.is_active = !user.is_active
    notificationsStore.showSuccess(`User ${user.is_active ? 'activated' : 'deactivated'}`)
  } catch (error) {
    notificationsStore.showError('Failed to update user status')
  }
}

const resolveEscalation = async (escalation) => {
  try {
    await escalationsService.resolve(escalation.id)
    escalations.value = escalations.value.filter(e => e.id !== escalation.id)
    notificationsStore.showSuccess('Escalation resolved')
  } catch (error) {
    notificationsStore.showError('Failed to resolve escalation')
  }
}

const updateSettings = async () => {
  try {
    await societiesService.updateSettings(settings)
    notificationsStore.showSuccess('Settings updated')
  } catch (error) {
    notificationsStore.showError('Failed to update settings')
  }
}

// Task management functions
const runTask = async (taskName) => {
  taskRunning[taskName] = true
  taskResults[taskName] = ''
  
  try {
    let result
    switch (taskName) {
      case 'escalate':
        result = await tasksService.runEscalation()
        taskResults[taskName] = result.data.message
        break
      case 'reminders':
        result = await tasksService.runReminders()
        taskResults[taskName] = result.data.message
        break
      case 'cleanup':
        result = await tasksService.runCleanup()
        taskResults[taskName] = result.data.message
        break
      case 'stats':
        result = await tasksService.calculateStats()
        taskResults[taskName] = 'Statistics recalculated successfully'
        break
    }
    notificationsStore.showSuccess(taskResults[taskName])
  } catch (error) {
    taskResults[taskName] = ''
    notificationsStore.showError(`Task failed: ${error.response?.data?.error || error.message}`)
  } finally {
    taskRunning[taskName] = false
  }
}

const fetchTaskStatus = async () => {
  try {
    const res = await tasksService.getStatus()
    taskStatus.value = res.data.data || {}
  } catch (error) {
    console.error('Failed to fetch task status:', error)
  }
}

onMounted(async () => {
  try {
    // Fetch admin stats
    const statsRes = await dashboardService.getAdminStats()
    stats.value = statsRes.data.data || {}
    
    // Fetch users
    const usersRes = await societiesService.getMembers()
    users.value = usersRes.data.data || []
    
    // Fetch escalations
    const escalationsRes = await escalationsService.getAll()
    escalations.value = escalationsRes.data.data || []
    
    // Fetch society settings
    const settingsRes = await societiesService.getSettings()
    Object.assign(settings, settingsRes.data.data || {})
    
    // Fetch task status
    await fetchTaskStatus()
  } catch (error) {
    console.error('Failed to fetch admin data:', error)
  }
})
</script>
