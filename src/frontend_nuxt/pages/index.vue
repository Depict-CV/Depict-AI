<script setup>
import { ref } from 'vue'
import { FolderOpen, BarChart3, Bot, Settings, User, ChevronDown, Download, Upload, Microscope, Filter } from 'lucide-vue-next'

const { isSignedIn, user, signOut } = useAuth()

const showProfileMenu = ref(false)
const showSettingsDialog = ref(false)

// Redirect to login if not authenticated
if (!isSignedIn.value) {
  navigateTo('/login')
}

const activeMenu = ref(null)
const projects = ref([])

// Mock organization data - TODO: Replace with API call
const organizationMembers = ref([
  { id: 1, name: 'John Doe', email: 'john.doe@example.com', role: 'Admin', status: 'active' },
  { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com', role: 'Editor', status: 'active' },
  { id: 3, name: 'Bob Johnson', email: 'bob.johnson@example.com', role: 'Viewer', status: 'active' },
  { id: 4, name: 'Alice Williams', email: 'alice.williams@example.com', role: 'Editor', status: 'active' },
  { id: 5, name: 'Charlie Brown', email: 'charlie.brown@example.com', role: 'Viewer', status: 'inactive' }
])

definePageMeta({
  middleware: 'auth'
})

// Fetch projects
const api = useApi()
const fetchProjects = async () => {
  try {
    projects.value = await api.get('/projects/my-projects')
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  }
}

onMounted(async () => {
  await fetchProjects()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Top Navigation Bar -->
    <header class="fixed top-0 left-0 right-0 h-16 bg-white shadow-md z-50 flex items-center justify-between px-6">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-lg">D</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900">Depict AI</h1>
      </div>
      
      <div class="flex items-center gap-4 relative">
        <button 
          @click="showProfileMenu = !showProfileMenu"
          class="flex items-center gap-3 px-4 py-2 border border-gray-200 hover:bg-gray-50 rounded-lg transition-colors"
        >
          <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center">
            <User :size="18" />
          </div>
          <span class="text-gray-700 font-medium">
            {{ user?.username || user?.firstName || 'Account' }}
          </span>
          <ChevronDown :size="16" class="text-gray-500" />
        </button>
        
        <!-- Profile Dropdown Menu -->
        <ProfileMenu 
          :user="user"
          :showProfileMenu="showProfileMenu"
          @close="showProfileMenu = false"
          @openPanel="(panel) => activeMenu = panel"
          @openSettings="showSettingsDialog = true; showProfileMenu = false"
          @signOut="signOut"
        />
      </div>
    </header>

    <!-- Main Layout -->
    <div class="pt-16 flex">
      <!-- Sidebar -->
      <aside class="w-20 bg-white shadow-lg fixed left-0 top-16 bottom-0 z-40">
        <nav class="flex flex-col items-center py-6 gap-6 h-full">
          <div class="flex flex-col items-center gap-6">
            <button 
              @click="activeMenu = activeMenu === 'projects' ? null : 'projects'"
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200',
                activeMenu === 'projects' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              ]"
              title="Projects"
            >
              <FolderOpen :size="24" />
            </button>
            
            <button 
              @click="activeMenu = activeMenu === 'stats' ? null : 'stats'"
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200',
                activeMenu === 'stats' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              ]"
              title="Statistics"
            >
              <BarChart3 :size="24" />
            </button>
            
            <button 
              @click="activeMenu = activeMenu === 'ai' ? null : 'ai'"
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200',
                activeMenu === 'ai' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              ]"
              title="AI Tools"
            >
              <Bot :size="24" />
            </button>
            
            <button 
              @click="activeMenu = activeMenu === 'import-export' ? null : 'import-export'"
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200',
                activeMenu === 'import-export' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              ]"
              title="Import/Export"
            >
              <div class="relative w-6 h-6">
                <Upload :size="16" class="absolute top-0 left-0" />
                <Download :size="16" class="absolute bottom-0 right-0" />
              </div>
            </button>
            
            <button 
              @click="activeMenu = activeMenu === 'model-analysis' ? null : 'model-analysis'"
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200',
                activeMenu === 'model-analysis' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              ]"
              title="Model Analysis"
            >
              <Microscope :size="24" />
            </button>
            
            <button 
              @click="activeMenu = activeMenu === 'filter' ? null : 'filter'"
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200',
                activeMenu === 'filter' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              ]"
              title="Filter"
            >
              <Filter :size="24" />
            </button>
          </div>
          
          <!-- Settings at bottom -->
          <div class="mt-auto mb-6">
            <button 
              @click="showSettingsDialog = true"
              class="w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200 bg-gray-100 hover:bg-gray-200 text-gray-700"
              title="Settings"
            >
              <Settings :size="24" />
            </button>
          </div>
        </nav>
      </aside>

      <!-- Side Panel (conditionally shown) -->
      <aside 
        v-if="activeMenu"
        class="w-80 bg-white shadow-lg fixed left-20 top-16 bottom-0 z-30 overflow-y-auto"
      >
        <div class="p-6">
          <ProjectsPanel v-if="activeMenu === 'projects'" :projects="projects" @refreshProjects="fetchProjects" />
          <StatsPanel v-if="activeMenu === 'stats'" />
          <AIPanel v-if="activeMenu === 'ai'" />
          <SubscriptionPanel v-if="activeMenu === 'subscription'" />
          <OrganisationPanel v-if="activeMenu === 'organisation'" :members="organizationMembers" />
          <ImportExportPanel v-if="activeMenu === 'import-export'" />
          <ModelAnalysisPanel v-if="activeMenu === 'model-analysis'" />
          <FilterPanel v-if="activeMenu === 'filter'" />
        </div>
      </aside>
      
      <!-- Settings Dialog -->
      <SettingsDialog 
        v-if="showSettingsDialog"
        :user="user"
        @close="showSettingsDialog = false"
        @signOut="signOut"
      />

      <!-- Main Content Area -->
      <main 
        :class="[
          'flex-1 p-8 transition-all duration-300',
          activeMenu ? 'ml-[400px]' : 'ml-20'
        ]"
      >
        <div class="max-w-7xl mx-auto">
          <div class="card">
            <h2 class="text-3xl font-bold text-gray-900 mb-4">Welcome to Depict AI</h2>
            <p class="text-gray-600 text-lg mb-6">
              Manage your computer vision datasets, annotations, and AI models.
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div class="p-6 bg-blue-50 rounded-lg border border-blue-200">
                <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                  <FolderOpen :size="24" class="text-white" />
                </div>
                <h3 class="font-semibold text-lg mb-2">Projects</h3>
                <p class="text-gray-600 text-sm">Organize your datasets into projects</p>
              </div>
              
              <div class="p-6 bg-purple-50 rounded-lg border border-purple-200">
                <div class="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 :size="24" class="text-white" />
                </div>
                <h3 class="font-semibold text-lg mb-2">Analytics</h3>
                <p class="text-gray-600 text-sm">Track annotation progress</p>
              </div>
              
              <div class="p-6 bg-green-50 rounded-lg border border-green-200">
                <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
                  <Bot :size="24" class="text-white" />
                </div>
                <h3 class="font-semibold text-lg mb-2">AI Annotation</h3>
                <p class="text-gray-600 text-sm">Automate with machine learning</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
