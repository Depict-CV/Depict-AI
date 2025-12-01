<script setup>
import { ref } from 'vue';
import { Plus, UserPlus, FolderOpen, Users, Calendar } from 'lucide-vue-next';

// Mock projects data - TODO: Replace with API call
const projects = ref([
  { 
    id: 1, 
    name: 'Wildlife Dataset', 
    description: 'Animal classification project',
    members: 5, 
    images: 1250, 
    status: 'active',
    createdAt: '2025-11-15',
    role: 'Admin'
  },
  { 
    id: 2, 
    name: 'Medical Imaging', 
    description: 'X-ray annotation project',
    members: 3, 
    images: 840, 
    status: 'active',
    createdAt: '2025-11-20',
    role: 'Editor'
  },
  { 
    id: 3, 
    name: 'Retail Products', 
    description: 'Product detection and labeling',
    members: 8, 
    images: 2100, 
    status: 'active',
    createdAt: '2025-10-10',
    role: 'Viewer'
  },
  { 
    id: 4, 
    name: 'Traffic Analysis', 
    description: 'Vehicle and pedestrian tracking',
    members: 4, 
    images: 560, 
    status: 'archived',
    createdAt: '2025-09-05',
    role: 'Editor'
  }
]);

const createProject = () => {
  console.log('Creating new project...');
  const projectName = prompt('Enter project name:');
  if (projectName) {
    projects.value.unshift({
      id: Date.now(),
      name: projectName,
      description: 'New project',
      members: 1,
      images: 0,
      status: 'active',
      createdAt: new Date().toISOString().split('T')[0],
      role: 'Admin'
    });
  }
};

const joinProject = () => {
  console.log('Joining project...');
  const projectCode = prompt('Enter project code to join:');
  if (projectCode) {
    alert(`Joining project with code: ${projectCode}`);
  }
};

const selectProject = (project) => {
  console.log('Selected project:', project);
  alert(`Opening project: ${project.name}`);
};
</script>

<template>
  <div class="projects-panel">
    <div class="project-actions">
      <button class="panel-button primary" @click="createProject">
        <Plus :size="20" />
        Create Project
      </button>
      <button class="panel-button secondary" @click="joinProject">
        <UserPlus :size="20" />
        Join Project
      </button>
    </div>
    
    <div class="projects-list">
      <div class="projects-header">
        <h4>My Projects ({{ projects.length }})</h4>
      </div>
      
      <div 
        v-for="project in projects" 
        :key="project.id" 
        class="project-card"
        :class="{ archived: project.status === 'archived' }"
        @click="selectProject(project)"
      >
        <div class="project-header">
          <div class="project-icon">
            <FolderOpen :size="20" />
          </div>
          <div class="project-info">
            <h5 class="project-name">{{ project.name }}</h5>
            <p class="project-description">{{ project.description }}</p>
          </div>
        </div>
        
        <div class="project-meta">
          <div class="project-stat">
            <Users :size="14" />
            <span>{{ project.members }}</span>
          </div>
          <div class="project-stat">
            <FolderOpen :size="14" />
            <span>{{ project.images }}</span>
          </div>
        </div>
        
        <div class="project-footer">
          <span class="project-role" :class="'role-' + project.role.toLowerCase()">{{ project.role }}</span>
          <span class="project-date">
            <Calendar :size="12" />
            {{ new Date(project.createdAt).toLocaleDateString() }}
          </span>
        </div>
      </div>
      
      <div v-if="projects.length === 0" class="empty-projects">
        <FolderOpen :size="48" />
        <p>No projects yet</p>
        <small>Create or join a project to get started</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
.projects-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.project-actions {
  display: flex;
  flex-direction: column;
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

.panel-button.secondary {
  background: white;
  color: #3498db;
  border: 2px solid #3498db;
}

.panel-button.secondary:hover {
  background: #3498db;
  color: white;
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.projects-header {
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.projects-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.project-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.project-card:hover {
  border-color: #3498db;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
  transform: translateX(2px);
}

.project-card.archived {
  opacity: 0.6;
  background: #f8f9fa;
}

.project-header {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.project-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-description {
  margin: 0;
  font-size: 11px;
  color: #7f8c8d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  padding: 8px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.project-stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #7f8c8d;
}

.project-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.project-role {
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
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

.project-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: #95a5a6;
}

.empty-projects {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #bdc3c7;
  text-align: center;
}

.empty-projects p {
  margin: 12px 0 4px 0;
  font-size: 14px;
  font-weight: 600;
}

.empty-projects small {
  font-size: 12px;
  color: #95a5a6;
}
</style>
