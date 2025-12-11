<script setup>
import { ref, onMounted } from 'vue'
import { Filter, X, Calendar, Tag, User, CheckSquare, ChevronDown } from 'lucide-vue-next'
import { useApi } from '../composables/useApi'

const props = defineProps({
  projectId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['applyFilters'])
const api = useApi()

const selectedDateRange = ref('all')
const selectedStatus = ref([])
const selectedTags = ref([])
const selectedUsers = ref([])

const showDateRange = ref(false)
const showStatus = ref(false)
const showTags = ref(false)
const showUsers = ref(false)

const tags = ref([])
const users = ref([])

const dateRanges = [
  { value: 'all', label: 'All Time' },
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'custom', label: 'Custom Range' }
]

const statuses = [
  { value: 'to review', label: 'To Review', color: 'blue' },
  { value: 'human annotation', label: 'Human Annotation', color: 'purple' },
  { value: 'ml annotation', label: 'ML Annotation', color: 'amber' },
  { value: 'certified', label: 'Certified', color: 'green' },
  { value: 'rejected', label: 'Rejected', color: 'red' }
]

const fetchTags = async () => {
  try {
    const annotations = await api.get(`/annotations/?project_id=${props.projectId}`)
    // Extract unique tags from annotations
    const uniqueTags = new Set()
    annotations.forEach(annotation => {
      if (annotation.label) {
        uniqueTags.add(annotation.label)
      }
    })
    tags.value = Array.from(uniqueTags).sort()
  } catch (error) {
    console.error('Error fetching tags:', error)
  }
}

const fetchUsers = async () => {
  try {
    if (!props.projectId) return
    
    const projectUsers = await api.get(`/projects/${props.projectId}/users`)
    users.value = projectUsers
  } catch (error) {
    console.error('Error fetching users:', error)
  }
}

onMounted(async () => {
  await fetchTags()
  await fetchUsers()
})

const toggleStatus = (status) => {
  const index = selectedStatus.value.indexOf(status)
  if (index > -1) {
    selectedStatus.value.splice(index, 1)
  } else {
    selectedStatus.value.push(status)
  }
}

const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tag)
  }
}

const toggleUser = (userId) => {
  const index = selectedUsers.value.indexOf(userId)
  if (index > -1) {
    selectedUsers.value.splice(index, 1)
  } else {
    selectedUsers.value.push(userId)
  }
}

const clearAllFilters = () => {
  selectedDateRange.value = 'all'
  selectedStatus.value = []
  selectedTags.value = []
  selectedUsers.value = []
}

const applyFilters = () => {
  // Emit filters to parent component
  emit('applyFilters', {
    dateRange: selectedDateRange.value,
    status: selectedStatus.value,
    tags: selectedTags.value,
    users: selectedUsers.value
  })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold">Filters</h2>
      <button 
        @click="clearAllFilters"
        class="text-sm text-gray-500 hover:text-gray-700 font-medium"
      >
        Clear All
      </button>
    </div>
    
    <div class="space-y-6">
      <!-- Date Range Filter -->
      <div>
        <button
          @click="showDateRange = !showDateRange"
          class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <Calendar :size="18" class="text-gray-600" />
            <h3 class="font-semibold text-gray-900">Date Range</h3>
          </div>
          <ChevronDown 
            :size="18" 
            class="text-gray-400 transition-transform"
            :class="{ 'rotate-180': showDateRange }"
          />
        </button>
        <div v-if="showDateRange" class="mt-2 space-y-2">
          <label 
            v-for="range in dateRanges" 
            :key="range.value"
            class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <input 
              type="radio" 
              v-model="selectedDateRange" 
              :value="range.value"
              class="w-4 h-4 text-blue-600"
            />
            <span class="text-gray-700">{{ range.label }}</span>
          </label>
        </div>
      </div>

      <!-- Status Filter -->
      <div>
        <button
          @click="showStatus = !showStatus"
          class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <CheckSquare :size="18" class="text-gray-600" />
            <h3 class="font-semibold text-gray-900">Status</h3>
            <span v-if="selectedStatus.length > 0" class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              {{ selectedStatus.length }}
            </span>
          </div>
          <ChevronDown 
            :size="18" 
            class="text-gray-400 transition-transform"
            :class="{ 'rotate-180': showStatus }"
          />
        </button>
        <div v-if="showStatus" class="mt-2 space-y-2">
          <label 
            v-for="status in statuses" 
            :key="status.value"
            class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <input 
              type="checkbox" 
              :checked="selectedStatus.includes(status.value)"
              @change="toggleStatus(status.value)"
              class="w-4 h-4 rounded text-blue-600"
            />
            <span 
              :class="[
                'w-3 h-3 rounded-full',
                status.color === 'green' ? 'bg-green-500' :
                status.color === 'blue' ? 'bg-blue-500' :
                status.color === 'purple' ? 'bg-purple-500' :
                status.color === 'amber' ? 'bg-amber-400' :
                status.color === 'red' ? 'bg-red-500' :
                'bg-gray-400'
              ]"
            ></span>
            <span class="text-gray-700">{{ status.label }}</span>
          </label>
        </div>
      </div>

      <!-- Tags Filter -->
      <div>
        <button
          @click="showTags = !showTags"
          class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <Tag :size="18" class="text-gray-600" />
            <h3 class="font-semibold text-gray-900">Tags</h3>
            <span v-if="selectedTags.length > 0" class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              {{ selectedTags.length }}
            </span>
          </div>
          <ChevronDown 
            :size="18" 
            class="text-gray-400 transition-transform"
            :class="{ 'rotate-180': showTags }"
          />
        </button>
        <div v-if="showTags" class="mt-2 flex flex-wrap gap-2">
          <div v-if="tags.length === 0" class="text-sm text-gray-500 p-3">
            No tags found in annotations
          </div>
          <button
            v-for="tag in tags"
            :key="tag"
            @click="toggleTag(tag)"
            :class="[
              'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
              selectedTags.includes(tag)
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- Users Filter -->
      <div>
        <button
          @click="showUsers = !showUsers"
          class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <User :size="18" class="text-gray-600" />
            <h3 class="font-semibold text-gray-900">Annotators</h3>
            <span v-if="selectedUsers.length > 0" class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              {{ selectedUsers.length }}
            </span>
          </div>
          <ChevronDown 
            :size="18" 
            class="text-gray-400 transition-transform"
            :class="{ 'rotate-180': showUsers }"
          />
        </button>
        <div v-if="showUsers" class="mt-2 space-y-2">
          <label 
            v-for="annotator in users" 
            :key="annotator.id"
            class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <input 
              type="checkbox" 
              :checked="selectedUsers.includes(annotator.id)"
              @change="toggleUser(annotator.id)"
              class="w-4 h-4 rounded text-blue-600"
            />
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 text-white flex items-center justify-center text-sm font-semibold">
              {{ annotator.name.split(' ').map(n => n[0]).join('') }}
            </div>
            <span class="text-gray-700">{{ annotator.name }}</span>
          </label>
        </div>
      </div>

      <!-- Apply Button -->
      <button 
        @click="applyFilters"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Filter :size="18" />
        <span>Apply Filters</span>
      </button>
    </div>
  </div>
</template>
