<script setup>
const props = defineProps({
  user: Object
})

const emit = defineEmits(['signOut'])
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Settings</h2>
    
    <div class="space-y-6">
      <!-- User Profile -->
      <div class="pb-6 border-b border-gray-200">
        <h3 class="text-lg font-semibold mb-4">Profile</h3>
        <div class="space-y-3">
          <div>
            <label class="text-sm text-gray-600">Username</label>
            <p class="text-gray-900 font-medium">{{ user?.username || 'Not set' }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-600">Email</label>
            <p class="text-gray-900 font-medium">{{ user?.primaryEmailAddress?.emailAddress }}</p>
          </div>
        </div>
      </div>

      <!-- Preferences -->
      <div class="pb-6 border-b border-gray-200">
        <h3 class="text-lg font-semibold mb-4">Preferences</h3>
        <div class="space-y-3">
          <label class="flex items-center justify-between">
            <span class="text-gray-700">Dark Mode</span>
            <input type="checkbox" class="w-5 h-5 rounded text-blue-600">
          </label>
          <label class="flex items-center justify-between">
            <span class="text-gray-700">Email Notifications</span>
            <input type="checkbox" class="w-5 h-5 rounded text-blue-600" checked>
          </label>
        </div>
      </div>

      <!-- Account Actions -->
      <div>
        <h3 class="text-lg font-semibold mb-4">Account</h3>
        <button 
          @click="$emit('signOut')"
          class="w-full bg-red-50 hover:bg-red-100 text-red-600 font-medium py-3 px-4 rounded-lg transition-colors border border-red-200"
        >
          Sign Out
        </button>
      </div>
    </div>
  </div>
</template>
