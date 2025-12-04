<script setup>
const { openSignIn, isSignedIn } = useAuth()

// Redirect if already signed in
watch(isSignedIn, (signedIn) => {
  if (signedIn) {
    navigateTo('/')
  }
}, { immediate: true })
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100">
    <div class="bg-white p-10 rounded-2xl shadow-2xl max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-3">Depict AI</h1>
        <p class="text-gray-600 text-lg">Image data tool for computer vision</p>
      </div>

      <button 
        @click="openSignIn"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
      >
        Sign in with Clerk
      </button>

      <div class="mt-8 text-center">
        <p class="text-sm text-gray-500">
          Secure authentication powered by Clerk
        </p>
      </div>
    </div>
  </div>
</template>
