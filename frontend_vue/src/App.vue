<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const images = ref([]);
const loading = ref(false);
const hasMore = ref(true);
const skip = ref(0);
const limit = 20;
const activeMenu = ref('gallery');

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
</script>

<template>
  <div class="app-layout">
    <!-- Left Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>Depict AI</h2>
      </div>
      
      <nav class="sidebar-nav">
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'gallery' }"
          @click="activeMenu = 'gallery'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
          <span>Gallery</span>
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'upload' }"
          @click="activeMenu = 'upload'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <span>Upload</span>
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'projects' }"
          @click="activeMenu = 'projects'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <span>Projects</span>
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'settings' }"
          @click="activeMenu = 'settings'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"/>
          </svg>
          <span>Settings</span>
        </button>
      </nav>
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
      <h1>Image Gallery</h1>
      
      <div class="image-grid">
      <div v-for="image in images" :key="image.id" class="image-item">
        <img 
          :src="image.location" 
          :alt="`Image ${image.id}`"
          loading="lazy"
        />
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
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: #ecebee;
  color: rgba(43, 33, 33, 0);
  padding: 20px;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-header h2 {
  margin: 0 0 30px 0;
  font-size: 24px;
  color: #b420207f;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #000000;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
  text-align: left;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background: #3498db;
  color: white;
}

.nav-item svg {
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  margin-left: 240px;
  padding: 20px;
  max-width: calc(100% - 240px);
}

h1 {
  text-align: center;
  color: #243125;
  margin-bottom: 30px;
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
