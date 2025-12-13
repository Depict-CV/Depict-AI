import { Clerk } from '@clerk/clerk-js'

export default defineNuxtPlugin({
  name: 'clerk',
  enforce: 'pre', // Load before other plugins
  async setup() {
    const config = useRuntimeConfig()
    const clerkPublishableKey = config.public.clerkPublishableKey

    if (!clerkPublishableKey) {
      console.error('Missing VITE_CLERK_PUBLISHABLE_KEY in environment variables')
      return {
        provide: {
          clerk: null,
        },
      }
    }

    const clerk = new Clerk(clerkPublishableKey)
    await clerk.load()

    return {
      provide: {
        clerk,
      },
    }
  },
})
