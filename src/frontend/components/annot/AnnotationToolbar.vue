<script setup lang="ts">
import { Hand, MousePointer, Square, Pentagon, User, Brush, Undo, Redo, Copy, Download, Trash2 } from 'lucide-vue-next'

interface Props {
  drawingMode: string
  isDrawingPolygon: boolean
  currentSkeleton: any
  canUndo: boolean
  canRedo: boolean
  selectedShape: any
  shapesCount: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  setMode: [mode: string]
  undo: []
  redo: []
  copy: []
  export: []
  deleteSelected: []
  clearMasks: []
  clearAll: []
  finishSkeleton: []
  cancelSkeleton: []
}>()
</script>

<template>
  <div class="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-4 space-y-3 z-10 max-w-xs">
    <div class="font-bold text-sm text-gray-700 mb-2 border-b pb-2">Annotation Tools</div>

    <!-- Mode Buttons -->
    <div class="grid grid-cols-2 gap-2">
      <button
        @click="emit('setMode', 'pan')"
        :class="[
          'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
          drawingMode === 'pan' ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        ]"
        title="Pan Mode (P) - Drag to move image"
      >
        <Hand :size="18" />
        <span>Pan</span>
      </button>
      <button
        @click="emit('setMode', 'select')"
        :class="[
          'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
          drawingMode === 'select' ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        ]"
        title="Select Mode (S) - Click to select shapes"
      >
        <MousePointer :size="18" />
        <span>Select</span>
      </button>
      <button
        @click="emit('setMode', 'rectangle')"
        :class="[
          'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
          drawingMode === 'rectangle'
            ? 'bg-blue-500 text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        ]"
        title="Rectangle Mode (R) - Draw bounding boxes"
      >
        <Square :size="18" />
        <span>Box</span>
      </button>
      <button
        @click="emit('setMode', 'polygon')"
        :class="[
          'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
          drawingMode === 'polygon'
            ? 'bg-blue-500 text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        ]"
        title="Polygon Mode (G) - Click to add points, Enter to finish"
      >
        <Pentagon :size="18" />
        <span>Polygon</span>
      </button>
      <button
        @click="emit('setMode', 'skeleton')"
        :class="[
          'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
          drawingMode === 'skeleton'
            ? 'bg-blue-500 text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        ]"
        title="Skeleton Mode - Place keypoints for pose"
      >
        <User :size="18" />
        <span>Pose</span>
      </button>
      <button
        @click="emit('setMode', 'mask')"
        :class="[
          'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
          drawingMode === 'mask' ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        ]"
        title="Mask Mode - Draw freely, auto-creates bounding box"
      >
        <Brush :size="18" />
        <span>Mask</span>
      </button>
    </div>

    <!-- Polygon Instructions -->
    <div
      v-if="drawingMode === 'polygon' && isDrawingPolygon"
      class="text-xs bg-blue-50 p-2 rounded border border-blue-200"
    >
      <div class="font-medium text-blue-700 mb-1">Drawing Polygon</div>
      <div class="text-blue-600">Click to add points<br />Press Enter to finish<br />Press Escape to cancel</div>
    </div>

    <!-- Skeleton Instructions -->
    <div v-if="drawingMode === 'skeleton' && currentSkeleton" class="flex gap-2">
      <button
        @click="emit('finishSkeleton')"
        class="flex-1 p-2 rounded bg-green-100 hover:bg-green-200 transition-colors text-xs font-medium text-green-700"
        title="Finish Skeleton"
      >
        Done
      </button>
      <button
        @click="emit('cancelSkeleton')"
        class="flex-1 p-2 rounded bg-yellow-100 hover:bg-yellow-200 transition-colors text-xs font-medium text-yellow-700"
        title="Cancel Skeleton"
      >
        Cancel
      </button>
    </div>

    <!-- Edit Actions -->
    <div class="pt-2 border-t space-y-2">
      <div class="grid grid-cols-2 gap-2">
        <button
          @click="emit('undo')"
          :disabled="!canUndo"
          :class="[
            'flex items-center justify-center gap-1 p-2 rounded-lg transition-all text-sm',
            !canUndo ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
          ]"
          title="Undo (Ctrl+Z)"
        >
          <Undo :size="16" />
          <span>Undo</span>
        </button>
        <button
          @click="emit('redo')"
          :disabled="!canRedo"
          :class="[
            'flex items-center justify-center gap-1 p-2 rounded-lg transition-all text-sm',
            !canRedo ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
          ]"
          title="Redo (Ctrl+Y)"
        >
          <Redo :size="16" />
          <span>Redo</span>
        </button>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <button
          @click="emit('copy')"
          :disabled="!selectedShape"
          :class="[
            'flex items-center justify-center gap-1 p-2 rounded-lg transition-all text-sm',
            !selectedShape
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
          ]"
          title="Copy (Ctrl+C)"
        >
          <Copy :size="16" />
          <span>Copy</span>
        </button>
        <button
          @click="emit('export')"
          class="flex items-center justify-center gap-1 p-2 rounded-lg transition-all text-sm bg-gray-100 text-gray-700 hover:bg-gray-200"
          title="Export Annotations"
        >
          <Download :size="16" />
          <span>Export</span>
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="pt-2 border-t space-y-1">
      <button
        @click="emit('deleteSelected')"
        :disabled="!selectedShape"
        :class="[
          'w-full flex items-center justify-center gap-2 p-2 rounded-lg transition-all text-sm',
          !selectedShape ? 'bg-red-100 text-red-400 cursor-not-allowed' : 'bg-red-100 text-red-600 hover:bg-red-200',
        ]"
        title="Delete Selected (Delete)"
      >
        <Trash2 :size="16" />
        <span>Delete Selected</span>
      </button>
      <button
        v-if="selectedShape && selectedShape.masks && selectedShape.masks.length > 0"
        @click="emit('clearMasks')"
        class="w-full p-2 rounded-lg transition-all text-xs bg-purple-100 text-purple-600 hover:bg-purple-200"
        title="Clear Masks"
      >
        Clear Masks
      </button>
      <button
        @click="emit('clearAll')"
        :disabled="shapesCount === 0"
        :class="[
          'w-full p-2 rounded-lg transition-all text-xs',
          shapesCount === 0
            ? 'bg-orange-100 text-orange-400 cursor-not-allowed'
            : 'bg-orange-100 text-orange-600 hover:bg-orange-200',
        ]"
        title="Clear All Annotations"
      >
        Clear All
      </button>
    </div>
  </div>
</template>
