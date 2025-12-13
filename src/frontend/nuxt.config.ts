// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: ['@nuxtjs/tailwindcss'],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      clerkPublishableKey: process.env.VITE_CLERK_PUBLISHABLE_KEY || '',
      apiBaseUrl: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
    },
  },

  app: {
    head: {
      title: 'Depict AI',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Image data tool for computer vision' },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },

  compatibilityDate: '2024-12-03',
})
