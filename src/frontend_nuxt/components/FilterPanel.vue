<script setup>
import { ref } from 'vue'
import { Filter, X, Calendar, Tag, User, CheckSquare } from 'lucide-vue-next'

const selectedDateRange = ref('all')
const selectedStatus = ref([])
const selectedTags = ref([])
const selectedUsers = ref([])

const dateRanges = [
  { value: 'all', label: 'All Time' },
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'custom', label: 'Custom Range' }
]

const statuses = [
  { value: 'annotated', label: 'Annotated', color: 'green' },
  { value: 'in-progress', label: 'In Progress', color: 'yellow' },
  { value: 'pending', label: 'Pending', color: 'gray' },
  { value: 'reviewed', label: 'Reviewed', color: 'blue' }
]

const tags = [
  'vehicle', 'person', 'animal', 'building', 'outdoor', 'indoor'
]

const users = [
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
  { id: 3, name: 'Bob Johnson' }
]

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
  // TODO: Implement filter logic with API
  console.log('Applying filters:', {
    dateRange: selectedDateRange.value,
    status: selectedStatus.value,
    tags: selectedTags.value,
    users: selectedUsers.value
  })
  alert('Filters applied!')
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
        <div class="flex items-center gap-2 mb-3">
          <Calendar :size="18" class="text-gray-600" />
          <h3 class="font-semibold text-gray-900">Date Range</h3>
        </div>
        <div class="space-y-2">
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
      <div class="pb-6 border-b border-gray-200">
        <div class="flex items-center gap-2 mb-3">
          <CheckSquare :size="18" class="text-gray-600" />
          <h3 class="font-semibold text-gray-900">Status</h3>
        </div>
        <div class="space-y-2">
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
                status.color === 'yellow' ? 'bg-yellow-500' :
                status.color === 'blue' ? 'bg-blue-500' :
                'bg-gray-400'
              ]"
            ></span>
            <span class="text-gray-700">{{ status.label }}</span>
          </label>
        </div>
      </div>

      <!-- Tags Filter -->
      <div class="pb-6 border-b border-gray-200">
        <div class="flex items-center gap-2 mb-3">
          <Tag :size="18" class="text-gray-600" />
          <h3 class="font-semibold text-gray-900">Tags</h3>
        </div>
        <div class="flex flex-wrap gap-2">
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
        <div class="flex items-center gap-2 mb-3">
          <User :size="18" class="text-gray-600" />
          <h3 class="font-semibold text-gray-900">Annotators</h3>
        </div>
        <div class="space-y-2">
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
