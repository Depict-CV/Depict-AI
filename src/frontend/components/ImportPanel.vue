<script setup>
import { ref } from 'vue'
import { Upload, FolderOpen, Database as DatabaseIcon } from 'lucide-vue-next'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const importMethod = ref('local') // 'local', 'minio'
const isImporting = ref(false)
const basePath = ref('')
const minioBucket = ref('')

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
      directory_path: basePath.value,
    })

    if (!scanResult.images || scanResult.images.length === 0) {
      alert('No images found in the specified directory')
      isImporting.value = false
      return
    }

    // Prepare data for batch upload
    const dataList = scanResult.images.map((imagePath) => ({
      location: imagePath,
      user_id: user.value.id,
      project_id: currentProjectId,
      creation_date: new Date().toISOString(),
      type: 'image',
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

const syncMinIOStorage = async () => {
  if (!minioBucket.value) {
    alert('Please enter a bucket name')
    return
  }

  const currentProjectId = props.projectId
  if (!currentProjectId) {
    alert('Please select a project first')
    return
  }

  isImporting.value = true
  try {
    // Call the manual sync endpoint with bucket name
    const response = await api.post(`/projects/${currentProjectId}/minio/sync`, {
      bucket_name: minioBucket.value,
    })

    const synced = response.images_synced || 0
    const skipped = response.images_skipped || 0

    alert(`✓ MinIO sync completed!\n\n` + `Images imported: ${synced}\n` + `Images skipped (duplicates): ${skipped}`)
    minioBucket.value = ''
  } catch (error) {
    console.error('Failed to sync MinIO:', error)
    const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'

    if (errorMsg.includes('not configured')) {
      alert('✗ MinIO sync failed!\n\n' + errorMsg + '\n\nPlease configure MinIO credentials in Project Settings first.')
    } else {
      alert('✗ MinIO sync failed!\n\n' + errorMsg)
    }
  } finally {
    isImporting.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Import Data</h2>

    <div class="space-y-6">
      <!-- Import Method Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-3">Select Import Method</label>
        <div class="space-y-2">
          <!-- Local Directory -->
          <label
            class="flex items-center gap-3 p-3 border-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            :class="importMethod === 'local' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
          >
            <input type="radio" v-model="importMethod" value="local" class="w-4 h-4 text-blue-600" />
            <FolderOpen :size="20" class="text-gray-600" />
            <div class="flex-1">
              <div class="font-medium text-gray-900">Local Directory</div>
              <div class="text-xs text-gray-500">Import images from your computer</div>
            </div>
          </label>

          <!-- MinIO Storage -->
          <label
            class="flex items-center gap-3 p-3 border-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            :class="importMethod === 'minio' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
          >
            <input type="radio" v-model="importMethod" value="minio" class="w-4 h-4 text-blue-600" />
            <DatabaseIcon :size="20" class="text-gray-600" />
            <div class="flex-1">
              <div class="font-medium text-gray-900">MinIO Storage</div>
              <div class="text-xs text-gray-500">Sync from configured MinIO bucket</div>
            </div>
          </label>
        </div>
      </div>

      <!-- Local Directory Import -->
      <div v-if="importMethod === 'local'" class="space-y-4">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <FolderOpen :size="20" class="text-blue-600" />
          </div>
          <h3 class="text-lg font-semibold">Import from Local Directory</h3>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Base Directory Path</label>
          <input
            v-model="basePath"
            type="text"
            placeholder="e.g., C:/Users/YourName/Pictures or /home/user/images"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="text-xs text-gray-500 mt-1">
            Enter the full path to the folder containing your images. All images in the folder and subfolders will be
            imported.
          </p>
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

      <!-- MinIO Storage Import -->
      <div v-if="importMethod === 'minio'" class="space-y-4">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <DatabaseIcon :size="20" class="text-blue-600" />
          </div>
          <h3 class="text-lg font-semibold">Sync from MinIO Storage</h3>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Bucket Name</label>
          <input
            v-model="minioBucket"
            type="text"
            placeholder="e.g., my-images-bucket"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="text-xs text-gray-500 mt-1">Enter the name of the MinIO bucket to sync images from.</p>
        </div>

        <div class="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p class="text-sm text-amber-800">
            <strong>Prerequisites:</strong> MinIO credentials must be configured in
            <strong>Project Settings</strong> before syncing.
          </p>
        </div>

        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-sm text-blue-800">
            This will sync all images from the configured MinIO bucket to your project. Images already in the database
            will be skipped.
          </p>
        </div>

        <button
          @click="syncMinIOStorage"
          :disabled="!projectId || !minioBucket || isImporting"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <DatabaseIcon :size="18" />
          <span v-if="!isImporting">Sync MinIO Storage</span>
          <span v-else>Syncing...</span>
        </button>
      </div>
    </div>
  </div>
</template>
