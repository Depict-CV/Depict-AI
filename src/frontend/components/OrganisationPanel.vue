<script setup>
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  members: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['close'])

const getInitials = (name) => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

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
        <h2 class="text-2xl font-bold">Organisation</h2>
        <button @click="closeDialog" class="text-gray-400 hover:text-gray-600 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto flex-1">
        <!-- Stats -->
        <div class="grid grid-cols-3 gap-3 mb-6">
          <div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
            <div class="text-2xl font-bold text-blue-600">
              {{ members.length }}
            </div>
            <div class="text-xs text-gray-600 mt-1">Total</div>
          </div>
          <div class="bg-green-50 rounded-lg p-4 text-center border border-green-200">
            <div class="text-2xl font-bold text-green-600">
              {{ members.filter((m) => m.status === 'active').length }}
            </div>
            <div class="text-xs text-gray-600 mt-1">Active</div>
          </div>
          <div class="bg-orange-50 rounded-lg p-4 text-center border border-orange-200">
            <div class="text-2xl font-bold text-orange-600">
              {{ members.filter((m) => m.role === 'Admin').length }}
            </div>
            <div class="text-xs text-gray-600 mt-1">Admins</div>
          </div>
        </div>

        <!-- Members List -->
        <div class="space-y-3">
          <div
            v-for="member in members"
            :key="member.id"
            class="p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 text-white flex items-center justify-center font-semibold text-sm flex-shrink-0"
              >
                {{ getInitials(member.name) }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="font-semibold text-gray-900 text-sm">
                  {{ member.name }}
                </div>
                <div class="text-xs text-gray-500 truncate">
                  {{ member.email }}
                </div>
              </div>
              <div class="flex flex-col items-end gap-1">
                <span
                  :class="[
                    'text-xs font-semibold px-2 py-0.5 rounded',
                    member.role === 'Admin'
                      ? 'bg-orange-100 text-orange-700'
                      : member.role === 'Editor'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-blue-100 text-blue-700',
                  ]"
                >
                  {{ member.role }}
                </span>
                <span
                  :class="[
                    'text-xs font-medium px-2 py-0.5 rounded',
                    member.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600',
                  ]"
                >
                  {{ member.status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <button
          class="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
        >
          Invite Member
        </button>
      </div>
    </div>
  </div>
</template>
