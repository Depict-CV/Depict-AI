<script setup>
import { ref, onMounted, watch } from 'vue'
import {
  Image as ImageIcon,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  Database,
  Tag,
  Calendar,
} from 'lucide-vue-next'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const api = useApi()
const loading = ref(false)
const stats = ref({
  totalImages: 0,
  annotatedImages: 0,
  pendingImages: 0,
  approvedImages: 0,
  totalAnnotations: 0,
  annotationsByType: {},
  annotationsByLabel: {},
  recentActivity: [],
  completionRate: 0,
})

const fetchStats = async () => {
  if (!props.projectId) return

  loading.value = true
  try {
    // Use the new statistics endpoint
    const statistics = await api.get(`/projects/${props.projectId}/statistics`)

    // Update stats with response
    stats.value.totalImages = statistics.total_images
    stats.value.totalAnnotations = statistics.total_annotations
    stats.value.annotatedImages = statistics.annotated_images
    stats.value.pendingImages = statistics.pending_images
    stats.value.completionRate = statistics.completion_rate

    // Annotations by status
    stats.value.annotationsByType = statistics.by_status || {}

    // Annotations by label
    stats.value.annotationsByLabel = statistics.by_label || {}

    // Recent activity
    stats.value.recentActivity = statistics.recent_activity || []
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  } finally {
    loading.value = false
  }
}

// Watch for projectId changes
watch(
  () => props.projectId,
  (newId) => {
    if (newId) {
      fetchStats()
    }
  }
)

onMounted(() => {
  if (props.projectId) {
    fetchStats()
  }
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString()
}
</script>

<template>
  <div class="stats-panel">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Project Statistics</h2>
      <button
        @click="fetchStats"
        :disabled="!projectId || loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
      >
        <TrendingUp :size="18" />
        <span>Refresh</span>
      </button>
    </div>

    <div v-if="!projectId" class="empty-state">
      <Database :size="48" class="text-gray-300 mb-3" />
      <p class="text-gray-500 text-lg">Please select a project to view statistics</p>
    </div>

    <div v-else-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p class="text-gray-600">Loading statistics...</p>
    </div>

    <div v-else class="stats-content">
      <!-- Overview Cards -->
      <div class="flex flex-col gap-1 mb-6">
        <div class="stat-card">
          <div class="stat-icon bg-blue-100 text-blue-600">
            <ImageIcon :size="15" />
          </div>
          <div class="stat-info">
            <p class="stat-label">Total Images</p>
            <p class="stat-value">{{ stats.totalImages }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-green-100 text-green-600">
            <CheckCircle :size="15" />
          </div>
          <div class="stat-info">
            <p class="stat-label">Annotated</p>
            <p class="stat-value">{{ stats.annotatedImages }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-amber-100 text-amber-600">
            <Clock :size="15" />
          </div>
          <div class="stat-info">
            <p class="stat-label">Pending</p>
            <p class="stat-value">{{ stats.pendingImages }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-purple-100 text-purple-600">
            <Tag :size="15" />
          </div>
          <div class="stat-info">
            <p class="stat-label">Annotations</p>
            <p class="stat-value">{{ stats.totalAnnotations }}</p>
          </div>
        </div>
      </div>

      <!-- Completion Progress -->
      <div class="progress-card mb-6">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-gray-800">Completion Progress</h3>
          <span class="text-2xl font-bold text-blue-600">{{ stats.completionRate }}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: stats.completionRate + '%' }"></div>
        </div>
        <div class="flex justify-between text-sm text-gray-600 mt-2">
          <span>{{ stats.annotatedImages }} / {{ stats.totalImages }} images annotated</span>
          <span>{{ stats.pendingImages }} remaining</span>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="flex flex-col gap-6 mb-6">
        <!-- Annotations by Type -->
        <div class="chart-card">
          <h3 class="chart-title">Annotations by Status</h3>
          <div v-if="Object.keys(stats.annotationsByType).length === 0" class="empty-chart">
            <AlertCircle :size="32" class="text-gray-300 mb-2" />
            <p class="text-gray-400 text-sm">No annotations yet</p>
          </div>
          <div v-else class="chart-content">
            <div v-for="(count, type) in stats.annotationsByType" :key="type" class="chart-item">
              <div class="flex items-center justify-between mb-2">
                <span class="chart-label">{{ type }}</span>
                <span class="chart-value">{{ count }}</span>
              </div>
              <div class="chart-bar-container">
                <div
                  class="chart-bar bg-blue-500"
                  :style="{
                    width: (count / stats.totalAnnotations) * 100 + '%',
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Annotations by Label -->
        <div class="chart-card">
          <h3 class="chart-title">Annotations by Label</h3>
          <div v-if="Object.keys(stats.annotationsByLabel).length === 0" class="empty-chart">
            <AlertCircle :size="32" class="text-gray-300 mb-2" />
            <p class="text-gray-400 text-sm">No labels assigned</p>
          </div>
          <div v-else class="chart-content">
            <div v-for="(count, label) in stats.annotationsByLabel" :key="label" class="chart-item">
              <div class="flex items-center justify-between mb-2">
                <span class="chart-label">{{ label }}</span>
                <span class="chart-value">{{ count }}</span>
              </div>
              <div class="chart-bar-container">
                <div
                  class="chart-bar bg-green-500"
                  :style="{
                    width: (count / stats.totalAnnotations) * 100 + '%',
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="activity-card">
        <h3 class="activity-title">
          <Calendar :size="20" />
          <span>Recent Activity</span>
        </h3>
        <div v-if="stats.recentActivity.length === 0" class="empty-activity">
          <Clock :size="32" class="text-gray-300 mb-2" />
          <p class="text-gray-400 text-sm">No recent activity</p>
        </div>
        <div v-else class="activity-list">
          <div v-for="activity in stats.recentActivity" :key="activity.id" class="activity-item">
            <div class="activity-indicator"></div>
            <div class="activity-content">
              <div class="activity-header">
                <span class="activity-type">{{ activity.annotation_type || 'Annotation' }}</span>
                <span v-if="activity.label" class="activity-label">{{ activity.label }}</span>
              </div>
              <div class="activity-meta">
                <span
                  class="activity-status"
                  :class="{
                    'status-pending': activity.status === 'PENDING',
                    'status-approved': activity.status === 'APPROVED',
                    'status-ml': activity.status === 'ML_ANNOTATION',
                  }"
                >
                  {{ activity.status || 'PENDING' }}
                </span>
                <span class="activity-time">{{ formatDate(activity.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-panel {
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.spinner {
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Stat Cards */
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 5px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 25px;
  height: 25px;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

/* Progress Card */
.progress-card {
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-bar-container {
  width: 100%;
  height: 24px;
  background: #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  transition: width 0.5s ease;
  border-radius: 12px;
}

/* Chart Cards */
.chart-card {
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.empty-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.chart-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-item {
  /* No additional styles needed */
}

.chart-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  text-transform: capitalize;
}

.chart-value {
  font-size: 14px;
  font-weight: 700;
  color: #6b7280;
}

.chart-bar-container {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.chart-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* Activity Card */
.activity-card {
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.activity-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.empty-activity {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
  transition: all 0.2s;
}

.activity-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.activity-indicator {
  width: 12px;
  height: 12px;
  background: #3b82f6;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.activity-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.activity-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.activity-type {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  text-transform: capitalize;
}

.activity-label {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.activity-status {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-approved {
  background: #d1fae5;
  color: #065f46;
}

.status-ml {
  background: #e0e7ff;
  color: #3730a3;
}

.activity-time {
  color: #6b7280;
}
</style>
