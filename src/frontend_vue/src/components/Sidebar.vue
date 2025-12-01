<script setup>
import { ref } from 'vue';
import { ArrowRightLeft, FolderOpen, Settings, Filter, BarChart, Sparkles } from 'lucide-vue-next';
import SettingsModal from './panels/SettingsModal.vue';

defineProps({
  activeMenu: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['update:activeMenu']);

const showSettingsModal = ref(false);

const toggleMenu = (menu) => {
  if (menu === 'settings') {
    showSettingsModal.value = true;
  } else {
    emit('update:activeMenu', menu);
  }
};

const closeSettingsModal = () => {
  showSettingsModal.value = false;
};

const handleSaveSettings = (settingsData) => {
  console.log('Saving settings:', settingsData);
  // TODO: Implement API call to save settings
  alert('Settings saved successfully!');
  closeSettingsModal();
};
</script>

<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <div class="nav-main">
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'projects' }"
          @click="toggleMenu('projects')"
          title="Projects"
        >
          <FolderOpen :size="24" />
        </button>

        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'import_export' }"
          @click="toggleMenu('import_export')"
          title="Import / Export"
        >
          <ArrowRightLeft :size="24" />
        </button>

        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'ai-annotation' }"
          @click="toggleMenu('ai-annotation')"
          title="AI Annotation"
        >
          <Sparkles :size="24" />
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'filter' }"
          @click="toggleMenu('filter')"
          title="Filter Images"
        >
          <Filter :size="24" />
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'statistics' }"
          @click="toggleMenu('statistics')"
          title="Statistics"
        >
          <BarChart :size="24" />
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
  
  <!-- Settings Modal -->
  <SettingsModal 
    :show="showSettingsModal" 
    @close="closeSettingsModal"
    @save="handleSaveSettings"
  />
</template>

<style scoped>
.sidebar {
  width: 40px;
  background: #ecebee;
  color: rgba(43, 33, 33, 0);
  padding: 5px;
  border: 1px solid #d0d0d0;
  position: fixed;
  height: 90vh;
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
  background: #2c3e5057;
  color: white;
}

.nav-item svg {
  flex-shrink: 0;
}
</style>
