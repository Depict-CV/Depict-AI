export const useAuth = () => {
  const config = useRuntimeConfig()
  const authEnabled = config.public.authEnabled
  const { $clerk } = useNuxtApp()

  const localUser = {
    id: 'local-dev-user',
    username: 'local-dev-user',
    emailAddresses: [{ emailAddress: 'local-dev-user@local.dev' }],
  }

  const isSignedIn = computed(() => {
    if (!authEnabled) return true
    if (!$clerk) return false
    return !!$clerk.session
  })

  const user = computed(() => {
    if (!authEnabled) return localUser
    if (!$clerk) return null
    return $clerk.user
  })

  const signOut = async () => {
    if (!authEnabled) return
    if (!$clerk) return
    await $clerk.signOut()
    navigateTo('/login')
  }

  const openSignIn = async () => {
    if (!authEnabled) {
      navigateTo('/')
      return
    }
    if (!$clerk) return
    await $clerk.openSignIn({
      afterSignInUrl: '/',
      redirectUrl: '/',
    })
  }

  return {
    isSignedIn,
    user,
    signOut,
    openSignIn,
  }
}
