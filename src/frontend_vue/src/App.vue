<script setup>
import { ref, onMounted } from 'vue';
import LoginPage from './components/LoginPage.vue';
import Menubar from './components/Menubar.vue';
import Sidebar from './components/Sidebar.vue';
import NavPanel from './components/NavPanel.vue';
import ImageGallery from './components/ImageGallery.vue';
import ManualAnnotationPage from './pages/ManualAnnotationPage.vue';

const isAuthenticated = ref(false);
const currentUser = ref(null);
const activeMenu = ref(null);
const selectedImage = ref(null);
const modifyRequests = ref([]);

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
  localStorage.removeItem('token');
};

// Check for OAuth token in URL (from OAuth redirect)
const checkOAuthToken = async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  
  if (token) {
    // Store the token
    localStorage.setItem('token', token);
    
    // Fetch user info using the token
    try {
      const response = await fetch('http://localhost:8000/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        handleLogin({
          email: userData.email,
          username: userData.username,
          user_id: userData.id
        });
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
    
    // Clean URL by removing token parameter
    window.history.replaceState({}, document.title, window.location.pathname);
  }
};

// Check for existing session
const checkAuth = () => {
  const user = localStorage.getItem('user');
  if (user) {
    currentUser.value = JSON.parse(user);
    isAuthenticated.value = true;
  }
};

const handleSelectImage = (image) => {
  selectedImage.value = image;
};

const handleCloseAnnotation = () => {
  selectedImage.value = null;
};

const handleModifyRequest = (image) => {
  // Check if image is already in modify requests
  const exists = modifyRequests.value.find(req => req.id === image.id);
  if (!exists) {
    modifyRequests.value.push({
      ...image,
      requestedAt: new Date().toISOString()
    });
  }
};

const handleRemoveModifyRequest = (imageId) => {
  modifyRequests.value = modifyRequests.value.filter(req => req.id !== imageId);
};

const handleClearAllModifyRequests = () => {
  modifyRequests.value = [];
};

onMounted(async () => {
  // Check for OAuth token first (from OAuth redirect)
  await checkOAuthToken();
  // Then check for existing session
  checkAuth();
});
</script>

<template>
  <!-- Login Page -->
  <LoginPage v-if="!isAuthenticated" @login="handleLogin" />
  
  <!-- Main App -->
  <div v-else class="app-wrapper">
    <!-- Show annotation page when image is selected -->
    <ManualAnnotationPage 
      v-if="selectedImage" 
      :image="selectedImage" 
      @close="handleCloseAnnotation" 
    />
    
    <!-- Show gallery view when no image is selected -->
    <template v-else>
      <Menubar 
        :currentUser="currentUser" 
        :modifyRequests="modifyRequests"
        @logout="handleLogout" 
        @remove-modify-request="handleRemoveModifyRequest"
        @clear-modify-requests="handleClearAllModifyRequests"
      />
      
      <div class="app-layout">
        <Sidebar 
          :activeMenu="activeMenu" 
          @update:activeMenu="(menu) => activeMenu = activeMenu === menu ? null : menu"
        />
        
        <NavPanel v-if="activeMenu" :activeMenu="activeMenu" />
      
        <!-- Main Content -->
        <main class="main-content">
          <ImageGallery 
            @select-image="handleSelectImage" 
            @modify-request="handleModifyRequest"
          />
        </main>
      </div>
    </template>
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
</style>
