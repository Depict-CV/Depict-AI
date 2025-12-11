<script setup>
import { ref } from 'vue'
import { Settings2 } from 'lucide-vue-next'

const props = defineProps({
  projectId: Number
})

// Cloud storage form data
const endpointUrl = ref('')
const bucketName = ref('')
const accessKeyId = ref('')
const secretAccessKey = ref('')
const useSSL = ref(false)
const autoSync = ref(true)
const syncInterval = ref(24) // hours

const api = useApi()

const handleTestConnection = async () => {
  try {
    const response = await api.post(`/projects/${props.projectId}/minio/test`, {
      endpoint: endpointUrl.value,
      bucket_name: bucketName.value,
      access_key: accessKeyId.value,
      secret_key: secretAccessKey.value,
      use_ssl: useSSL.value
    })
    
    if (response.bucket_exists) {
      alert('✓ Connection successful!\n\n' + 
            'Bucket exists: Yes\n' +
            'Read access: ' + (response.has_read_access ? 'Yes' : 'No'))
    } else {
      alert('⚠ Connection established but bucket not found.\n\n' + response.message)
    }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
    alert('✗ Connection failed!\n\n' + errorMsg)
    console.error('MinIO test error:', error)
  }
}

const handleSaveSettings = async () => {
  try {
    const response = await api.post(`/projects/${props.projectId}/minio/configure`, {
      endpoint: endpointUrl.value,
      bucket_name: bucketName.value,
      access_key: accessKeyId.value,
      secret_key: secretAccessKey.value,
      use_ssl: useSSL.value,
      auto_sync: autoSync.value,
      sync_interval_hours: syncInterval.value
    })
    
    const synced = response.images_synced || 0
    const skipped = response.images_skipped || 0
    
    alert('✓ Settings saved and sync completed!\n\n' +
          `Images imported: ${synced}\n` +
          `Images skipped (duplicates): ${skipped}\n` +
          `Auto-sync: ${response.auto_sync_enabled ? 'Enabled' : 'Disabled'}`)
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
          
          <!-- Bucket Name -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">
              Bucket Name
            </label>
            <input 
              v-model="bucketName"
              type="text"
              placeholder="my-bucket"
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
      
      <!-- Auto-Sync Configuration -->
      <div>
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Synchronization Settings</h3>
        
        <div class="space-y-4">
          <!-- Auto Sync -->
          <div class="flex items-center gap-2">
            <input 
              v-model="autoSync"
              type="checkbox"
              id="auto-sync"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label for="auto-sync" class="text-xs font-medium text-gray-600">
              Enable automatic synchronization
            </label>
          </div>
          
          <!-- Sync Interval -->
          <div v-if="autoSync">
            <label class="block text-xs font-medium text-gray-600 mb-1">
              Sync Interval (hours)
            </label>
            <select 
              v-model="syncInterval"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option :value="1">Every hour</option>
              <option :value="6">Every 6 hours</option>
              <option :value="12">Every 12 hours</option>
              <option :value="24">Every 24 hours (Daily)</option>
              <option :value="168">Every 7 days (Weekly)</option>
            </select>
          </div>
          
          <div class="bg-amber-50 border border-amber-200 rounded-md p-3">
            <p class="text-xs text-amber-800">
              <strong>Auto-sync:</strong> When enabled, all images from the MinIO bucket will be automatically imported to the database and kept in sync at the specified interval.
            </p>
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
          Save Settings
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

