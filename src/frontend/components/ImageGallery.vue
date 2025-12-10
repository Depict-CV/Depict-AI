<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Check, Edit, Trash2, Pencil } from 'lucide-vue-next'

const emit = defineEmits(['selectImage', 'modifyRequest'])

const props = defineProps({
  projectId: {
    type: Number,
    default: null
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
    // TODO: Replace with actual API call when backend endpoint is ready
    // const response = await api.get(`/images?project_id=${props.projectId}&skip=${skip.value}&limit=${limit}`)
    // images.value.push(...response.images)
    // hasMore.value = response.has_more
    
    // Mock data for now
    const shapes = ['square', 'portrait', 'landscape']
    const dimensions = {
      square: { width: 400, height: 400 },
      portrait: { width: 300, height: 450 },
      landscape: { width: 450, height: 300 }
    }
    
    const newImages = []
    for (let i = 0; i < limit; i++) {
      const imageId = skip.value + i + 1
      const shape = shapes[Math.floor(Math.random() * shapes.length)]
      const { width, height } = dimensions[shape]
      
      newImages.push({
        id: imageId,
        location: `https://picsum.photos/${width}/${height}?random=${imageId}`,
        type: shape,
        status: ['pending', 'annotated', 'approved'][Math.floor(Math.random() * 3)]
      })
    }
    
    if (skip.value >= 1000) {
      hasMore.value = false
    } else {
      images.value.push(...newImages)
      skip.value += limit
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

// Watch for projectId changes
watch(() => props.projectId, (newProjectId) => {
  if (newProjectId) {
    // Reset state when project changes
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
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const handleApprove = async (image, event) => {
  event.stopPropagation()
  try {
    // TODO: Implement API call
    // await api.post(`/images/${image.id}/approve`)
    console.log('Approve image:', image.id)
    alert(`Image ${image.id} approved!`)
  } catch (error) {
    console.error('Failed to approve image:', error)
  }
}

const handleModify = (image, event) => {
  event.stopPropagation()
  emit('modifyRequest', image)
}

const handleAnnotate = (image, event) => {
  event.stopPropagation()
  // Navigate to annotation page
  navigateTo(`/annotate/${image.id}`)
}

const handleDelete = async (image, event) => {
  event.stopPropagation()
  if (confirm(`Delete image ${image.id}?`)) {
    try {
      // TODO: Implement API call
      // await api.delete(`/images/${image.id}`)
      images.value = images.value.filter(img => img.id !== image.id)
      console.log('Delete image:', image.id)
    } catch (error) {
      console.error('Failed to delete image:', error)
    }
  }
}
</script>

<template>
  <div class="w-full">
    <div class="flex flex-wrap gap-1.5 mb-5">
      <div 
        v-for="image in images" 
        :key="image.id" 
        class="relative overflow-hidden bg-gray-100 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-200 h-[250px] group"
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
            'bg-amber-400/90 text-amber-900': image.status === 'pending',
            'bg-blue-500/90 text-blue-950': image.status === 'annotated',
            'bg-green-500/90 text-green-950': image.status === 'approved'
          }"
        >
          {{ image.status }}
        </div>
        
        <!-- Action Buttons Overlay -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex gap-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10">
          <button 
            class="w-11 h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-green-600/95 hover:bg-green-600 text-white"
            @click="handleApprove(image, $event)"
            title="Approve image"
          >
            <Check :size="20" />
          </button>
          <button 
            class="w-11 h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-purple-600/95 hover:bg-purple-600 text-white"
            @click="handleAnnotate(image, $event)"
            title="Annotate image manually"
          >
            <Pencil :size="20" />
          </button>
          <button 
            class="w-11 h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-blue-500/95 hover:bg-blue-500 text-white"
            @click="handleModify(image, $event)"
            title="Request annotation change"
          >
            <Edit :size="20" />
          </button>
          <button 
            class="w-11 h-11 border-0 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 shadow-md backdrop-blur-sm hover:scale-110 hover:shadow-lg bg-red-500/95 hover:bg-red-500 text-white"
            @click="handleDelete(image, $event)"
            title="Delete image"
          >
            <Trash2 :size="20" />
          </button>
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
      <p class="text-gray-500">No images found</p>
    </div>
  </div>
</template>

<style scoped>
/* Responsive design - Tailwind breakpoints: sm:640px md:768px lg:1024px xl:1280px */
@media (max-width: 1200px) {
  .flex-wrap {
    gap: 0.5rem;
  }
  
  .h-\[250px\] {
    height: 220px;
  }
}

@media (max-width: 900px) {
  .flex-wrap {
    gap: 0.625rem;
  }
  
  .h-\[250px\] {
    height: 200px;
  }
}

@media (max-width: 600px) {
  .flex-wrap {
    gap: 0.75rem;
  }
  
  .h-\[250px\] {
    height: 180px;
  }
  
  .w-11 {
    width: 36px;
    height: 36px;
  }
}
</style>
