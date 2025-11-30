<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { Image, Upload, FolderOpen, Settings, ChevronLeft, ChevronRight } from 'lucide-vue-next';

const images = ref([]);
const loading = ref(false);
const hasMore = ref(true);
const skip = ref(0);
const limit = 20;
const activeMenu = ref(null);

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
      <nav class="sidebar-nav">
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'gallery' }"
          @click="activeMenu = activeMenu === 'gallery' ? null : 'gallery'"
          title="Gallery"
        >
          <Image :size="24" />
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'upload' }"
          @click="activeMenu = activeMenu === 'upload' ? null : 'upload'"
          title="Upload"
        >
          <Upload :size="24" />
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'projects' }"
          @click="activeMenu = activeMenu === 'projects' ? null : 'projects'"
          title="Projects"
        >
          <FolderOpen :size="24" />
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'settings' }"
          @click="activeMenu = activeMenu === 'settings' ? null : 'settings'"
          title="Settings"
        >
          <Settings :size="24" />
        </button>
      </nav>
    </aside>

    <!-- Extended Navigation Panel -->
    <aside v-if="activeMenu" class="nav-panel">
      <div class="nav-panel-header">
        <h3>{{ activeMenu.charAt(0).toUpperCase() + activeMenu.slice(1) }}</h3>
      </div>
      
      <div class="nav-panel-content">
        <!-- Gallery Content -->
        <div v-if="activeMenu === 'gallery'">
          <p class="text-gray-600">Gallery navigation</p>
        </div>
        
        <!-- Upload Content -->
        <div v-if="activeMenu === 'upload'" class="upload-panel">
          <button class="panel-button primary">
            <Upload :size="20" />
            Upload
          </button>
          <div class="nav-buttons">
            <button class="panel-button">
              <ChevronLeft :size="20" />
              Prev
            </button>
            <button class="panel-button">
              <ChevronRight :size="20" />
              Next
            </button>
          </div>
        </div>
        
        <!-- Projects Content -->
        <div v-if="activeMenu === 'projects'">
          <p class="text-gray-600">Projects navigation</p>
        </div>
        
        <!-- Settings Content -->
        <div v-if="activeMenu === 'settings'">
          <p class="text-gray-600">Settings navigation</p>
        </div>
      </div>
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
      <div class="sidebar-header">
        <h2>Depict AI</h2>
      </div>
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
  width: 40px;
  background: #ecebee;
  color: rgba(43, 33, 33, 0);
  padding: 3px;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  margin-bottom: 20px;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  position: relative;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #000000;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
  width: 100%;
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

.nav-panel {
  position: fixed;
  left: 80px;
  top: 0;
  width: 240px;
  height: 100vh;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  padding: 20px;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.nav-panel-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.nav-panel-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
  text-transform: capitalize;
}

.nav-panel-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.upload-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.nav-buttons {
  display: flex;
  gap: 10px;
}

.panel-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: white;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  color: #2c3e50;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
  flex: 1;
}

.panel-button:hover {
  background: #f0f0f0;
  border-color: #3498db;
}

.panel-button.primary {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.panel-button.primary:hover {
  background: #2980b9;
  border-color: #2980b9;
}

.main-content {
  flex: 1;
  margin-left: 80px;
  padding: 20px;
  transition: margin-left 0.3s ease;
}

.app-layout:has(.nav-panel) .main-content {
  margin-left: calc(80px + 240px);
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
