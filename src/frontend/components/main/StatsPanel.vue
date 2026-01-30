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
  <div class="p-5">
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

    <div v-if="!projectId" class="flex flex-col items-center justify-center p-20 text-center">
      <Database :size="48" class="text-gray-300 mb-3" />
      <p class="text-gray-500 text-lg">Please select a project to view statistics</p>
    </div>

    <div v-else-if="loading" class="flex flex-col items-center justify-center p-20 gap-4">
      <div class="border-4 border-gray-200 border-t-blue-500 rounded-full w-10 h-10 animate-spin"></div>
      <p class="text-gray-600">Loading statistics...</p>
    </div>

    <div v-else>
      <!-- Overview Cards -->
      <div class="flex flex-col gap-1 mb-6">
        <div
          class="flex items-center gap-4 p-1 bg-white rounded-lg shadow hover:shadow-md hover:-translate-y-0.5 transition-all"
        >
          <div class="flex items-center justify-center w-6 h-6 rounded-lg bg-blue-100 text-blue-600 flex-shrink-0">
            <ImageIcon :size="15" />
          </div>
          <div>
            <p class="text-sm text-gray-600 mb-1">Total Images</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalImages }}</p>
          </div>
        </div>

        <div
          class="flex items-center gap-4 p-1 bg-white rounded-lg shadow hover:shadow-md hover:-translate-y-0.5 transition-all"
        >
          <div class="flex items-center justify-center w-6 h-6 rounded-lg bg-green-100 text-green-600 flex-shrink-0">
            <CheckCircle :size="15" />
          </div>
          <div>
            <p class="text-sm text-gray-600 mb-1">Annotated</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.annotatedImages }}</p>
          </div>
        </div>

        <div
          class="flex items-center gap-4 p-1 bg-white rounded-lg shadow hover:shadow-md hover:-translate-y-0.5 transition-all"
        >
          <div class="flex items-center justify-center w-6 h-6 rounded-lg bg-amber-100 text-amber-600 flex-shrink-0">
            <Clock :size="15" />
          </div>
          <div>
            <p class="text-sm text-gray-600 mb-1">Pending</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.pendingImages }}</p>
          </div>
        </div>

        <div
          class="flex items-center gap-4 p-1 bg-white rounded-lg shadow hover:shadow-md hover:-translate-y-0.5 transition-all"
        >
          <div class="flex items-center justify-center w-6 h-6 rounded-lg bg-purple-100 text-purple-600 flex-shrink-0">
            <Tag :size="15" />
          </div>
          <div>
            <p class="text-sm text-gray-600 mb-1">Annotations</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalAnnotations }}</p>
          </div>
        </div>
      </div>

      <!-- Completion Progress -->
      <div class="p-6 bg-white rounded-lg shadow mb-6">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-gray-800">Completion Progress</h3>
          <span class="text-2xl font-bold text-blue-600">{{ stats.completionRate }}%</span>
        </div>
        <div class="w-full h-6 bg-gray-200 rounded-lg overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg transition-all duration-500"
            :style="{ width: stats.completionRate + '%' }"
          ></div>
        </div>
        <div class="flex justify-between text-sm text-gray-600 mt-2">
          <span>{{ stats.annotatedImages }} / {{ stats.totalImages }} images annotated</span>
          <span>{{ stats.pendingImages }} remaining</span>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="flex flex-col gap-6 mb-6">
        <!-- Annotations by Type -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h3 class="text-lg font-semibold text-gray-900 mb-5">Annotations by Status</h3>
          <div
            v-if="Object.keys(stats.annotationsByType).length === 0"
            class="flex flex-col items-center justify-center p-10 text-center"
          >
            <AlertCircle :size="32" class="text-gray-300 mb-2" />
            <p class="text-gray-400 text-sm">No annotations yet</p>
          </div>
          <div v-else class="flex flex-col gap-4">
            <div v-for="(count, type) in stats.annotationsByType" :key="type">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-semibold text-gray-700 capitalize">{{ type }}</span>
                <span class="text-sm font-bold text-gray-600">{{ count }}</span>
              </div>
              <div class="w-full h-2 bg-gray-200 rounded overflow-hidden">
                <div
                  class="h-full bg-blue-500 rounded transition-all duration-500"
                  :style="{
                    width: (count / stats.totalAnnotations) * 100 + '%',
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Annotations by Label -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h3 class="text-lg font-semibold text-gray-900 mb-5">Annotations by Label</h3>
          <div
            v-if="Object.keys(stats.annotationsByLabel).length === 0"
            class="flex flex-col items-center justify-center p-10 text-center"
          >
            <AlertCircle :size="32" class="text-gray-300 mb-2" />
            <p class="text-gray-400 text-sm">No labels assigned</p>
          </div>
          <div v-else class="flex flex-col gap-4">
            <div v-for="(count, label) in stats.annotationsByLabel" :key="label">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-semibold text-gray-700 capitalize">{{ label }}</span>
                <span class="text-sm font-bold text-gray-600">{{ count }}</span>
              </div>
              <div class="w-full h-2 bg-gray-200 rounded overflow-hidden">
                <div
                  class="h-full bg-green-500 rounded transition-all duration-500"
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
      <div class="p-6 bg-white rounded-lg shadow">
        <h3 class="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-5">
          <Calendar :size="20" />
          <span>Recent Activity</span>
        </h3>
        <div
          v-if="stats.recentActivity.length === 0"
          class="flex flex-col items-center justify-center p-10 text-center"
        >
          <Clock :size="32" class="text-gray-300 mb-2" />
          <p class="text-gray-400 text-sm">No recent activity</p>
        </div>
        <div v-else class="flex flex-col gap-4">
          <div
            v-for="activity in stats.recentActivity"
            :key="activity.id"
            class="flex gap-4 p-4 bg-gray-50 rounded border-l-4 border-blue-600 hover:bg-gray-100 hover:translate-x-1 transition-all"
          >
            <div class="w-3 h-3 bg-blue-600 rounded-full flex-shrink-0 mt-1"></div>
            <div class="flex flex-col gap-2">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-sm font-semibold text-gray-900 capitalize">{{
                  activity.annotation_type || 'Annotation'
                }}</span>
                <span v-if="activity.label" class="text-xs font-semibold px-2 py-1 bg-blue-100 text-blue-900 rounded">{{
                  activity.label
                }}</span>
              </div>
              <div class="flex items-center gap-3 text-xs">
                <span
                  class="font-semibold px-2 py-1 rounded uppercase"
                  :class="{
                    'bg-yellow-100 text-yellow-900': activity.status === 'PENDING',
                    'bg-green-100 text-green-900': activity.status === 'APPROVED',
                    'bg-indigo-100 text-indigo-900': activity.status === 'ML_ANNOTATION',
                  }"
                >
                  {{ activity.status || 'PENDING' }}
                </span>
                <span class="text-gray-600">{{ formatDate(activity.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
