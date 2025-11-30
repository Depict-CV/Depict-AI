<script setup>
import { Upload, ChevronLeft, ChevronRight } from 'lucide-vue-next';

defineProps({
  activeMenu: {
    type: String,
    required: true
  }
});
</script>

<template>
  <aside class="nav-panel">
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
</template>

<style scoped>
.nav-panel {
  position: fixed;
  left: 60px;
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
</style>
