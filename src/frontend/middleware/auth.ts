export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip auth check on server-side
  if (process.server) {
    return
  }

  const { $clerk } = useNuxtApp()
  
  // Wait for Clerk to be ready
  if (!$clerk) {
    return
  }

  // Check if user is signed in
  const isSignedIn = $clerk.user !== null && $clerk.user !== undefined
  
  if (!isSignedIn && to.path !== '/login') {
    return navigateTo('/login')
  }

  if (isSignedIn && to.path === '/login') {
    return navigateTo('/')
  }
})
