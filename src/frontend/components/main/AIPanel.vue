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
  selectedImages: {
    type: Set,
    default: () => new Set(),
  },
})

const emit = defineEmits(['inferenceResults'])

const api = useApi()

const inferenceMode = ref('project') // 'project' or 'selected'
const selectedModel = ref('resnet50')
const inferenceLimit = ref(null)
const isInferring = ref(false)
const inferenceResult = ref(null)
const selectedImages = ref([]) // For future: allow selecting specific images
const rememberedSelection = ref(null) // Store the selection used for inference

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
  { id: 'depth-estimation', name: 'Depth Estimation', description: 'Estimate depth information from images' },
  {
    id: 'image-classification',
    name: 'Image Classification',
    description: 'Classify images into predefined categories',
  },
  { id: 'object-detection', name: 'Object Detection', description: 'Detect and localize objects in images' },
  {
    id: 'image-segmentation',
    name: 'Image Segmentation',
    description: 'Segment images into semantic or instance regions',
  },
  { id: 'text-to-image', name: 'Text-to-Image', description: 'Generate images from text prompts' },
  { id: 'image-to-text', name: 'Image-to-Text', description: 'Generate textual descriptions from images' },
  { id: 'image-to-image', name: 'Image-to-Image', description: 'Transform images into other images' },
  { id: 'image-to-video', name: 'Image-to-Video', description: 'Generate videos from images' },
  {
    id: 'unconditional-image-generation',
    name: 'Unconditional Image Generation',
    description: 'Generate images without any conditioning input',
  },
  { id: 'video-classification', name: 'Video Classification', description: 'Classify videos into categories' },
  { id: 'text-to-video', name: 'Text-to-Video', description: 'Generate videos from text prompts' },
  {
    id: 'zero-shot-image-classification',
    name: 'Zero-Shot Image Classification',
    description: 'Classify images without task-specific training',
  },
  { id: 'mask-generation', name: 'Mask Generation', description: 'Generate segmentation masks for images' },
  {
    id: 'zero-shot-object-detection',
    name: 'Zero-Shot Object Detection',
    description: 'Detect objects using text queries without training',
  },
  { id: 'text-to-3d', name: 'Text-to-3D', description: 'Generate 3D assets from text prompts' },
  { id: 'image-to-3d', name: 'Image-to-3D', description: 'Reconstruct 3D assets from images' },
  {
    id: 'image-feature-extraction',
    name: 'Image Feature Extraction',
    description: 'Extract embeddings or features from images',
  },
  { id: 'keypoint-detection', name: 'Keypoint Detection', description: 'Detect keypoints or landmarks in images' },
  { id: 'video-to-video', name: 'Video-to-Video', description: 'Transform or edit videos using AI models' },
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

    // Use remembered selection, or current selection, or all images
    const currentSelection = rememberedSelection.value || (props.selectedImages?.size > 0 ? props.selectedImages : null)

    if (currentSelection) {
      // Store the selection for future inference runs
      if (!rememberedSelection.value) {
        rememberedSelection.value = new Set(currentSelection)
      }
      payload.data_ids = Array.from(currentSelection)
      console.log(`Running inference on ${currentSelection.size} selected images`)
    } else if (inferenceLimit.value && inferenceLimit.value > 0) {
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
      if (hasSelectedImages.value) {
        // Use batch endpoint for selected images
        result = await api.post('/infer/resnet50/batch', payload)
      } else {
        // Use project endpoint for all images
        result = await api.post('/infer/resnet50/project', payload)
      }
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

    // Emit results to parent for display in ImageGallery
    emit('inferenceResults', {
      results: result,
      modelId: selectedModel.value,
      task: selectedTask.value,
      isHuggingFace: isHuggingFaceModel.value,
    })

    if (result.successful > 0) {
      // Don't alert immediately, let user review
      const target = hasSelectedImages.value ? `${selectedImagesCount.value} selected images` : 'project images'
      console.log(`Generated ${result.successful} predictions on ${target}. View them in the image gallery.`)
    } else if (result.total === 0) {
      const msg = hasSelectedImages.value
        ? 'No selected images found or all already have annotations.'
        : 'No unannotated images found in this project.'
      console.warn(msg)
      reviewMode.value = false
    } else {
      console.error(`Inference failed for all ${result.failed} images. Check console for errors.`)
      reviewMode.value = false
    }
  } catch (error) {
    console.error('Inference failed:', error.response?.data?.detail || error.message, error)
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

const selectedImagesCount = computed(() => rememberedSelection.value?.size || props.selectedImages?.size || 0)
const hasSelectedImages = computed(() => selectedImagesCount.value > 0)

const clearRememberedSelection = () => {
  rememberedSelection.value = null
}
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
        <div class="max-h-96 overflow-y-auto space-y-2 bg-white p-2 rounded-lg border border-gray-200">
          <label
            v-for="model in huggingFaceModels"
            :key="model.fullId"
            class="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-orange-50 cursor-pointer transition-colors"
            :class="{ 'border-orange-500 bg-orange-100': selectedModel === model.fullId }"
          >
            <input
              type="radio"
              v-model="selectedModel"
              :value="model.fullId"
              class="w-4 h-4 text-orange-600 mt-1 flex-shrink-0"
            />
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900 text-sm break-words" :title="model.fullId">
                {{ model.name }}
              </div>
              <div class="text-xs text-gray-600 mt-0.5 break-all" :title="model.fullId">
                {{ model.fullId }}
              </div>
              <div class="text-xs text-gray-500 mt-1 flex items-center gap-3 flex-wrap">
                <span class="whitespace-nowrap">📥 {{ model.downloads.toLocaleString() }}</span>
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
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Upload Model</label>
        <div
          class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-purple-400 transition-colors"
        >
          <input
            type="file"
            @change="handleModelUpload"
            accept=".h5,.pt,.pth,.onnx,.pkl"
            class="hidden"
            id="model-upload"
          />
          <label for="model-upload" class="cursor-pointer">
            <Microscope :size="28" class="mx-auto text-gray-400 mb-2" />
            <p class="text-sm text-gray-600 mb-1">
              <span class="text-purple-600 font-medium">Upload model file</span>
            </p>
            <p class="text-xs text-gray-500">PyTorch, TensorFlow, ONNX</p>
          </label>
        </div>

        <div
          v-if="modelFile"
          class="mt-3 p-3 bg-purple-50 border border-purple-200 rounded-lg flex items-center justify-between"
        >
          <div class="flex items-center gap-2">
            <Microscope :size="18" class="text-purple-600" />
            <span class="text-sm font-medium text-gray-900">{{ modelFile.name }}</span>
          </div>
          <button @click="modelFile = null" class="text-red-600 hover:text-red-700 text-sm font-medium">Remove</button>
        </div>
      </div>

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

    <!-- Remembered Selection Notice -->
    <div v-if="rememberedSelection" class="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <CheckCircle :size="18" class="text-blue-600" />
          <div>
            <p class="text-sm font-medium text-blue-900">
              Using remembered selection: {{ rememberedSelection.size }} images
            </p>
            <p class="text-xs text-blue-700 mt-0.5">Subsequent predictions will use the same images</p>
          </div>
        </div>
        <button
          @click="clearRememberedSelection"
          class="text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded transition-colors"
        >
          Clear Selection
        </button>
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
        <span v-if="hasSelectedImages">Generate Predictions for {{ selectedImagesCount }} Selected</span>
        <span v-else>Generate Predictions (Preview Mode)</span>
      </template>
    </button>

    <!-- Results Summary -->
    <div v-if="hasResults" class="space-y-4">
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
    </div>

    <!-- No Project Selected -->
    <div v-if="!projectId" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
      <p class="text-sm text-yellow-800"><strong>Note:</strong> Please select a project to run inference.</p>
    </div>
  </div>
</template>
