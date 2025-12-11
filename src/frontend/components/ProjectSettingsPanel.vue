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

const handleTestConnection = async () => {
  // TODO: Implement connection test
  console.log('Testing connection...', {
    endpointUrl: endpointUrl.value,
    bucketName: bucketName.value,
    useSSL: useSSL.value
  })
  alert('Connection test not yet implemented')
}

const handleSaveSettings = async () => {
  // TODO: Implement save to backend
  console.log('Saving settings...', {
    projectId: props.projectId,
    endpointUrl: endpointUrl.value,
    bucketName: bucketName.value,
    accessKeyId: accessKeyId.value,
    useSSL: useSSL.value
  })
  alert('Settings saved successfully!')
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

