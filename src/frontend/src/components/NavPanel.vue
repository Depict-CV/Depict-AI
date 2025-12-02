<script setup>
import { computed } from 'vue';
import ImportExportPanel from './panels/ImportExportPanel.vue';
import ProjectsPanel from './panels/ProjectsPanel.vue';
import FilterPanel from './panels/FilterPanel.vue';
import StatisticsPanel from './panels/StatisticsPanel.vue';
import AiAnnotationPanel from './panels/AiAnnotationPanel.vue';

const props = defineProps({
  activeMenu: {
    type: String,
    required: true
  }
});

const panelTitle = computed(() => {
  const titles = {
    'ArrowRightLeft': 'Import / Export',
    'projects': 'Projects',
    'filter': 'Filter',
    'statistics': 'Statistics',
    'ai-annotation': 'AI Annotation',
    'gallery': 'Gallery'
  };
  return titles[props.activeMenu] || props.activeMenu.charAt(0).toUpperCase() + props.activeMenu.slice(1);
});
</script>

<template>
  <aside class="nav-panel">
    <div class="nav-panel-header">
      <h3>{{ panelTitle }}</h3>
    </div>
    
    <div class="nav-panel-content">  
      <!-- Projects Panel -->
      <ProjectsPanel v-if="activeMenu === 'projects'" />

      <!-- Upload/Export Panel -->
      <ImportExportPanel v-if="activeMenu === 'import_export'" />

      <!-- AI Annotation Panel -->
      <AiAnnotationPanel v-if="activeMenu === 'ai-annotation'" />
      
      <!-- Filter Panel -->
      <FilterPanel v-if="activeMenu === 'filter'" />
      
      <!-- Statistics Panel -->
      <StatisticsPanel v-if="activeMenu === 'statistics'" />
    </div>
  </aside>
</template>

<style scoped>
/* Nav Panel Container - child components handle their own styling */
.nav-panel {
  position: fixed;
  left: 60px;
  top: 0;
  width: 240px;
  height: 100vh;
  background: var(--color-background, #f8f9fa);
  border-right: 1px solid var(--color-border, #e0e0e0);
  padding: var(--spacing-lg, 20px);
  overflow-y: auto;
  box-shadow: var(--shadow-md, 2px 0 10px rgba(0, 0, 0, 0.05));
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
  margin-bottom: var(--spacing-lg, 20px);
  padding-bottom: var(--spacing-sm, 10px);
  border-bottom: 2px solid var(--color-border, #e0e0e0);
}

.nav-panel-header h3 {
  margin: 0;
  font-size: var(--font-size-xl, 20px);
  color: var(--color-text-primary, #2c3e50);
  text-transform: capitalize;
}

.nav-panel-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md, 15px);
}
</style>
