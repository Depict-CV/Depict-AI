<script setup>
import { ref } from 'vue';
import { Image, Upload, FolderOpen, Settings, X, Moon, Sun, Bell, Lock, Palette, Database, Globe, Filter, BarChart, Sparkles } from 'lucide-vue-next';

defineProps({
  activeMenu: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['update:activeMenu']);

const showSettingsModal = ref(false);
const activeSettingsTab = ref('general');

// Settings state
const settings = ref({
  general: {
    theme: 'light',
    language: 'en',
    autoSave: true,
    confirmDelete: true
  },
  notifications: {
    emailNotifications: true,
    pushNotifications: false,
    annotationAlerts: true,
    weeklyReport: false
  },
  appearance: {
    compactMode: false,
    showImageInfo: true,
    gridSize: 'medium',
    animationsEnabled: true
  },
  privacy: {
    shareAnalytics: false,
    publicProfile: false,
    showEmail: true
  },
  storage: {
    cacheImages: true,
    maxCacheSize: '500',
    autoCleanup: true
  }
});

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

const saveSettings = () => {
  console.log('Saving settings:', settings.value);
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
        
        <button 
          class="nav-item" 
          :class="{ active: activeMenu === 'ai-annotation' }"
          @click="toggleMenu('ai-annotation')"
          title="AI Annotation"
        >
          <Sparkles :size="24" />
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
  <div v-if="showSettingsModal" class="settings-overlay" @click="closeSettingsModal">
    <div class="settings-modal" @click.stop>
      <div class="settings-header">
        <div class="settings-title">
          <Settings :size="24" />
          <h2>Settings</h2>
        </div>
        <button class="settings-close" @click="closeSettingsModal">
          <X :size="20" />
        </button>
      </div>
      
      <div class="settings-content">
        <div class="settings-tabs">
          <button 
            :class="['settings-tab', { active: activeSettingsTab === 'general' }]"
            @click="activeSettingsTab = 'general'"
          >
            <Globe :size="18" />
            <span>General</span>
          </button>
          <button 
            :class="['settings-tab', { active: activeSettingsTab === 'notifications' }]"
            @click="activeSettingsTab = 'notifications'"
          >
            <Bell :size="18" />
            <span>Notifications</span>
          </button>
          <button 
            :class="['settings-tab', { active: activeSettingsTab === 'appearance' }]"
            @click="activeSettingsTab = 'appearance'"
          >
            <Palette :size="18" />
            <span>Appearance</span>
          </button>
          <button 
            :class="['settings-tab', { active: activeSettingsTab === 'privacy' }]"
            @click="activeSettingsTab = 'privacy'"
          >
            <Lock :size="18" />
            <span>Privacy</span>
          </button>
          <button 
            :class="['settings-tab', { active: activeSettingsTab === 'storage' }]"
            @click="activeSettingsTab = 'storage'"
          >
            <Database :size="18" />
            <span>Storage</span>
          </button>
        </div>
        
        <div class="settings-panel">
          <!-- General Settings -->
          <div v-if="activeSettingsTab === 'general'" class="settings-section">
            <h3>General Settings</h3>
            
            <div class="setting-item">
              <label class="setting-label">Theme</label>
              <div class="setting-control">
                <select v-model="settings.general.theme" class="setting-select">
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label class="setting-label">Language</label>
              <div class="setting-control">
                <select v-model="settings.general.language" class="setting-select">
                  <option value="en">English</option>
                  <option value="fr">Français</option>
                  <option value="es">Español</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Auto-save changes</span>
                  <p class="toggle-description">Automatically save your work</p>
                </label>
                <input type="checkbox" v-model="settings.general.autoSave" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Confirm before delete</span>
                  <p class="toggle-description">Show confirmation dialog when deleting items</p>
                </label>
                <input type="checkbox" v-model="settings.general.confirmDelete" class="toggle-checkbox" />
              </div>
            </div>
          </div>
          
          <!-- Notifications Settings -->
          <div v-if="activeSettingsTab === 'notifications'" class="settings-section">
            <h3>Notification Preferences</h3>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Email notifications</span>
                  <p class="toggle-description">Receive updates via email</p>
                </label>
                <input type="checkbox" v-model="settings.notifications.emailNotifications" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Push notifications</span>
                  <p class="toggle-description">Receive browser push notifications</p>
                </label>
                <input type="checkbox" v-model="settings.notifications.pushNotifications" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Annotation alerts</span>
                  <p class="toggle-description">Get notified when annotations need review</p>
                </label>
                <input type="checkbox" v-model="settings.notifications.annotationAlerts" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Weekly report</span>
                  <p class="toggle-description">Receive weekly activity summary</p>
                </label>
                <input type="checkbox" v-model="settings.notifications.weeklyReport" class="toggle-checkbox" />
              </div>
            </div>
          </div>
          
          <!-- Appearance Settings -->
          <div v-if="activeSettingsTab === 'appearance'" class="settings-section">
            <h3>Appearance & Display</h3>
            
            <div class="setting-item">
              <label class="setting-label">Grid size</label>
              <div class="setting-control">
                <select v-model="settings.appearance.gridSize" class="setting-select">
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Compact mode</span>
                  <p class="toggle-description">Use compact layout for more content</p>
                </label>
                <input type="checkbox" v-model="settings.appearance.compactMode" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Show image info</span>
                  <p class="toggle-description">Display image details on hover</p>
                </label>
                <input type="checkbox" v-model="settings.appearance.showImageInfo" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Enable animations</span>
                  <p class="toggle-description">Use smooth animations and transitions</p>
                </label>
                <input type="checkbox" v-model="settings.appearance.animationsEnabled" class="toggle-checkbox" />
              </div>
            </div>
          </div>
          
          <!-- Privacy Settings -->
          <div v-if="activeSettingsTab === 'privacy'" class="settings-section">
            <h3>Privacy & Security</h3>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Share analytics</span>
                  <p class="toggle-description">Help improve the app by sharing usage data</p>
                </label>
                <input type="checkbox" v-model="settings.privacy.shareAnalytics" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Public profile</span>
                  <p class="toggle-description">Make your profile visible to others</p>
                </label>
                <input type="checkbox" v-model="settings.privacy.publicProfile" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Show email address</span>
                  <p class="toggle-description">Display your email on your profile</p>
                </label>
                <input type="checkbox" v-model="settings.privacy.showEmail" class="toggle-checkbox" />
              </div>
            </div>
          </div>
          
          <!-- Storage Settings -->
          <div v-if="activeSettingsTab === 'storage'" class="settings-section">
            <h3>Storage & Cache</h3>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Cache images</span>
                  <p class="toggle-description">Store images locally for faster loading</p>
                </label>
                <input type="checkbox" v-model="settings.storage.cacheImages" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <label class="setting-label">Max cache size (MB)</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.storage.maxCacheSize" 
                  class="setting-input"
                  min="100"
                  max="5000"
                  step="100"
                />
              </div>
            </div>
            
            <div class="setting-item">
              <div class="setting-toggle">
                <label class="toggle-label">
                  <span>Auto cleanup</span>
                  <p class="toggle-description">Automatically clear old cached data</p>
                </label>
                <input type="checkbox" v-model="settings.storage.autoCleanup" class="toggle-checkbox" />
              </div>
            </div>
            
            <div class="setting-item">
              <button class="clear-cache-btn">
                <Database :size="16" />
                Clear Cache Now
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="settings-footer">
        <button class="settings-btn cancel" @click="closeSettingsModal">Cancel</button>
        <button class="settings-btn save" @click="saveSettings">Save Changes</button>
      </div>
    </div>
  </div>
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

/* Settings Modal */
.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.settings-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.settings-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #2c3e50;
}

.settings-title h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.settings-close {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7f8c8d;
  transition: all 0.2s;
}

.settings-close:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.settings-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.settings-tabs {
  width: 200px;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  padding: 16px 0;
  overflow-y: auto;
}

.settings-tab {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  color: #2c3e50;
  font-size: 14px;
  text-align: left;
}

.settings-tab:hover {
  background: rgba(52, 152, 219, 0.1);
}

.settings-tab.active {
  background: white;
  color: #3498db;
  border-right: 3px solid #3498db;
  font-weight: 600;
}

.settings-panel {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.settings-section h3 {
  margin: 0 0 24px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.setting-item {
  margin-bottom: 24px;
}

.setting-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.setting-control {
  width: 100%;
}

.setting-select,
.setting-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  color: #2c3e50;
  transition: all 0.2s;
}

.setting-select:focus,
.setting-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.setting-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: background 0.2s;
}

.setting-toggle:hover {
  background: #ecf0f1;
}

.toggle-label {
  flex: 1;
  cursor: pointer;
}

.toggle-label span {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.toggle-description {
  margin: 0;
  font-size: 12px;
  color: #7f8c8d;
}

.toggle-checkbox {
  width: 48px;
  height: 26px;
  appearance: none;
  background: #bdc3c7;
  border-radius: 13px;
  position: relative;
  cursor: pointer;
  transition: background 0.3s;
  flex-shrink: 0;
}

.toggle-checkbox::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  top: 3px;
  left: 3px;
  transition: transform 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-checkbox:checked {
  background: #27ae60;
}

.toggle-checkbox:checked::before {
  transform: translateX(22px);
}

.clear-cache-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.clear-cache-btn:hover {
  background: #c0392b;
}

.settings-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
}

.settings-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.settings-btn.cancel {
  background: transparent;
  color: #7f8c8d;
  border: 1px solid #e0e0e0;
}

.settings-btn.cancel:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.settings-btn.save {
  background: #3498db;
  color: white;
}

.settings-btn.save:hover {
  background: #2980b9;
}
</style>
