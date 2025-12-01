<script setup>
import GalleryPanel from './panels/GalleryPanel.vue';
import UploadPanel from './panels/UploadPanel.vue';
import ProjectsPanel from './panels/ProjectsPanel.vue';
import FilterPanel from './panels/FilterPanel.vue';
import StatisticsPanel from './panels/StatisticsPanel.vue';
import AiAnnotationPanel from './panels/AiAnnotationPanel.vue';

defineProps({
  activeMenu: {
    type: String,
    required: true
  }
});
</script>

<template>
  <aside class="nav-panel">
    <div class="nav-panel-header">
      <h3>{{ activeMenu.charAt(0).toUpperCase() + activeMenu.slice(1) }}</h3>
    </div>
    
    <div class="nav-panel-content">
      <!-- Gallery Panel -->
      <GalleryPanel v-if="activeMenu === 'gallery'" />
      
      <!-- Upload Panel -->
      <UploadPanel v-if="activeMenu === 'upload'" />
      
      <!-- Projects Panel -->
      <ProjectsPanel v-if="activeMenu === 'projects'" />
      
      <!-- Filter Panel -->
      <FilterPanel v-if="activeMenu === 'filter'" />
      
      <!-- Statistics Panel -->
      <StatisticsPanel v-if="activeMenu === 'statistics'" />
      
      <!-- AI Annotation Panel -->
      <AiAnnotationPanel v-if="activeMenu === 'ai-annotation'" />
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
