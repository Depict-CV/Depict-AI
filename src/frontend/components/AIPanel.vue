<script setup>
import { ref, computed } from 'vue'
import { Bot, Play, CheckCircle, AlertCircle, Loader, Zap, Image as ImageIcon } from 'lucide-vue-next'

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  }
})

const api = useApi()

const inferenceMode = ref('project') // 'project' or 'selected'
const selectedModel = ref('resnet50')
const saveAnnotations = ref(true)
const inferenceLimit = ref(null)
const isInferring = ref(false)
const inferenceResult = ref(null)
const selectedImages = ref([]) // For future: allow selecting specific images

const availableModels = [
  {
    id: 'resnet50',
    name: 'ResNet-50',
    description: 'Image classification (1000 classes)',
    type: 'Classification',
    dataset: 'ImageNet'
  }
  // Future models can be added here
  // { id: 'yolov8', name: 'YOLOv8', description: 'Object detection', type: 'Detection' }
]

const runInference = async () => {
  if (!props.projectId) {
    alert('Please select a project first')
    return
  }
  
  isInferring.value = true
  inferenceResult.value = null
  
  try {
    const payload = {
      project_id: props.projectId,
      save_annotations: saveAnnotations.value
    }
    
    if (inferenceLimit.value && inferenceLimit.value > 0) {
      payload.limit = inferenceLimit.value
    }
    
    // Call inference endpoint
    const result = await api.post('/infer/resnet50/project', payload)
    
    inferenceResult.value = result
    
    if (result.successful > 0) {
      const message = `Successfully processed ${result.successful} images!\n` +
        `Failed: ${result.failed}\n` +
        (saveAnnotations.value ? 'Annotations saved to database.' : 'Annotations not saved.')
      alert(message)
    } else if (result.total === 0) {
      alert('No unannotated images found in this project.')
    } else {
      alert(`Inference failed for all ${result.failed} images. Check console for errors.`)
    }
    
  } catch (error) {
    console.error('Inference failed:', error)
    alert('Inference failed: ' + (error.response?.data?.detail || error.message))
  } finally {
    isInferring.value = false
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
    
    <!-- Model Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">Select Model</label>
      <div class="space-y-2">
        <label 
          v-for="model in availableModels" 
          :key="model.id"
          class="flex items-start gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          :class="{ 'border-blue-500 bg-blue-50': selectedModel === model.id }"
        >
          <input 
            type="radio" 
            v-model="selectedModel" 
            :value="model.id" 
            class="w-4 h-4 text-blue-600 mt-1"
          />
          <div class="flex-1">
            <div class="font-medium text-gray-900 flex items-center gap-2">
              {{ model.name }}
              <span class="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-semibold rounded">
                {{ model.type }}
              </span>
            </div>
            <div class="text-sm text-gray-600 mt-1">{{ model.description }}</div>
            <div class="text-xs text-gray-500 mt-1">Trained on: {{ model.dataset }}</div>
          </div>
        </label>
      </div>
    </div>
    
    <!-- Inference Options -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">Options</label>
      <div class="space-y-3">
        <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
          <div>
            <div class="font-medium text-gray-900">Save as Annotations</div>
            <div class="text-sm text-gray-500">Automatically save predictions to database</div>
          </div>
          <input 
            type="checkbox" 
            v-model="saveAnnotations" 
            class="w-5 h-5 rounded text-blue-600"
          />
        </label>
        
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
            <li>• Predictions are marked as "ML Annotation" status</li>
            <li>• You can review and approve/modify predictions later</li>
            <li>• {{ selectedModel === 'resnet50' ? 'ResNet-50 classifies images into 1000 ImageNet categories' : '' }}</li>
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
        <span>Run Inference on Project</span>
      </template>
    </button>
    
    <!-- Results Display -->
    <div v-if="hasResults" class="space-y-4">
      <h3 class="text-lg font-semibold">Inference Results</h3>
      
      <!-- Summary Stats -->
      <div class="grid grid-cols-3 gap-3">
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-gray-900">{{ inferenceResult.total }}</div>
          <div class="text-xs text-gray-600 mt-1 flex items-center gap-1">
            <ImageIcon :size="14" />
            <span>Total Processed</span>
          </div>
        </div>
        
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-green-700">{{ inferenceResult.successful }}</div>
          <div class="text-xs text-green-600 mt-1 flex items-center gap-1">
            <CheckCircle :size="14" />
            <span>Successful</span>
          </div>
        </div>
        
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="text-2xl font-bold text-red-700">{{ inferenceResult.failed }}</div>
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
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 truncate">
                  {{ result.location.split('/').pop() }}
                </div>
                <div v-if="result.status === 'success'" class="text-xs text-gray-600 mt-1">
                  Prediction: <span class="font-semibold text-purple-700">{{ result.prediction.class_name }}</span>
                  <span class="text-gray-400 ml-1">(ID: {{ result.prediction.class_id }})</span>
                </div>
                <div v-else class="text-xs text-red-600 mt-1">
                  Error: {{ result.error }}
                </div>
              </div>
              <div>
                <CheckCircle 
                  v-if="result.status === 'success'" 
                  :size="18" 
                  class="text-green-600" 
                />
                <AlertCircle 
                  v-else 
                  :size="18" 
                  class="text-red-600" 
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Info about saved annotations -->
      <div v-if="inferenceResult.annotations_saved" class="bg-green-50 border border-green-200 rounded-lg p-3">
        <p class="text-sm text-green-800">
          ✓ Annotations have been saved to the database with status "ML Annotation"
        </p>
      </div>
    </div>
    
    <!-- No Project Selected -->
    <div v-if="!projectId" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
      <p class="text-sm text-yellow-800">
        <strong>Note:</strong> Please select a project to run inference.
      </p>
    </div>
  </div>
</template>
