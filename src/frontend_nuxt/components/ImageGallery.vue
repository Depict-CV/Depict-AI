<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
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
  if (loading.value || !hasMore.value) return
  
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
  fetchImages()
  window.addEventListener('scroll', handleScroll)
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
  <div class="image-gallery">
    <div class="image-grid">
      <div v-for="image in images" :key="image.id" class="image-item">
        <img 
          :src="image.location" 
          :alt="`Image ${image.id}`"
          loading="lazy"
          class="image-img"
        />
        
        <!-- Status Badge -->
        <div class="status-badge" :class="`status-${image.status}`">
          {{ image.status }}
        </div>
        
        <!-- Action Buttons Overlay -->
        <div class="image-actions">
          <button 
            class="action-btn approve-btn" 
            @click="handleApprove(image, $event)"
            title="Approve image"
          >
            <Check :size="20" />
          </button>
          <button 
            class="action-btn annotate-btn" 
            @click="handleAnnotate(image, $event)"
            title="Annotate image manually"
          >
            <Pencil :size="20" />
          </button>
          <button 
            class="action-btn modify-btn" 
            @click="handleModify(image, $event)"
            title="Edit image metadata"
          >
            <Edit :size="20" />
          </button>
          <button 
            class="action-btn delete-btn" 
            @click="handleDelete(image, $event)"
            title="Delete image"
          >
            <Trash2 :size="20" />
          </button>
        </div>
        
        <div class="image-info">
          <span class="image-id">ID: {{ image.id }}</span>
          <span class="image-type">{{ image.type }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p class="text-gray-600">Loading more images...</p>
    </div>
    
    <div v-if="!hasMore && images.length > 0" class="end-message">
      <p class="text-gray-500">No more images to load</p>
    </div>
    
    <div v-if="images.length === 0 && !loading" class="empty-message">
      <p class="text-gray-500">No images found</p>
    </div>
  </div>
</template>

<style scoped>
.image-gallery {
  width: 100%;
}

.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 20px;
}

.image-item {
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  height: 250px;
  border-radius: 8px;
  background: #f3f4f6;
}

.image-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.image-img {
  width: auto;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Status Badge */
.status-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  z-index: 5;
  backdrop-filter: blur(4px);
}

.status-pending {
  background: rgba(251, 191, 36, 0.9);
  color: #78350f;
}

.status-annotated {
  background: rgba(59, 130, 246, 0.9);
  color: #1e3a8a;
}

.status-approved {
  background: rgba(34, 197, 94, 0.9);
  color: #14532d;
}

/* Action Buttons Overlay */
.image-actions {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 10;
}

.image-item:hover .image-actions {
  opacity: 1;
}

.action-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(4px);
}

.action-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.approve-btn {
  background: rgba(39, 174, 96, 0.95);
  color: white;
}

.approve-btn:hover {
  background: #27ae60;
}

.annotate-btn {
  background: rgba(155, 89, 182, 0.95);
  color: white;
}

.annotate-btn:hover {
  background: #9b59b6;
}

.modify-btn {
  background: rgba(52, 152, 219, 0.95);
  color: white;
}

.modify-btn:hover {
  background: #3498db;
}

.delete-btn {
  background: rgba(231, 76, 60, 0.95);
  color: white;
}

.delete-btn:hover {
  background: #e74c3c;
}

.image-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  padding: 8px;
  color: white;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 5;
}

.image-item:hover .image-info {
  opacity: 1;
}

.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.end-message,
.empty-message {
  text-align: center;
  padding: 40px;
}

/* Responsive design */
@media (max-width: 1200px) {
  .image-grid {
    gap: 8px;
  }
  
  .image-item {
    height: 220px;
  }
}

@media (max-width: 900px) {
  .image-grid {
    gap: 10px;
  }
  
  .image-item {
    height: 200px;
  }
}

@media (max-width: 600px) {
  .image-grid {
    gap: 12px;
  }
  
  .image-item {
    height: 180px;
  }
  
  .action-btn {
    width: 36px;
    height: 36px;
  }
}
</style>
