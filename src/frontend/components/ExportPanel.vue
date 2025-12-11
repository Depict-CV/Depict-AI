<script setup>
import { ref } from 'vue'
import { Download, FileJson, FileImage, Database } from 'lucide-vue-next'

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  }
})

const exportFormat = ref('json')
const isExporting = ref(false)

const handleExport = async () => {
  isExporting.value = true
  try {
    // TODO: Implement actual export logic with API
    console.log('Exporting format:', exportFormat.value)
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
    alert('Export successful!')
  } catch (error) {
    console.error('Export failed:', error)
    alert('Export failed!')
  } finally {
    isExporting.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Export Data</h2>
    
    <div class="space-y-4">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
          <Download :size="20" class="text-green-600" />
        </div>
        <p class="text-sm text-gray-600">Export project data and annotations</p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
        <div class="space-y-2">
          <label class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
            <input type="radio" v-model="exportFormat" value="json" class="w-4 h-4 text-blue-600">
            <FileJson :size="18" class="text-gray-600" />
            <div class="flex-1">
              <div class="font-medium text-gray-900">JSON</div>
              <div class="text-xs text-gray-500">COCO format, annotations included</div>
            </div>
          </label>
          
          <label class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
            <input type="radio" v-model="exportFormat" value="csv" class="w-4 h-4 text-blue-600">
            <Database :size="18" class="text-gray-600" />
            <div class="flex-1">
              <div class="font-medium text-gray-900">CSV</div>
              <div class="text-xs text-gray-500">Tabular data, metadata only</div>
            </div>
          </label>
          
          <label class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
            <input type="radio" v-model="exportFormat" value="images" class="w-4 h-4 text-blue-600">
            <FileImage :size="18" class="text-gray-600" />
            <div class="flex-1">
              <div class="font-medium text-gray-900">Images + Annotations</div>
              <div class="text-xs text-gray-500">ZIP archive with images and labels</div>
            </div>
          </label>
        </div>
      </div>
      
      <button 
        @click="handleExport"
        :disabled="isExporting"
        class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Download :size="18" />
        <span v-if="!isExporting">Export Data</span>
        <span v-else>Exporting...</span>
      </button>
    </div>
  </div>
</template>
