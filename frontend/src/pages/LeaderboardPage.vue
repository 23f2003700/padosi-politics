<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full mb-4 shadow-lg shadow-amber-500/30">
        <TrophyIcon class="w-8 h-8 text-white" />
      </div>
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Karma Leaderboard</h1>
      <p class="text-gray-500">Recognizing the top contributors in your society</p>
    </div>
    
    <!-- My Rank Card -->
    <div v-if="myRank" class="card p-4 sm:p-6 mb-8 bg-gradient-to-r from-primary-600 via-primary-700 to-indigo-700 text-white relative overflow-hidden">
      <div class="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full transform translate-x-10 -translate-y-10"></div>
      <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full transform -translate-x-10 translate-y-10"></div>
      <div class="flex flex-col sm:flex-row items-center sm:justify-between relative z-10 gap-4">
        <div class="flex items-center">
          <div class="w-14 h-14 sm:w-16 sm:h-16 bg-white/20 backdrop-blur rounded-full flex items-center justify-center ring-4 ring-white/30">
            <span class="text-xl sm:text-2xl font-bold">#{{ myRank.rank }}</span>
          </div>
          <div class="ml-4">
            <p class="text-base sm:text-lg font-semibold">Your Position</p>
            <p class="text-primary-100 text-sm">Keep contributing to climb up!</p>
          </div>
        </div>
        <div class="text-center sm:text-right">
          <p class="text-3xl sm:text-4xl font-bold">{{ myRank.karma_points }}</p>
          <p class="text-primary-100 text-sm">karma points</p>
        </div>
      </div>
    </div>
    
    <!-- Time Filter -->
    <div class="flex justify-center mb-6 px-2">
      <div class="inline-flex rounded-xl bg-gray-100 p-1 overflow-x-auto max-w-full">
        <button 
          v-for="period in periods"
          :key="period.value"
          @click="selectedPeriod = period.value; fetchLeaderboard()"
          class="px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap"
          :class="selectedPeriod === period.value 
            ? 'bg-white text-primary-600 shadow-md' 
            : 'text-gray-500 hover:text-gray-700'"
        >
          {{ period.label }}
        </button>
      </div>
    </div>
    
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Leaderboard -->
    <div v-else class="card overflow-hidden">
      <!-- Top 3 -->
      <div class="p-4 sm:p-6 bg-gradient-to-b from-gray-50 to-white">
        <div class="flex justify-center items-end space-x-2 sm:space-x-4 md:space-x-8">
          <!-- 2nd Place -->
          <div v-if="leaderboard[1]" class="text-center">
            <div class="relative">
              <div class="w-14 h-14 sm:w-20 sm:h-20 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center mx-auto shadow-lg">
                <span class="text-lg sm:text-2xl font-bold text-gray-600">
                  {{ leaderboard[1].full_name?.charAt(0).toUpperCase() }}
                </span>
              </div>
              <div class="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 w-6 h-6 sm:w-8 sm:h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold shadow text-sm sm:text-base">
                2
              </div>
            </div>
            <p class="mt-2 font-semibold text-gray-900 truncate max-w-[60px] sm:max-w-[80px] text-xs sm:text-sm">{{ leaderboard[1].full_name }}</p>
            <p class="text-xs sm:text-sm text-gray-500">{{ leaderboard[1].karma_score }} pts</p>
          </div>
          
          <!-- 1st Place -->
          <div v-if="leaderboard[0]" class="text-center -mt-4">
            <div class="relative">
              <div class="w-18 h-18 sm:w-24 sm:h-24 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full flex items-center justify-center mx-auto shadow-xl ring-4 ring-yellow-200" style="width: 4.5rem; height: 4.5rem;">
                <span class="text-2xl sm:text-3xl font-bold text-white">
                  {{ leaderboard[0].full_name?.charAt(0).toUpperCase() }}
                </span>
              </div>
              <div class="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 w-7 h-7 sm:w-10 sm:h-10 bg-yellow-500 rounded-full flex items-center justify-center shadow-lg">
                <TrophyIcon class="w-4 h-4 sm:w-6 sm:h-6 text-white" />
              </div>
            </div>
            <p class="mt-2 font-bold text-gray-900 truncate max-w-[70px] sm:max-w-[100px] text-xs sm:text-base">{{ leaderboard[0].full_name }}</p>
            <p class="text-xs sm:text-sm font-semibold text-yellow-600">{{ leaderboard[0].karma_score }} pts</p>
          </div>
          
          <!-- 3rd Place -->
          <div v-if="leaderboard[2]" class="text-center">
            <div class="relative">
              <div class="w-14 h-14 sm:w-20 sm:h-20 bg-orange-200 rounded-full flex items-center justify-center mx-auto">
                <span class="text-lg sm:text-2xl font-bold text-orange-600">
                  {{ leaderboard[2].full_name?.charAt(0).toUpperCase() }}
                </span>
              </div>
              <div class="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 w-6 h-6 sm:w-8 sm:h-8 bg-orange-400 rounded-full flex items-center justify-center text-white font-bold shadow text-sm sm:text-base">
                3
              </div>
            </div>
            <p class="mt-2 font-semibold text-gray-900 truncate max-w-[60px] sm:max-w-[80px] text-xs sm:text-sm">{{ leaderboard[2].full_name }}</p>
            <p class="text-xs sm:text-sm text-gray-500">{{ leaderboard[2].karma_score }} pts</p>
          </div>
        </div>
      </div>
      
      <!-- Rest of the list -->
      <div class="divide-y">
        <div 
          v-for="(user, index) in leaderboard.slice(3)"
          :key="user.user_id"
          class="flex items-center p-4 hover:bg-gray-50 transition-colors"
          :class="{ 'bg-primary-50': user.user_id === authStore.user?.id }"
        >
          <span class="w-8 text-center font-semibold text-gray-500">{{ index + 4 }}</span>
          <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center ml-4">
            <span class="font-semibold text-gray-600">
              {{ user.full_name?.charAt(0).toUpperCase() }}
            </span>
          </div>
          <div class="ml-4 flex-1">
            <p class="font-medium text-gray-900">{{ user.full_name }}</p>
            <p class="text-xs text-gray-500">{{ user.flat_number }}</p>
          </div>
          <div class="text-right">
            <p class="font-bold text-gray-900">{{ user.karma_score }}</p>
            <p class="text-xs text-gray-500">points</p>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="leaderboard.length === 0" class="p-12 text-center">
        <TrophyIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No data yet</h3>
        <p class="text-gray-500">Start contributing to appear on the leaderboard!</p>
      </div>
    </div>
    
    <!-- How to Earn Karma -->
    <div class="card p-6 mt-8">
      <h3 class="font-semibold text-gray-900 mb-4">How to Earn Karma Points</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex items-start">
          <div class="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
            <span class="text-success-600 font-bold">+5</span>
          </div>
          <div>
            <p class="font-medium text-gray-900">File a Complaint</p>
            <p class="text-sm text-gray-500">Report issues to earn points</p>
          </div>
        </div>
        <div class="flex items-start">
          <div class="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
            <span class="text-success-600 font-bold">+10</span>
          </div>
          <div>
            <p class="font-medium text-gray-900">Complaint Resolved</p>
            <p class="text-sm text-gray-500">When your complaint is resolved</p>
          </div>
        </div>
        <div class="flex items-start">
          <div class="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
            <span class="text-success-600 font-bold">+2</span>
          </div>
          <div>
            <p class="font-medium text-gray-900">Comment on Complaints</p>
            <p class="text-sm text-gray-500">Engage with community issues</p>
          </div>
        </div>
        <div class="flex items-start">
          <div class="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
            <span class="text-success-600 font-bold">+1</span>
          </div>
          <div>
            <p class="font-medium text-gray-900">Vote on Complaints</p>
            <p class="text-sm text-gray-500">Support important issues</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { karmaService } from '@/services/api'
import { TrophyIcon } from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const loading = ref(true)
const leaderboard = ref([])
const myRank = ref(null)
const selectedPeriod = ref('all')

const periods = [
  { value: 'all', label: 'All Time' },
  { value: 'month', label: 'This Month' },
  { value: 'week', label: 'This Week' }
]

const fetchLeaderboard = async () => {
  loading.value = true
  try {
    const res = await karmaService.getLeaderboard({ 
      limit: 20,
      period: selectedPeriod.value
    })
    leaderboard.value = res.data.data?.leaderboard || []
    
    // Find current user's rank
    const userIndex = leaderboard.value.findIndex(u => u.user_id === authStore.user?.id)
    if (userIndex !== -1) {
      myRank.value = {
        rank: userIndex + 1,
        karma_points: leaderboard.value[userIndex].karma_score
      }
    }
  } catch (error) {
    console.error('Failed to fetch leaderboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLeaderboard()
})
</script>
