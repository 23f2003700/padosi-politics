<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Toast Notifications -->
    <Teleport to="body">
      <ToastNotification />
    </Teleport>
    
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ToastNotification from '@/components/common/ToastNotification.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Check for existing token and load user
  authStore.initializeAuth()
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
