<script setup>
import { ref } from 'vue'
import { Microscope, Upload, Play, AlertCircle, CheckCircle, TrendingUp, TrendingDown } from 'lucide-vue-next'

const modelFile = ref(null)
const dataFile = ref(null)
const isAnalyzing = ref(false)
const analysisResults = ref(null)

const handleModelUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    modelFile.value = file
  }
}

const handleDataUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    dataFile.value = file
  }
}

const runAnalysis = async () => {
  if (!modelFile.value || !dataFile.value) return
  
  isAnalyzing.value = true
  try {
    // TODO: Implement actual analysis logic with API
    console.log('Analyzing model:', modelFile.value.name, 'with data:', dataFile.value.name)
    await new Promise(resolve => setTimeout(resolve, 3000)) // Simulate API call
    
    // Mock results
    analysisResults.value = {
      accuracy: 0.94,
      precision: 0.92,
      recall: 0.89,
      f1Score: 0.90,
      totalPredictions: 1000,
      correctPredictions: 940,
      falsePositives: 32,
      falseNegatives: 28,
      confusionMatrix: [
        [450, 20],
        [8, 522]
      ]
    }
  } catch (error) {
    console.error('Analysis failed:', error)
    alert('Analysis failed!')
  } finally {
    isAnalyzing.value = false
  }
}

const clearAnalysis = () => {
  modelFile.value = null
  dataFile.value = null
  analysisResults.value = null
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Model Analysis</h2>
    
    <div class="space-y-6">
      <!-- Upload Section -->
      <div v-if="!analysisResults" class="space-y-4">
        <!-- Model Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Upload Model</label>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-purple-400 transition-colors">
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
          
          <div v-if="modelFile" class="mt-3 p-3 bg-purple-50 border border-purple-200 rounded-lg flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Microscope :size="18" class="text-purple-600" />
              <span class="text-sm font-medium text-gray-900">{{ modelFile.name }}</span>
            </div>
            <button 
              @click="modelFile = null"
              class="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Remove
            </button>
          </div>
        </div>

        <!-- Data Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Upload Test Data</label>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
            <input 
              type="file" 
              @change="handleDataUpload"
              accept=".json,.csv,.zip"
              class="hidden" 
              id="data-upload"
            />
            <label for="data-upload" class="cursor-pointer">
              <Upload :size="28" class="mx-auto text-gray-400 mb-2" />
              <p class="text-sm text-gray-600 mb-1">
                <span class="text-blue-600 font-medium">Upload test data</span>
              </p>
              <p class="text-xs text-gray-500">Images, annotations, or dataset</p>
            </label>
          </div>
          
          <div v-if="dataFile" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Upload :size="18" class="text-blue-600" />
              <span class="text-sm font-medium text-gray-900">{{ dataFile.name }}</span>
            </div>
            <button 
              @click="dataFile = null"
              class="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Remove
            </button>
          </div>
        </div>

        <!-- Run Analysis Button -->
        <button 
          @click="runAnalysis"
          :disabled="!modelFile || !dataFile || isAnalyzing"
          class="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Play :size="18" />
          <span v-if="!isAnalyzing">Run Analysis</span>
          <span v-else>Analyzing...</span>
        </button>
      </div>

      <!-- Results Section -->
      <div v-if="analysisResults" class="space-y-4">
        <!-- Key Metrics -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-green-50 rounded-lg p-4 border border-green-200">
            <div class="flex items-center gap-2 mb-2">
              <CheckCircle :size="16" class="text-green-600" />
              <span class="text-xs font-medium text-gray-600">Accuracy</span>
            </div>
            <div class="text-2xl font-bold text-green-700">{{ (analysisResults.accuracy * 100).toFixed(1) }}%</div>
          </div>
          
          <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div class="flex items-center gap-2 mb-2">
              <TrendingUp :size="16" class="text-blue-600" />
              <span class="text-xs font-medium text-gray-600">Precision</span>
            </div>
            <div class="text-2xl font-bold text-blue-700">{{ (analysisResults.precision * 100).toFixed(1) }}%</div>
          </div>
          
          <div class="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <div class="flex items-center gap-2 mb-2">
              <TrendingDown :size="16" class="text-orange-600" />
              <span class="text-xs font-medium text-gray-600">Recall</span>
            </div>
            <div class="text-2xl font-bold text-orange-700">{{ (analysisResults.recall * 100).toFixed(1) }}%</div>
          </div>
          
          <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div class="flex items-center gap-2 mb-2">
              <Microscope :size="16" class="text-purple-600" />
              <span class="text-xs font-medium text-gray-600">F1 Score</span>
            </div>
            <div class="text-2xl font-bold text-purple-700">{{ (analysisResults.f1Score * 100).toFixed(1) }}%</div>
          </div>
        </div>

        <!-- Detailed Stats -->
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h3 class="font-semibold text-gray-900 mb-3">Prediction Summary</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Total Predictions</span>
              <span class="font-medium text-gray-900">{{ analysisResults.totalPredictions }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Correct Predictions</span>
              <span class="font-medium text-green-600">{{ analysisResults.correctPredictions }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">False Positives</span>
              <span class="font-medium text-orange-600">{{ analysisResults.falsePositives }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">False Negatives</span>
              <span class="font-medium text-red-600">{{ analysisResults.falseNegatives }}</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-2">
          <button class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors">
            Download Report
          </button>
          <button 
            @click="clearAnalysis"
            class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors"
          >
            New Analysis
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
