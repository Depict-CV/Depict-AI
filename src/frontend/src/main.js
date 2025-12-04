 import { createApp } from 'vue'
import { clerkPlugin } from '@clerk/vue'
import App from './App.vue'
import './style.css'

const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!clerkPublishableKey) {
  throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY in environment variables')
}

const app = createApp(App)

app.use(clerkPlugin, {
  publishableKey: clerkPublishableKey,
})

app.mount('#app')
