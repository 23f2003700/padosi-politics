import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// Capacitor
import { Capacitor } from '@capacitor/core'
import { SplashScreen } from '@capacitor/splash-screen'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Hide splash screen after app is mounted
app.mount('#app')

// Handle Capacitor splash screen
if (Capacitor.isNativePlatform()) {
  // Wait a bit for the app to render, then hide splash
  setTimeout(async () => {
    await SplashScreen.hide({
      fadeOutDuration: 500
    })
  }, 1500)
}
