<script setup>
import { ref } from 'vue'
import { X, User, Bell, Moon, Cloud, Key, Save } from 'lucide-vue-next'

const props = defineProps({
  user: Object
})

const emit = defineEmits(['close', 'signOut'])

const activeTab = ref('profile')

// Form data
const darkMode = ref(false)
const emailNotifications = ref(true)
const pushNotifications = ref(false)

// Cloud storage credentials
const cloudProvider = ref('s3')
const s3AccessKey = ref('')
const s3SecretKey = ref('')
const s3BucketName = ref('')
const s3Region = ref('us-east-1')

const azureConnectionString = ref('')
const azureContainerName = ref('')

const gcsProjectId = ref('')
const gcsCredentials = ref(null)

const handleSaveSettings = () => {
  // TODO: Implement save logic with API
  console.log('Saving settings...', {
    darkMode: darkMode.value,
    emailNotifications: emailNotifications.value,
    cloudProvider: cloudProvider.value,
  })
  alert('Settings saved successfully!')
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    gcsCredentials.value = file
  }
}
</script>

<template>
  <!-- Modal Overlay -->
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click="$emit('close')">
    <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col" @click.stop>
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-2xl font-bold text-gray-900">Settings</h2>
        <button 
          @click="$emit('close')"
          class="w-10 h-10 rounded-lg hover:bg-gray-100 flex items-center justify-center transition-colors"
        >
          <X :size="20" class="text-gray-500" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex flex-1 overflow-hidden">
        <!-- Sidebar Tabs -->
        <div class="w-48 border-r border-gray-200 p-4 space-y-1">
          <button 
            @click="activeTab = 'profile'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
              activeTab === 'profile' ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700 hover:bg-gray-50'
            ]"
          >
            <User :size="18" />
            <span>Profile</span>
          </button>
          
          <button 
            @click="activeTab = 'notifications'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
              activeTab === 'notifications' ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700 hover:bg-gray-50'
            ]"
          >
            <Bell :size="18" />
            <span>Notifications</span>
          </button>
          
          <button 
            @click="activeTab = 'appearance'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
              activeTab === 'appearance' ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700 hover:bg-gray-50'
            ]"
          >
            <Moon :size="18" />
            <span>Appearance</span>
          </button>
          
          <button 
            @click="activeTab = 'cloud'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
              activeTab === 'cloud' ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700 hover:bg-gray-50'
            ]"
          >
            <Cloud :size="18" />
            <span>Cloud Storage</span>
          </button>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 p-6 overflow-y-auto">
          <!-- Profile Tab -->
          <div v-if="activeTab === 'profile'" class="space-y-6">
            <div>
              <h3 class="text-lg font-semibold mb-4">Profile Information</h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                  <input 
                    type="text" 
                    :value="user?.username || 'Not set'" 
                    disabled
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input 
                    type="email" 
                    :value="user?.primaryEmailAddress?.emailAddress" 
                    disabled
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                  />
                </div>
                <div class="pt-4">
                  <p class="text-sm text-gray-500">Profile information is managed through your Clerk account.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Notifications Tab -->
          <div v-if="activeTab === 'notifications'" class="space-y-6">
            <div>
              <h3 class="text-lg font-semibold mb-4">Notification Preferences</h3>
              <div class="space-y-4">
                <label class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <div class="font-medium text-gray-900">Email Notifications</div>
                    <div class="text-sm text-gray-500">Receive updates via email</div>
                  </div>
                  <input type="checkbox" v-model="emailNotifications" class="w-5 h-5 rounded text-blue-600">
                </label>
                
                <label class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <div class="font-medium text-gray-900">Push Notifications</div>
                    <div class="text-sm text-gray-500">Browser notifications for important events</div>
                  </div>
                  <input type="checkbox" v-model="pushNotifications" class="w-5 h-5 rounded text-blue-600">
                </label>
              </div>
            </div>
          </div>

          <!-- Appearance Tab -->
          <div v-if="activeTab === 'appearance'" class="space-y-6">
            <div>
              <h3 class="text-lg font-semibold mb-4">Appearance Settings</h3>
              <div class="space-y-4">
                <label class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <div class="font-medium text-gray-900">Dark Mode</div>
                    <div class="text-sm text-gray-500">Enable dark theme across the application</div>
                  </div>
                  <input type="checkbox" v-model="darkMode" class="w-5 h-5 rounded text-blue-600">
                </label>
              </div>
            </div>
          </div>

          <!-- Cloud Storage Tab -->
          <div v-if="activeTab === 'cloud'" class="space-y-6">
            <div>
              <h3 class="text-lg font-semibold mb-4">Cloud Storage Configuration</h3>
              
              <!-- Provider Selection -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-3">Storage Provider</label>
                <div class="space-y-2">
                  <label class="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                    <input type="radio" v-model="cloudProvider" value="s3" class="w-4 h-4 text-blue-600">
                    <div>
                      <div class="font-medium text-gray-900">Amazon S3</div>
                      <div class="text-xs text-gray-500">AWS Simple Storage Service</div>
                    </div>
                  </label>
                  
                  <label class="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                    <input type="radio" v-model="cloudProvider" value="azure" class="w-4 h-4 text-blue-600">
                    <div>
                      <div class="font-medium text-gray-900">Azure Blob Storage</div>
                      <div class="text-xs text-gray-500">Microsoft Azure storage</div>
                    </div>
                  </label>
                  
                  <label class="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                    <input type="radio" v-model="cloudProvider" value="gcs" class="w-4 h-4 text-blue-600">
                    <div>
                      <div class="font-medium text-gray-900">Google Cloud Storage</div>
                      <div class="text-xs text-gray-500">GCP storage buckets</div>
                    </div>
                  </label>
                </div>
              </div>

              <!-- AWS S3 Configuration -->
              <div v-if="cloudProvider === 's3'" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Access Key ID</label>
                  <input 
                    type="text" 
                    v-model="s3AccessKey"
                    placeholder="AKIAIOSFODNN7EXAMPLE"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Secret Access Key</label>
                  <input 
                    type="password" 
                    v-model="s3SecretKey"
                    placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Bucket Name</label>
                  <input 
                    type="text" 
                    v-model="s3BucketName"
                    placeholder="my-bucket-name"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Region</label>
                  <select 
                    v-model="s3Region"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="us-east-1">US East (N. Virginia)</option>
                    <option value="us-west-2">US West (Oregon)</option>
                    <option value="eu-west-1">EU (Ireland)</option>
                    <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                  </select>
                </div>
              </div>

              <!-- Azure Configuration -->
              <div v-if="cloudProvider === 'azure'" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Connection String</label>
                  <textarea 
                    v-model="azureConnectionString"
                    placeholder="DefaultEndpointsProtocol=https;AccountName=..."
                    rows="3"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Container Name</label>
                  <input 
                    type="text" 
                    v-model="azureContainerName"
                    placeholder="my-container"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <!-- GCS Configuration -->
              <div v-if="cloudProvider === 'gcs'" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Project ID</label>
                  <input 
                    type="text" 
                    v-model="gcsProjectId"
                    placeholder="my-project-id"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Service Account Credentials</label>
                  <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                    <input 
                      type="file" 
                      @change="handleFileUpload"
                      accept=".json"
                      class="hidden" 
                      id="gcs-credentials"
                    />
                    <label for="gcs-credentials" class="cursor-pointer">
                      <Key :size="32" class="mx-auto text-gray-400 mb-2" />
                      <p class="text-sm text-gray-600 mb-1">
                        <span class="text-blue-600 font-medium">Upload credentials JSON</span>
                      </p>
                      <p class="text-xs text-gray-500">Service account key file</p>
                    </label>
                  </div>
                  
                  <div v-if="gcsCredentials" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <Key :size="18" class="text-blue-600" />
                      <span class="text-sm font-medium text-gray-900">{{ gcsCredentials.name }}</span>
                    </div>
                    <button 
                      @click="gcsCredentials = null"
                      class="text-red-600 hover:text-red-700 text-sm font-medium"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>

              <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
                <p class="text-sm text-yellow-800">
                  <strong>Note:</strong> Credentials are encrypted and stored securely. They are used only for accessing your cloud storage.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
        <button 
          @click="$emit('signOut')"
          class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
        >
          Sign Out
        </button>
        
        <div class="flex gap-3">
          <button 
            @click="$emit('close')"
            class="px-6 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors font-medium"
          >
            Cancel
          </button>
          <button 
            @click="handleSaveSettings"
            class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium flex items-center gap-2"
          >
            <Save :size="18" />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
