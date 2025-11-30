<script setup>
import { Image, Upload, FolderOpen, Settings } from 'lucide-vue-next';

defineProps({
  activeMenu: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['update:activeMenu']);

const toggleMenu = (menu) => {
  emit('update:activeMenu', menu);
};
</script>

<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <div class="nav-main">
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'gallery' }"
          @click="toggleMenu('gallery')"
          title="Gallery"
        >
          <Image :size="24" />
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'upload' }"
          @click="toggleMenu('upload')"
          title="Upload"
        >
          <Upload :size="24" />
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'projects' }"
          @click="toggleMenu('projects')"
          title="Projects"
        >
          <FolderOpen :size="24" />
        </button>
      </div>
      
      <div class="nav-bottom">
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'settings' }"
          @click="toggleMenu('settings')"
          title="Settings"
        >
          <Settings :size="24" />
        </button>
      </div>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 40px;
  background: #ecebee;
  color: rgba(43, 33, 33, 0);
  padding: 5px;
  border: 1px solid #e0e0e0;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.nav-main {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-bottom {
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
</style>
