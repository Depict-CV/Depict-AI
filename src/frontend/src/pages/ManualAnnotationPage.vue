<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { Square, Circle, Save, Check, X, ArrowLeft, Trash2, History, Clock, Plus, Undo } from 'lucide-vue-next';

const props = defineProps({
  image: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

// Drawing state
const canvas = ref(null);
const ctx = ref(null);
const imageElement = ref(null);
const activeTool = ref('rectangle'); // 'rectangle' or 'circle'
const isDrawing = ref(false);
const startX = ref(0);
const startY = ref(0);
const annotations = ref([]);
const currentAnnotation = ref(null);

// History tracking
const history = ref([]);
const showHistory = ref(false);

// Canvas dimensions
const canvasWidth = ref(0);
const canvasHeight = ref(0);

// Add history entry
const addHistoryEntry = (action, details) => {
  const entry = {
    id: Date.now(),
    action,
    details,
    timestamp: new Date().toISOString(),
    annotationCount: annotations.value.length
  };
  history.value.unshift(entry);
};

// Initialize canvas will be called in main onMounted at the end

const setupCanvas = (img) => {
  // Get the container size
  const container = canvas.value.parentElement;
  const containerWidth = container.clientWidth;
  const containerHeight = container.clientHeight;
  
  // Calculate scaling to fit image in container while maintaining aspect ratio
  const scale = Math.min(
    containerWidth / img.width,
    containerHeight / img.height
  );
  
  canvasWidth.value = img.width * scale;
  canvasHeight.value = img.height * scale;
  
  canvas.value.width = canvasWidth.value;
  canvas.value.height = canvasHeight.value;
  
  // Draw the image
  ctx.value.drawImage(img, 0, 0, canvasWidth.value, canvasHeight.value);
  imageElement.value = img;
};

// Drawing functions
const startDrawing = (e) => {
  isDrawing.value = true;
  const rect = canvas.value.getBoundingClientRect();
  startX.value = e.clientX - rect.left;
  startY.value = e.clientY - rect.top;
};

const draw = (e) => {
  if (!isDrawing.value) return;
  
  const rect = canvas.value.getBoundingClientRect();
  const currentX = e.clientX - rect.left;
  const currentY = e.clientY - rect.top;
  
  // Redraw image and existing annotations
  redrawCanvas();
  
  // Draw current annotation
  ctx.value.strokeStyle = '#3498db';
  ctx.value.lineWidth = 2;
  ctx.value.setLineDash([5, 5]);
  
  if (activeTool.value === 'rectangle') {
    const width = currentX - startX.value;
    const height = currentY - startY.value;
    ctx.value.strokeRect(startX.value, startY.value, width, height);
  } else if (activeTool.value === 'circle') {
    const radius = Math.sqrt(
      Math.pow(currentX - startX.value, 2) + 
      Math.pow(currentY - startY.value, 2)
    );
    ctx.value.beginPath();
    ctx.value.arc(startX.value, startY.value, radius, 0, 2 * Math.PI);
    ctx.value.stroke();
  }
  
  ctx.value.setLineDash([]);
};

const stopDrawing = (e) => {
  if (!isDrawing.value) return;
  
  const rect = canvas.value.getBoundingClientRect();
  const endX = e.clientX - rect.left;
  const endY = e.clientY - rect.top;
  
  // Create annotation object
  const annotation = {
    id: Date.now(),
    type: activeTool.value,
    color: '#3498db',
    created: new Date().toISOString()
  };
  
  if (activeTool.value === 'rectangle') {
    annotation.x = Math.min(startX.value, endX);
    annotation.y = Math.min(startY.value, endY);
    annotation.width = Math.abs(endX - startX.value);
    annotation.height = Math.abs(endY - startY.value);
  } else if (activeTool.value === 'circle') {
    annotation.centerX = startX.value;
    annotation.centerY = startY.value;
    annotation.radius = Math.sqrt(
      Math.pow(endX - startX.value, 2) + 
      Math.pow(endY - startY.value, 2)
    );
  }
  
  // Only add if annotation has meaningful size
  if (
    (annotation.type === 'rectangle' && annotation.width > 5 && annotation.height > 5) ||
    (annotation.type === 'circle' && annotation.radius > 5)
  ) {
    annotations.value.push(annotation);
    redrawCanvas();
    
    // Add history entry
    addHistoryEntry('added', `${annotation.type} annotation added at ${formatCoords(annotation)}`);
  }
  
  isDrawing.value = false;
};

const redrawCanvas = () => {
  if (!ctx.value || !imageElement.value) return;
  
  // Clear canvas
  ctx.value.clearRect(0, 0, canvasWidth.value, canvasHeight.value);
  
  // Draw image
  ctx.value.drawImage(imageElement.value, 0, 0, canvasWidth.value, canvasHeight.value);
  
  // Draw all annotations
  annotations.value.forEach(ann => {
    ctx.value.strokeStyle = ann.color;
    ctx.value.lineWidth = 2;
    ctx.value.setLineDash([]);
    
    if (ann.type === 'rectangle') {
      ctx.value.strokeRect(ann.x, ann.y, ann.width, ann.height);
      ctx.value.fillStyle = ann.color + '20';
      ctx.value.fillRect(ann.x, ann.y, ann.width, ann.height);
    } else if (ann.type === 'circle') {
      ctx.value.beginPath();
      ctx.value.arc(ann.centerX, ann.centerY, ann.radius, 0, 2 * Math.PI);
      ctx.value.stroke();
      ctx.value.fillStyle = ann.color + '20';
      ctx.value.fill();
    }
  });
};

const deleteAnnotation = (id) => {
  const annotation = annotations.value.find(ann => ann.id === id);
  annotations.value = annotations.value.filter(ann => ann.id !== id);
  redrawCanvas();
  
  // Add history entry
  if (annotation) {
    addHistoryEntry('deleted', `${annotation.type} annotation removed`);
  }
};

const clearAllAnnotations = () => {
  const count = annotations.value.length;
  annotations.value = [];
  redrawCanvas();
  
  // Add history entry
  if (count > 0) {
    addHistoryEntry('cleared', `All ${count} annotations cleared`);
  }
};

const saveAnnotations = () => {
  console.log('Saving annotations:', annotations.value);
  // TODO: Implement API call to save annotations
  addHistoryEntry('saved', `${annotations.value.length} annotations saved`);
  alert('Annotations saved! (Currently console.log only)');
};

const approveAnnotations = () => {
  console.log('Approving annotations:', annotations.value);
  // TODO: Implement API call to approve annotations
  addHistoryEntry('approved', `${annotations.value.length} annotations approved`);
  alert('Annotations approved! (Currently console.log only)');
};

const toggleHistory = () => {
  showHistory.value = !showHistory.value;
};

const getActionIcon = (action) => {
  switch(action) {
    case 'opened': return Clock;
    case 'added': return Plus;
    case 'deleted': return Trash2;
    case 'cleared': return X;
    case 'saved': return Save;
    case 'approved': return Check;
    default: return History;
  }
};

const getActionColor = (action) => {
  switch(action) {
    case 'opened': return '#3498db';
    case 'added': return '#27ae60';
    case 'deleted': return '#e74c3c';
    case 'cleared': return '#e67e22';
    case 'saved': return '#3498db';
    case 'approved': return '#27ae60';
    default: return '#95a5a6';
  }
};

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  
  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  
  return date.toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

const handleClose = () => {
  emit('close');
};

const formatCoords = (annotation) => {
  if (annotation.type === 'rectangle') {
    return `(${Math.round(annotation.x)}, ${Math.round(annotation.y)}) - ${Math.round(annotation.width)}×${Math.round(annotation.height)}`;
  } else if (annotation.type === 'circle') {
    return `Center: (${Math.round(annotation.centerX)}, ${Math.round(annotation.centerY)}), R: ${Math.round(annotation.radius)}`;
  }
  return '';
};

// Mock history data
const initMockHistory = () => {
  const mockEntries = [
    { action: 'opened', details: 'Image opened for annotation', timestamp: new Date(Date.now() - 300000).toISOString(), annotationCount: 0 },
    { action: 'added', details: 'Rectangle annotation added at (120, 85) - 200×150', timestamp: new Date(Date.now() - 240000).toISOString(), annotationCount: 1 },
    { action: 'added', details: 'Circle annotation added at Center: (400, 300), R: 80', timestamp: new Date(Date.now() - 180000).toISOString(), annotationCount: 2 },
    { action: 'deleted', details: 'Rectangle annotation removed', timestamp: new Date(Date.now() - 120000).toISOString(), annotationCount: 1 },
    { action: 'saved', details: '1 annotation saved', timestamp: new Date(Date.now() - 60000).toISOString(), annotationCount: 1 },
  ];
  
  mockEntries.forEach((entry, index) => {
    history.value.push({ ...entry, id: Date.now() + index });
  });
};

onMounted(() => {
  if (canvas.value) {
    ctx.value = canvas.value.getContext('2d');
    const img = new Image();
    img.onload = () => {
      setupCanvas(img);
    };
    img.src = props.image.location;
  }
  
  // Initialize with mock history
  initMockHistory();
});
</script>

<template>
  <div class="annotation-page">
    <!-- Left Sidebar -->
    <div class="annotation-sidebar">
      <div class="sidebar-header">
        <h2>Annotations</h2>
        <span class="annotation-count">{{ annotations.length }}</span>
      </div>
      
      <!-- Drawing Tools -->
      <div class="tools-section">
        <h3>Drawing Tools</h3>
        <div class="tool-buttons">
          <button 
            :class="['tool-btn', { active: activeTool === 'rectangle' }]"
            @click="activeTool = 'rectangle'"
          >
            <Square :size="20" />
            <span>Rectangle</span>
          </button>
          <button 
            :class="['tool-btn', { active: activeTool === 'circle' }]"
            @click="activeTool = 'circle'"
          >
            <Circle :size="20" />
            <span>Circle</span>
          </button>
        </div>
      </div>
      
      <!-- Annotations List -->
      <div class="annotations-list">
        <h3>Shapes ({{ annotations.length }})</h3>
        <div v-if="annotations.length === 0" class="empty-state">
          <p>No annotations yet</p>
          <p class="hint">Draw on the image to create annotations</p>
        </div>
        <div v-else class="annotation-items">
          <div 
            v-for="annotation in annotations" 
            :key="annotation.id" 
            class="annotation-item"
          >
            <div class="annotation-info">
              <div class="annotation-type">
                <Square v-if="annotation.type === 'rectangle'" :size="16" />
                <Circle v-if="annotation.type === 'circle'" :size="16" />
                <span>{{ annotation.type }}</span>
              </div>
              <div class="annotation-coords">
                {{ formatCoords(annotation) }}
              </div>
            </div>
            <button 
              class="delete-btn" 
              @click="deleteAnnotation(annotation.id)"
              title="Delete annotation"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="action-buttons">
        <button class="action-btn save-btn" @click="saveAnnotations">
          <Save :size="20" />
          <span>Save</span>
        </button>
        <button class="action-btn approve-btn" @click="approveAnnotations">
          <Check :size="20" />
          <span>Approve</span>
        </button>
        <button class="action-btn clear-btn" @click="clearAllAnnotations">
          <Trash2 :size="20" />
          <span>Clear All</span>
        </button>
        <button class="action-btn history-btn" @click="toggleHistory">
          <History :size="20" />
          <span>History ({{ history.length }})</span>
        </button>
      </div>
    </div>
    
    <!-- History Panel -->
    <div v-if="showHistory" class="history-panel">
      <div class="history-header">
        <div class="history-title">
          <History :size="20" />
          <h2>Modification History</h2>
        </div>
        <button class="close-history-btn" @click="showHistory = false">
          <X :size="20" />
        </button>
      </div>
      
      <div class="history-content">
        <div v-if="history.length === 0" class="history-empty">
          <History :size="48" />
          <p>No history yet</p>
        </div>
        
        <div v-else class="history-timeline">
          <div 
            v-for="entry in history" 
            :key="entry.id" 
            class="history-entry"
          >
            <div class="history-icon" :style="{ background: getActionColor(entry.action) + '20', color: getActionColor(entry.action) }">
              <component :is="getActionIcon(entry.action)" :size="16" />
            </div>
            <div class="history-details">
              <div class="history-action">{{ entry.action }}</div>
              <div class="history-description">{{ entry.details }}</div>
              <div class="history-meta">
                <span class="history-time">{{ formatTime(entry.timestamp) }}</span>
                <span class="history-count">{{ entry.annotationCount }} annotations</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main Canvas Area -->
    <div class="annotation-main">
      <div class="main-header">
        <button class="back-btn" @click="handleClose">
          <ArrowLeft :size="20" />
          <span>Back to Gallery</span>
        </button>
        <div class="image-info">
          <h2>Image #{{ image.id }}</h2>
          <span class="image-meta">{{ image.type }} | Active tool: {{ activeTool }}</span>
        </div>
      </div>
      
      <div class="canvas-container">
        <canvas 
          ref="canvas"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @mouseleave="stopDrawing"
        ></canvas>
      </div>
    </div>
  </div>
</template>

<style scoped>
.annotation-page {
  display: flex;
  height: 100vh;
  background: #f5f6fa;
}

/* Sidebar */
.annotation-sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #e1e8ed;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.annotation-count {
  background: #3498db;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

/* Tools Section */
.tools-section {
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.tools-section h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tool-buttons {
  display: flex;
  gap: 8px;
}

.tool-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border: 2px solid #e1e8ed;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #2c3e50;
}

.tool-btn:hover {
  border-color: #3498db;
  background: #f8f9fa;
}

.tool-btn.active {
  border-color: #3498db;
  background: #3498db;
  color: white;
}

.tool-btn span {
  font-size: 12px;
  font-weight: 600;
}

/* Annotations List */
.annotations-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.annotations-list h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #95a5a6;
}

.empty-state p {
  margin: 0 0 8px 0;
}

.empty-state .hint {
  font-size: 12px;
  color: #bdc3c7;
}

.annotation-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.annotation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
  transition: all 0.2s;
}

.annotation-item:hover {
  background: #ecf0f1;
  border-color: #bdc3c7;
}

.annotation-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.annotation-type {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 14px;
}

.annotation-coords {
  font-size: 11px;
  color: #7f8c8d;
  font-family: 'Courier New', monospace;
}

.delete-btn {
  padding: 6px;
  border: none;
  background: transparent;
  color: #cfc9c8;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: #e74c3c;
  color: white;
}

/* Action Buttons */
.action-buttons {
  padding: 20px;
  border-top: 1px solid #e1e8ed;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.save-btn {
  background: #3498db;
  color: white;
}

.save-btn:hover {
  background: #2980b9;
}

.approve-btn {
  background: #27ae60;
  color: white;
}

.approve-btn:hover {
  background: #229954;
}

.clear-btn {
  background: #e74c3c;
  color: white;
}

.clear-btn:hover {
  background: #c0392b;
}

.history-btn {
  background: #9b59b6;
  color: white;
}

.history-btn:hover {
  background: #8e44ad;
}

/* History Panel */
.history-panel {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  height: 100vh;
  background: white;
  border-left: 1px solid #e1e8ed;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.history-header {
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #2c3e50;
}

.history-title h2 {
  margin: 0;
  font-size: 18px;
}

.close-history-btn {
  padding: 8px;
  border: none;
  background: transparent;
  color: #7f8c8d;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-history-btn:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.history-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #bdc3c7;
  text-align: center;
}

.history-empty p {
  margin: 16px 0 0 0;
  font-size: 14px;
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-entry {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.history-entry:hover {
  background: #ecf0f1;
  transform: translateX(4px);
}

.history-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.history-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-action {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  text-transform: capitalize;
}

.history-description {
  font-size: 13px;
  color: #7f8c8d;
  line-height: 1.4;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.history-time {
  font-size: 11px;
  color: #95a5a6;
}

.history-count {
  font-size: 11px;
  color: #95a5a6;
  padding: 2px 8px;
  background: white;
  border-radius: 10px;
}

/* Main Area */
.annotation-main {
  background: #ffffff;
  color: white;
}

.clear-btn:hover {
  background: #c0392b;
}

/* Main Area */
.annotation-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-header {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #e1e8ed;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f8f9fa;
  border-color: #bdc3c7;
}

.image-info h2 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #2c3e50;
}

.image-meta {
  font-size: 13px;
  color: #7f8c8d;
}

.canvas-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: auto;
}

canvas {
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  cursor: crosshair;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: white;
}
</style>
