<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Check, Edit, Trash2, Pencil } from 'lucide-vue-next'

const emit = defineEmits(['selectImage', 'modifyRequest'])

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  },
  filters: {
    type: Object,
    default: () => ({})
  }
})

const api = useApi()
const images = ref([])
const loading = ref(false)
const hasMore = ref(true)
const skip = ref(0)
const limit = 20

const fetchImages = async () => {
  if (loading.value || !hasMore.value || !props.projectId) return
  
  loading.value = true
  try {
    // First, fetch annotations for the project
    const annotations = await api.get('/annotations/', {
      project_id: props.projectId,
      skip: skip.value,
      limit: limit
    })
    
    console.log('Annotations response:', annotations)
    console.log('Number of annotations fetched:', annotations.length)
    
    if (annotations.length === 0) {
      hasMore.value = false
      loading.value = false
      return
    }
    
    // Apply status filter if provided
    let filteredAnnotations = annotations
    if (props.filters?.status && props.filters.status.length > 0) {
      filteredAnnotations = annotations.filter(ann => 
        props.filters.status.includes(ann.status)
      )
      console.log('Filtered annotations by status:', filteredAnnotations.length)
    }
    
    if (filteredAnnotations.length === 0) {
      hasMore.value = false
      loading.value = false
      return
    }
    
    // Get unique data IDs from annotations
    const dataIds = [...new Set(filteredAnnotations.map(ann => ann.data_id))]
    console.log('Unique data IDs:', dataIds)
    
    // Fetch the corresponding data (images) for these annotations
    const imagesResponse = await api.post('/data/batch', {
      data_ids: dataIds
    })
    
    console.log('Images response:', imagesResponse)
    
    // Create a map of data_id to status (use the first annotation's status)
    const annotationsMap = {}
    annotations.forEach(ann => {
      if (!annotationsMap[ann.data_id]) {
        annotationsMap[ann.data_id] = ann.status
      }
    })
    
    // Transform database response to match expected format
    const newImages = imagesResponse.map(item => {
      console.log('Item location:', item.location)
      
      // Check if location is a URL or file path
      let imageUrl = item.location
      if (!item.location.startsWith('http://') && !item.location.startsWith('https://')) {
        // Local file path - serve through backend
        const encodedPath = encodeURIComponent(item.location)
        imageUrl = `http://localhost:8000/images/serve?path=${encodedPath}`
        console.log('Converted to backend URL:', imageUrl)
      }
      
      return {
        id: item.id,
        location: imageUrl,
        type: item.type,
        status: annotationsMap[item.id] || 'to review'
      }
    })
    
    console.log('Transformed images:', newImages)
    
    images.value.push(...newImages)
    skip.value += annotations.length
    
    // If we got fewer annotations than limit, we've reached the end
    if (annotations.length < limit) {
      hasMore.value = false
    }
  } catch (error) {
    console.error('Error fetching images:', error)
  } finally {
    loading.value = false
  }
}

const handleScroll = () => {
  const scrollHeight = document.documentElement.scrollHeight
  const scrollTop = document.documentElement.scrollTop
  const clientHeight = document.documentElement.clientHeight
  
  if (scrollTop + clientHeight >= scrollHeight - 300) {
    fetchImages()
  }
}

onMounted(() => {
  if (props.projectId) {
    fetchImages()
  }
  window.addEventListener('scroll', handleScroll)
})

// Watch for projectId or filters changes
watch(() => [props.projectId, props.filters], ([newProjectId, newFilters]) => {
  if (newProjectId) {
    // Reset state when project or filters change
    images.value = []
    skip.value = 0
    hasMore.value = true
    fetchImages()
  } else {
    // Clear images when no project selected
    images.value = []
    skip.value = 0
    hasMore.value = true
  }
}, { deep: true })

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const handleApprove = async (image, event) => {
  event.stopPropagation()
  try {
    // Call the approve endpoint
    const response = await api.post(`/annotations/approve/${image.id}`)
    console.log('Approve response:', response)
    
    // Update the image status in the UI
    const imageIndex = images.value.findIndex(img => img.id === image.id)
    if (imageIndex !== -1) {
      images.value[imageIndex].status = 'certified'
    }
    
  } catch (error) {
    console.error('Failed to approve image:', error)
    alert(`Failed to approve image: ${error?.data?.detail || error?.message || 'Unknown error'}`)
  }
}

const handleModify = async (image, event) => {
  event.stopPropagation()
  try {
    // Call the request-review endpoint (similar to approve but for requesting review)
    const response = await api.post(`/annotations/request-review/${image.id}`)
    console.log('Request review response:', response)
    
    // Update the image status in the UI
    const imageIndex = images.value.findIndex(img => img.id === image.id)
    if (imageIndex !== -1) {
      images.value[imageIndex].status = 'to review'
    }
    
    emit('modifyRequest', image)
  } catch (error) {
    console.error('Failed to request review:', error)
    alert(`Failed to request annotation review: ${error?.data?.detail || error?.message || 'Unknown error'}`)
  }
}

const handleAnnotate = (image, event) => {
  event.stopPropagation()
  // Store image data in sessionStorage for the annotation page
  sessionStorage.setItem('currentImage', JSON.stringify(image))
  // Navigate to annotation page
  navigateTo(`/annotate/${image.id}`)
}

const handleDelete = async (image, event) => {
  event.stopPropagation()
  try {
    // Call the reject endpoint (similar to approve but for rejection)
    const response = await api.post(`/annotations/reject/${image.id}`)
    console.log('Reject response:', response)
    
    // Update the image status in the UI
    const imageIndex = images.value.findIndex(img => img.id === image.id)
    if (imageIndex !== -1) {
      images.value[imageIndex].status = 'rejected'
    }
    
  } catch (error) {
    console.error('Failed to reject image:', error)
    alert(`Failed to reject image: ${error?.data?.detail || error?.message || 'Unknown error'}`)
  }
}
</script>

<template>
  <div class="w-full">
    <div class="flex flex-wrap gap-1.5 sm:gap-3 md:gap-2.5 lg:gap-1.5 mb-5">
      <div 
        v-for="image in images" 
        :key="image.id" 
        class="relative overflow-hidden bg-gray-100 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-200 h-[180px] sm:h-[250px] md:h-[200px] lg:h-[220px] xl:h-[250px] group"
      >
        <img 
          :src="image.location" 
          :alt="`Image ${image.id}`"
          loading="lazy"
          class="w-auto h-full object-cover block"
        />
        
        <!-- Status Badge -->
        <div 
          class="absolute top-2 right-2 px-2 py-1 rounded-xl text-xs font-semibold uppercase z-[5] backdrop-blur-sm"
          :class="{
            'bg-blue-500/90 text-blue-950': image.status === 'to review',
            'bg-purple-500/90 text-purple-950': image.status === 'human annotation',
            'bg-amber-400/90 text-amber-900': image.status === 'ml annotation',
            'bg-green-500/90 text-green-950': image.status === 'certified',
            'bg-red-500/90 text-red-950': image.status === 'rejected'
          }"
        >
          {{ image.status }}
        </div>
        
        <!-- Action Buttons Overlay -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10">
          <div class="flex gap-2">
            <button 
              class="w-9 h-9 sm:w-11 sm:h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-green-600/95 hover:bg-green-600 text-white"
              @click="handleApprove(image, $event)"
              title="certify annotation"
            >
              <Check :size="20" />
            </button>
            <button 
              class="w-9 h-9 sm:w-11 sm:h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-purple-600/95 hover:bg-purple-600 text-white"
              @click="handleAnnotate(image, $event)"
              title="Annotate manually"
            >
              <Pencil :size="20" />
            </button>
          </div>
          <div class="flex gap-2">
            <button 
              class="w-9 h-9 sm:w-11 sm:h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-blue-500/95 hover:bg-blue-500 text-white"
              @click="handleModify(image, $event)"
              title="Request annotation change"
            >
              <Edit :size="20" />
            </button>
            <button 
              class="w-9 h-9 sm:w-11 sm:h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-red-500/95 hover:bg-red-500 text-white"
              @click="handleDelete(image, $event)"
              title="Reject annotation"
            >
              <Trash2 :size="20" />
            </button>
          </div>
        </div>
        
        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent px-2 py-2 text-white text-xs flex justify-between opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-[5]">
          <span>ID: {{ image.id }}</span>
          <span>{{ image.type }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="text-center py-10">
      <div class="border-4 border-gray-200 border-t-blue-500 rounded-full w-10 h-10 animate-spin mx-auto mb-2.5"></div>
      <p class="text-gray-600">Loading more images...</p>
    </div>
    
    <div v-if="!hasMore && images.length > 0" class="text-center py-10">
      <p class="text-gray-500">No more images to load</p>
    </div>
    
    <div v-if="!projectId" class="text-center py-20">
      <p class="text-gray-500 text-lg">Please select a project first</p>
    </div>
    
    <div v-else-if="images.length === 0 && !loading" class="text-center py-10">
      <p class="text-gray-500 text-lg">No annotated images found in this project</p>
      <p class="text-gray-400 text-sm mt-2">Create annotations using the AI Tools or annotate images manually</p>
    </div>
  </div>
</template>
