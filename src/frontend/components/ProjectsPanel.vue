<script setup>
import { ref } from 'vue'
import { Plus, Users, Search, X } from 'lucide-vue-next'

const props = defineProps({
  projects: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['selectProject', 'refreshProjects'])

const api = useApi()

const showCreateDialog = ref(false)
const showJoinDialog = ref(false)
const newProjectName = ref('')
const newProjectDescription = ref('')
const joinProjectCode = ref('')
const isCreating = ref(false)
const isJoining = ref(false)
const errorMessage = ref('')

const handleCreateProject = async () => {
  if (!newProjectName.value.trim()) return
  
  isCreating.value = true
  errorMessage.value = ''
  
  try {
    const newProject = await api.post('/projects/', {
      name: newProjectName.value,
      description: newProjectDescription.value
    })
    
    // Reset form
    newProjectName.value = ''
    newProjectDescription.value = ''
    showCreateDialog.value = false
    
    // Refresh the projects list
    emit('refreshProjects')
    
    // Show success message
    alert(`Project "${newProject.name}" created successfully!`)
  } catch (error) {
    console.error('Failed to create project:', error)
    errorMessage.value = error.data?.detail || 'Failed to create project. Please try again.'
  } finally {
    isCreating.value = false
  }
}

const handleJoinProject = async () => {
  if (!joinProjectCode.value.trim()) return
  
  isJoining.value = true
  errorMessage.value = ''
  
  try {
    await api.post(`/projects/join/${joinProjectCode.value}`)
    
    // Reset form
    joinProjectCode.value = ''
    showJoinDialog.value = false
    
    // Refresh the projects list
    emit('refreshProjects')
    
    // Show success message
    alert('Successfully joined project!')
  } catch (error) {
    console.error('Failed to join project:', error)
    errorMessage.value = error.data?.detail || 'Failed to join project. Please check the code and try again.'
  } finally {
    isJoining.value = false
  }
}

const selectProject = (project) => {
  emit('selectProject', project)
  // TODO: Navigate to project detail page
  console.log('Selected project:', project)
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">My Projects</h2>
    
    <!-- Action Buttons -->
    <div class="space-y-2 mb-6">
      <button 
        @click="showCreateDialog = true"
        class="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
      >
        <Plus :size="18" />
        <span>Create Project</span>
      </button>
      
      <button 
        @click="showJoinDialog = true"
        class="w-full flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors"
      >
        <Users :size="18" />
        <span>Join Project</span>
      </button>
    </div>
    
    <!-- Projects List -->
    <div v-if="projects.length === 0" class="text-center py-12">
      <Search :size="48" class="mx-auto text-gray-300 mb-3" />
      <p class="text-gray-500 text-sm">No projects yet</p>
      <p class="text-gray-400 text-xs mt-1">Create or join a project to get started</p>
    </div>
    
    <div v-else class="space-y-3">
      <div 
        v-for="project in projects" 
        :key="project.id"
        @click="selectProject(project)"
        class="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
      >
        <h3 class="font-semibold text-gray-900">{{ project.name }}</h3>
        <p class="text-sm text-gray-500 mt-1">{{ project.description || 'No description' }}</p>
        <div class="flex gap-4 mt-3 text-xs text-gray-400">
          <span>{{ project.images || 0 }} images</span>
          <span>{{ project.members || 0 }} members</span>
        </div>
      </div>
    </div>

    <!-- Create Project Dialog -->
    <div v-if="showCreateDialog" class="fixed inset-0 bg-black bg-opacity-50 z-[100] flex items-center justify-center p-4" @click="showCreateDialog = false">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6" @click.stop>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900">Create New Project</h3>
          <button @click="showCreateDialog = false" class="text-gray-400 hover:text-gray-600">
            <X :size="20" />
          </button>
        </div>
        
        <div class="space-y-4">
          <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {{ errorMessage }}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Project Name *</label>
            <input 
              v-model="newProjectName"
              type="text" 
              placeholder="e.g., Vehicle Detection Dataset"
              :disabled="isCreating"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea 
              v-model="newProjectDescription"
              placeholder="Brief description of your project..."
              rows="3"
              :disabled="isCreating"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            ></textarea>
          </div>
          
          <div class="flex gap-3 pt-4">
            <button 
              @click="showCreateDialog = false"
              :disabled="isCreating"
              class="flex-1 px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors font-medium disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button 
              @click="handleCreateProject"
              :disabled="!newProjectName.trim() || isCreating"
              class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium"
            >
              {{ isCreating ? 'Creating...' : 'Create' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Join Project Dialog -->
    <div v-if="showJoinDialog" class="fixed inset-0 bg-black bg-opacity-50 z-[100] flex items-center justify-center p-4" @click="showJoinDialog = false">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6" @click.stop>
        <div class="space-y-4">
          <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {{ errorMessage }}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Project Invite Code *</label>
            <input 
              v-model="joinProjectCode"
              type="text" 
              placeholder="e.g., ABC123XYZ"
              :disabled="isJoining"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase disabled:bg-gray-100"
            />
            <p class="text-xs text-gray-500 mt-2">Enter the invite code shared by the project owner</p>
          </div>
          
          <div class="flex gap-3 pt-4">
            <button 
              @click="showJoinDialog = false"
              :disabled="isJoining"
              class="flex-1 px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors font-medium disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button 
              @click="handleJoinProject"
              :disabled="!joinProjectCode.trim() || isJoining"
              class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium"
            >
              {{ isJoining ? 'Joining...' : 'Join' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
