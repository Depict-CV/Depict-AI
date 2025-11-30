<script setup>
import { ref, onMounted } from 'vue';
import LoginPage from './components/LoginPage.vue';
import Menubar from './components/Menubar.vue';
import Sidebar from './components/Sidebar.vue';
import NavPanel from './components/NavPanel.vue';
import ImageGallery from './components/ImageGallery.vue';

const isAuthenticated = ref(false);
const currentUser = ref(null);
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

onMounted(() => {
  checkAuth();
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
      <ImageGallery />
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
</style>
