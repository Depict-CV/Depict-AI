<script setup>
import { ref, computed } from 'vue'
import {
  Bot,
  Play,
  CheckCircle,
  AlertCircle,
  Loader,
  Zap,
  Image as ImageIcon,
  Database,
  RefreshCw,
} from 'lucide-vue-next'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const api = useApi()

const inferenceMode = ref('project') // 'project' or 'selected'
const selectedModel = ref('resnet50')
const inferenceLimit = ref(null)
const isInferring = ref(false)
const inferenceResult = ref(null)
const selectedImages = ref([]) // For future: allow selecting specific images

// Hugging Face integration
const selectedTask = ref('image-classification')
const huggingFaceModels = ref([])
const isLoadingModels = ref(false)
const showHuggingFaceModels = ref(false)

// Test inference
const testInput = ref('')
const testResult = ref(null)
const isTestingModel = ref(false)

// Review mode
const reviewMode = ref(false)
const selectedPredictions = ref(new Set())
const isSavingAnnotations = ref(false)

const availableTasks = [
  { id: 'image-classification', name: 'Image Classification', description: 'Classify images into categories' },
  { id: 'object-detection', name: 'Object Detection', description: 'Detect objects in images' },
  { id: 'image-segmentation', name: 'Image Segmentation', description: 'Segment images into regions' },
  { id: 'image-to-image', name: 'Image-to-Image', description: 'Transform images' },
  { id: 'depth-estimation', name: 'Depth Estimation', description: 'Estimate depth from images' },
  { id: 'zero-shot-image-classification', name: 'Zero-Shot Classification', description: 'Classify without training' },
]

const availableModels = [
  {
    id: 'resnet50',
    name: 'ResNet-50',
    description: 'Image classification (1000 classes)',
    type: 'Classification',
    dataset: 'ImageNet',
  },
  // Future models can be added here
  // { id: 'yolov8', name: 'YOLOv8', description: 'Object detection', type: 'Detection' }
]

const fetchHuggingFaceModels = async () => {
  isLoadingModels.value = true
  try {
    const models = await api.get(`/infer/models?task=${selectedTask.value}`)
    huggingFaceModels.value = models.map((m) => ({
      id: m.id,
      name: m.id.split('/').pop() || m.id,
      fullId: m.id,
      description: `${m.downloads.toLocaleString()} downloads, ${m.likes} likes`,
      type: selectedTask.value,
      downloads: m.downloads,
      likes: m.likes,
    }))
    showHuggingFaceModels.value = true
  } catch (error) {
    console.error('Failed to fetch Hugging Face models:', error)
    alert('Failed to fetch models: ' + (error.response?.data?.detail || error.message))
  } finally {
    isLoadingModels.value = false
  }
}

const isHuggingFaceModel = computed(() => {
  // Check if selected model is from HuggingFace (contains '/' in the ID)
  return selectedModel.value && selectedModel.value.includes('/')
})

const runTestInference = async () => {
  if (!testInput.value) {
    alert('Please provide a test input (image URL or path)')
    return
  }

  if (!selectedModel.value) {
    alert('Please select a model first')
    return
  }

  isTestingModel.value = true
  testResult.value = null

  try {
    let result

    if (isHuggingFaceModel.value) {
      // Hugging Face model
      const payload = {
        model_id: selectedModel.value,
        task: selectedTask.value,
        input: testInput.value,
      }
      result = await api.post('/infer/huggingface/run', payload)
    } else {
      // Built-in model (resnet50)
      const payload = {
        image_path: testInput.value,
      }
      result = await api.post('/infer/resnet50', payload)
    }

    testResult.value = result
  } catch (error) {
    console.error('Test inference failed:', error)
    testResult.value = {
      success: false,
      error: error.response?.data?.detail || error.message,
    }
  } finally {
    isTestingModel.value = false
  }
}

const runInference = async () => {
  if (!props.projectId) {
    alert('Please select a project first')
    return
  }

  isInferring.value = true
  inferenceResult.value = null
  reviewMode.value = false
  selectedPredictions.value = new Set()

  try {
    const payload = {
      project_id: props.projectId,
      save_annotations: false, // Always preview first
    }

    if (inferenceLimit.value && inferenceLimit.value > 0) {
      payload.limit = inferenceLimit.value
    }

    let result

    // Use different endpoints for HuggingFace vs built-in models
    if (isHuggingFaceModel.value) {
      payload.model_id = selectedModel.value
      payload.task = selectedTask.value
      result = await api.post('/infer/huggingface/batch', payload)
    } else {
      // Built-in model (resnet50)
      result = await api.post('/infer/resnet50/project', payload)
    }

    inferenceResult.value = result
    reviewMode.value = true // Enable review mode

    // Auto-select all successful predictions
    if (result.results) {
      const successfulIndices = result.results
        .map((r, i) => (r.status === 'success' ? i : null))
        .filter((i) => i !== null)
      selectedPredictions.value = new Set(successfulIndices)
    }

    if (result.successful > 0) {
      // Don't alert immediately, let user review
      console.log(`Generated ${result.successful} predictions. Review them below.`)
    } else if (result.total === 0) {
      alert('No unannotated images found in this project.')
      reviewMode.value = false
    } else {
      alert(`Inference failed for all ${result.failed} images. Check console for errors.`)
      reviewMode.value = false
    }
  } catch (error) {
    console.error('Inference failed:', error)
    alert('Inference failed: ' + (error.response?.data?.detail || error.message))
    reviewMode.value = false
  } finally {
    isInferring.value = false
  }
}

const togglePrediction = (index) => {
  if (selectedPredictions.value.has(index)) {
    selectedPredictions.value.delete(index)
  } else {
    selectedPredictions.value.add(index)
  }
}

const selectAllPredictions = () => {
  if (!inferenceResult.value) return
  selectedPredictions.value = new Set(
    inferenceResult.value.results.map((r, i) => (r.status === 'success' ? i : null)).filter((i) => i !== null)
  )
}

const deselectAllPredictions = () => {
  selectedPredictions.value = new Set()
}

const saveSelectedAnnotations = async () => {
  if (selectedPredictions.value.size === 0) {
    alert('Please select at least one prediction to save')
    return
  }

  isSavingAnnotations.value = true

  try {
    const selectedResults = Array.from(selectedPredictions.value).map((index) => inferenceResult.value.results[index])

    // Prepare data for saving
    const dataIds = selectedResults.map((r) => r.data_id)

    const payload = {
      project_id: props.projectId,
      data_ids: dataIds,
      save_annotations: true,
    }

    let result

    // Use different endpoints for HuggingFace vs built-in models
    if (isHuggingFaceModel.value) {
      payload.model_id = selectedModel.value
      payload.task = selectedTask.value
      result = await api.post('/infer/huggingface/batch', payload)
    } else {
      result = await api.post('/infer/resnet50/batch', payload)
    }

    alert(`Successfully saved ${selectedPredictions.value.size} annotations!`)

    // Update the inference result to mark saved items
    selectedResults.forEach((r) => {
      r.saved = true
    })

    reviewMode.value = false
    selectedPredictions.value = new Set()
  } catch (error) {
    console.error('Failed to save annotations:', error)
    alert('Failed to save annotations: ' + (error.response?.data?.detail || error.message))
  } finally {
    isSavingAnnotations.value = false
  }
}

const discardPredictions = () => {
  if (confirm('Are you sure you want to discard all predictions without saving?')) {
    inferenceResult.value = null
    reviewMode.value = false
    selectedPredictions.value = new Set()
  }
}

const hasResults = computed(() => inferenceResult.value !== null)
const successRate = computed(() => {
  if (!inferenceResult.value || inferenceResult.value.total === 0) return 0
  return Math.round((inferenceResult.value.successful / inferenceResult.value.total) * 100)
})
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">AI Inference</h2>

    <!-- Hugging Face Model Browser -->
    <div class="mb-6 bg-gradient-to-r from-yellow-50 to-orange-50 border border-orange-200 rounded-lg p-4">
      <div class="flex items-center gap-2 mb-4">
        <Database :size="20" class="text-orange-600" />
        <h3 class="text-lg font-semibold text-gray-900">Browse Hugging Face Models</h3>
      </div>

      <!-- Task Selection -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Select Task</label>
        <select
          v-model="selectedTask"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white"
        >
          <option v-for="task in availableTasks" :key="task.id" :value="task.id">
            {{ task.name }} - {{ task.description }}
          </option>
        </select>
      </div>

      <!-- Fetch Models Button -->
      <button
        @click="fetchHuggingFaceModels"
        :disabled="isLoadingModels"
        class="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <template v-if="isLoadingModels">
          <Loader :size="18" class="animate-spin" />
          <span>Loading Models...</span>
        </template>
        <template v-else>
          <RefreshCw :size="18" />
          <span>Fetch Models from Hugging Face</span>
        </template>
      </button>

      <!-- Display Hugging Face Models -->
      <div v-if="showHuggingFaceModels && huggingFaceModels.length > 0" class="mt-4">
        <div class="text-sm font-medium text-gray-700 mb-2">
          Found {{ huggingFaceModels.length }} models (sorted by downloads)
        </div>
        <div class="max-h-64 overflow-y-auto space-y-2 bg-white p-2 rounded-lg border border-gray-200">
          <label
            v-for="model in huggingFaceModels"
            :key="model.fullId"
            class="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-orange-50 cursor-pointer transition-colors"
            :class="{ 'border-orange-500 bg-orange-100': selectedModel === model.fullId }"
          >
            <input type="radio" v-model="selectedModel" :value="model.fullId" class="w-4 h-4 text-orange-600 mt-1" />
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900 text-sm truncate" :title="model.fullId">
                {{ model.name }}
              </div>
              <div class="text-xs text-gray-600 mt-0.5 truncate" :title="model.fullId">
                {{ model.fullId }}
              </div>
              <div class="text-xs text-gray-500 mt-1 flex items-center gap-3">
                <span>📥 {{ model.downloads.toLocaleString() }}</span>
                <span>❤️ {{ model.likes }}</span>
              </div>
            </div>
          </label>
        </div>
      </div>

      <div v-else-if="showHuggingFaceModels && huggingFaceModels.length === 0" class="mt-4">
        <div class="text-sm text-gray-600 bg-white p-3 rounded-lg border border-gray-200">
          No models found for this task.
        </div>
      </div>
    </div>

    <!-- Built-in Model Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">Or Select Built-in Model</label>
      <div class="space-y-2">
        <label
          v-for="model in availableModels"
          :key="model.id"
          class="flex items-start gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          :class="{ 'border-blue-500 bg-blue-50': selectedModel === model.id }"
        >
          <input type="radio" v-model="selectedModel" :value="model.id" class="w-4 h-4 text-blue-600 mt-1" />
          <div class="flex-1">
            <div class="font-medium text-gray-900 flex items-center gap-2">
              {{ model.name }}
              <span class="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-semibold rounded">
                {{ model.type }}
              </span>
            </div>
            <div class="text-sm text-gray-600 mt-1">
              {{ model.description }}
            </div>
            <div class="text-xs text-gray-500 mt-1">Trained on: {{ model.dataset }}</div>
          </div>
        </label>
      </div>
    </div>

    <!-- Test Model Section -->
    <div
      v-if="selectedModel"
      class="mb-6 bg-gradient-to-r from-green-50 to-teal-50 border border-teal-200 rounded-lg p-4"
    >
      <div class="flex items-center gap-2 mb-4">
        <Play :size="20" class="text-teal-600" />
        <h3 class="text-lg font-semibold text-gray-900">Test Model</h3>
      </div>

      <div class="mb-3">
        <label class="block text-sm font-medium text-gray-700 mb-2"> Test Input (Image URL or Path) </label>
        <input
          v-model="testInput"
          type="text"
          placeholder="e.g., https://example.com/image.jpg or /path/to/image.jpg"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
        />
      </div>

      <button
        @click="runTestInference"
        :disabled="isTestingModel || !testInput"
        class="w-full bg-teal-600 hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 mb-3"
      >
        <template v-if="isTestingModel">
          <Loader :size="18" class="animate-spin" />
          <span>Testing...</span>
        </template>
        <template v-else>
          <Play :size="18" />
          <span>Test Selected Model</span>
        </template>
      </button>

      <!-- Test Result Display -->
      <div v-if="testResult" class="bg-white border border-gray-200 rounded-lg p-3">
        <div v-if="testResult.success || testResult.output" class="space-y-2">
          <div class="flex items-center gap-2 text-green-700 font-medium text-sm mb-2">
            <CheckCircle :size="16" />
            <span>Test Successful!</span>
          </div>
          <div class="text-xs text-gray-600"><strong>Model:</strong> {{ selectedModel }}</div>
          <div v-if="isHuggingFaceModel" class="text-xs text-gray-600"><strong>Task:</strong> {{ selectedTask }}</div>
          <div class="mt-2">
            <strong class="text-xs text-gray-700">Output:</strong>
            <pre class="text-xs bg-gray-50 p-2 rounded mt-1 overflow-x-auto">{{
              JSON.stringify(testResult.output || testResult, null, 2)
            }}</pre>
          </div>
        </div>
        <div v-else-if="testResult.error" class="flex items-start gap-2 text-red-700">
          <AlertCircle :size="16" class="mt-0.5" />
          <div class="text-sm">
            <strong>Test Failed:</strong>
            <p class="mt-1 text-xs">{{ testResult.error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Inference Options -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">Options</label>
      <div class="space-y-3">
        <div class="p-3 border border-gray-200 rounded-lg">
          <label class="block text-sm font-medium text-gray-700 mb-2">Batch Limit (Optional)</label>
          <input
            type="number"
            v-model.number="inferenceLimit"
            placeholder="Leave empty to process all images"
            min="1"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p class="text-xs text-gray-500 mt-1">Limit number of images to process (useful for testing)</p>
        </div>

        <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
          <p class="text-sm text-indigo-900 font-medium mb-1">📋 Preview Mode Enabled</p>
          <p class="text-xs text-indigo-700">
            All predictions will be shown for review before saving. You can select which ones to keep as annotations.
          </p>
        </div>
      </div>
    </div>

    <!-- Info Box -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div class="flex items-start gap-3">
        <Bot :size="20" class="text-blue-600 mt-0.5" />
        <div>
          <p class="text-sm font-semibold text-blue-900 mb-1">How it works</p>
          <ul class="text-xs text-blue-800 space-y-1">
            <li>• Only processes images without existing annotations</li>
            <li>• All predictions are shown for review before saving</li>
            <li>• You can select which predictions to keep as annotations</li>
            <li>• Saved predictions are marked as "ML Annotation" status</li>
            <li v-if="isHuggingFaceModel">
              • Using Hugging Face model: <strong>{{ selectedModel }}</strong> ({{ selectedTask }})
            </li>
            <li v-else-if="selectedModel === 'resnet50'">
              • ResNet-50 classifies images into 1000 ImageNet categories
            </li>
            <li v-else>• Select a model to start</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Run Inference Button -->
    <button
      @click="runInference"
      :disabled="isInferring || !projectId"
      class="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 mb-6"
    >
      <template v-if="isInferring">
        <Loader :size="20" class="animate-spin" />
        <span>Running Inference...</span>
      </template>
      <template v-else>
        <Zap :size="20" />
        <span>Generate Predictions (Preview Mode)</span>
      </template>
    </button>

    <!-- Results Display -->
    <div v-if="hasResults" class="space-y-4">
      <!-- Review Mode Header -->
      <div v-if="reviewMode" class="bg-purple-50 border-2 border-purple-300 rounded-lg p-4">
        <h3 class="text-lg font-semibold text-purple-900 mb-2 flex items-center gap-2">
          <Bot :size="22" />
          Review Predictions
        </h3>
        <p class="text-sm text-purple-700 mb-3">
          Review the predictions below and select which ones you want to save as annotations. Uncheck any predictions
          you don't want to keep.
        </p>
        <div class="flex gap-2">
          <button
            @click="selectAllPredictions"
            class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded transition-colors"
          >
            Select All
          </button>
          <button
            @click="deselectAllPredictions"
            class="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded transition-colors"
          >
            Deselect All
          </button>
          <span class="text-sm text-purple-700 self-center ml-auto"> {{ selectedPredictions.size }} selected </span>
        </div>
      </div>

      <h3 v-else class="text-lg font-semibold">Inference Results</h3>

      <!-- Summary Stats -->
      <div class="grid grid-cols-3 gap-3">
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-gray-900">
            {{ inferenceResult.total }}
          </div>
          <div class="text-xs text-gray-600 mt-1 flex items-center gap-1">
            <ImageIcon :size="14" />
            <span>Total Processed</span>
          </div>
        </div>

        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-green-700">
            {{ inferenceResult.successful }}
          </div>
          <div class="text-xs text-green-600 mt-1 flex items-center gap-1">
            <CheckCircle :size="14" />
            <span>Successful</span>
          </div>
        </div>

        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-red-700">
            {{ inferenceResult.failed }}
          </div>
          <div class="text-xs text-red-600 mt-1 flex items-center gap-1">
            <AlertCircle :size="14" />
            <span>Failed</span>
          </div>
        </div>
      </div>

      <!-- Success Rate -->
      <div class="bg-white border border-gray-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Success Rate</span>
          <span class="text-sm font-bold text-gray-900">{{ successRate }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="bg-green-600 h-2 rounded-full transition-all duration-500"
            :style="{ width: successRate + '%' }"
          ></div>
        </div>
      </div>

      <!-- Detailed Results (scrollable) -->
      <div class="border border-gray-200 rounded-lg">
        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <h4 class="font-medium text-gray-900">Detailed Results</h4>
        </div>
        <div class="max-h-64 overflow-y-auto">
          <div
            v-for="(result, index) in inferenceResult.results"
            :key="index"
            class="px-4 py-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50"
            :class="{ 'bg-purple-50': reviewMode && selectedPredictions.has(index) }"
          >
            <div class="flex items-start gap-3">
              <!-- Checkbox for review mode -->
              <input
                v-if="reviewMode && result.status === 'success'"
                type="checkbox"
                :checked="selectedPredictions.has(index)"
                @change="togglePrediction(index)"
                class="w-5 h-5 rounded text-purple-600 mt-0.5 cursor-pointer"
              />

              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 truncate">
                  {{ result.location.split('/').pop() }}
                </div>
                <div v-if="result.status === 'success'" class="text-xs text-gray-600 mt-1">
                  Prediction:
                  <span class="font-semibold text-purple-700">
                    {{
                      result.prediction.class_name ||
                      (Array.isArray(result.prediction) && result.prediction[0]?.label) ||
                      JSON.stringify(result.prediction)
                    }}
                  </span>
                  <span v-if="result.prediction.class_id" class="text-gray-400 ml-1"
                    >(ID: {{ result.prediction.class_id }})</span
                  >
                </div>
                <div v-else class="text-xs text-red-600 mt-1">Error: {{ result.error }}</div>

                <div v-if="result.saved" class="text-xs text-green-600 mt-1 flex items-center gap-1">
                  <CheckCircle :size="12" />
                  <span>Saved as annotation</span>
                </div>
              </div>
              <div>
                <CheckCircle v-if="result.status === 'success'" :size="18" class="text-green-600" />
                <AlertCircle v-else :size="18" class="text-red-600" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Review Actions -->
      <div v-if="reviewMode" class="flex gap-3">
        <button
          @click="saveSelectedAnnotations"
          :disabled="isSavingAnnotations || selectedPredictions.size === 0"
          class="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <template v-if="isSavingAnnotations">
            <Loader :size="20" class="animate-spin" />
            <span>Saving...</span>
          </template>
          <template v-else>
            <CheckCircle :size="20" />
            <span>Save Selected ({{ selectedPredictions.size }})</span>
          </template>
        </button>

        <button
          @click="discardPredictions"
          :disabled="isSavingAnnotations"
          class="bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <AlertCircle :size="20" />
          <span>Discard All</span>
        </button>
      </div>

      <!-- Info about saved annotations (only show when not in review mode) -->
      <div
        v-if="inferenceResult.annotations_saved && !reviewMode"
        class="bg-green-50 border border-green-200 rounded-lg p-3"
      >
        <p class="text-sm text-green-800">✓ Annotations have been saved to the database with status "ML Annotation"</p>
      </div>
    </div>

    <!-- No Project Selected -->
    <div v-if="!projectId" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
      <p class="text-sm text-yellow-800"><strong>Note:</strong> Please select a project to run inference.</p>
    </div>
  </div>
</template>
