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

</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Import</h2>
    
    <div class="space-y-6">
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

