<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useKonvaCanvas } from '../../composables/useKonvaCanvas'
import { useShapeDrawing } from '../../composables/useShapeDrawing'
import { useShapeManagement } from '../../composables/useShapeManagement'
import { useAnnotationData } from '../../composables/useAnnotationData'
import AnnotationToolbar from './AnnotationToolbar.vue'
import AnnotationInfoPanel from './AnnotationInfoPanel.vue'
import AnnotationControlsPanel from './AnnotationControlsPanel.vue'

const emit = defineEmits(['save', 'reject', 'accept'])

const props = defineProps({
  imageId: {
    type: [String, Number],
    required: true,
  },
  imageSrc: {
    type: String,
    required: true,
  },
  projectId: {
    type: Number,
    required: true,
  },
  userId: {
    type: Number,
    required: true,
  },
})

// Refs
const imageRef = ref(null)
const konvaContainerRef = ref(null)
const drawingMode = ref('pan')

// Image adjustments
const brightness = ref(0)
const contrast = ref(0)
const redChannel = ref(0)
const greenChannel = ref(0)
const blueChannel = ref(0)
const saturation = ref(0)
const hue = ref(0)

// Composables
const canvas = useKonvaCanvas()
const annotationData = useAnnotationData(props.projectId, props.imageId, props.userId)

const drawing = useShapeDrawing(
  canvas.stage,
  canvas.layer,
  drawingMode,
  annotationData.selectedLabel,
  annotationData.getLabelColor
)

const management = useShapeManagement(
  canvas.layer,
  canvas.transformer,
  drawing.shapes,
  drawingMode,
  annotationData.getLabelColor
)

// Initialize
onMounted(async () => {
  await annotationData.fetchLabels()
  await annotationData.loadExistingAnnotation()

  if (imageRef.value) {
    imageRef.value.onload = () => initKonva()
    if (imageRef.value.complete) {
      initKonva()
    }
  }

  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
})

const initKonva = () => {
  if (!konvaContainerRef.value || !imageRef.value) return

  canvas.initCanvas(konvaContainerRef.value, imageRef.value, {
    brightness: brightness.value,
    contrast: contrast.value,
    redChannel: redChannel.value,
    greenChannel: greenChannel.value,
    blueChannel: blueChannel.value,
    saturation: saturation.value,
    hue: hue.value,
  })

  canvas.setupZoomAndPan(drawingMode, () => {
    if (management.selectedShape.value) {
      management.deselectShape()
    }
  })

  drawing.setupDrawingEvents(
    (shape) => management.selectShape(shape),
    () => management.saveHistory()
  )
}

const setDrawingMode = (mode) => {
  drawingMode.value = mode

  if (canvas.stage.value) {
    if (mode === 'pan') {
      canvas.stage.value.container().style.cursor = 'grab'
    } else {
      canvas.stage.value.container().style.cursor = 'default'
    }
  }

  if (mode !== 'select') {
    drawing.shapes.value.forEach((item) => {
      if (item.className === 'Rect' || item.className === 'Circle' || item.className === 'Line') {
        item.draggable(false)
      } else if (item.group) {
        item.group.draggable(false)
        item.keypoints?.forEach((kp) => {
          kp.circle.draggable(false)
        })
      }
    })
  }

  if (management.selectedShape.value) {
    management.deselectShape()
  }

  if (canvas.transformer.value) {
    if (mode === 'select') {
      canvas.transformer.value.show()
    } else {
      canvas.transformer.value.nodes([])
      canvas.transformer.value.hide()
    }
  }
}

const handleKeyboard = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    management.undo()
  } else if ((e.ctrlKey || e.metaKey) && ((e.shiftKey && e.key === 'z') || e.key === 'y')) {
    e.preventDefault()
    management.redo()
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'c' && management.selectedShape.value) {
    e.preventDefault()
    management.copyShape()
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
    e.preventDefault()
    management.pasteShape()
  } else if (e.key === 'Delete' && management.selectedShape.value) {
    management.deleteSelectedShape()
  } else if (e.key === 'Enter' && drawing.isDrawingPolygon.value) {
    e.preventDefault()
    drawing.finishPolygon(
      (shape) => management.selectShape(shape),
      () => management.saveHistory()
    )
  } else if (e.key === 'Escape') {
    if (drawing.isDrawingPolygon.value) {
      drawing.cancelPolygon()
    } else if (management.selectedShape.value) {
      management.deselectShape()
    }
  } else if (e.key === 'p' || e.key === 'P') {
    setDrawingMode('pan')
  } else if (e.key === 's' || e.key === 'S') {
    setDrawingMode('select')
  } else if (e.key === 'r' || e.key === 'R') {
    setDrawingMode('rectangle')
  } else if (e.key === 'g' || e.key === 'G') {
    setDrawingMode('polygon')
  }
}

const applyImageFilters = () => {
  canvas.applyImageFilters({
    brightness: brightness.value,
    contrast: contrast.value,
    redChannel: redChannel.value,
    greenChannel: greenChannel.value,
    blueChannel: blueChannel.value,
    saturation: saturation.value,
    hue: hue.value,
  })
}

const resetImageFilters = () => {
  brightness.value = 0
  contrast.value = 0
  redChannel.value = 0
  greenChannel.value = 0
  blueChannel.value = 0
  saturation.value = 0
  hue.value = 0
  applyImageFilters()
}

const handleFinishSkeleton = () => {
  const count = drawing.finishSkeletonEarly()
  if (count > 0) {
    alert(`Skeleton saved with ${count} keypoints`)
  }
}
</script>

<template>
  <div class="flex-1 flex flex-col">
    <!-- Image Display Area with Konva -->
    <div class="flex-1 flex flex-col items-center justify-center p-4 bg-gray-100 relative overflow-hidden">
      <!-- Toolbar -->
      <AnnotationToolbar
        :drawingMode="drawingMode"
        :isDrawingPolygon="drawing.isDrawingPolygon.value"
        :currentSkeleton="drawing.currentSkeleton.value"
        :canUndo="management.canUndo.value"
        :canRedo="management.canRedo.value"
        :selectedShape="management.selectedShape.value"
        :shapesCount="drawing.shapes.value.length"
        @setMode="setDrawingMode"
        @undo="management.undo"
        @redo="management.redo"
        @copy="management.copyShape"
        @export="() => management.exportAnnotations(props.imageId)"
        @deleteSelected="management.deleteSelectedShape"
        @clearMasks="management.clearMasksFromSelectedBox"
        @clearAll="management.clearAllShapes"
        @finishSkeleton="handleFinishSkeleton"
        @cancelSkeleton="drawing.clearCurrentSkeleton"
      />

      <!-- Info Panel -->
      <AnnotationInfoPanel
        :zoomLevel="canvas.zoomLevel.value"
        :brightness="brightness"
        :contrast="contrast"
        :redChannel="redChannel"
        :greenChannel="greenChannel"
        :blueChannel="blueChannel"
        :saturation="saturation"
        :hue="hue"
        :selectedShape="management.selectedShape.value"
        :getLabelColor="annotationData.getLabelColor"
        @resetZoom="canvas.resetZoom"
        @update:brightness="
          (v) => {
            brightness = v
            applyImageFilters()
          }
        "
        @update:contrast="
          (v) => {
            contrast = v
            applyImageFilters()
          }
        "
        @update:redChannel="
          (v) => {
            redChannel = v
            applyImageFilters()
          }
        "
        @update:greenChannel="
          (v) => {
            greenChannel = v
            applyImageFilters()
          }
        "
        @update:blueChannel="
          (v) => {
            blueChannel = v
            applyImageFilters()
          }
        "
        @update:saturation="
          (v) => {
            saturation = v
            applyImageFilters()
          }
        "
        @update:hue="
          (v) => {
            hue = v
            applyImageFilters()
          }
        "
        @resetFilters="resetImageFilters"
      />

      <!-- Konva Container -->
      <div ref="konvaContainerRef" class="relative bg-white rounded-lg shadow-md w-full h-full"></div>

      <!-- Hidden image for reference -->
      <img ref="imageRef" :src="imageSrc" alt="Annotation image" class="hidden" />
    </div>

    <!-- Annotation Controls Panel -->
    <AnnotationControlsPanel
      :description="annotationData.description.value"
      :selectedLabel="annotationData.selectedLabel.value"
      :availableLabels="annotationData.availableLabels.value"
      :newLabel="annotationData.newLabel.value"
      :showLabelInput="annotationData.showLabelInput.value"
      :saving="annotationData.saving.value"
      @update:description="(v) => (annotationData.description.value = v)"
      @update:selectedLabel="(v) => (annotationData.selectedLabel.value = v)"
      @update:newLabel="(v) => (annotationData.newLabel.value = v)"
      @update:showLabelInput="(v) => (annotationData.showLabelInput.value = v)"
      @addLabel="annotationData.addLabel"
      @save="() => annotationData.saveAnnotation(emit)"
      @accept="() => annotationData.acceptAnnotation(emit)"
      @reject="() => annotationData.rejectAnnotation(emit)"
    />
  </div>
</template>
