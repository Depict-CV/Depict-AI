<script setup>
import { ref } from 'vue';
import { Tag, CheckSquare, XSquare, ImageIcon, Clock } from 'lucide-vue-next';

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
</script>

<template>
  <div class="filter-panel">
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
</template>

<style scoped>
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
</style>
