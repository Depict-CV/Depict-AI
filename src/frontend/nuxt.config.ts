// https://nuxt.com/docs/api/configuration/nuxt-config
declare const process: { env: Record<string, string | undefined> }

const localMode = (process.env.VITE_LOCAL_MODE || 'false').toLowerCase() === 'true'
const authEnabled = (process.env.VITE_AUTH_ENABLED || (localMode ? 'false' : 'true')).toLowerCase() !== 'false'
const flag = (name: string, defaultValue = true) => {
  const value = process.env[name]
  if (value === undefined) return defaultValue
  return value.toLowerCase() !== 'false'
}

export default defineNuxtConfig({
  devtools: { enabled: true },

  experimental: {
    appManifest: false,
  },

  modules: ['@nuxtjs/tailwindcss'],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      clerkPublishableKey: process.env.VITE_CLERK_PUBLISHABLE_KEY || '',
      apiBaseUrl: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
      localMode,
      authEnabled,
      features: {
        annotatePage: flag('VITE_FEATURE_ANNOTATE_PAGE', true),
        sidebarProjects: flag('VITE_FEATURE_SIDEBAR_PROJECTS', true),
        sidebarDataAcquisition: flag('VITE_FEATURE_SIDEBAR_DATA_ACQUISITION', true),
        sidebarImport: flag('VITE_FEATURE_SIDEBAR_IMPORT', true),
        sidebarAi: flag('VITE_FEATURE_SIDEBAR_AI', true),
        sidebarFilter: flag('VITE_FEATURE_SIDEBAR_FILTER', true),
        sidebarStats: flag('VITE_FEATURE_SIDEBAR_STATS', true),
        sidebarModelAnalysis: flag('VITE_FEATURE_SIDEBAR_MODEL_ANALYSIS', true),
        sidebarExport: flag('VITE_FEATURE_SIDEBAR_EXPORT', true),
        sidebarProjectSettings: flag('VITE_FEATURE_SIDEBAR_PROJECT_SETTINGS', true),
        pageSubscription: flag('VITE_FEATURE_PAGE_SUBSCRIPTION', true),
        pageOrganisation: flag('VITE_FEATURE_PAGE_ORGANISATION', true),
        pageSettings: flag('VITE_FEATURE_PAGE_SETTINGS', true),
      },
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
