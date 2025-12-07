<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Subscription</h2>
    
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
            <div class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">✓</div>
            <span class="text-gray-700">Unlimited projects</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">✓</div>
            <span class="text-gray-700">10,000 images per month</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">✓</div>
            <span class="text-gray-700">AI-powered annotation</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">✓</div>
            <span class="text-gray-700">Priority support</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">✓</div>
            <span class="text-gray-700">Team collaboration (up to 5 members)</span>
          </li>
        </ul>
      </div>

      <!-- Actions -->
      <div class="space-y-3">
        <button class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors">
          Upgrade to Enterprise
        </button>
        <button class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors">
          Manage Billing
        </button>
        <button class="w-full bg-red-50 hover:bg-red-100 text-red-600 font-medium py-3 px-4 rounded-lg transition-colors border border-red-200">
          Cancel Subscription
        </button>
      </div>
    </div>
  </div>
</template>
