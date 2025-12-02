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
const showOrgModal = ref(false);

const notificationCount = computed(() => props.modifyRequests.length);

// Mock organization data - TODO: Replace with API call
const organizationMembers = ref([
  { id: 1, name: 'John Doe', email: 'john.doe@example.com', role: 'Admin', avatar: null, status: 'active' },
  { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com', role: 'Editor', avatar: null, status: 'active' },
  { id: 3, name: 'Bob Johnson', email: 'bob.johnson@example.com', role: 'Viewer', avatar: null, status: 'active' },
  { id: 4, name: 'Alice Williams', email: 'alice.williams@example.com', role: 'Editor', avatar: null, status: 'active' },
  { id: 5, name: 'Charlie Brown', email: 'charlie.brown@example.com', role: 'Viewer', avatar: null, status: 'inactive' }
]);

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

const openOrgModal = () => {
  showOrgModal.value = true;
  showProfileMenu.value = false;
};

const closeOrgModal = () => {
  showOrgModal.value = false;
};

const getInitials = (name) => {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase();
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
          
          <button class="dropdown-item" @click="openOrgModal">
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
    
    <!-- Organization Modal -->
    <div v-if="showOrgModal" class="modal-overlay" @click="closeOrgModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <div class="modal-title">
            <Building2 :size="24" />
            <h2>Organization Members</h2>
          </div>
          <button class="modal-close" @click="closeOrgModal">
            <X :size="20" />
          </button>
        </div>
        
        <div class="modal-body">
          <div class="members-stats">
            <div class="stat-item">
              <span class="stat-value">{{ organizationMembers.length }}</span>
              <span class="stat-label">Total Members</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ organizationMembers.filter(m => m.status === 'active').length }}</span>
              <span class="stat-label">Active</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ organizationMembers.filter(m => m.role === 'Admin').length }}</span>
              <span class="stat-label">Admins</span>
            </div>
          </div>
          
          <div class="members-list">
            <div 
              v-for="member in organizationMembers" 
              :key="member.id" 
              class="member-card"
            >
              <div class="member-avatar">
                <span>{{ getInitials(member.name) }}</span>
              </div>
              <div class="member-info">
                <div class="member-name">{{ member.name }}</div>
                <div class="member-email">{{ member.email }}</div>
              </div>
              <div class="member-meta">
                <span class="member-role" :class="'role-' + member.role.toLowerCase()">{{ member.role }}</span>
                <span class="member-status" :class="'status-' + member.status">{{ member.status }}</span>
              </div>
            </div>
          </div>
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

/* Organization Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 80vh;
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

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #2c3e50;
}

.modal-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.modal-close {
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

.modal-close:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.members-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #3498db;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s;
}

.member-card:hover {
  border-color: #3498db;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
}

.member-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.member-email {
  font-size: 13px;
  color: #7f8c8d;
}

.member-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.member-role,
.member-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.member-role {
  background: #e8f4f8;
  color: #3498db;
}

.role-admin {
  background: #fef5e7;
  color: #f39c12;
}

.role-editor {
  background: #e8f8f5;
  color: #27ae60;
}

.role-viewer {
  background: #e8f4f8;
  color: #3498db;
}

.member-status {
  background: #d5f4e6;
  color: #27ae60;
}

.status-inactive {
  background: #fadbd8;
  color: #e74c3c;
}
</style>