<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Search, X, UserPlus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  projects: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['selectProject', 'refreshProjects'])

const api = useApi()

const showCreateDialog = ref(false)
const newProjectName = ref('')
const newProjectDescription = ref('')
const isCreating = ref(false)
const joiningProjectId = ref(null)
const errorMessage = ref('')
const allProjects = ref([])

// Fetch all projects on mount
const fetchAllProjects = async () => {
  try {
    allProjects.value = await api.get('/projects/all')
  } catch (error) {
    console.error('Failed to fetch all projects:', error)
  }
}

onMounted(() => {
  fetchAllProjects()
})

// Check if user is a member of a project
const isMember = (project) => {
  return props.projects.some(p => p.id === project.id)
}

const handleCreateProject = async () => {
  if (!newProjectName.value.trim()) return
  
  isCreating.value = true
  errorMessage.value = ''
  
  try {
    const payload = {
      name: newProjectName.value.trim(),
      description: newProjectDescription.value.trim() || undefined
    }
    
    const newProject = await api.post('/projects/', payload)
    
    console.log('Project created successfully:', newProject)
    
    // Reset form
    newProjectName.value = ''
    newProjectDescription.value = ''
    showCreateDialog.value = false
    
    // Refresh the projects list
    emit('refreshProjects')
    

  } catch (error) {
    console.error('Failed to create project:', error)
    errorMessage.value = error?.data?.detail || error?.message || 'Failed to create project. Please try again.'
  } finally {
    isCreating.value = false
  }
}

const handleJoinProject = async (project) => {
  joiningProjectId.value = project.id
  
  try {
    await api.post(`/projects/join/${project.name}`)
    
    // Refresh the projects list
    emit('refreshProjects')
    await fetchAllProjects()
    
    
  } catch (error) {
    console.error('Failed to join project:', error)
    const message = error?.data?.detail || error?.message || 'Failed to join project.'
    alert(message)
  } finally {
    joiningProjectId.value = null
  }
}

const handleDeleteProject = async (project, event) => {
  event.stopPropagation()
  
  try {
    await api.delete(`/projects/${project.id}`)
    
    // Refresh the projects list
    emit('refreshProjects')
    await fetchAllProjects()
    
  } catch (error) {
    console.error('Failed to delete project:', error)
    const message = error?.data?.detail || error?.message || 'Failed to delete project.'
    alert(message)
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
    <div class="mb-6">
      <button 
        @click="showCreateDialog = true"
        class="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
      >
        <Plus :size="18" />
        <span>Create Project</span>
      </button>
    </div>
    
    <!-- Projects List -->
    <div v-if="allProjects.length === 0" class="text-center py-12">
      <Search :size="48" class="mx-auto text-gray-300 mb-3" />
      <p class="text-gray-500 text-sm">No projects yet</p>
      <p class="text-gray-400 text-xs mt-1">Create a project to get started</p>
    </div>
    
    <div v-else class="space-y-3">
      <div 
        v-for="project in allProjects" 
        :key="project.id"
        class="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all relative"
        :class="{ 'cursor-pointer': isMember(project) }"
        @click="isMember(project) ? selectProject(project) : null"
      >
        <div class="flex items-start justify-between mb-2">
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900">{{ project.name }}</h3>
            <p class="text-sm text-gray-500 mt-1">{{ project.description || 'No description' }}</p>
          </div>
          
          <div class="flex items-center gap-2 ml-3">
            <!-- Join Button for non-member projects -->
            <button
              v-if="!isMember(project)"
              @click.stop="handleJoinProject(project)"
              :disabled="joiningProjectId === project.id"
              class="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white text-sm font-medium rounded-lg transition-colors disabled:cursor-not-allowed"
            >
              <UserPlus :size="16" />
              <span>{{ joiningProjectId === project.id ? 'Joining...' : 'Join' }}</span>
            </button>
            
            <!-- Member Badge -->
            <div
              v-else
              class="px-3 py-2 bg-green-100 text-green-700 text-xs font-semibold rounded-lg"
            >
              Member
            </div>
          </div>
        </div>
        
        <div class="flex items-end justify-between">
          <div class="flex gap-4 text-xs text-gray-400">
            <span>{{ project.images || 0 }} images</span>
            <span>{{ project.members || 0 }} members</span>
          </div>
          
          <!-- Delete Button at bottom right -->
          <button
            @click="handleDeleteProject(project, $event)"
            class="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete project"
          >
            <Trash2 :size="18" />
          </button>
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
  </div>
</template>
