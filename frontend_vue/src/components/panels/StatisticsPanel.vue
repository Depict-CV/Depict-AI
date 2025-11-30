<script setup>
import { ref } from 'vue';
import { ImageIcon, CheckSquare, XSquare, TrendingUp, Clock, Edit, Trash2, Tag, BarChart, Users, Calendar } from 'lucide-vue-next';

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
</script>

<template>
  <div class="stats-panel">
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
</template>

<style scoped>
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
</style>
