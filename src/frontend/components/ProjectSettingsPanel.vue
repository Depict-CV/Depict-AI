<script setup>
import { ref, watch, onMounted } from 'vue'
import { Settings2 } from 'lucide-vue-next'

const props = defineProps({
  projectId: Number
})

// Cloud storage form data
const endpointUrl = ref('')
const accessKeyId = ref('')
const secretAccessKey = ref('')
const useSSL = ref(false)
const isLoading = ref(false)

const api = useApi()

// Load MinIO configuration when project changes
const loadMinIOConfig = async () => {
  if (!props.projectId) return
  
  isLoading.value = true
  try {
    const response = await api.get(`/projects/${props.projectId}/minio/config`)
    
    if (response.configured) {
      endpointUrl.value = response.endpoint
      accessKeyId.value = response.access_key
      secretAccessKey.value = response.secret_key
      useSSL.value = response.use_ssl
    } else {
      // Reset form if no config exists
      resetForm()
    }
  } catch (error) {
    console.error('Failed to load MinIO config:', error)
    // Reset form on error
    resetForm()
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  endpointUrl.value = ''
  accessKeyId.value = ''
  secretAccessKey.value = ''
  useSSL.value = false
}

// Watch for project ID changes
watch(() => props.projectId, (newProjectId) => {
  if (newProjectId) {
    loadMinIOConfig()
  } else {
    resetForm()
  }
}, { immediate: true })

// Load on mount
onMounted(() => {
  if (props.projectId) {
    loadMinIOConfig()
  }
})

const handleTestConnection = async () => {
  try {
    const response = await api.post(`/projects/${props.projectId}/minio/test`, {
      endpoint: endpointUrl.value,
      access_key: accessKeyId.value,
      secret_key: secretAccessKey.value,
      use_ssl: useSSL.value
    })
    
    alert('✓ MinIO connection successful!\n\nServer is accessible and credentials are valid.')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
    alert('✗ Connection failed!\n\n' + errorMsg)
    console.error('MinIO test error:', error)
  }
}

const handleSaveSettings = async () => {
  try {
    await api.post(`/projects/${props.projectId}/minio/configure`, {
      endpoint: endpointUrl.value,
      access_key: accessKeyId.value,
      secret_key: secretAccessKey.value,
      use_ssl: useSSL.value
    })
    
    alert('✓ Settings saved successfully!')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
    alert('✗ Save failed!\n\n' + errorMsg)
    console.error('MinIO save error:', error)
  }
}
</script>

<template>
  <div>
    <h2 class="text-lg font-bold text-gray-900 mb-6">Project Settings</h2>
    
    <div v-if="!projectId" class="text-center py-8">
      <Settings2 :size="48" class="mx-auto text-gray-300 mb-3" />
      <p class="text-gray-500 text-sm">No project selected</p>
      <p class="text-gray-400 text-xs mt-1">Select a project to configure settings</p>
    </div>
    
    <div v-else-if="isLoading" class="text-center py-8">
      <Settings2 :size="48" class="mx-auto text-blue-300 mb-3 animate-pulse" />
      <p class="text-gray-500 text-sm">Loading configuration...</p>
    </div>
    
    <div v-else class="space-y-6">
      <div>
        <h3 class="text-sm font-semibold text-gray-700 mb-3">MinIO Storage Configuration</h3>
        
        <div class="space-y-4">
          <!-- Endpoint URL -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">
              MinIO Endpoint URL
            </label>
            <input 
              v-model="endpointUrl"
              type="text"
              placeholder="http://localhost:9000"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <!-- Access Key -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">
              Access Key
            </label>
            <input 
              v-model="accessKeyId"
              type="text"
              placeholder="minioadmin"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <!-- Secret Key -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">
              Secret Key
            </label>
            <input 
              v-model="secretAccessKey"
              type="password"
              placeholder="minioadmin"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <!-- Use SSL -->
          <div class="flex items-center gap-2">
            <input 
              v-model="useSSL"
              type="checkbox"
              id="use-ssl"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label for="use-ssl" class="text-xs font-medium text-gray-600">
              Use SSL/TLS
            </label>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="flex gap-2 pt-4 border-t border-gray-200">
        <button 
          @click="handleTestConnection"
          class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors"
        >
          Test Connection
        </button>
        <button 
          @click="handleSaveSettings"
          class="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors"
        >
          Save Credentials
        </button>
      </div>
      
      <!-- Info Message -->
      <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
        <p class="text-xs text-blue-800">
          <strong>Note:</strong> Credentials are encrypted and stored securely. They will be used to sync images and annotations with your MinIO storage.
        </p>
      </div>
    </div>
  </div>
</template>
