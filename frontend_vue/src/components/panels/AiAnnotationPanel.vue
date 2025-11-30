<script setup>
import { ref } from 'vue';
import { Cpu, Sparkles, Settings, Zap, AlertCircle } from 'lucide-vue-next';

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
  alert(`Starting AI annotation with ${activeModel?.name}...`);
};
</script>

<template>
  <div class="ai-panel">
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
</template>

<style scoped>
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

.panel-button.primary {
  background: #3498db;
  color: white;
  border-color: #3498db;
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
