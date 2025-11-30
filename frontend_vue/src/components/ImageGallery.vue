<script setup>
import { ref, onMounted, onUnmounted, defineEmits } from 'vue';
import { Check, Edit, Trash2, Pencil } from 'lucide-vue-next';

const emit = defineEmits(['select-image', 'modify-request']);

const images = ref([]);
const loading = ref(false);
const hasMore = ref(true);
const skip = ref(0);
const limit = 20;

const fetchImages = async () => {
  if (loading.value || !hasMore.value) return;
  
  loading.value = true;
  try {
    // Generate mock images with random shapes
    const shapes = ['square', 'portrait', 'landscape'];
    const dimensions = {
      square: { width: 400, height: 400 },
      portrait: { width: 300, height: 450 },
      landscape: { width: 450, height: 300 }
    };
    
    const newImages = [];
    for (let i = 0; i < limit; i++) {
      const imageId = skip.value + i + 1;
      const shape = shapes[Math.floor(Math.random() * shapes.length)];
      const { width, height } = dimensions[shape];
      
      newImages.push({
        id: imageId,
        location: `https://picsum.photos/${width}/${height}?random=${imageId}`,
        type: shape
      });
    }
    
    // Stop after 100 images
    if (skip.value >= 100) {
      hasMore.value = false;
    } else {
      images.value.push(...newImages);
      skip.value += limit;
    }
  } catch (error) {
    console.error('Error generating images:', error);
  } finally {
    loading.value = false;
  }
};

const handleScroll = () => {
  const scrollHeight = document.documentElement.scrollHeight;
  const scrollTop = document.documentElement.scrollTop;
  const clientHeight = document.documentElement.clientHeight;
  
  // Load more when user is 300px from bottom
  if (scrollTop + clientHeight >= scrollHeight - 300) {
    fetchImages();
  }
};

onMounted(() => {
  fetchImages();
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});

const handleImageClick = (image) => {
  emit('select-image', image);
};

const handleApprove = (image, event) => {
  event.stopPropagation();
  console.log('Approve image:', image.id);
  // TODO: Implement API call to approve image
  alert(`Image ${image.id} approved!`);
};

const handleModify = (image, event) => {
  event.stopPropagation();
  console.log('Modify image metadata:', image.id);
  emit('modify-request', image);
};

const handleAnnotate = (image, event) => {
  event.stopPropagation();
  emit('select-image', image);
};

const handleDelete = (image, event) => {
  event.stopPropagation();
  if (confirm(`Delete image ${image.id}?`)) {
    console.log('Delete image:', image.id);
    // TODO: Implement API call to delete image
    images.value = images.value.filter(img => img.id !== image.id);
  }
};
</script>

<template>
  <div class="image-gallery">
    <div class="image-grid">
      <div v-for="image in images" :key="image.id" class="image-item">
        <img 
          :src="image.location" 
          :alt="`Image ${image.id}`"
          loading="lazy"
        />
        
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
      <p>Loading more images...</p>
    </div>
    
    <div v-if="!hasMore && images.length > 0" class="end-message">
      <p>No more images to load</p>
    </div>
    
    <div v-if="images.length === 0 && !loading" class="empty-message">
      <p>No images found</p>
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
}

.image-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
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

.image-item img {
  width: auto;
  height: 100%;
  object-fit: cover;
  display: block;
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
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
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
  color: #7f8c8d;
}

/* Responsive design */
@media (max-width: 1200px) {
  .image-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 900px) {
  .image-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .image-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (max-width: 400px) {
  .image-grid {
    grid-template-columns: 1fr;
  }
}
</style>
