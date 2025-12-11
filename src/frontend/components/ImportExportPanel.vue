<script setup>
import { ref } from 'vue'
import { Upload, Download, FileJson, FileImage, Database } from 'lucide-vue-next'

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  }
})

const selectedProject = ref(null)
const exportFormat = ref('json')
const importFile = ref(null)
const isExporting = ref(false)
const isImporting = ref(false)
const selectedImages = ref([])
const folderPath = ref('')
const basePath = ref('')

const api = useApi()
const { user } = useAuth()

const loadImagesFromPath = async () => {
  if (!basePath.value) {
    alert('Please enter a base directory path')
    return
  }
  
  const currentProjectId = props.projectId
  if (!currentProjectId) {
    alert('Please select a project first')
    return
  }
  
  isImporting.value = true
  try {
    // First, scan directory to get all image files
    const scanResult = await api.post('/data/scan-directory', {
      directory_path: basePath.value
    })
    
    if (!scanResult.images || scanResult.images.length === 0) {
      alert('No images found in the specified directory')
      isImporting.value = false
      return
    }
    
    // Prepare data for batch upload
    const dataList = scanResult.images.map(imagePath => ({
      location: imagePath,
      user_id: user.value.id,
      project_id: currentProjectId,
      creation_date: new Date().toISOString(),
      type: 'image'
    }))
    
    // Call batch endpoint to add all images
    const result = await api.post('/data/add_batch', dataList)
    
    alert(`Successfully loaded ${result.created} images! ${result.skipped} duplicates were skipped.`)
    basePath.value = ''
  } catch (error) {
    console.error('Failed to import images:', error)
    const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
    alert('Failed to import images: ' + errorMsg)
  } finally {
    isImporting.value = false
  }
}



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
    <h2 class="text-2xl font-bold mb-6">Import / Export</h2>
    
    <div class="space-y-6">
      <!-- Export Section -->
      <div class="pb-6 border-b border-gray-200">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <Download :size="20" class="text-green-600" />
          </div>
          <h3 class="text-lg font-semibold">Export Data</h3>
        </div>
        
        <div class="space-y-4">
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

      <!-- Import Section -->
      <div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Upload :size="20" class="text-blue-600" />
          </div>
          <h3 class="text-lg font-semibold">Import Data</h3>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Base Directory Path</label>
            <input 
              v-model="basePath"
              type="text"
              placeholder="e.g., C:/Users/YourName/Pictures or /home/user/images"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">Enter the full path to the folder containing your images. All images in the folder and subfolders will be imported.</p>
          </div>
          
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p class="text-sm text-yellow-800">
              <strong>Note:</strong> Importing will add data to your existing project. Duplicate entries will be skipped.
            </p>
          </div>
          
          <button 
            @click="loadImagesFromPath"
            :disabled="!basePath || isImporting"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <Upload :size="18" />
            <span v-if="!isImporting">Load Images from Directory</span>
            <span v-else>Loading...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
