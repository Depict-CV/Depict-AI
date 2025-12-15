<script setup>
import { ref, computed } from 'vue'
import { Tag, CheckCircle, AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
  selectedImages: {
    type: Set,
    default: () => new Set(),
  },
})

const emit = defineEmits(['annotationsCreated'])

const api = useApi()
const label = ref('')
const isAnnotating = ref(false)
const annotationResult = ref(null)

const selectedCount = computed(() => props.selectedImages.size)

const applyBatchAnnotation = async () => {
  if (!props.projectId) {
    alert('Please select a project first')
    return
  }

  if (selectedCount.value === 0) {
    alert('Please select images from the gallery first')
    return
  }

  if (!label.value.trim()) {
    alert('Please enter a label')
    return
  }

  const confirmed = confirm(
    `Apply label "${label.value}" to ${selectedCount.value} image${selectedCount.value > 1 ? 's' : ''}?`
  )

  if (!confirmed) return

  isAnnotating.value = true
  annotationResult.value = null

  try {
    const imageIds = Array.from(props.selectedImages)
    let successful = 0
    let failed = 0
    const errors = []

    for (const imageId of imageIds) {
      try {
        // Create annotation for each image
        await api.post('/annotations/', {
          data_id: imageId,
          project_id: props.projectId,
          label: label.value.trim(),
          status: 'human annotation',
        })
        successful++
      } catch (error) {
        console.error(`Failed to annotate image ${imageId}:`, error)
        failed++
        errors.push({
          imageId,
          error: error.response?.data?.detail || error.message,
        })
      }
    }

    annotationResult.value = {
      total: imageIds.length,
      successful,
      failed,
      errors,
    }

    if (successful > 0) {
      const message = `✓ Batch annotation completed!\n\nSuccessful: ${successful}\nFailed: ${failed}`
      alert(message)

      // Clear label input
      label.value = ''

      // Notify parent to refresh gallery
      emit('annotationsCreated', { successful, failed })
    } else {
      alert(`✗ All annotations failed.\n\nPlease check the console for errors.`)
    }
  } catch (error) {
    console.error('Batch annotation failed:', error)
    alert('Batch annotation failed: ' + (error.response?.data?.detail || error.message))
  } finally {
    isAnnotating.value = false
  }
}

const clearResults = () => {
  annotationResult.value = null
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Batch Annotation</h2>

    <!-- Selection Info -->
    <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="flex items-start gap-3">
        <Tag :size="20" class="text-blue-600 mt-0.5" />
        <div>
          <p class="text-sm font-semibold text-blue-900 mb-1">
            {{ selectedCount }} image{{ selectedCount !== 1 ? 's' : '' }}
            selected
          </p>
          <p class="text-xs text-blue-700">
            {{
              selectedCount === 0
                ? 'Enable selection mode in the gallery and select images to annotate'
                : 'Enter a label below to apply to all selected images'
            }}
          </p>
        </div>
      </div>
    </div>

    <!-- Label Input -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2"> Annotation Label </label>
      <input
        v-model="label"
        type="text"
        placeholder="e.g., cat, dog, person, vehicle..."
        :disabled="selectedCount === 0 || isAnnotating"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
      />
      <p class="text-xs text-gray-500 mt-1">
        This label will be applied to all {{ selectedCount }} selected image{{ selectedCount !== 1 ? 's' : '' }}
      </p>
    </div>

    <!-- Apply Button -->
    <button
      @click="applyBatchAnnotation"
      :disabled="!projectId || selectedCount === 0 || !label.trim() || isAnnotating"
      class="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 mb-6"
    >
      <template v-if="isAnnotating">
        <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        <span>Applying Annotations...</span>
      </template>
      <template v-else>
        <Tag :size="20" />
        <span>Apply to {{ selectedCount }} Image{{ selectedCount !== 1 ? 's' : '' }}</span>
      </template>
    </button>

    <!-- Results Summary -->
    <div v-if="annotationResult" class="space-y-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-lg font-semibold">Annotation Results</h3>
        <button @click="clearResults" class="text-sm text-gray-500 hover:text-gray-700">Clear</button>
      </div>

      <!-- Summary Stats -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-green-700">
            {{ annotationResult.successful }}
          </div>
          <div class="text-xs text-green-600 mt-1 flex items-center gap-1">
            <CheckCircle :size="14" />
            <span>Successful</span>
          </div>
        </div>

        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-red-700">
            {{ annotationResult.failed }}
          </div>
          <div class="text-xs text-red-600 mt-1 flex items-center gap-1">
            <AlertCircle :size="14" />
            <span>Failed</span>
          </div>
        </div>
      </div>

      <!-- Error Details -->
      <div v-if="annotationResult.errors.length > 0" class="border border-red-200 rounded-lg">
        <div class="bg-red-50 px-4 py-3 border-b border-red-200">
          <h4 class="font-medium text-red-900">Failed Annotations</h4>
        </div>
        <div class="max-h-48 overflow-y-auto">
          <div
            v-for="(error, index) in annotationResult.errors"
            :key="index"
            class="px-4 py-3 border-b border-red-100 last:border-b-0"
          >
            <div class="text-sm font-medium text-red-900">Image #{{ error.imageId }}</div>
            <div class="text-xs text-red-600 mt-1">
              {{ error.error }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <div class="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div class="flex items-start gap-3">
        <Tag :size="20" class="text-gray-600 mt-0.5" />
        <div>
          <p class="text-sm font-semibold text-gray-900 mb-1">How to use</p>
          <ul class="text-xs text-gray-700 space-y-1">
            <li>1. Enable selection mode in the image gallery</li>
            <li>2. Select the images you want to annotate</li>
            <li>3. Enter a label in the field above</li>
            <li>4. Click "Apply" to annotate all selected images</li>
            <li>5. Annotations will be marked as "Human Annotation"</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- No Project Warning -->
    <div v-if="!projectId" class="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <p class="text-sm text-yellow-800"><strong>Note:</strong> Please select a project to use batch annotation.</p>
    </div>
  </div>
</template>
