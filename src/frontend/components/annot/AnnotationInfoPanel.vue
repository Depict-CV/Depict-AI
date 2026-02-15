<script setup lang="ts">
import ImageAdjustments from './ImageAdjustments.vue'

interface Props {
  zoomLevel: number
  brightness: number
  contrast: number
  redChannel: number
  greenChannel: number
  blueChannel: number
  saturation: number
  hue: number
  selectedShape: any
  getLabelColor: (label: string) => string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  resetZoom: []
  'update:brightness': [value: number]
  'update:contrast': [value: number]
  'update:redChannel': [value: number]
  'update:greenChannel': [value: number]
  'update:blueChannel': [value: number]
  'update:saturation': [value: number]
  'update:hue': [value: number]
  resetFilters: []
}>()
</script>

<template>
  <div class="absolute top-4 right-4 space-y-4 z-10">
    <!-- Zoom Indicator -->
    <div class="bg-white rounded-lg shadow-lg p-3">
      <div class="text-xs font-medium text-gray-600 mb-1">Zoom</div>
      <div class="text-lg font-bold text-gray-800">{{ Math.round(zoomLevel * 100) }}%</div>
      <button
        @click="emit('resetZoom')"
        class="mt-2 w-full px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs font-medium transition-colors"
        title="Reset Zoom (100%)"
      >
        Reset
      </button>
    </div>

    <!-- Image Adjustments -->
    <ImageAdjustments
      :brightness="brightness"
      :contrast="contrast"
      :redChannel="redChannel"
      :greenChannel="greenChannel"
      :blueChannel="blueChannel"
      :saturation="saturation"
      :hue="hue"
      @update:brightness="emit('update:brightness', $event)"
      @update:contrast="emit('update:contrast', $event)"
      @update:redChannel="emit('update:redChannel', $event)"
      @update:greenChannel="emit('update:greenChannel', $event)"
      @update:blueChannel="emit('update:blueChannel', $event)"
      @update:saturation="emit('update:saturation', $event)"
      @update:hue="emit('update:hue', $event)"
      @reset="emit('resetFilters')"
    />

    <!-- Shape Info -->
    <div v-if="selectedShape" class="bg-white rounded-lg shadow-lg p-3">
      <div class="text-xs font-medium text-gray-600 mb-2">Selected</div>
      <div class="space-y-1 text-xs text-gray-700">
        <div><span class="font-medium">Type:</span> {{ selectedShape.metadata?.type || 'N/A' }}</div>
        <div><span class="font-medium">Label:</span> {{ selectedShape.metadata?.label || 'None' }}</div>
        <div v-if="selectedShape.attrs?.width">
          <span class="font-medium">Size:</span> {{ Math.round(selectedShape.attrs.width) }}×{{
            Math.round(selectedShape.attrs.height)
          }}
        </div>
      </div>
      <div
        v-if="selectedShape.metadata?.label"
        class="mt-2 w-full h-2 rounded"
        :style="{ backgroundColor: getLabelColor(selectedShape.metadata.label) }"
      ></div>
    </div>
  </div>
</template>
