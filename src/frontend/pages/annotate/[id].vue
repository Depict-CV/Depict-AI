<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import AnnotationHistory from '@/components/annot/AnnotationHistory.vue'
import AIAnnotationButton from '@/components/annot/AIAnnotationButton.vue'
import AnnotationEditor from '@/components/annot/AnnotationEditor.vue'

const route = useRoute()
const router = useRouter()
const api = useApi()

const image = ref(null)
const projectId = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const imageId = route.params.id

    // Try to get projectId from sessionStorage first, otherwise from API
    const storedProjectId = sessionStorage.getItem('currentProjectId')
    if (storedProjectId) {
      projectId.value = parseInt(storedProjectId)
    }

    // Fetch the actual image data from the API
    const response = await api.post('/data/batch', {
      data_ids: [imageId],
    })

    if (response && response.length > 0) {
      const imageData = response[0]

      // Update projectId from API response if not already set
      if (!projectId.value && imageData.project_id) {
        projectId.value = imageData.project_id
      }

      let imageUrl = imageData.location

      // Handle different image location types
      if (imageData.location.startsWith('minio://')) {
        // MinIO URL - serve through backend MinIO endpoint
        const minioPath = imageData.location.replace('minio://', '')
        imageUrl = `http://localhost:8000/images/minio/${imageData.project_id}?object_path=${encodeURIComponent(minioPath)}`
      } else if (!imageData.location.startsWith('http://') && !imageData.location.startsWith('https://')) {
        // Local file path - serve through backend
        const encodedPath = encodeURIComponent(imageData.location)
        imageUrl = `http://localhost:8000/images/serve?path=${encodedPath}`
      }

      image.value = {
        id: imageData.id,
        location: imageUrl,
        type: imageData.type || 'image',
      }
    }
  } catch (error) {
    console.error('Failed to fetch image:', error)
  } finally {
    loading.value = false
  }
})

const goBack = () => {
  router.back()
}

const handleAIAnnotation = (annotation) => {
  console.log('AI annotation generated:', annotation)
  // Refresh history component - you may want to emit an event or refetch
}

const handleAnnotationSaved = (annotation) => {
  console.log('Annotation saved:', annotation)
  // Refresh history after saving
}

const handleAnnotationAccepted = (result) => {
  console.log('Annotation accepted:', result)
}

const handleAnnotationRejected = (result) => {
  console.log('Annotation rejected:', result)
}
</script>

<template>
  <div class="w-full h-screen flex">
    <!-- Loading state -->
    <div v-if="loading" class="w-full flex items-center justify-center bg-white">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Loading image...</p>
      </div>
    </div>

    <!-- Main content -->
    <template v-else>
      <!-- Left Sidebar -->
      <div class="w-64 bg-white flex flex-col shadow-lg border-r border-gray-200 overflow-y-auto">
        <AnnotationHistory :imageId="route.params.id" :projectId="projectId" />
        <AIAnnotationButton :imageId="route.params.id" @generateAnnotation="handleAIAnnotation" />
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 flex flex-col">
        <!-- Header -->
        <div class="bg-white px-4 py-3 flex items-center gap-3 border-b border-gray-200 shadow-sm">
          <button @click="goBack" class="text-gray-700 hover:text-gray-900 transition" title="Go back">
            <ArrowLeft size="24" />
          </button>
          <div>
            <p class="text-sm text-gray-600">Image ID: {{ route.params.id }}</p>
          </div>
        </div>

        <!-- Annotation Editor -->
        <AnnotationEditor
          v-if="image"
          :imageId="route.params.id"
          :imageSrc="image.location"
          @save="handleAnnotationSaved"
          @accept="handleAnnotationAccepted"
          @reject="handleAnnotationRejected"
        />
      </div>
    </template>
  </div>
</template>
