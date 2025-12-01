<script setup>
import { Upload, ChevronLeft, ChevronRight } from 'lucide-vue-next';
</script>

<template>
  <div class="upload-panel">
    <button class="panel-button primary">
      <Upload :size="20" />
      Upload
    </button>
    <div class="nav-buttons">
      <button class="panel-button">
        <ChevronLeft :size="20" />
        Prev
      </button>
      <button class="panel-button">
        <ChevronRight :size="20" />
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
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
</style>
