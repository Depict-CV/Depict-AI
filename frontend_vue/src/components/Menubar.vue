<script setup>
import { ref } from 'vue';
import { User, Settings, CreditCard, Building2, LogOut, ChevronDown } from 'lucide-vue-next';
import logo from '../assets/logo.svg';

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ username: 'User', email: '' })
  }
});

const emit = defineEmits(['logout']);
const showProfileMenu = ref(false);

const handleLogout = () => {
  showProfileMenu.value = false;
  emit('logout');
};

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value;
};

const handleClickOutside = (event) => {
  const menu = document.querySelector('.profile-dropdown');
  const button = document.querySelector('.profile-button');
  if (menu && !menu.contains(event.target) && !button.contains(event.target)) {
    showProfileMenu.value = false;
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