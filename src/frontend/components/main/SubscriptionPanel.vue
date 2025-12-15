<script setup>
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const closeDialog = () => {
  emit('close')
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="closeDialog"
  >
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-2xl font-bold">Subscription</h2>
        <button @click="closeDialog" class="text-gray-400 hover:text-gray-600 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto flex-1">
        <div class="space-y-6">
          <!-- Current Plan -->
          <div class="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border-2 border-blue-200">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xl font-bold text-blue-900">Pro Plan</h3>
              <span class="px-3 py-1 bg-blue-600 text-white text-xs font-semibold rounded-full">Active</span>
            </div>
            <p class="text-3xl font-bold text-blue-900 mb-2">$29<span class="text-lg font-normal">/month</span></p>
            <p class="text-sm text-blue-700">Renews on January 3, 2026</p>
          </div>

          <!-- Features -->
          <div>
            <h3 class="text-lg font-semibold mb-4">Plan Features</h3>
            <ul class="space-y-3">
              <li class="flex items-start gap-3">
                <div
                  class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5"
                >
                  ✓
                </div>
                <span class="text-gray-700">Unlimited projects</span>
              </li>
              <li class="flex items-start gap-3">
                <div
                  class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5"
                >
                  ✓
                </div>
                <span class="text-gray-700">10,000 images per month</span>
              </li>
              <li class="flex items-start gap-3">
                <div
                  class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5"
                >
                  ✓
                </div>
                <span class="text-gray-700">AI-powered annotation</span>
              </li>
              <li class="flex items-start gap-3">
                <div
                  class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5"
                >
                  ✓
                </div>
                <span class="text-gray-700">Priority support</span>
              </li>
              <li class="flex items-start gap-3">
                <div
                  class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5"
                >
                  ✓
                </div>
                <span class="text-gray-700">Team collaboration (up to 5 members)</span>
              </li>
            </ul>
          </div>

          <!-- Actions -->
          <div class="space-y-3">
            <button
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              Upgrade to Enterprise
            </button>
            <button
              class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors"
            >
              Manage Billing
            </button>
            <button
              class="w-full bg-red-50 hover:bg-red-100 text-red-600 font-medium py-3 px-4 rounded-lg transition-colors border border-red-200"
            >
              Cancel Subscription
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
