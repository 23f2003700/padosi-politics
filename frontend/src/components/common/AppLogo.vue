<template>
  <div class="flex items-center" :class="containerClass">
    <!-- SVG Logo -->
    <div 
      class="relative flex items-center justify-center rounded-xl overflow-hidden"
      :class="[sizeClasses.container, variant === 'light' ? 'bg-white/10 backdrop-blur-sm' : 'bg-gradient-to-br from-primary-500 to-primary-700']"
    >
      <!-- Building Icon -->
      <svg 
        :class="sizeClasses.icon" 
        viewBox="0 0 40 40" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Main Building -->
        <rect x="8" y="12" width="24" height="24" rx="2" :fill="variant === 'light' ? 'white' : '#ffffff'" fill-opacity="0.9"/>
        <!-- Windows Row 1 -->
        <rect x="11" y="15" width="4" height="4" rx="0.5" :fill="variant === 'light' ? '#7c3aed' : '#7c3aed'"/>
        <rect x="18" y="15" width="4" height="4" rx="0.5" :fill="variant === 'light' ? '#7c3aed' : '#7c3aed'"/>
        <rect x="25" y="15" width="4" height="4" rx="0.5" :fill="variant === 'light' ? '#7c3aed' : '#7c3aed'"/>
        <!-- Windows Row 2 -->
        <rect x="11" y="22" width="4" height="4" rx="0.5" :fill="variant === 'light' ? '#7c3aed' : '#7c3aed'"/>
        <rect x="18" y="22" width="4" height="4" rx="0.5" :fill="variant === 'light' ? '#7c3aed' : '#7c3aed'"/>
        <rect x="25" y="22" width="4" height="4" rx="0.5" :fill="variant === 'light' ? '#7c3aed' : '#7c3aed'"/>
        <!-- Door -->
        <rect x="16" y="29" width="8" height="7" rx="1" :fill="variant === 'light' ? '#7c3aed' : '#7c3aed'"/>
        <!-- Roof -->
        <path d="M6 14L20 4L34 14H6Z" :fill="variant === 'light' ? 'white' : '#ffffff'" fill-opacity="0.9"/>
        <!-- Chimney -->
        <rect x="26" y="6" width="4" height="6" rx="0.5" :fill="variant === 'light' ? 'white' : '#ffffff'" fill-opacity="0.7"/>
        <!-- Speech bubbles representing community -->
        <circle cx="8" cy="8" r="3" :fill="variant === 'light' ? '#22c55e' : '#22c55e'" fill-opacity="0.9"/>
        <circle cx="32" cy="8" r="3" :fill="variant === 'light' ? '#f59e0b' : '#f59e0b'" fill-opacity="0.9"/>
      </svg>
    </div>
    
    <!-- Text -->
    <div v-if="showText" :class="['ml-3', sizeClasses.textContainer]">
      <h1 :class="[sizeClasses.title, variant === 'light' ? 'text-white' : 'text-gray-900']">
        Padosi<span :class="variant === 'light' ? 'text-primary-200' : 'text-primary-600'">Politics</span>
      </h1>
      <p v-if="showTagline" :class="[sizeClasses.tagline, variant === 'light' ? 'text-primary-100' : 'text-gray-800 font-bold']">
        Society Complaint Management
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md', // sm, md, lg, xl
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  variant: {
    type: String,
    default: 'dark', // dark, light
    validator: (value) => ['dark', 'light'].includes(value)
  },
  showText: {
    type: Boolean,
    default: true
  },
  showTagline: {
    type: Boolean,
    default: false
  }
})

const containerClass = computed(() => {
  return props.showText ? '' : 'justify-center'
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: {
      container: 'w-8 h-8',
      icon: 'w-6 h-6',
      textContainer: '',
      title: 'text-sm font-bold',
      tagline: 'text-xs'
    },
    md: {
      container: 'w-10 h-10',
      icon: 'w-7 h-7',
      textContainer: '',
      title: 'text-lg font-bold',
      tagline: 'text-xs'
    },
    lg: {
      container: 'w-14 h-14',
      icon: 'w-10 h-10',
      textContainer: '',
      title: 'text-xl font-bold',
      tagline: 'text-sm'
    },
    xl: {
      container: 'w-20 h-20',
      icon: 'w-14 h-14',
      textContainer: '',
      title: 'text-3xl font-bold',
      tagline: 'text-base'
    }
  }
  return sizes[props.size]
})
</script>
