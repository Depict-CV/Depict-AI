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

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  
  if (imageFiles.length > 0) {
    selectedImages.value = imageFiles.map(file => ({
      file: file,
      path: file.path || file.webkitRelativePath || file.name // Full path (Electron) or relative path
    }))
    if (imageFiles[0].webkitRelativePath) {
      folderPath.value = imageFiles[0].webkitRelativePath.split('/')[0]
    } else {
      folderPath.value = `${imageFiles.length} image(s)`
    }
  } else {
    // Single file upload (non-image)
    const file = files[0]
    if (file) {
      importFile.value = file
    }
  }
}

const handleImport = async () => {
  // Check if importing images or annotation file
  if (selectedImages.value.length > 0) {
    // Import images
    const currentProjectId = props.projectId
    if (!currentProjectId) {
      alert('Please select a project first')
      return
    }
    
    isImporting.value = true
    try {
      // Prepare data for batch upload
      // TODO: Upload files to remote storage (S3, MinIO) and use remote URLs
      // For now, using local file paths
      const dataList = selectedImages.value.map(item => {
        // Construct full path: base path + relative path
        let fullPath = item.path
        if (basePath.value && !item.path.includes(basePath.value)) {
          // Normalize path separators
          const normalizedBase = basePath.value.replace(/\\/g, '/')
          const normalizedRelative = item.path.replace(/\\/g, '/')
          fullPath = `${normalizedBase}/${normalizedRelative}`.replace(/\/+/g, '/')
        }
        
        return {
          location: fullPath, // Full local file path
          user_id: user.value.id,
          project_id: currentProjectId,
          type: 'image'
        }
      })
      
      // Call batch endpoint
      const result = await api.post('/data/add_batch', dataList)
      
      alert(`Successfully loaded ${result.created} images! ${result.skipped} duplicates were skipped.`)
      
      // Clear selection
      selectedImages.value = []
      folderPath.value = ''
    } catch (error) {
      console.error('Failed to import images:', error)
      alert('Failed to import images')
    } finally {
      isImporting.value = false
    }
  } else if (importFile.value) {
    // Import annotation file
    isImporting.value = true
    try {
      // TODO: Implement actual import logic with API
      console.log('Importing:', importFile.value.name)
      await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
      alert('Import successful!')
    } catch (error) {
      console.error('Import failed:', error)
      alert('Import failed!')
    } finally {
      isImporting.value = false
      importFile.value = null
    }
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
            <p class="text-xs text-gray-500 mt-1">Enter the full path to the folder containing your images</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload Images or Folder</label>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
              <input 
                type="file" 
                @change="handleFileUpload"
                webkitdirectory
                directory
                multiple
                accept=".jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.tiff,.tif,.ico"
                class="hidden" 
                id="file-upload"
              />
              <label for="file-upload" class="cursor-pointer">
                <Upload :size="32" class="mx-auto text-gray-400 mb-2" />
                <p class="text-sm text-gray-600 mb-1">
                  <span class="text-blue-600 font-medium">Click to select folder</span> with images
                </p>
                <p class="text-xs text-gray-500">Supported: JPG, PNG, GIF, BMP, WEBP, SVG, TIFF</p>
              </label>
            </div>
            
            <div v-if="selectedImages.length > 0" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <FileImage :size="18" class="text-blue-600" />
                  <span class="text-sm font-medium text-gray-900">{{ folderPath }}</span>
                </div>
                <button 
                  @click="selectedImages = []; folderPath = ''"
                  class="text-red-600 hover:text-red-700 text-sm font-medium"
                >
                  Clear
                </button>
              </div>
              <p class="text-xs text-gray-600">{{ selectedImages.length }} images selected</p>
            </div>

            <div v-else-if="importFile" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between">
              <div class="flex items-center gap-2">
                <FileJson :size="18" class="text-blue-600" />
                <span class="text-sm font-medium text-gray-900">{{ importFile.name }}</span>
              </div>
              <button 
                @click="importFile = null"
                class="text-red-600 hover:text-red-700 text-sm font-medium"
              >
                Remove
              </button>
            </div>
          </div>
          
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p class="text-sm text-yellow-800">
              <strong>Note:</strong> Importing will add data to your existing project. Duplicate entries will be skipped.
            </p>
          </div>
          
          <button 
            @click="handleImport"
            :disabled="(!importFile && selectedImages.length === 0) || isImporting"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <Upload :size="18" />
            <span v-if="!isImporting">{{ selectedImages.length > 0 ? 'Load Images to Database' : 'Import Data' }}</span>
            <span v-else>{{ selectedImages.length > 0 ? 'Loading...' : 'Importing...' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
