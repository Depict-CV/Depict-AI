import { ref, computed, type Ref } from 'vue'
import Konva from 'konva'

export function useShapeManagement(
  layer: Ref<Konva.Layer | null>,
  transformer: Ref<Konva.Transformer | null>,
  shapes: Ref<any[]>,
  drawingMode: Ref<string>,
  getLabelColor: (label: string) => string
) {
  const selectedShape = ref<any>(null)
  const clipboard = ref<any>(null)

  // History management
  const history = ref<any[]>([])
  const historyStep = ref(-1)
  const maxHistory = 50

  const selectShape = (shape: any) => {
    // Deselect previous
    if (selectedShape.value && selectedShape.value !== shape) {
      const oldColor = getLabelColor(selectedShape.value.metadata?.label || '')
      selectedShape.value.stroke(oldColor)
      selectedShape.value.strokeWidth(2)
      selectedShape.value.draggable(false)
    }

    // Select new
    selectedShape.value = shape
    shape.stroke('#ff0000')
    shape.strokeWidth(3)
    shape.draggable(true)

    // Attach transformer
    if (transformer.value && drawingMode.value === 'select') {
      transformer.value.nodes([shape])
      transformer.value.show()
    }

    layer.value?.draw()
  }

  const deselectShape = () => {
    if (selectedShape.value) {
      const color = getLabelColor(selectedShape.value.metadata?.label || '')
      selectedShape.value.stroke(color)
      selectedShape.value.strokeWidth(2)
      selectedShape.value.draggable(false)
      selectedShape.value = null

      if (transformer.value) {
        transformer.value.nodes([])
        transformer.value.hide()
      }

      layer.value?.draw()
    }
  }

  const deleteSelectedShape = () => {
    if (!selectedShape.value) return

    // Destroy masks
    if (selectedShape.value.masks) {
      selectedShape.value.masks.forEach((mask: any) => mask.destroy())
    }

    selectedShape.value.destroy()
    shapes.value = shapes.value.filter((s) => s !== selectedShape.value)

    if (transformer.value) {
      transformer.value.nodes([])
      transformer.value.hide()
    }

    selectedShape.value = null
    saveHistory()
    layer.value?.draw()
  }

  const clearMasksFromSelectedBox = () => {
    if (!selectedShape.value || !selectedShape.value.masks) return

    if (!confirm('Clear all masks from this box?')) return

    selectedShape.value.masks.forEach((mask: any) => mask.destroy())
    selectedShape.value.masks = []
    layer.value?.draw()
  }

  const clearAllShapes = () => {
    if (!confirm('Are you sure you want to clear all shapes?')) return

    shapes.value.forEach((shape) => {
      if (shape.masks) {
        shape.masks.forEach((mask: any) => mask.destroy())
      }
      shape.destroy ? shape.destroy() : shape.group?.destroy()
    })
    shapes.value = []
    selectedShape.value = null

    if (transformer.value) {
      transformer.value.nodes([])
      transformer.value.hide()
    }

    layer.value?.draw()
  }

  const copyShape = () => {
    if (!selectedShape.value) return
    clipboard.value = {
      type: selectedShape.value.className,
      config: selectedShape.value.toJSON(),
      metadata: selectedShape.value.metadata,
    }
  }

  const pasteShape = () => {
    if (!clipboard.value) return

    const config = JSON.parse(JSON.stringify(clipboard.value.config))
    config.attrs.x += 20
    config.attrs.y += 20

    let newShape
    if (clipboard.value.type === 'Rect') {
      newShape = Konva.Node.create(config)
      newShape.metadata = clipboard.value.metadata
      newShape.on('click tap', (e: any) => {
        if (drawingMode.value === 'select') {
          e.cancelBubble = true
          selectShape(newShape)
        }
      })
      layer.value?.add(newShape)
      shapes.value.push(newShape)
      saveHistory()
    }

    layer.value?.draw()
  }

  const exportAnnotations = (imageId: string | number) => {
    const annotations = shapes.value.map((shape) => {
      const attrs = shape.attrs || {}
      return {
        type: shape.metadata?.type || shape.className,
        label: shape.metadata?.label || '',
        x: attrs.x || 0,
        y: attrs.y || 0,
        width: attrs.width || 0,
        height: attrs.height || 0,
        points: attrs.points || [],
        metadata: shape.metadata,
      }
    })

    const data = JSON.stringify(annotations, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `annotations_${imageId}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // History functions
  const saveHistory = () => {
    const state = shapes.value.map((shape) => ({
      type: shape.className || shape.group?.className,
      config: shape.toJSON ? shape.toJSON() : null,
      metadata: shape.metadata,
    }))

    if (historyStep.value < history.value.length - 1) {
      history.value = history.value.slice(0, historyStep.value + 1)
    }

    history.value.push(state)
    historyStep.value++

    if (history.value.length > maxHistory) {
      history.value.shift()
      historyStep.value--
    }
  }

  const undo = () => {
    if (historyStep.value <= 0) return
    historyStep.value--
    restoreHistory()
  }

  const redo = () => {
    if (historyStep.value >= history.value.length - 1) return
    historyStep.value++
    restoreHistory()
  }

  const restoreHistory = () => {
    shapes.value.forEach((shape) => {
      if (shape.masks) {
        shape.masks.forEach((mask: any) => mask.destroy())
      }
      shape.destroy ? shape.destroy() : shape.group?.destroy()
    })
    shapes.value = []
    layer.value?.draw()
  }

  const canUndo = computed(() => historyStep.value > 0)
  const canRedo = computed(() => historyStep.value < history.value.length - 1)

  return {
    selectedShape,
    selectShape,
    deselectShape,
    deleteSelectedShape,
    clearMasksFromSelectedBox,
    clearAllShapes,
    copyShape,
    pasteShape,
    exportAnnotations,
    saveHistory,
    undo,
    redo,
    canUndo,
    canRedo,
  }
}
