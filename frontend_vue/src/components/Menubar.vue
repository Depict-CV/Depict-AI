<script setup>
import { ref, computed } from 'vue';
import { User, Settings, CreditCard, Building2, LogOut, ChevronDown, Bell, X } from 'lucide-vue-next';
import logo from '../assets/logo.svg';

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ username: 'User', email: '' })
  },
  modifyRequests: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['logout', 'remove-modify-request', 'clear-modify-requests']);
const showProfileMenu = ref(false);
const showNotifications = ref(false);

const notificationCount = computed(() => props.modifyRequests.length);

const handleLogout = () => {
  showProfileMenu.value = false;
  emit('logout');
};

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value;
  showNotifications.value = false;
};

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value;
  showProfileMenu.value = false;
};

const removeNotification = (imageId) => {
  emit('remove-modify-request', imageId);
};

const clearAllNotifications = () => {
  emit('clear-modify-requests');
  showNotifications.value = false;
};

const handleClickOutside = (event) => {
  const menu = document.querySelector('.profile-dropdown');
  const button = document.querySelector('.profile-button');
  const notifMenu = document.querySelector('.notification-dropdown');
  const notifButton = document.querySelector('.notification-button');
  
  if (menu && !menu.contains(event.target) && !button.contains(event.target)) {
    showProfileMenu.value = false;
  }
  
  if (notifMenu && !notifMenu.contains(event.target) && !notifButton.contains(event.target)) {
    showNotifications.value = false;
  }
};

// Add click outside listener when component is mounted
if (typeof window !== 'undefined') {
  document.addEventListener('click', handleClickOutside);
}
</script>

<template>
  <header class="menubar">
    <div class="menubar-left">
      <img :src="logo" alt="Depict AI" class="app-logo" />
    </div>
    
    <div class="menubar-right">
      <!-- Notifications -->
      <div class="notification-section">
        <button class="notification-button" @click="toggleNotifications">
          <Bell :size="20" />
          <span v-if="notificationCount > 0" class="notification-badge">{{ notificationCount }}</span>
        </button>
        
        <div v-if="showNotifications" class="notification-dropdown">
          <div class="notification-header">
            <h3>Modify Requests</h3>
            <button v-if="notificationCount > 0" class="clear-all-btn" @click="clearAllNotifications">
              Clear All
            </button>
          </div>
          
          <div v-if="notificationCount === 0" class="empty-notifications">
            <Bell :size="32" />
            <p>No modification requests</p>
          </div>
          
          <div v-else class="notification-list">
            <div 
              v-for="request in modifyRequests" 
              :key="request.id" 
              class="notification-item"
            >
              <img :src="request.location" :alt="`Image ${request.id}`" class="notification-thumb" />
              <div class="notification-info">
                <div class="notification-title">Image #{{ request.id }}</div>
                <div class="notification-meta">{{ request.type }} · Needs modification</div>
              </div>
              <button class="notification-remove" @click="removeNotification(request.id)">
                <X :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="profile-section">
        <button class="profile-button" @click="toggleProfileMenu">
          <div class="profile-avatar">
            <User :size="20" />
          </div>
          <span class="profile-name">{{ currentUser?.username || 'Account' }}</span>
          <ChevronDown :size="16" />
        </button>
        
        <div v-if="showProfileMenu" class="profile-dropdown">
          <button class="dropdown-item">
            <User :size="18" />
            <span>Profile</span>
          </button>
          
          <button class="dropdown-item">
            <CreditCard :size="18" />
            <span>Subscription</span>
          </button>
          
          <button class="dropdown-item">
            <Settings :size="18" />
            <span>Settings</span>
          </button>
          
          <button class="dropdown-item">
            <Building2 :size="18" />
            <span>Organisation</span>
          </button>
          
          <div class="dropdown-divider"></div>
          
          <button class="dropdown-item danger" @click="handleLogout">
            <LogOut :size="18" />
            <span>Log Out</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.menubar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.menubar-left {
  display: flex;
  align-items: center;
}

.app-logo {
  height: 40px;
  width: auto;
  object-fit: contain;
}

.menubar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-section {
  position: relative;
}

.notification-button {
  position: relative;
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2c3e50;
  transition: all 0.2s;
}

.notification-button:hover {
  background: #f8f9fa;
}

.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #e74c3c;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1.2;
}

.notification-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 360px;
  max-height: 500px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.2s ease;
  display: flex;
  flex-direction: column;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.notification-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.clear-all-btn {
  padding: 4px 12px;
  background: transparent;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #7f8c8d;
  transition: all 0.2s;
}

.clear-all-btn:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.empty-notifications {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #bdc3c7;
}

.empty-notifications p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

.notification-list {
  overflow-y: auto;
  max-height: 400px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background: #f8f9fa;
}

.notification-thumb {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.notification-info {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.notification-meta {
  font-size: 12px;
  color: #7f8c8d;
}

.notification-remove {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #95a5a6;
  transition: all 0.2s;
  flex-shrink: 0;
}

.notification-remove:hover {
  background: #e74c3c;
  color: white;
}

.profile-section {
  position: relative;
}

.profile-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #2c3e50;
}

.profile-button:hover {
  background: #f8f9fa;
  border-color: #d0d0d0;
}

.profile-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-name {
  font-size: 14px;
  font-weight: 500;
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 220px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 8px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #2c3e50;
  font-size: 14px;
  text-align: left;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.dropdown-item.danger {
  color: #e74c3c;
}

.dropdown-item.danger:hover {
  background: #fee;
}

.dropdown-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 8px 0;
}
</style>