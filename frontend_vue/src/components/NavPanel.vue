<script setup>
import { ref } from 'vue';
import { Upload, ChevronLeft, ChevronRight, Plus, UserPlus, FolderOpen, Users, Calendar, Tag, CheckSquare, XSquare, ImageIcon, Clock, BarChart, TrendingUp, Edit, Trash2, AlertCircle, Sparkles, Cpu, Zap, Settings } from 'lucide-vue-next';

defineProps({
  activeMenu: {
    type: String,
    required: true
  }
});

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
  // TODO: Implement create project modal/flow
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
  // TODO: Implement join project flow
  const projectCode = prompt('Enter project code to join:');
  if (projectCode) {
    alert(`Joining project with code: ${projectCode}`);
  }
};

const selectProject = (project) => {
  console.log('Selected project:', project);
  // TODO: Implement project selection logic
  alert(`Opening project: ${project.name}`);
};

// Filter state
const filters = ref({
  status: {
    annotated: false,
    unannotated: false,
    approved: false,
    pending: false
  },
  type: {
    square: false,
    portrait: false,
    landscape: false
  },
  dateRange: {
    today: false,
    week: false,
    month: false,
    all: true
  },
  tags: []
});

const availableTags = ref([
  { id: 1, name: 'Animals', color: '#27ae60' },
  { id: 2, name: 'Vehicles', color: '#3498db' },
  { id: 3, name: 'People', color: '#e74c3c' },
  { id: 4, name: 'Nature', color: '#16a085' },
  { id: 5, name: 'Buildings', color: '#f39c12' },
  { id: 6, name: 'Food', color: '#9b59b6' }
]);

const toggleTag = (tagId) => {
  const index = filters.value.tags.indexOf(tagId);
  if (index > -1) {
    filters.value.tags.splice(index, 1);
  } else {
    filters.value.tags.push(tagId);
  }
};

const applyFilters = () => {
  console.log('Applying filters:', filters.value);
  // TODO: Implement filter logic to update image gallery
  alert('Filters applied!');
};

const clearFilters = () => {
  filters.value = {
    status: {
      annotated: false,
      unannotated: false,
      approved: false,
      pending: false
    },
    type: {
      square: false,
      portrait: false,
      landscape: false
    },
    dateRange: {
      today: false,
      week: false,
      month: false,
      all: true
    },
    tags: []
  };
  console.log('Filters cleared');
};

// Statistics data - TODO: Replace with API call
const statistics = ref({
  totalImages: 3450,
  annotatedImages: 2890,
  unannotatedImages: 560,
  approvedImages: 2654,
  pendingReview: 236,
  modifyRequests: 12,
  deletedAnnotations: 48,
  totalLabels: 15670,
  uniqueLabels: 87,
  activeUsers: 8,
  avgAnnotationsPerImage: 5.4,
  completionRate: 83.8
});

const recentActivity = ref([
  { action: 'Approved', count: 45, time: '2 hours ago', color: '#27ae60' },
  { action: 'Annotated', count: 23, time: '4 hours ago', color: '#3498db' },
  { action: 'Modified', count: 8, time: '6 hours ago', color: '#f39c12' },
  { action: 'Deleted', count: 3, time: '1 day ago', color: '#e74c3c' }
]);

// AI Annotation state
const aiModels = ref([
  { id: 1, name: 'YOLO v8', description: 'Object detection', accuracy: 92, speed: 'Fast', active: true },
  { id: 2, name: 'Mask R-CNN', description: 'Instance segmentation', accuracy: 88, speed: 'Medium', active: false },
  { id: 3, name: 'EfficientDet', description: 'Object detection', accuracy: 90, speed: 'Fast', active: false },
  { id: 4, name: 'DeepLab v3', description: 'Semantic segmentation', accuracy: 85, speed: 'Slow', active: false }
]);

const aiSettings = ref({
  confidenceThreshold: 0.7,
  autoApprove: false,
  batchProcessing: true,
  maxBatchSize: 50
});

const selectAiModel = (modelId) => {
  aiModels.value.forEach(model => {
    model.active = model.id === modelId;
  });
  console.log('Selected AI model:', modelId);
};

const runAiAnnotation = () => {
  const activeModel = aiModels.value.find(m => m.active);
  console.log('Running AI annotation with:', activeModel?.name, aiSettings.value);
  // TODO: Implement AI annotation API call
  alert(`Starting AI annotation with ${activeModel?.name}...`);
};
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
      <div v-if="activeMenu === 'projects'" class="projects-panel">
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
      
      <!-- Filter Content -->
      <div v-if="activeMenu === 'filter'" class="filter-panel">
        <!-- Status Filters -->
        <div class="filter-section">
          <h4 class="filter-title">
            <CheckSquare :size="16" />
            Annotation Status
          </h4>
          <div class="filter-options">
            <label class="filter-checkbox">
              <input type="checkbox" v-model="filters.status.annotated" />
              <span>Annotated</span>
            </label>
            <label class="filter-checkbox">
              <input type="checkbox" v-model="filters.status.unannotated" />
              <span>Unannotated</span>
            </label>
            <label class="filter-checkbox">
              <input type="checkbox" v-model="filters.status.approved" />
              <span>Approved</span>
            </label>
            <label class="filter-checkbox">
              <input type="checkbox" v-model="filters.status.pending" />
              <span>Pending Review</span>
            </label>
          </div>
        </div>
        
        <!-- Image Type Filters -->
        <div class="filter-section">
          <h4 class="filter-title">
            <ImageIcon :size="16" />
            Image Type
          </h4>
          <div class="filter-options">
            <label class="filter-checkbox">
              <input type="checkbox" v-model="filters.type.square" />
              <span>Square</span>
            </label>
            <label class="filter-checkbox">
              <input type="checkbox" v-model="filters.type.portrait" />
              <span>Portrait</span>
            </label>
            <label class="filter-checkbox">
              <input type="checkbox" v-model="filters.type.landscape" />
              <span>Landscape</span>
            </label>
          </div>
        </div>
        
        <!-- Date Range Filters -->
        <div class="filter-section">
          <h4 class="filter-title">
            <Clock :size="16" />
            Date Range
          </h4>
          <div class="filter-options">
            <label class="filter-radio">
              <input type="radio" v-model="filters.dateRange.all" name="dateRange" :value="true" @change="filters.dateRange = { today: false, week: false, month: false, all: true }" />
              <span>All Time</span>
            </label>
            <label class="filter-radio">
              <input type="radio" name="dateRange" :value="true" @change="filters.dateRange = { today: true, week: false, month: false, all: false }" />
              <span>Today</span>
            </label>
            <label class="filter-radio">
              <input type="radio" name="dateRange" :value="true" @change="filters.dateRange = { today: false, week: true, month: false, all: false }" />
              <span>This Week</span>
            </label>
            <label class="filter-radio">
              <input type="radio" name="dateRange" :value="true" @change="filters.dateRange = { today: false, week: false, month: true, all: false }" />
              <span>This Month</span>
            </label>
          </div>
        </div>
        
        <!-- Tags Filter -->
        <div class="filter-section">
          <h4 class="filter-title">
            <Tag :size="16" />
            Tags
          </h4>
          <div class="filter-tags">
            <button 
              v-for="tag in availableTags" 
              :key="tag.id"
              class="filter-tag"
              :class="{ active: filters.tags.includes(tag.id) }"
              :style="{ borderColor: tag.color, color: filters.tags.includes(tag.id) ? 'white' : tag.color, background: filters.tags.includes(tag.id) ? tag.color : 'transparent' }"
              @click="toggleTag(tag.id)"
            >
              {{ tag.name }}
            </button>
          </div>
        </div>
        
        <!-- Filter Actions -->
        <div class="filter-actions">
          <button class="panel-button primary" @click="applyFilters">
            <CheckSquare :size="18" />
            Apply Filters
          </button>
          <button class="panel-button" @click="clearFilters">
            <XSquare :size="18" />
            Clear All
          </button>
        </div>
      </div>
      
      <!-- Statistics Content -->
      <div v-if="activeMenu === 'statistics'" class="stats-panel">
        <!-- Overview Stats -->
        <div class="stats-overview">
          <h4 class="stats-section-title">Overview</h4>
          <div class="stats-grid">
            <div class="stat-card primary">
              <div class="stat-icon">
                <ImageIcon :size="20" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ statistics.totalImages.toLocaleString() }}</div>
                <div class="stat-label">Total Images</div>
              </div>
            </div>
            
            <div class="stat-card success">
              <div class="stat-icon">
                <CheckSquare :size="20" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ statistics.annotatedImages.toLocaleString() }}</div>
                <div class="stat-label">Annotated</div>
              </div>
            </div>
            
            <div class="stat-card warning">
              <div class="stat-icon">
                <XSquare :size="20" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ statistics.unannotatedImages.toLocaleString() }}</div>
                <div class="stat-label">Unannotated</div>
              </div>
            </div>
            
            <div class="stat-card info">
              <div class="stat-icon">
                <TrendingUp :size="20" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ statistics.completionRate }}%</div>
                <div class="stat-label">Completion</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Approval Stats -->
        <div class="stats-section">
          <h4 class="stats-section-title">Approval Status</h4>
          <div class="stats-list">
            <div class="stats-item">
              <div class="stats-item-label">
                <CheckSquare :size="16" />
                <span>Approved Images</span>
              </div>
              <div class="stats-item-value success">{{ statistics.approvedImages.toLocaleString() }}</div>
            </div>
            <div class="stats-item">
              <div class="stats-item-label">
                <Clock :size="16" />
                <span>Pending Review</span>
              </div>
              <div class="stats-item-value warning">{{ statistics.pendingReview.toLocaleString() }}</div>
            </div>
            <div class="stats-item">
              <div class="stats-item-label">
                <Edit :size="16" />
                <span>Modify Requests</span>
              </div>
              <div class="stats-item-value info">{{ statistics.modifyRequests.toLocaleString() }}</div>
            </div>
            <div class="stats-item">
              <div class="stats-item-label">
                <Trash2 :size="16" />
                <span>Deleted Annotations</span>
              </div>
              <div class="stats-item-value danger">{{ statistics.deletedAnnotations.toLocaleString() }}</div>
            </div>
          </div>
        </div>
        
        <!-- Labels Stats -->
        <div class="stats-section">
          <h4 class="stats-section-title">Labels & Annotations</h4>
          <div class="stats-list">
            <div class="stats-item">
              <div class="stats-item-label">
                <Tag :size="16" />
                <span>Total Labels</span>
              </div>
              <div class="stats-item-value primary">{{ statistics.totalLabels.toLocaleString() }}</div>
            </div>
            <div class="stats-item">
              <div class="stats-item-label">
                <Tag :size="16" />
                <span>Unique Labels</span>
              </div>
              <div class="stats-item-value primary">{{ statistics.uniqueLabels }}</div>
            </div>
            <div class="stats-item">
              <div class="stats-item-label">
                <BarChart :size="16" />
                <span>Avg per Image</span>
              </div>
              <div class="stats-item-value info">{{ statistics.avgAnnotationsPerImage }}</div>
            </div>
          </div>
        </div>
        
        <!-- Team Stats -->
        <div class="stats-section">
          <h4 class="stats-section-title">Team Activity</h4>
          <div class="stats-list">
            <div class="stats-item">
              <div class="stats-item-label">
                <Users :size="16" />
                <span>Active Users</span>
              </div>
              <div class="stats-item-value success">{{ statistics.activeUsers }}</div>
            </div>
          </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="stats-section">
          <h4 class="stats-section-title">Recent Activity</h4>
          <div class="activity-list">
            <div v-for="(activity, index) in recentActivity" :key="index" class="activity-item">
              <div class="activity-indicator" :style="{ background: activity.color }"></div>
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-action">{{ activity.action }}</span>
                  <span class="activity-count" :style="{ color: activity.color }">{{ activity.count }}</span>
                </div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- AI Annotation Content -->
      <div v-if="activeMenu === 'ai-annotation'" class="ai-panel">
        <!-- AI Models Section -->
        <div class="ai-section">
          <h4 class="ai-section-title">
            <Cpu :size="16" />
            Available Models
          </h4>
          <div class="ai-models-list">
            <div 
              v-for="model in aiModels" 
              :key="model.id" 
              class="ai-model-card"
              :class="{ active: model.active }"
              @click="selectAiModel(model.id)"
            >
              <div class="ai-model-header">
                <div class="ai-model-icon">
                  <Sparkles :size="18" />
                </div>
                <div class="ai-model-info">
                  <h5 class="ai-model-name">{{ model.name }}</h5>
                  <p class="ai-model-description">{{ model.description }}</p>
                </div>
              </div>
              <div class="ai-model-stats">
                <div class="ai-model-stat">
                  <span class="stat-label">Accuracy</span>
                  <span class="stat-value">{{ model.accuracy }}%</span>
                </div>
                <div class="ai-model-stat">
                  <span class="stat-label">Speed</span>
                  <span class="stat-value" :class="'speed-' + model.speed.toLowerCase()">{{ model.speed }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- AI Settings Section -->
        <div class="ai-section">
          <h4 class="ai-section-title">
            <Settings :size="16" />
            Configuration
          </h4>
          <div class="ai-settings-list">
            <div class="ai-setting-item">
              <label class="ai-setting-label">Confidence Threshold</label>
              <div class="ai-setting-control">
                <input 
                  type="range" 
                  v-model="aiSettings.confidenceThreshold" 
                  min="0" 
                  max="1" 
                  step="0.05"
                  class="ai-slider"
                />
                <span class="ai-slider-value">{{ (aiSettings.confidenceThreshold * 100).toFixed(0) }}%</span>
              </div>
            </div>
            
            <div class="ai-setting-item">
              <label class="ai-setting-label">Max Batch Size</label>
              <div class="ai-setting-control">
                <input 
                  type="number" 
                  v-model="aiSettings.maxBatchSize" 
                  min="1" 
                  max="100" 
                  class="ai-number-input"
                />
              </div>
            </div>
            
            <div class="ai-setting-item">
              <label class="ai-checkbox">
                <input type="checkbox" v-model="aiSettings.autoApprove" />
                <span>Auto-approve annotations</span>
              </label>
            </div>
            
            <div class="ai-setting-item">
              <label class="ai-checkbox">
                <input type="checkbox" v-model="aiSettings.batchProcessing" />
                <span>Enable batch processing</span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- Action Button -->
        <div class="ai-actions">
          <button class="panel-button primary ai-run-btn" @click="runAiAnnotation">
            <Zap :size="20" />
            Run AI Annotation
          </button>
          <div class="ai-info">
            <AlertCircle :size="14" />
            <span>AI will process unannotated images only</span>
          </div>
        </div>
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

/* Projects Panel */
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

/* Filter Panel */
.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filter-checkbox,
.filter-radio {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.filter-checkbox:hover,
.filter-radio:hover {
  background: #f8f9fa;
}

.filter-checkbox input,
.filter-radio input {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #3498db;
}

.filter-checkbox span,
.filter-radio span {
  font-size: 14px;
  color: #2c3e50;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  padding: 6px 12px;
  border: 2px solid;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
}

.filter-tag:hover {
  opacity: 0.8;
  transform: scale(1.05);
}

.filter-tag.active {
  color: white !important;
}

.filter-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

/* Statistics Panel */
.stats-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-section-title {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stats-overview {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.stat-card.warning {
  background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
  color: white;
}

.stat-card.info {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  opacity: 0.9;
  font-weight: 500;
}

.stats-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.stats-item:hover {
  background: #ecf0f1;
}

.stats-item-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-size: 13px;
}

.stats-item-value {
  font-size: 16px;
  font-weight: 700;
}

.stats-item-value.primary {
  color: #667eea;
}

.stats-item-value.success {
  color: #27ae60;
}

.stats-item-value.warning {
  color: #f39c12;
}

.stats-item-value.info {
  color: #3498db;
}

.stats-item-value.danger {
  color: #e74c3c;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #ecf0f1;
}

.activity-indicator {
  width: 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.activity-action {
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
}

.activity-count {
  font-size: 14px;
  font-weight: 700;
}

.activity-time {
  font-size: 11px;
  color: #95a5a6;
}

/* AI Annotation Panel */
.ai-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.ai-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ai-models-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-model-card {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-model-card:hover {
  border-color: #667eea;
  background: #f8f9fa;
}

.ai-model-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.ai-model-header {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.ai-model-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.ai-model-info {
  flex: 1;
}

.ai-model-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.ai-model-description {
  margin: 0;
  font-size: 11px;
  color: #7f8c8d;
}

.ai-model-stats {
  display: flex;
  gap: 12px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
}

.ai-model-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ai-model-stat .stat-label {
  font-size: 10px;
  color: #95a5a6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ai-model-stat .stat-value {
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
}

.ai-model-stat .speed-fast {
  color: #27ae60;
}

.ai-model-stat .speed-medium {
  color: #f39c12;
}

.ai-model-stat .speed-slow {
  color: #e74c3c;
}

.ai-settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-setting-label {
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
}

.ai-setting-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  outline: none;
  appearance: none;
}

.ai-slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.ai-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.ai-slider-value {
  font-size: 13px;
  font-weight: 600;
  color: #667eea;
  min-width: 40px;
  text-align: right;
}

.ai-number-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  color: #2c3e50;
}

.ai-number-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.ai-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.ai-checkbox:hover {
  background: #ecf0f1;
}

.ai-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.ai-checkbox span {
  font-size: 13px;
  color: #2c3e50;
}

.ai-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-run-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.ai-run-btn:hover {
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.ai-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 6px;
  font-size: 11px;
  color: #856404;
}
</style>
