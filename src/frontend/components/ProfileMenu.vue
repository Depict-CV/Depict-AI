<script setup>
import { User, CreditCard, Settings, Building2, LogOut } from 'lucide-vue-next'

const props = defineProps({
  user: Object,
  showProfileMenu: Boolean
})

const emit = defineEmits(['close', 'openPanel', 'signOut', 'openSettings'])

const openPanel = (panel) => {
  emit('openPanel', panel)
  emit('close')
}

const handleSignOut = () => {
  emit('signOut')
  emit('close')
}

const openSettings = () => {
  emit('openSettings')
  emit('close')
}
</script>

<template>
  <div 
    v-if="showProfileMenu"
    class="absolute top-full right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-50"
  >
    <button 
      @click="openPanel('subscription')"
      class="w-full flex items-center gap-3 px-4 py-2.5 text-gray-700 hover:bg-gray-50 transition-colors text-left"
    >
      <CreditCard :size="18" />
      <span>Subscription</span>
    </button>
    
    <button 
      @click="openSettings"
      class="w-full flex items-center gap-3 px-4 py-2.5 text-gray-700 hover:bg-gray-50 transition-colors text-left"
    >
      <Settings :size="18" />
      <span>Settings</span>
    </button>
    
    <button 
      @click="openPanel('organisation')"
      class="w-full flex items-center gap-3 px-4 py-2.5 text-gray-700 hover:bg-gray-50 transition-colors text-left"
    >
      <Building2 :size="18" />
      <span>Organisation</span>
    </button>
    
    <div class="border-t border-gray-200 my-2"></div>
    
    <button 
      @click="handleSignOut" 
      class="w-full flex items-center gap-3 px-4 py-2.5 text-red-600 hover:bg-red-50 transition-colors text-left"
    >
      <LogOut :size="18" />
      <span>Sign Out</span>
    </button>
  </div>
</template>
