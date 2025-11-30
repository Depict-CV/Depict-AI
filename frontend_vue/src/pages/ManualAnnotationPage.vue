<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { Square, Circle, Save, Check, X, ArrowLeft, Trash2 } from 'lucide-vue-next';

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

// Canvas dimensions
const canvasWidth = ref(0);
const canvasHeight = ref(0);

// Initialize canvas
onMounted(() => {
  if (canvas.value) {
    ctx.value = canvas.value.getContext('2d');
    // Wait for image to load
    const img = new Image();
    img.onload = () => {
      setupCanvas(img);
    };
    img.src = props.image.location;
  }
});

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
  annotations.value = annotations.value.filter(ann => ann.id !== id);
  redrawCanvas();
};

const clearAllAnnotations = () => {
  annotations.value = [];
  redrawCanvas();
};

const saveAnnotations = () => {
  console.log('Saving annotations:', annotations.value);
  // TODO: Implement API call to save annotations
  alert('Annotations saved! (Currently console.log only)');
};

const approveAnnotations = () => {
  console.log('Approving annotations:', annotations.value);
  // TODO: Implement API call to approve annotations
  alert('Annotations approved! (Currently console.log only)');
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
  color: #e74c3c;
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
