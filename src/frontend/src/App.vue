<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAuth, useUser } from '@clerk/vue';
import LoginPage from './components/LoginPage.vue';
import Menubar from './components/Menubar.vue';
import Sidebar from './components/Sidebar.vue';
import NavPanel from './components/NavPanel.vue';
import ImageGallery from './components/ImageGallery.vue';
import ManualAnnotationPage from './pages/ManualAnnotationPage.vue';

const { isSignedIn, signOut } = useAuth();
const { user } = useUser();

const isAuthenticated = ref(false);
const currentUser = ref(null);
const activeMenu = ref(null);
const selectedImage = ref(null);
const modifyRequests = ref([]);

// Watch Clerk auth state changes
watch([isSignedIn, user], ([signedIn, clerkUser]) => {
  if (signedIn && clerkUser) {
    isAuthenticated.value = true;
    currentUser.value = {
      email: clerkUser.primaryEmailAddress?.emailAddress || '',
      username: clerkUser.username || clerkUser.firstName || 'User',
      user_id: clerkUser.id,
    };
  } else {
    isAuthenticated.value = false;
    currentUser.value = null;
  }
}, { immediate: true });

const handleLogin = () => {
  // Clerk handles login - just update local state
  isAuthenticated.value = true;
};

const handleLogout = async () => {
  await signOut();
  currentUser.value = null;
  isAuthenticated.value = false;
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
</script>

<template>
  <!-- Login Page -->
  <LoginPage v-if="!isAuthenticated" @login="handleLogin" />
  
  <!-- Main App -->
  <div v-else class="min-h-screen bg-gray-50">
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
      
      <div class="flex min-h-[calc(100vh-60px)] mt-[60px]">
        <Sidebar 
          :activeMenu="activeMenu" 
          @update:activeMenu="(menu) => activeMenu = activeMenu === menu ? null : menu"
        />
        
        <NavPanel v-if="activeMenu" :activeMenu="activeMenu" />
      
        <!-- Main Content -->
        <main 
          class="flex-1 p-5 transition-[margin-left] duration-300 ease-in-out"
          :class="activeMenu ? 'ml-[320px]' : 'ml-20'"
        >
          <ImageGallery 
            @select-image="handleSelectImage" 
            @modify-request="handleModifyRequest"
          />
        </main>
      </div>
    </template>
  </div>
</template>
