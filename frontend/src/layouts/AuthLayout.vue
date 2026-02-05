<template>
  <div class="min-h-screen flex">
    <!-- Left Panel - Branding with bg.png -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden">
      <!-- Background Image -->
      <img src="/bg.png" alt="" class="absolute inset-0 w-full h-full object-cover" />
      <!-- White overlay for translucency -->
      <div class="absolute inset-0 bg-white/60"></div>
      
      <!-- Content with dark text for visibility -->
      <div class="relative z-10 flex flex-col items-center w-full h-full px-12 py-8">
        <!-- Logo at top center -->
        <div class="w-full flex justify-center">
          <AppLogo size="xl" variant="dark" :showText="true" :showTagline="true" />
        </div>
        
        <!-- Features in middle -->
        <div class="flex-1 flex flex-col justify-center">
          <div class="space-y-6 max-w-md">
            <div class="flex items-start space-x-4 bg-white/80 backdrop-blur-md rounded-xl p-4 shadow-lg">
              <div class="w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <ClipboardDocumentCheckIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-gray-900 font-bold">Voice Your Concerns</h3>
                <p class="text-gray-600 text-sm">File complaints and track their resolution in real-time</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 bg-white/80 backdrop-blur-md rounded-xl p-4 shadow-lg">
              <div class="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <UsersIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-gray-900 font-bold">Community Driven</h3>
                <p class="text-gray-600 text-sm">Support complaints with votes and build community consensus</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 bg-white/80 backdrop-blur-md rounded-xl p-4 shadow-lg">
              <div class="w-12 h-12 bg-amber-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <SparklesIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-gray-900 font-bold">Earn Karma Points</h3>
                <p class="text-gray-600 text-sm">Contribute positively and climb the society leaderboard</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Right Panel - Auth Form with Role Icons -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-50 to-gray-100 relative overflow-hidden min-h-screen">
      <!-- Floating Role Icons as Background -->
      <img src="/admin-icon.svg" alt="" class="absolute top-10 right-10 w-16 sm:w-24 h-16 sm:h-24 opacity-10 animate-float" style="animation-delay: 0s;" />
      <img src="/secretary-icon.svg" alt="" class="absolute bottom-32 right-20 w-14 sm:w-20 h-14 sm:h-20 opacity-10 animate-float hidden sm:block" style="animation-delay: 0.5s;" />
      <img src="/resident-icon.svg" alt="" class="absolute top-1/3 right-8 w-12 sm:w-16 h-12 sm:h-16 opacity-10 animate-float hidden sm:block" style="animation-delay: 1s;" />
      <img src="/admin-icon.svg" alt="" class="absolute bottom-10 right-1/3 w-10 sm:w-14 h-10 sm:h-14 opacity-5 animate-float hidden sm:block" style="animation-delay: 1.5s;" />
      <img src="/resident-icon.svg" alt="" class="absolute top-20 left-10 w-12 sm:w-16 h-12 sm:h-16 opacity-5 animate-float lg:hidden" style="animation-delay: 0.3s;" />
      
      <!-- Decorative circles -->
      <div class="absolute -top-20 -right-20 w-48 sm:w-64 h-48 sm:h-64 bg-primary-100 rounded-full opacity-30 blur-3xl"></div>
      <div class="absolute -bottom-32 -left-20 w-64 sm:w-80 h-64 sm:h-80 bg-indigo-100 rounded-full opacity-30 blur-3xl"></div>
      
      <div class="w-full max-w-md relative z-10">
        <!-- Mobile Logo -->
        <div class="lg:hidden text-center mb-6 sm:mb-8">
          <AppLogo size="lg" variant="dark" :showText="true" :showTagline="true" />
        </div>
        
        <!-- Auth Card -->
        <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-2xl p-5 sm:p-8 border border-white/50">
          <router-view />
        </div>
        
        <!-- Role Badges -->
        <div class="mt-4 sm:mt-6 flex justify-center gap-2 sm:gap-4 flex-wrap">
          <div class="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 bg-white/60 backdrop-blur rounded-full border border-amber-200">
            <img src="/admin-icon.svg" alt="" class="w-4 h-4 sm:w-5 sm:h-5" />
            <span class="text-xs font-medium text-amber-700">Admin</span>
          </div>
          <div class="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 bg-white/60 backdrop-blur rounded-full border border-blue-200">
            <img src="/secretary-icon.svg" alt="" class="w-5 h-5" />
            <span class="text-xs font-medium text-blue-700">Secretary</span>
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur rounded-full border border-green-200">
            <img src="/resident-icon.svg" alt="" class="w-5 h-5" />
            <span class="text-xs font-medium text-green-700">Resident</span>
          </div>
        </div>
        
        <!-- Footer -->
        <p class="text-center text-gray-400 text-xs mt-6">
          Built for IIT Madras BS Program by Aaryan (23F2003700)
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import AppLogo from '@/components/common/AppLogo.vue'
import { ClipboardDocumentCheckIcon, UsersIcon, SparklesIcon } from '@heroicons/vue/24/outline'
</script>

<style scoped>
@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(5deg); }
}

.animate-float {
  animation: float 4s ease-in-out infinite;
}
</style>
