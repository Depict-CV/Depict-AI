<script setup>
import { ref } from 'vue'
import { Zap, Check, RefreshCw } from 'lucide-vue-next'

const emit = defineEmits(['generateAnnotation', 'approveAnnotation', 'regenerateAnnotation'])

const props = defineProps({
  imageId: {
    type: [String, Number],
    required: true,
  },
})

const api = useApi()
const loading = ref(false)
const annotationGenerated = ref(false)
const currentAnnotation = ref(null)

const generateAnnotation = async (isRegenerate = false) => {
  if (!props.imageId) {
    alert('No image selected')
    return
  }

  const confirmGenerate = confirm(
    isRegenerate ? 'Generate another AI annotation for this image?' : 'Generate AI annotation for this image?'
  )
  if (!confirmGenerate) return

  loading.value = true
  try {
    // Call the ML endpoint to generate annotations
    const response = await api.post('/ml/predict', {
      data_id: props.imageId,
    })

    console.log('AI annotation generated:', response)
    currentAnnotation.value = response
    annotationGenerated.value = true
    emit('generateAnnotation', response)
    if (isRegenerate) {
      emit('regenerateAnnotation', response)
    }
    alert('✓ AI annotation generated successfully!')
  } catch (error) {
    console.error('Failed to generate annotation:', error)
    alert(`Failed to generate annotation: ${error?.data?.detail || error?.message || 'Unknown error'}`)
  } finally {
    loading.value = false
  }
}

const approveAnnotation = () => {
  if (!currentAnnotation.value) return

  emit('approveAnnotation', currentAnnotation.value)
  annotationGenerated.value = false
  currentAnnotation.value = null
  alert('✓ Annotation approved!')
}
</script>

<template>
  <div class="p-4 border-t border-gray-200 bg-gray-50">
    <!-- Initial Generate Button -->
    <button
      v-if="!annotationGenerated"
      @click="generateAnnotation(false)"
      :disabled="loading"
      class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold rounded-lg transition-all duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed"
    >
      <Zap :size="18" :class="{ 'animate-spin': loading }" />
      <span>{{ loading ? 'Generating...' : 'Generate with AI' }}</span>
    </button>

    <!-- Approve/Regenerate Buttons -->
    <div v-else class="space-y-3">
      <div class="p-3 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-sm font-medium text-green-800">✓ Annotation generated successfully</p>
      </div>

      <div class="flex gap-2">
        <button
          @click="approveAnnotation"
          :disabled="loading"
          class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold rounded-lg transition-all duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed"
        >
          <Check :size="18" />
          <span>Approve</span>
        </button>

        <button
          @click="generateAnnotation(true)"
          :disabled="loading"
          class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold rounded-lg transition-all duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed"
        >
          <RefreshCw :size="18" :class="{ 'animate-spin': loading }" />
          <span>{{ loading ? 'Generating...' : 'Another AI' }}</span>
        </button>
      </div>

      <p class="text-xs text-gray-500 text-center">
        Approve this annotation or generate another one using different AI
      </p>
    </div>

    <!-- Original hint text for generate button -->
    <p v-if="!annotationGenerated" class="text-xs text-gray-500 mt-2 text-center">
      Use AI to automatically annotate this image
    </p>
  </div>
</template>
