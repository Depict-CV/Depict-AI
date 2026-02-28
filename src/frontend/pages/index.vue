<script setup>
import { ref } from 'vue'
import {
  FolderOpen,
  BarChart3,
  Bot,
  ChevronDown,
  Download,
  Upload,
  Database,
  Microscope,
  Filter,
  Bell,
  X,
  Trash2,
  CheckCircle,
  Settings2,
} from 'lucide-vue-next'
import ProjectsPanel from '~/components/main/ProjectsPanel.vue'
import StatsPanel from '~/components/main/StatsPanel.vue'
import AIPanel from '~/components/main/AIPanel.vue'
import ImportPanel from '~/components/main/ImportPanel.vue'
import DataAquisitionPanel from '~/components/main/DataAquisitionPanel.vue'
import ExportPanel from '~/components/main/ExportPanel.vue'
import ModelAnalysisPanel from '~/components/main/ModelAnalysisPanel.vue'
import FilterPanel from '~/components/main/FilterPanel.vue'
import ProjectSettingsPanel from '~/components/main/ProjectSettingsPanel.vue'
import ProfileMenu from '~/components/main/ProfileMenu.vue'
import SettingsDialog from '~/components/main/SettingsDialog.vue'
import SubscriptionPanel from '~/components/main/SubscriptionPanel.vue'
import OrganisationPanel from '~/components/main/OrganisationPanel.vue'
import ImageGallery from '~/components/main/ImageGallery.vue'
import SatelliteStacPanel from '~/components/main/SatelliteStacPanel.vue'

const { isSignedIn, user, signOut } = useAuth()

const showProfileMenu = ref(false)
const showSettingsDialog = ref(false)

// Redirect to login if not authenticated
if (!isSignedIn.value) {
  navigateTo('/login')
}

const activeMenu = ref(null)
const projects = ref([])
const selectedProject = ref(null)
const showImageGallery = ref(true)
const selectedImage = ref(null)
const changeRequests = ref([])
const showNotificationCenter = ref(false)
const currentFilters = ref({})
const selectedImagesFromGallery = ref(new Set())
const imageGalleryKey = ref(0)
const inferenceResults = ref(null)
const mainViewMode = ref('gallery')

const handleApplyFilters = (filters) => {
  currentFilters.value = filters
  console.log('Filters applied:', filters)
}

const handleInferenceResults = (results) => {
  inferenceResults.value = results
  console.log('Inference results received:', results)
}

const handleSelectionChange = (selectedImages) => {
  selectedImagesFromGallery.value = selectedImages
}

const handleDataAquisitionSelect = (category) => {
  if (category?.key === 'satellite') {
    mainViewMode.value = 'satellite-stac'
    return
  }

  if (category?.key === 'hugging-face-dataset') {
    mainViewMode.value = 'hf-datasets'
    return
  }

  mainViewMode.value = 'gallery'
}

const handleSelectProject = (project) => {
  selectedProject.value = project
  showImageGallery.value = true
  // Keep sidebar open after selecting project
  // Persist selected project to sessionStorage
  if (project) {
    sessionStorage.setItem('selectedProject', JSON.stringify(project))
  }
}

const handleSelectImage = (image) => {
  selectedImage.value = image
  navigateTo(`/annotate/${image.id}`)
}

const handleModifyRequest = (image) => {
  // Add change request to notification center
  const newRequest = {
    id: Date.now(),
    imageId: image.id,
    image,
    type: 'annotation_change',
    status: 'pending',
    createdAt: new Date().toISOString(),
    project: selectedProject.value?.name || 'Unknown Project',
    projectId: selectedProject.value?.id,
  }

  // Add to the beginning of the array (top of the list)
  changeRequests.value.unshift(newRequest)

  // Save to localStorage
  saveNotificationsToStorage()

  console.log('Change request added:', image)
}

const organizationMembers = ref([])

definePageMeta({
  middleware: 'auth',
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

// Fetch organization members
const fetchOrganizationMembers = async () => {
  try {
    const users = await api.get('/users/')
    // Transform user data to match the expected format
    organizationMembers.value = users.map((user) => ({
      id: user.id,
      name: user.username,
      email: user.email,
      role: getRoleFromPermission(user.permission),
      status: 'active', // You can add a status field to User model if needed
    }))
  } catch (error) {
    console.error('Failed to fetch organization members:', error)
  }
}

// Map permission enum to role display
const getRoleFromPermission = (permission) => {
  const roleMap = {
    'can certify': 'Admin',
    'edit & delete': 'Editor',
    edit: 'Editor',
    'view only': 'Viewer',
  }
  return roleMap[permission] || 'Viewer'
}

const saveNotificationsToStorage = () => {
  try {
    localStorage.setItem('changeRequests', JSON.stringify(changeRequests.value))
  } catch (error) {
    console.error('Failed to save notifications:', error)
  }
}

const loadNotificationsFromStorage = () => {
  try {
    const saved = localStorage.getItem('changeRequests')
    if (saved) {
      changeRequests.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('Failed to load notifications:', error)
  }
}

const removeChangeRequest = (requestId) => {
  changeRequests.value = changeRequests.value.filter((req) => req.id !== requestId)
  saveNotificationsToStorage()
}

const markAsCompleted = (requestId) => {
  // Remove the request instead of marking it as completed
  changeRequests.value = changeRequests.value.filter((req) => req.id !== requestId)
  saveNotificationsToStorage()
}

const openChangeRequest = (request) => {
  // Navigate to annotation page for the image
  navigateTo(`/annotate/${request.imageId}`)
  showNotificationCenter.value = false
}

onMounted(async () => {
  await fetchProjects()
  await fetchOrganizationMembers()

  // Restore selected project from sessionStorage
  const savedProject = sessionStorage.getItem('selectedProject')
  if (savedProject) {
    try {
      selectedProject.value = JSON.parse(savedProject)
    } catch (error) {
      console.error('Failed to restore selected project:', error)
    }
  }

  // Load notifications from localStorage
  loadNotificationsFromStorage()
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Top Navigation Bar -->
    <header
      class="fixed top-0 left-0 right-0 h-14 bg-white border-b border-gray-100 z-50 flex items-center justify-between px-8"
    >
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-bold text-blue-950">Depict AI</h1>
      </div>

      <div class="flex items-center gap-4 relative">
        <!-- Notification Bell -->
        <button
          class="relative p-2 hover:bg-gray-50 rounded-md transition-colors"
          title="Change Requests"
          @click="showNotificationCenter = !showNotificationCenter"
        >
          <Bell :size="20" class="text-gray-600" />
          <span
            v-if="changeRequests.filter((r) => r.status === 'pending').length > 0"
            class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold"
          >
            {{ changeRequests.filter((r) => r.status === 'pending').length }}
          </span>
        </button>

        <button
          class="flex items-center gap-2 px-3 py-1.5 hover:bg-gray-50 rounded-md transition-colors"
          @click="showProfileMenu = !showProfileMenu"
        >
          <div class="w-7 h-7 rounded-full bg-blue-950 text-white flex items-center justify-center text-xs font-medium">
            <span v-if="(user?.username || user?.firstName || 'U')[0].toUpperCase() === 'E'" class="text-blue-400">{{
              (user?.username || user?.firstName || 'U')[0].toUpperCase()
            }}</span>
            <span v-else>{{ (user?.username || user?.firstName || 'U')[0].toUpperCase() }}</span>
          </div>
          <span class="text-sm text-gray-700">
            {{ user?.username || user?.firstName || 'Account' }}
          </span>
          <ChevronDown :size="14" class="text-gray-400" />
        </button>

        <!-- Profile Dropdown Menu -->
        <ProfileMenu
          :user="user"
          :show-profile-menu="showProfileMenu"
          @close="showProfileMenu = false"
          @open-panel="(panel) => (activeMenu = panel)"
          @open-settings="
            () => {
              showSettingsDialog = true
              showProfileMenu = false
            }
          "
          @sign-out="signOut"
        />
      </div>
    </header>

    <!-- Main Layout -->
    <div class="pt-14 flex">
      <!-- Sidebar -->
      <aside class="w-16 bg-white border-r border-gray-100 fixed left-0 top-14 bottom-0 z-40">
        <nav class="flex flex-col items-center py-4 gap-1 h-full">
          <div class="flex flex-col items-center gap-1">
            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'projects'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Projects"
              @click="activeMenu = activeMenu === 'projects' ? null : 'projects'"
            >
              <FolderOpen :size="20" />
            </button>

            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'import'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Import"
              @click="activeMenu = activeMenu === 'import' ? null : 'import'"
            >
              <Download :size="20" />
            </button>

            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'data-aquisition'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Data aquisition"
              @click="activeMenu = activeMenu === 'data-aquisition' ? null : 'data-aquisition'"
            >
              <Database :size="20" />
            </button>

            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'ai' ? 'bg-blue-950 text-white' : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="AI Tools"
              @click="activeMenu = activeMenu === 'ai' ? null : 'ai'"
            >
              <Bot :size="20" />
            </button>

            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'filter'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Filter"
              @click="activeMenu = activeMenu === 'filter' ? null : 'filter'"
            >
              <Filter :size="20" />
            </button>

            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'stats'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Statistics"
              @click="activeMenu = activeMenu === 'stats' ? null : 'stats'"
            >
              <BarChart3 :size="20" />
            </button>

            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'model-analysis'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Model Analysis"
              @click="activeMenu = activeMenu === 'model-analysis' ? null : 'model-analysis'"
            >
              <Microscope :size="20" />
            </button>

            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'export'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Export"
              @click="activeMenu = activeMenu === 'export' ? null : 'export'"
            >
              <Upload :size="20" />
            </button>
          </div>

          <!-- Bottom Section -->
          <div class="mt-auto flex flex-col items-center gap-1">
            <button
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                activeMenu === 'project-settings'
                  ? 'bg-blue-950 text-white'
                  : 'text-gray-400 hover:text-blue-950 hover:bg-blue-50',
              ]"
              title="Project Settings"
              @click="activeMenu = activeMenu === 'project-settings' ? null : 'project-settings'"
            >
              <Settings2 :size="20" />
            </button>
          </div>
        </nav>
      </aside>

      <!-- Side Panel (conditionally shown) -->
      <aside
        v-if="activeMenu"
        class="w-72 bg-white border-r border-gray-100 fixed left-16 top-14 bottom-0 z-30 overflow-y-auto"
      >
        <div class="p-6">
          <ProjectsPanel
            v-if="activeMenu === 'projects'"
            :projects="projects"
            @refresh-projects="fetchProjects"
            @select-project="handleSelectProject"
          />
          <StatsPanel v-if="activeMenu === 'stats'" :project-id="selectedProject?.id" />
          <AIPanel
            v-if="activeMenu === 'ai'"
            :project-id="selectedProject?.id"
            :selected-images="selectedImagesFromGallery"
            @inference-results="handleInferenceResults"
          />
          <ImportPanel v-if="activeMenu === 'import'" :project-id="selectedProject?.id" />
          <DataAquisitionPanel v-if="activeMenu === 'data-aquisition'" @select-category="handleDataAquisitionSelect" />
          <ExportPanel v-if="activeMenu === 'export'" :project-id="selectedProject?.id" />
          <ModelAnalysisPanel v-if="activeMenu === 'model-analysis'" />
          <FilterPanel
            v-if="activeMenu === 'filter'"
            :project-id="selectedProject?.id"
            @apply-filters="handleApplyFilters"
          />
          <ProjectSettingsPanel v-if="activeMenu === 'project-settings'" :project-id="selectedProject?.id" />
        </div>
      </aside>

      <!-- Notification Center -->
      <div
        v-if="showNotificationCenter"
        class="fixed right-4 top-16 w-96 bg-white border border-gray-200 rounded-lg shadow-xl z-50 max-h-[80vh] flex flex-col"
      >
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Change Requests</h3>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ changeRequests.filter((r) => r.status === 'pending').length }}
              pending
            </p>
          </div>
          <button class="p-1 hover:bg-gray-100 rounded transition-colors" @click="showNotificationCenter = false">
            <X :size="20" class="text-gray-400" />
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto">
          <div v-if="changeRequests.length === 0" class="p-8 text-center">
            <Bell :size="48" class="mx-auto text-gray-300 mb-3" />
            <p class="text-gray-500 text-sm">No change requests</p>
            <p class="text-gray-400 text-xs mt-1">Requests will appear here</p>
          </div>

          <div v-else class="divide-y divide-gray-100">
            <div v-for="request in changeRequests" :key="request.id" class="p-4 hover:bg-gray-50 transition-colors">
              <div class="flex items-start gap-3">
                <!-- Image Thumbnail -->
                <div class="w-16 h-16 bg-gray-200 rounded flex-shrink-0 overflow-hidden">
                  <img
                    v-if="request.image?.location"
                    :src="request.image.location"
                    class="w-full h-full object-cover"
                    alt="Image"
                  />
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between">
                    <div>
                      <p class="text-sm font-semibold text-gray-900">Image #{{ request.imageId }}</p>
                      <p class="text-xs text-gray-500 mt-0.5">
                        {{ request.project }}
                      </p>
                      <p class="text-xs text-gray-400 mt-1">
                        {{ new Date(request.createdAt).toLocaleString() }}
                      </p>
                    </div>

                    <!-- Status Badge -->
                    <span class="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-semibold rounded"> Pending </span>
                  </div>

                  <!-- Actions -->
                  <div class="flex gap-2 mt-3">
                    <button
                      class="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors"
                      @click="openChangeRequest(request)"
                    >
                      <span>Open</span>
                    </button>

                    <button
                      class="flex items-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-medium rounded transition-colors"
                      title="Mark as completed"
                      @click="markAsCompleted(request.id)"
                    >
                      <CheckCircle :size="14" />
                    </button>

                    <button
                      class="flex items-center gap-1 px-3 py-1.5 bg-red-100 hover:bg-red-200 text-red-600 text-xs font-medium rounded transition-colors"
                      title="Remove"
                      @click="removeChangeRequest(request.id)"
                    >
                      <Trash2 :size="14" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings Dialog -->
      <SettingsDialog v-if="showSettingsDialog" :user="user" @close="showSettingsDialog = false" @sign-out="signOut" />

      <!-- Subscription Dialog -->
      <SubscriptionPanel :is-open="activeMenu === 'subscription'" @close="activeMenu = null" />

      <!-- Organisation Dialog -->
      <OrganisationPanel
        :is-open="activeMenu === 'organisation'"
        :members="organizationMembers"
        @close="activeMenu = null"
      />

      <!-- Main Content Area -->
      <main :class="['flex-1 p-6 transition-all duration-300', activeMenu ? 'ml-[352px]' : 'ml-16']">
        <!-- Image Gallery View -->
        <div class="w-full">
          <div class="mb-6">
            <div>
              <p class="text-sm text-gray-500 mt-1">
                <span v-if="selectedProject">{{ selectedProject.name }}</span>
              </p>
            </div>
          </div>
          <SatelliteStacPanel v-if="mainViewMode === 'satellite-stac'" :project-id="selectedProject?.id" />
          <HuggingFaceDatasetsPanel v-else-if="mainViewMode === 'hf-datasets'" />
          <ImageGallery
            v-else
            :key="imageGalleryKey"
            :project-id="selectedProject?.id"
            :filters="currentFilters"
            :inference-results="inferenceResults"
            @select-image="handleSelectImage"
            @modify-request="handleModifyRequest"
            @selection-change="handleSelectionChange"
          />
        </div>
      </main>
    </div>
  </div>
</template>
