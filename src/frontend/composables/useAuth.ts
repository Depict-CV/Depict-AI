export const useAuth = () => {
  const { $clerk } = useNuxtApp()

  const isSignedIn = computed(() => {
    if (!$clerk) return false
    return !!$clerk.session
  })

  const user = computed(() => {
    if (!$clerk) return null
    return $clerk.user
  })

  const signOut = async () => {
    if (!$clerk) return
    await $clerk.signOut()
    navigateTo('/login')
  }

  const openSignIn = async () => {
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
