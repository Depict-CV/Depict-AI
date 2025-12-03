<script setup>
import { ref, onMounted } from 'vue';
import { Plus, UserPlus, FolderOpen, Users, Calendar, AlertCircle } from 'lucide-vue-next';
import { useApi } from '../../composables/useApi';

const api = useApi();
const projects = ref([]);
const loading = ref(false);
const error = ref(null);

// Fetch user's projects from API
const fetchProjects = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const data = await api.get('/projects/my-projects');
    projects.value = data.map(p => ({
      ...p,
      createdAt: p.created_at
    }));
  } catch (err) {
    console.error('Error fetching projects:', err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const createProject = async () => {
  const projectName = prompt('Enter project name:');
  if (!projectName) return;

  const description = prompt('Enter project description (optional):') || '';

  loading.value = true;
  error.value = null;

  try {
    const newProject = await api.post('/projects/', {
      name: projectName,
      description: description
    });

    projects.value.unshift({
      ...newProject,
      createdAt: newProject.created_at
    });

    alert(`Project "${projectName}" created successfully!`);
  } catch (err) {
    console.error('Error creating project:', err);
    alert(`Error: ${err.message}`);
  } finally {
    loading.value = false;
  }
};

const joinProject = async () => {
  const projectCode = prompt('Enter project code/name to join:');
  if (!projectCode) return;

  loading.value = true;
  error.value = null;

  try {
    const result = await api.post(`/projects/join/${encodeURIComponent(projectCode)}`, {});
    alert(result.message || 'Successfully joined project!');
    
    // Refresh projects list
    await fetchProjects();
  } catch (err) {
    console.error('Error joining project:', err);
    alert(`Error: ${err.message}`);
  } finally {
    loading.value = false;
  }
};

const selectProject = (project) => {
  console.log('Selected project:', project);
  // TODO: Implement project navigation/switching
  alert(`Opening project: ${project.name}`);
};

// Fetch projects on component mount
onMounted(() => {
  fetchProjects();
});
</script>

<template>
  <div class="projects-panel">
    <!-- Error Message -->
    <div v-if="error" class="error-banner">
      <AlertCircle :size="16" />
      <span>{{ error }}</span>
      <button @click="fetchProjects" class="retry-btn">Retry</button>
    </div>

    <!-- Action Buttons -->
    <div class="project-actions">
      <button class="panel-button primary" @click="createProject" :disabled="loading">
        <Plus :size="20" />
        {{ loading ? 'Loading...' : 'Create Project' }}
      </button>
      <button class="panel-button secondary" @click="joinProject" :disabled="loading">
        <UserPlus :size="20" />
        Join Project
      </button>
    </div>
    
    <div class="projects-list">
      <div class="projects-header">
        <h4>My Projects ({{ projects.length }})</h4>
      </div>

      <!-- Loading State -->
      <div v-if="loading && projects.length === 0" class="loading-projects">
        <div class="spinner"></div>
        <p>Loading projects...</p>
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
      
      <!-- Empty State -->
      <div v-if="!loading && projects.length === 0" class="empty-projects">
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

.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
  font-size: 13px;
  margin-bottom: 12px;
}

.retry-btn {
  margin-left: auto;
  padding: 4px 12px;
  background: #c33;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.retry-btn:hover {
  background: #a22;
}

.loading-projects {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.panel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
