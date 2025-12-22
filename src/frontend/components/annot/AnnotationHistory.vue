<script setup>
import { ref, onMounted } from 'vue'
import { History } from 'lucide-vue-next'

const props = defineProps({
  imageId: {
    type: [String, Number],
    required: true,
  },
  projectId: {
    type: Number,
    required: true,
  },
})

const api = useApi()
const history = ref([])
const loading = ref(false)

const fetchHistory = async () => {
  if (!props.imageId || !props.projectId) return

  loading.value = true
  try {
    // Fetch all annotations for this project
    const response = await api.get('/annotations/', {
      project_id: props.projectId,
      skip: 0,
      limit: 1000,
    })

    // Filter annotations for this specific image (both HISTORY and CURRENT status)
    const imageAnnotations = response.filter((ann) => ann.data_id === props.imageId)

    // Sort by most recent first
    history.value = imageAnnotations.sort((a, b) => {
      const dateA = new Date(a.creation_date || 0)
      const dateB = new Date(b.creation_date || 0)
      return dateB - dateA
    })
  } catch (error) {
    console.error('Failed to fetch annotation history:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHistory()
})

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleString()
}

const getStatusColor = (status) => {
  switch (status) {
    case 'certified':
      return 'bg-green-100 text-green-800'
    case 'to review':
      return 'bg-blue-100 text-blue-800'
    case 'rejected':
      return 'bg-red-100 text-red-800'
    case 'human annotation':
      return 'bg-purple-100 text-purple-800'
    case 'ml annotation':
      return 'bg-amber-100 text-amber-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
</script>

<template>
  <div class="h-full flex flex-col bg-white border-r border-gray-200">
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center gap-2 mb-2">
        <History :size="18" class="text-gray-600" />
        <h2 class="font-semibold text-gray-800">Modification History</h2>
      </div>
      <p class="text-xs text-gray-500">Image ID: {{ imageId }}</p>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="p-4 text-center">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
        <p class="text-sm text-gray-500">Loading history...</p>
      </div>

      <div v-else-if="history.length === 0" class="p-4 text-center">
        <p class="text-sm text-gray-500">No annotation history yet</p>
      </div>

      <div v-else class="space-y-3 p-4">
        <div
          v-for="(item, index) in history"
          :key="index"
          class="border border-gray-200 rounded-lg p-3 hover:border-gray-300 transition-colors"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <div class="flex items-center gap-2">
              <span :class="['text-xs px-2 py-1 rounded-full font-medium', getStatusColor(item.status)]">
                {{ item.status }}
              </span>
              <span
                :class="[
                  'text-xs px-2 py-1 rounded-full font-medium',
                  item.history_status === 'current' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
                ]"
              >
                {{ item.history_status === 'current' ? '⭐ Current' : '📋 History' }}
              </span>
            </div>
            <span class="text-xs text-gray-500 whitespace-nowrap">v{{ index + 1 }}</span>
          </div>

          <p class="text-xs text-gray-600 mb-2">
            {{ formatDate(item.creation_date) }}
          </p>

          <div v-if="item.label" class="text-xs text-gray-700 mb-1"><strong>Label:</strong> {{ item.label }}</div>

          <div v-if="item.description" class="text-xs text-gray-700 mb-1">
            <strong>Description:</strong> {{ item.description }}
          </div>

          <div v-if="item.annotation_score" class="text-xs text-gray-700 mb-1">
            <strong>Score:</strong> {{ (item.annotation_score * 100).toFixed(1) }}%
          </div>

          <div v-if="item.author_id" class="text-xs text-gray-500">By: User #{{ item.author_id }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
