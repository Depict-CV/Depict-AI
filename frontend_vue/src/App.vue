<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import LoginPage from './components/LoginPage.vue';
import Menubar from './components/Menubar.vue';
import Sidebar from './components/Sidebar.vue';
import NavPanel from './components/NavPanel.vue';

const isAuthenticated = ref(false);
const currentUser = ref(null);
const images = ref([]);
const loading = ref(false);
const hasMore = ref(true);
const skip = ref(0);
const limit = 20;
const activeMenu = ref(null);

const handleLogin = (userData) => {
  currentUser.value = userData;
  isAuthenticated.value = true;
  // Store in localStorage for persistence
  localStorage.setItem('user', JSON.stringify(userData));
};

const handleLogout = () => {
  currentUser.value = null;
  isAuthenticated.value = false;
  localStorage.removeItem('user');
};

// Check for existing session
const checkAuth = () => {
  const user = localStorage.getItem('user');
  if (user) {
    currentUser.value = JSON.parse(user);
    isAuthenticated.value = true;
  }
};

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
  checkAuth();
  if (isAuthenticated.value) {
    fetchImages();
    window.addEventListener('scroll', handleScroll);
  }
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<template>
  <!-- Login Page -->
  <LoginPage v-if="!isAuthenticated" @login="handleLogin" />
  
  <!-- Main App -->
  <div v-else class="app-wrapper">
    <Menubar :currentUser="currentUser" @logout="handleLogout" />
    
    <div class="app-layout">
      <Sidebar 
        :activeMenu="activeMenu" 
        @update:activeMenu="(menu) => activeMenu = activeMenu === menu ? null : menu"
      />
      
      <NavPanel v-if="activeMenu" :activeMenu="activeMenu" />
    
    <!-- Main Content -->
    <main class="main-content">
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
  </div>
</template>

<style scoped>
.app-wrapper {
  min-height: 100vh;
}

.app-layout {
  display: flex;
  min-height: calc(100vh - 60px);
  margin-top: 60px;
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
