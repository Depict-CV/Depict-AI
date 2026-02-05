<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import {
  Save,
  Check,
  Trash2,
  Plus,
  Square,
  MousePointer,
  User,
  Hand,
  Brush,
  Undo,
  Redo,
  Copy,
  Download,
  Sun,
  Contrast,
  Pentagon,
} from 'lucide-vue-next'
import Konva from 'konva'
import ImageAdjustments from './ImageAdjustments.vue'

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

const api = useApi()
const imageRef = ref(null)
const konvaContainerRef = ref(null)
const stage = ref(null)
const layer = ref(null)
const imageNode = ref(null)
const transformer = ref(null)

// Drawing state
const drawingMode = ref('pan') // 'pan', 'select', 'rectangle', 'skeleton', 'mask', 'polygon'
const isDrawing = ref(false)
const currentShape = ref(null)
const shapes = ref([])
const selectedShape = ref(null)
const zoomLevel = ref(1)

// Mask drawing state
const currentMask = ref(null)
const maskPoints = ref([])
const isDrawingMask = ref(false)
const maskSubMode = ref('paint') // 'paint' or 'polygon'

// Polygon drawing state
const polygonPoints = ref([])
const currentPolygon = ref(null)
const isDrawingPolygon = ref(false)
const tempLine = ref(null)

// History for undo/redo
const history = ref([])
const historyStep = ref(-1)
const maxHistory = 50

// Clipboard
const clipboard = ref(null)

// Image adjustments
const brightness = ref(0)
const contrast = ref(0)
const redChannel = ref(0)
const greenChannel = ref(0)
const blueChannel = ref(0)
const saturation = ref(0)
const hue = ref(0)

// Label colors
const labelColors = ref({
  person: '#FF6B6B',
  car: '#4ECDC4',
  dog: '#95E1D3',
  cat: '#F38181',
  default: '#00ff00',
})

// Skeleton state
const currentSkeleton = ref(null)
const skeletonPhase = ref('nodes') // 'nodes', 'edges', 'labels'
const selectedNodeForEdge = ref(null)
const selectedNodeForLabel = ref(null)
const availableBodyParts = ref([
  'nose',
  'left_eye',
  'right_eye',
  'left_ear',
  'right_ear',
  'left_shoulder',
  'right_shoulder',
  'left_elbow',
  'right_elbow',
  'left_wrist',
  'right_wrist',
  'left_hip',
  'right_hip',
  'left_knee',
  'right_knee',
  'left_ankle',
  'right_ankle',
  'head',
  'neck',
  'torso',
  'other',
])

// Annotation state
const description = ref('')
const selectedLabel = ref('')
const availableLabels = ref([])
const newLabel = ref('')
const showLabelInput = ref(false)
const saving = ref(false)

const fetchLabels = async () => {
  try {
    const annotations = await api.get(`/annotations/?project_id=${props.projectId}`)
    // Extract unique labels from annotations
    const uniqueLabels = new Set()
    annotations.forEach((annotation) => {
      if (annotation.label) {
        uniqueLabels.add(annotation.label)
      }
    })
    availableLabels.value = Array.from(uniqueLabels).sort()

    // Assign colors to new labels
    availableLabels.value.forEach((label) => {
      if (!labelColors.value[label]) {
        labelColors.value[label] = generateRandomColor()
      }
    })
  } catch (error) {
    console.error('Error fetching labels:', error)
  }
}

const generateRandomColor = () => {
  const hue = Math.floor(Math.random() * 360)
  return `hsl(${hue}, 70%, 60%)`
}

const getLabelColor = (label) => {
  return labelColors.value[label] || labelColors.value['default']
}

const loadExistingAnnotation = async () => {
  try {
    const annotations = await api.get(`/annotations/?project_id=${props.projectId}`)
    // Find annotation for this specific image
    const existingAnnotation = annotations.find(
      (ann) => ann.data_id === props.imageId || ann.data_id === String(props.imageId)
    )

    if (existingAnnotation) {
      console.log('Found existing annotation:', existingAnnotation)
      // Load the description and label from the existing annotation
      description.value = existingAnnotation.description || ''
      selectedLabel.value = existingAnnotation.label || ''
    }
  } catch (error) {
    console.error('Error loading existing annotation:', error)
  }
}

onMounted(async () => {
  // Fetch available labels from dataset
  await fetchLabels()

  // Load existing annotation for this image if it exists
  await loadExistingAnnotation()

  // Initialize Konva after image loads
  if (imageRef.value) {
    imageRef.value.onload = initKonva
    // If image is already loaded
    if (imageRef.value.complete) {
      initKonva()
    }
  }

  // Setup keyboard shortcuts
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
})

const handleKeyboard = (e) => {
  // Ctrl/Cmd + Z: Undo
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    undo()
  }
  // Ctrl/Cmd + Shift + Z or Ctrl/Cmd + Y: Redo
  else if ((e.ctrlKey || e.metaKey) && ((e.shiftKey && e.key === 'z') || e.key === 'y')) {
    e.preventDefault()
    redo()
  }
  // Ctrl/Cmd + C: Copy
  else if ((e.ctrlKey || e.metaKey) && e.key === 'c' && selectedShape.value) {
    e.preventDefault()
    copyShape()
  }
  // Ctrl/Cmd + V: Paste
  else if ((e.ctrlKey || e.metaKey) && e.key === 'v' && clipboard.value) {
    e.preventDefault()
    pasteShape()
  }
  // Delete: Delete selected
  else if (e.key === 'Delete' && selectedShape.value) {
    deleteSelectedShape()
  }
  // Enter: Finish polygon
  else if (e.key === 'Enter' && isDrawingPolygon.value) {
    e.preventDefault()
    finishPolygon()
  }
  // Enter: Finish mask polygon
  else if (e.key === 'Enter' && isDrawingMask.value && maskSubMode.value === 'polygon') {
    e.preventDefault()
    finishMaskPolygon()
  }
  // Escape: Cancel current drawing or deselect
  else if (e.key === 'Escape') {
    if (isDrawingPolygon.value) {
      cancelPolygon()
    } else if (isDrawingMask.value && maskSubMode.value === 'polygon') {
      cancelMaskPolygon()
    } else if (selectedShape.value) {
      deselectShape()
    }
  }
  // P: Pan mode
  else if (e.key === 'p' || e.key === 'P') {
    setDrawingMode('pan')
  }
  // S: Select mode
  else if (e.key === 's' || e.key === 'S') {
    setDrawingMode('select')
  }
  // R: Rectangle mode
  else if (e.key === 'r' || e.key === 'R') {
    setDrawingMode('rectangle')
  }
  // G: Polygon mode
  else if (e.key === 'g' || e.key === 'G') {
    setDrawingMode('polygon')
  }
}

const initKonva = () => {
  if (!konvaContainerRef.value || !imageRef.value) return

  const containerWidth = konvaContainerRef.value.offsetWidth
  const containerHeight = konvaContainerRef.value.offsetHeight

  // Create stage
  stage.value = new Konva.Stage({
    container: konvaContainerRef.value,
    width: containerWidth,
    height: containerHeight,
  })

  // Create layer
  layer.value = new Konva.Layer()
  stage.value.add(layer.value)

  // Create transformer for resizing shapes
  transformer.value = new Konva.Transformer({
    rotateEnabled: false,
    borderStroke: '#ff0000',
    borderStrokeWidth: 2,
    anchorSize: 8,
    anchorStroke: '#ff0000',
    anchorFill: '#ffffff',
    anchorCornerRadius: 2,
  })
  layer.value.add(transformer.value)

  // Add image to layer
  const img = new Image()
  img.src = imageRef.value.src
  img.onload = () => {
    // Calculate scaling to fit image
    const scale = Math.min(containerWidth / img.width, containerHeight / img.height, 1)

    imageNode.value = new Konva.Image({
      image: img,
      x: (containerWidth - img.width * scale) / 2,
      y: (containerHeight - img.height * scale) / 2,
      width: img.width * scale,
      height: img.height * scale,
      listening: false,
      filters: [Konva.Filters.Brighten, Konva.Filters.Contrast, Konva.Filters.RGB, Konva.Filters.HSL],
      brightness: brightness.value / 100,
      contrast: contrast.value,
      red: redChannel.value,
      green: greenChannel.value,
      blue: blueChannel.value,
      saturation: saturation.value / 100,
      hue: hue.value,
    })

    layer.value.add(imageNode.value)
    imageNode.value.moveToBottom()
    layer.value.draw()

    // Setup drawing events
    setupDrawingEvents()

    // Setup zoom and pan
    setupZoomAndPan()
  }
}

const setupZoomAndPan = () => {
  if (!stage.value) return

  const scaleBy = 1.1
  const minScale = 0.1
  const maxScale = 10

  // Click on background to deselect
  stage.value.on('click tap', (e) => {
    // If clicked on stage background (not on a shape)
    if (e.target === stage.value) {
      if (selectedShape.value) {
        selectedShape.value.stroke('#00ff00')
        selectedShape.value.strokeWidth(2)
        selectedShape.value.draggable(false)
        selectedShape.value = null

        // Hide transformer
        if (transformer.value) {
          transformer.value.nodes([])
          transformer.value.hide()
        }

        layer.value.draw()
      }
    }
  })

  // Zoom with mouse wheel
  stage.value.on('wheel', (e) => {
    e.evt.preventDefault()

    const oldScale = stage.value.scaleX()
    const pointer = stage.value.getPointerPosition()

    const mousePointTo = {
      x: (pointer.x - stage.value.x()) / oldScale,
      y: (pointer.y - stage.value.y()) / oldScale,
    }

    let newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy

    // Limit zoom level
    if (newScale < minScale) newScale = minScale
    if (newScale > maxScale) newScale = maxScale

    stage.value.scale({ x: newScale, y: newScale })
    zoomLevel.value = newScale

    const newPos = {
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale,
    }

    stage.value.position(newPos)
    layer.value.batchDraw()
  })

  // Pan with drag in pan mode
  let isPanning = false
  let lastPos = null

  stage.value.on('mousedown touchstart', (e) => {
    if (drawingMode.value === 'pan') {
      isPanning = true
      lastPos = stage.value.getPointerPosition()
      stage.value.container().style.cursor = 'grabbing'
      e.cancelBubble = true
    }
  })

  stage.value.on('mousemove touchmove', (e) => {
    if (isPanning && drawingMode.value === 'pan') {
      e.evt.preventDefault()
      const pos = stage.value.getPointerPosition()
      if (!lastPos) {
        lastPos = pos
        return
      }

      const dx = pos.x - lastPos.x
      const dy = pos.y - lastPos.y

      stage.value.x(stage.value.x() + dx)
      stage.value.y(stage.value.y() + dy)

      lastPos = pos
      layer.value.batchDraw()
    }
  })

  stage.value.on('mouseup touchend', () => {
    if (isPanning) {
      isPanning = false
      lastPos = null
      if (drawingMode.value === 'pan') {
        stage.value.container().style.cursor = 'grab'
      }
    }
  })

  // Update cursor based on mode
  stage.value.on('mouseover', () => {
    if (drawingMode.value === 'pan') {
      stage.value.container().style.cursor = 'grab'
    } else {
      stage.value.container().style.cursor = 'default'
    }
  })
}

const setupDrawingEvents = () => {
  if (!stage.value) return

  let startPos = null

  stage.value.on('mousedown touchstart', (e) => {
    // Skip if in pan or select mode, or if clicking on background in pan mode
    if (drawingMode.value === 'pan' || drawingMode.value === 'select') return

    const pos = stage.value.getRelativePointerPosition()

    // Handle mask mode - draw mask freely or with polygon
    if (drawingMode.value === 'mask') {
      if (maskSubMode.value === 'paint') {
        // Paint mode - free drawing
        isDrawingMask.value = true
        maskPoints.value = [pos.x, pos.y]

        const color = selectedLabel.value ? getLabelColor(selectedLabel.value) : '#ff00ff'
        currentMask.value = new Konva.Line({
          points: maskPoints.value,
          stroke: color,
          strokeWidth: 2,
          lineCap: 'round',
          lineJoin: 'round',
          globalCompositeOperation: 'source-over',
        })

        layer.value.add(currentMask.value)
      } else if (maskSubMode.value === 'polygon') {
        // Polygon mode - click to add points
        if (!isDrawingMask.value) {
          // Start new mask polygon
          isDrawingMask.value = true
          maskPoints.value = [pos.x, pos.y]

          const color = selectedLabel.value ? getLabelColor(selectedLabel.value) : '#ff00ff'
          currentMask.value = new Konva.Line({
            points: maskPoints.value,
            stroke: color,
            strokeWidth: 2,
            closed: false,
            lineCap: 'round',
            lineJoin: 'round',
          })

          layer.value.add(currentMask.value)
        } else {
          // Add point to existing mask polygon
          maskPoints.value.push(pos.x, pos.y)
          currentMask.value.points(maskPoints.value)
        }

        // Draw point indicator
        const point = new Konva.Circle({
          x: pos.x,
          y: pos.y,
          radius: 4,
          fill: '#ffffff',
          stroke: '#ff0000',
          strokeWidth: 2,
        })
        layer.value.add(point)
        layer.value.draw()
      }
      return
    }

    // Handle skeleton mode - place keypoints
    if (drawingMode.value === 'skeleton') {
      addKeypoint(pos)
      return
    }

    // Handle polygon mode - add points
    if (drawingMode.value === 'polygon') {
      addPolygonPoint(pos)
      return
    }

    isDrawing.value = true
    startPos = pos

    // Create shape based on drawing mode
    if (drawingMode.value === 'rectangle') {
      const color = selectedLabel.value ? getLabelColor(selectedLabel.value) : '#00ff00'
      currentShape.value = new Konva.Rect({
        x: pos.x,
        y: pos.y,
        width: 0,
        height: 0,
        stroke: color,
        strokeWidth: 2,
        draggable: false,
        listening: true,
        strokeScaleEnabled: false,
      })

      // Store metadata
      currentShape.value.metadata = {
        type: 'rectangle',
        label: selectedLabel.value || '',
        createdAt: new Date().toISOString(),
      }

      // Add click event immediately
      const shapeRef = currentShape.value
      shapeRef.on('click tap', (e) => {
        if (drawingMode.value === 'select') {
          e.cancelBubble = true
          selectShape(shapeRef)
        }
      })

      // Add visual feedback on hover in select mode
      shapeRef.on('mouseenter', () => {
        if (drawingMode.value === 'select') {
          stage.value.container().style.cursor = 'pointer'
        }
      })

      shapeRef.on('mouseleave', () => {
        if (drawingMode.value === 'select') {
          stage.value.container().style.cursor = 'default'
        }
      })
    }

    if (currentShape.value) {
      layer.value.add(currentShape.value)
      layer.value.draw()
    }
  })

  stage.value.on('mousemove touchmove', (e) => {
    // Handle mask drawing (paint mode only)
    if (isDrawingMask.value && currentMask.value && maskSubMode.value === 'paint') {
      const pos = stage.value.getRelativePointerPosition()
      maskPoints.value.push(pos.x, pos.y)
      currentMask.value.points(maskPoints.value)
      layer.value.batchDraw()
      return
    }

    if (!isDrawing.value || !currentShape.value || drawingMode.value === 'pan' || drawingMode.value === 'select') return

    const pos = stage.value.getRelativePointerPosition()

    if (drawingMode.value === 'rectangle') {
      currentShape.value.width(pos.x - startPos.x)
      currentShape.value.height(pos.y - startPos.y)
    }

    layer.value.batchDraw()
  })

  stage.value.on('mouseup touchend', () => {
    // Handle mask drawing completion (paint mode only)
    if (isDrawingMask.value && maskSubMode.value === 'paint') {
      isDrawingMask.value = false

      if (currentMask.value && maskPoints.value.length >= 6) {
        // Close the mask path
        currentMask.value.closed(true)
        const maskColor = currentMask.value.stroke()
        currentMask.value.fill(maskColor + '30')

        // Calculate bounding box from mask points
        const xs = []
        const ys = []
        for (let i = 0; i < maskPoints.value.length; i += 2) {
          xs.push(maskPoints.value[i])
          ys.push(maskPoints.value[i + 1])
        }
        const minX = Math.min(...xs)
        const maxX = Math.max(...xs)
        const minY = Math.min(...ys)
        const maxY = Math.max(...ys)

        // Create bounding box
        const boundingBox = new Konva.Rect({
          x: minX,
          y: minY,
          width: maxX - minX,
          height: maxY - minY,
          stroke: maskColor,
          strokeWidth: 2,
          draggable: false,
          listening: true,
          strokeScaleEnabled: false,
        })

        // Store metadata
        boundingBox.metadata = {
          type: 'rectangle',
          label: selectedLabel.value || '',
          createdAt: new Date().toISOString(),
          hasMask: true,
        }

        // Initialize masks array and add the mask
        boundingBox.masks = [currentMask.value]

        // Add click event for selection
        boundingBox.on('click tap', (e) => {
          if (drawingMode.value === 'select') {
            e.cancelBubble = true
            selectShape(boundingBox)
          }
        })

        // Add visual feedback on hover
        boundingBox.on('mouseenter', () => {
          if (drawingMode.value === 'select') {
            stage.value.container().style.cursor = 'pointer'
          }
        })

        boundingBox.on('mouseleave', () => {
          if (drawingMode.value === 'select') {
            stage.value.container().style.cursor = 'default'
          }
        })

        // Add bounding box to layer and shapes
        layer.value.add(boundingBox)
        boundingBox.moveToTop()
        currentMask.value.moveToTop()
        shapes.value.push(boundingBox)
        saveHistory()

        currentMask.value = null
        maskPoints.value = []
        layer.value.draw()
      }
      return
    }

    if (!isDrawing.value) return

    isDrawing.value = false

    if (currentShape.value) {
      // Add mask property to store masks
      currentShape.value.masks = []
      shapes.value.push(currentShape.value)
      saveHistory()
      currentShape.value = null
    }
  })
}

const selectShape = (shape) => {
  // Deselect previous shape
  if (selectedShape.value && selectedShape.value !== shape) {
    selectedShape.value.stroke('#00ff00')
    selectedShape.value.strokeWidth(2)
    selectedShape.value.draggable(false)
  }

  // Select new shape
  selectedShape.value = shape
  shape.stroke('#ff0000')
  shape.strokeWidth(3)
  shape.draggable(true)

  // Attach transformer to enable resizing
  if (transformer.value && drawingMode.value === 'select') {
    transformer.value.nodes([shape])
    transformer.value.show()
  }

  layer.value.draw()
}

const deleteSelectedShape = () => {
  if (!selectedShape.value) return

  // Destroy any associated masks
  if (selectedShape.value.masks) {
    selectedShape.value.masks.forEach((mask) => mask.destroy())
  }

  selectedShape.value.destroy()
  shapes.value = shapes.value.filter((s) => s !== selectedShape.value)

  // Hide transformer
  if (transformer.value) {
    transformer.value.nodes([])
    transformer.value.hide()
  }

  selectedShape.value = null
  saveHistory()
  layer.value.draw()
}

const clearMasksFromSelectedBox = () => {
  if (!selectedShape.value || !selectedShape.value.masks) return

  if (!confirm('Clear all masks from this box?')) return

  selectedShape.value.masks.forEach((mask) => mask.destroy())
  selectedShape.value.masks = []
  layer.value.draw()
}

const clearAllShapes = () => {
  if (!confirm('Are you sure you want to clear all shapes?')) return

  shapes.value.forEach((shape) => {
    // Destroy any associated masks
    if (shape.masks) {
      shape.masks.forEach((mask) => mask.destroy())
    }
    shape.destroy()
  })
  shapes.value = []
  selectedShape.value = null

  // Hide transformer
  if (transformer.value) {
    transformer.value.nodes([])
    transformer.value.hide()
  }

  layer.value.draw()
}

const setDrawingMode = (mode) => {
  drawingMode.value = mode

  // Update cursor based on mode
  if (stage.value) {
    if (mode === 'pan') {
      stage.value.container().style.cursor = 'grab'
    } else {
      stage.value.container().style.cursor = 'default'
    }
  }

  // When leaving select mode, make all shapes non-draggable
  if (mode !== 'select') {
    shapes.value.forEach((item) => {
      // Handle regular shapes (rectangles)
      if (item.className === 'Rect' || item.className === 'Circle' || item.className === 'Line') {
        item.draggable(false)
      }
      // Handle skeleton groups
      else if (item.group) {
        item.group.draggable(false)
        item.keypoints?.forEach((kp) => {
          kp.circle.draggable(false)
        })
      }
    })
  }

  // Deselect any selected shape when changing mode
  if (selectedShape.value) {
    selectedShape.value.stroke('#00ff00')
    selectedShape.value.strokeWidth(2)
    selectedShape.value.draggable(false)
    selectedShape.value = null

    // Hide transformer
    if (transformer.value) {
      transformer.value.nodes([])
      transformer.value.hide()
    }

    layer.value?.draw()
  }

  // Show/hide transformer based on mode
  if (transformer.value) {
    if (mode === 'select') {
      transformer.value.show()
    } else {
      transformer.value.nodes([])
      transformer.value.hide()
    }
  }
}

const addKeypoint = (pos) => {
  if (skeletonPhase.value === 'nodes') {
    // Add node phase
    if (!currentSkeleton.value) {
      // Start a new skeleton
      currentSkeleton.value = {
        keypoints: [],
        connections: [],
        group: new Konva.Group({
          draggable: false,
        }),
      }
      layer.value.add(currentSkeleton.value.group)
    }

    const skeleton = currentSkeleton.value
    const keypointIndex = skeleton.keypoints.length

    // Create keypoint circle
    const keypoint = new Konva.Circle({
      x: pos.x,
      y: pos.y,
      radius: 6,
      fill: '#ff0000',
      stroke: '#ffffff',
      strokeWidth: 2,
      draggable: false,
    })

    // Add index label
    const label = new Konva.Text({
      x: pos.x + 10,
      y: pos.y - 10,
      text: `${keypointIndex}`,
      fontSize: 14,
      fill: '#ffffff',
      stroke: '#000000',
      strokeWidth: 1,
      fontStyle: 'bold',
    })

    // Add click handler for edge drawing and label assignment
    keypoint.on('click tap', (e) => {
      e.cancelBubble = true
      if (skeletonPhase.value === 'edges') {
        handleNodeClickForEdge(keypointIndex)
      } else if (skeletonPhase.value === 'labels') {
        handleNodeClickForLabel(keypointIndex)
      }
    })

    // Hover effect
    keypoint.on('mouseenter', () => {
      if (skeletonPhase.value === 'edges' || skeletonPhase.value === 'labels') {
        keypoint.radius(8)
        layer.value.draw()
      }
    })

    keypoint.on('mouseleave', () => {
      keypoint.radius(6)
      layer.value.draw()
    })

    skeleton.keypoints.push({
      circle: keypoint,
      label,
      pos: { x: pos.x, y: pos.y },
      bodyPart: null,
      index: keypointIndex,
    })
    skeleton.group.add(keypoint)
    skeleton.group.add(label)

    layer.value.draw()
  }
}

const handleNodeClickForEdge = (nodeIndex) => {
  if (!selectedNodeForEdge.value && selectedNodeForEdge.value !== 0) {
    // First node selected
    selectedNodeForEdge.value = nodeIndex
    const kp = currentSkeleton.value.keypoints[nodeIndex]
    kp.circle.stroke('#ffff00') // Highlight selected node
    kp.circle.strokeWidth(3)
    layer.value.draw()
  } else {
    // Second node selected - create edge
    const startIdx = selectedNodeForEdge.value
    const endIdx = nodeIndex

    if (startIdx !== endIdx) {
      addSkeletonEdge(startIdx, endIdx)
    }

    // Reset selection
    const kp = currentSkeleton.value.keypoints[startIdx]
    kp.circle.stroke('#ffffff')
    kp.circle.strokeWidth(2)
    selectedNodeForEdge.value = null
    layer.value.draw()
  }
}

const addSkeletonEdge = (startIdx, endIdx) => {
  const skeleton = currentSkeleton.value
  const startKp = skeleton.keypoints[startIdx]
  const endKp = skeleton.keypoints[endIdx]

  const line = new Konva.Line({
    points: [startKp.circle.x(), startKp.circle.y(), endKp.circle.x(), endKp.circle.y()],
    stroke: '#00ff00',
    strokeWidth: 3,
    lineCap: 'round',
    lineJoin: 'round',
  })

  line.metadata = {
    startIdx,
    endIdx,
  }

  skeleton.group.add(line)
  line.moveToBottom()
  skeleton.connections.push(line)
  layer.value.draw()
}

const handleNodeClickForLabel = (nodeIndex) => {
  selectedNodeForLabel.value = nodeIndex
}

const assignBodyPartToNode = (bodyPart) => {
  if (selectedNodeForLabel.value !== null && currentSkeleton.value) {
    const kp = currentSkeleton.value.keypoints[selectedNodeForLabel.value]
    kp.bodyPart = bodyPart

    // Update label text
    kp.label.text(`${selectedNodeForLabel.value}: ${bodyPart}`)

    selectedNodeForLabel.value = null
    layer.value.draw()
  }
}

const finishSkeleton = () => {
  if (currentSkeleton.value) {
    // Make the entire skeleton group selectable
    currentSkeleton.value.group.on('click tap', () => {
      selectShape(currentSkeleton.value.group)
    })

    shapes.value.push(currentSkeleton.value)
    currentSkeleton.value = null
  }
}

const clearCurrentSkeleton = () => {
  if (currentSkeleton.value) {
    currentSkeleton.value.group.destroy()
    currentSkeleton.value = null
    skeletonPhase.value = 'nodes'
    selectedNodeForEdge.value = null
    selectedNodeForLabel.value = null
    layer.value.draw()
  }
}

const finishSkeletonEarly = () => {
  if (currentSkeleton.value && currentSkeleton.value.keypoints.length > 0) {
    finishSkeleton()
    alert(`Skeleton saved with ${currentSkeleton.value?.keypoints.length || 0} keypoints`)
    skeletonPhase.value = 'nodes'
    selectedNodeForEdge.value = null
    selectedNodeForLabel.value = null
  }
}

const setSkeletonPhase = (phase) => {
  skeletonPhase.value = phase
  selectedNodeForEdge.value = null
  selectedNodeForLabel.value = null

  // Reset any highlights
  if (currentSkeleton.value) {
    currentSkeleton.value.keypoints.forEach((kp) => {
      kp.circle.stroke('#ffffff')
      kp.circle.strokeWidth(2)
    })
    layer.value.draw()
  }
}

const resetZoom = () => {
  if (!stage.value) return
  stage.value.scale({ x: 1, y: 1 })
  stage.value.position({ x: 0, y: 0 })
  zoomLevel.value = 1
  layer.value.batchDraw()
}

// History management
const saveHistory = () => {
  const state = shapes.value.map((shape) => ({
    type: shape.className || shape.group?.className,
    config: shape.toJSON ? shape.toJSON() : null,
    metadata: shape.metadata,
  }))

  // Remove future history if we're not at the end
  if (historyStep.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyStep.value + 1)
  }

  history.value.push(state)
  historyStep.value++

  // Limit history size
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
  // Clear current shapes
  shapes.value.forEach((shape) => {
    if (shape.masks) {
      shape.masks.forEach((mask) => mask.destroy())
    }
    shape.destroy ? shape.destroy() : shape.group?.destroy()
  })
  shapes.value = []

  // Restore from history
  // Note: Full restoration would require storing complete shape data
  layer.value.draw()
}

const canUndo = computed(() => historyStep.value > 0)
const canRedo = computed(() => historyStep.value < history.value.length - 1)

// Polygon drawing
const addPolygonPoint = (pos) => {
  if (!isDrawingPolygon.value) {
    // Start new polygon
    isDrawingPolygon.value = true
    polygonPoints.value = [pos.x, pos.y]

    const color = selectedLabel.value ? getLabelColor(selectedLabel.value) : '#00ff00'
    currentPolygon.value = new Konva.Line({
      points: polygonPoints.value,
      stroke: color,
      strokeWidth: 2,
      closed: false,
      draggable: false,
      listening: true,
      strokeScaleEnabled: false,
    })

    currentPolygon.value.metadata = {
      type: 'polygon',
      label: selectedLabel.value || '',
      createdAt: new Date().toISOString(),
    }

    layer.value.add(currentPolygon.value)
  } else {
    // Add point to existing polygon
    polygonPoints.value.push(pos.x, pos.y)
    currentPolygon.value.points(polygonPoints.value)
  }

  // Draw point indicator
  const point = new Konva.Circle({
    x: pos.x,
    y: pos.y,
    radius: 4,
    fill: '#ffffff',
    stroke: '#ff0000',
    strokeWidth: 2,
  })
  layer.value.add(point)
  layer.value.draw()
}

const finishPolygon = () => {
  if (!currentPolygon.value || polygonPoints.value.length < 6) return

  currentPolygon.value.closed(true)
  currentPolygon.value.fill(currentPolygon.value.stroke() + '20')

  // Add click event
  currentPolygon.value.on('click tap', (e) => {
    if (drawingMode.value === 'select') {
      e.cancelBubble = true
      selectShape(currentPolygon.value)
    }
  })

  shapes.value.push(currentPolygon.value)
  saveHistory()

  isDrawingPolygon.value = false
  currentPolygon.value = null
  polygonPoints.value = []
  layer.value.draw()
}

const cancelPolygon = () => {
  if (currentPolygon.value) {
    currentPolygon.value.destroy()
    currentPolygon.value = null
  }
  isDrawingPolygon.value = false
  polygonPoints.value = []
  layer.value.draw()
}

// Mask polygon functions
const finishMaskPolygon = () => {
  if (!currentMask.value || maskPoints.value.length < 6) return

  isDrawingMask.value = false

  // Close the mask path
  currentMask.value.closed(true)
  const maskColor = currentMask.value.stroke()
  currentMask.value.fill(maskColor + '30')

  // Calculate bounding box from mask points
  const xs = []
  const ys = []
  for (let i = 0; i < maskPoints.value.length; i += 2) {
    xs.push(maskPoints.value[i])
    ys.push(maskPoints.value[i + 1])
  }
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)

  // Create bounding box
  const boundingBox = new Konva.Rect({
    x: minX,
    y: minY,
    width: maxX - minX,
    height: maxY - minY,
    stroke: maskColor,
    strokeWidth: 2,
    draggable: false,
    listening: true,
    strokeScaleEnabled: false,
  })

  // Store metadata
  boundingBox.metadata = {
    type: 'mask',
    label: selectedLabel.value || '',
    createdAt: new Date().toISOString(),
    hasMask: true,
  }

  // Initialize masks array and add the mask
  boundingBox.masks = [currentMask.value]

  // Add click event for selection
  boundingBox.on('click tap', (e) => {
    if (drawingMode.value === 'select') {
      e.cancelBubble = true
      selectShape(boundingBox)
    }
  })

  // Add visual feedback on hover
  boundingBox.on('mouseenter', () => {
    if (drawingMode.value === 'select') {
      stage.value.container().style.cursor = 'pointer'
    }
  })

  boundingBox.on('mouseleave', () => {
    if (drawingMode.value === 'select') {
      stage.value.container().style.cursor = 'default'
    }
  })

  // Add bounding box to layer and shapes
  layer.value.add(boundingBox)
  boundingBox.moveToTop()
  currentMask.value.moveToTop()
  shapes.value.push(boundingBox)
  saveHistory()

  currentMask.value = null
  maskPoints.value = []
  layer.value.draw()
}

const cancelMaskPolygon = () => {
  if (currentMask.value) {
    currentMask.value.destroy()
    currentMask.value = null
  }
  isDrawingMask.value = false
  maskPoints.value = []
  layer.value.draw()
}

const setMaskSubMode = (mode) => {
  maskSubMode.value = mode
  // Cancel any current mask drawing when switching modes
  if (isDrawingMask.value) {
    cancelMaskPolygon()
  }
}

// Copy/Paste
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

  // Create new shape with offset
  const config = JSON.parse(JSON.stringify(clipboard.value.config))
  config.attrs.x += 20
  config.attrs.y += 20

  let newShape
  if (clipboard.value.type === 'Rect') {
    newShape = Konva.Node.create(config)
    newShape.metadata = clipboard.value.metadata
    newShape.on('click tap', (e) => {
      if (drawingMode.value === 'select') {
        e.cancelBubble = true
        selectShape(newShape)
      }
    })
    layer.value.add(newShape)
    shapes.value.push(newShape)
    saveHistory()
  }

  layer.value.draw()
}

// Image adjustments
const applyImageFilters = () => {
  if (!imageNode.value) return
  imageNode.value.brightness(brightness.value / 100)
  imageNode.value.contrast(contrast.value)
  imageNode.value.red(redChannel.value)
  imageNode.value.green(greenChannel.value)
  imageNode.value.blue(blueChannel.value)
  imageNode.value.saturation(saturation.value / 100)
  imageNode.value.hue(hue.value)
  imageNode.value.cache()
  layer.value.batchDraw()
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

// Deselect helper
const deselectShape = () => {
  if (selectedShape.value) {
    selectedShape.value.stroke(getLabelColor(selectedShape.value.metadata?.label || ''))
    selectedShape.value.strokeWidth(2)
    selectedShape.value.draggable(false)
    selectedShape.value = null

    if (transformer.value) {
      transformer.value.nodes([])
      transformer.value.hide()
    }

    layer.value.draw()
  }
}

// Export annotations
const exportAnnotations = (format = 'json') => {
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
  a.download = `annotations_${props.imageId}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const addLabel = async () => {
  if (!newLabel.value.trim()) return

  // Add to local list
  availableLabels.value.push(newLabel.value)
  selectedLabel.value = newLabel.value
  newLabel.value = ''
  showLabelInput.value = false

  // Optionally persist to API
  try {
    await api.post('/annotations/labels', { name: newLabel.value })
  } catch (error) {
    console.error('Failed to save label:', error)
  }
}

const saveAnnotation = async () => {
  // Validate required props
  if (!props.projectId) {
    alert('Error: Project ID is missing. Cannot save annotation.')
    console.error('Missing projectId prop:', props)
    return
  }

  if (!props.imageId) {
    alert('Error: Image ID is missing. Cannot save annotation.')
    console.error('Missing imageId prop:', props)
    return
  }

  saving.value = true
  try {
    // Check if annotation already exists for this image
    const existingAnnotations = await api.get(`/annotations/?project_id=${props.projectId}`)
    const existingAnnotation = existingAnnotations.find(
      (ann) => ann.data_id === props.imageId || ann.data_id === String(props.imageId)
    )

    if (existingAnnotation) {
      // Update existing annotation using PATCH
      const updateData = {
        id: existingAnnotation.id,
        description: description.value,
        label: selectedLabel.value,
      }
      const response = await api.patch('/annotations/', updateData)
      console.log('Annotation updated:', response)
      emit('save', response)
      alert('✓ Annotation updated successfully!')
    } else {
      // Create new annotation using POST
      const annotationData = {
        data_id: props.imageId,
        project_id: props.projectId,
        author_id: props.userId,
        description: description.value,
        label: selectedLabel.value,
        status: 'human annotation',
      }

      const response = await api.post('/annotations/', annotationData)
      console.log('Annotation saved:', response)
      emit('save', response)
      alert('✓ Annotation saved successfully!')
    }
  } catch (error) {
    console.error('Failed to save annotation:', error)
    alert(`Failed to save annotation: ${error?.data?.detail || error?.message || 'Unknown error'}`)
  } finally {
    saving.value = false
  }
}

const acceptAnnotation = async () => {
  saving.value = true
  try {
    const response = await api.post(`/annotations/update-status/${props.imageId}`, { status: 'certified' })
    emit('accept', response)
    alert('✓ Annotation accepted!')
  } catch (error) {
    console.error('Failed to accept annotation:', error)
    alert(`Failed to accept annotation: ${error?.data?.detail || error?.message || 'Unknown error'}`)
  } finally {
    saving.value = false
  }
}

const rejectAnnotation = async () => {
  const confirmReject = confirm('Are you sure you want to reject this annotation?')
  if (!confirmReject) return

  saving.value = true
  try {
    const response = await api.post(`/annotations/update-status/${props.imageId}`, { status: 'rejected' })
    emit('reject', response)
    alert('✓ Annotation rejected!')
  } catch (error) {
    console.error('Failed to reject annotation:', error)
    alert(`Failed to reject annotation: ${error?.data?.detail || error?.message || 'Unknown error'}`)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="flex-1 flex flex-col">
    <!-- Image Display Area with Konva -->
    <div class="flex-1 flex flex-col items-center justify-center p-4 bg-gray-100 relative overflow-hidden">
      <!-- Drawing Tools -->
      <div class="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-4 space-y-3 z-10 max-w-xs">
        <div class="font-bold text-sm text-gray-700 mb-2 border-b pb-2">Annotation Tools</div>

        <!-- Label Selection (Before Drawing) -->
        <div class="pb-3 border-b border-gray-200">
          <label class="block text-xs font-semibold text-gray-600 mb-1.5">Active Label</label>
          <div class="flex gap-1">
            <select
              v-model="selectedLabel"
              class="flex-1 px-2 py-1.5 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">No label</option>
              <option v-for="label in availableLabels" :key="label" :value="label">
                {{ label }}
              </option>
            </select>
            <button
              @click="showLabelInput = !showLabelInput"
              class="px-2 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
              title="Add new label"
            >
              <Plus :size="14" />
            </button>
          </div>

          <!-- Add New Label Input -->
          <div v-if="showLabelInput" class="mt-2 flex gap-1">
            <input
              v-model="newLabel"
              type="text"
              placeholder="New label name..."
              class="flex-1 px-2 py-1.5 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
              @keyup.enter="addLabel"
            />
            <button
              @click="addLabel"
              class="px-2 py-1.5 bg-green-500 hover:bg-green-600 text-white rounded transition-colors text-xs"
            >
              Add
            </button>
            <button
              @click="
                showLabelInput = false
                newLabel = ''
              "
              class="px-2 py-1.5 bg-gray-400 hover:bg-gray-500 text-white rounded transition-colors text-xs"
            >
              ×
            </button>
          </div>

          <!-- Current Label Color Indicator -->
          <div v-if="selectedLabel" class="mt-2 flex items-center gap-2">
            <div
              class="w-4 h-4 rounded border border-gray-300"
              :style="{ backgroundColor: getLabelColor(selectedLabel) }"
            ></div>
            <span class="text-xs text-gray-600"
              >Drawing with: <strong>{{ selectedLabel }}</strong></span
            >
          </div>
        </div>

        <!-- Mode Buttons -->
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="setDrawingMode('pan')"
            :class="[
              'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
              drawingMode === 'pan'
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
            ]"
            title="Pan Mode (P) - Drag to move image"
          >
            <Hand :size="18" />
            <span>Pan</span>
          </button>
          <button
            @click="setDrawingMode('select')"
            :class="[
              'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
              drawingMode === 'select'
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
            ]"
            title="Select Mode (S) - Click to select shapes"
          >
            <MousePointer :size="18" />
            <span>Select</span>
          </button>
          <button
            @click="setDrawingMode('rectangle')"
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
            @click="setDrawingMode('skeleton')"
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
            @click="setDrawingMode('mask')"
            :class="[
              'flex items-center gap-2 p-2 rounded-lg transition-all text-sm font-medium',
              drawingMode === 'mask'
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
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

        <!-- Mask Mode Options -->
        <div v-if="drawingMode === 'mask'" class="space-y-2">
          <!-- Sub-mode Selection -->
          <div class="grid grid-cols-2 gap-1">
            <button
              @click="setMaskSubMode('paint')"
              :class="[
                'p-1.5 rounded text-xs font-medium transition-all',
                maskSubMode === 'paint' ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              ]"
            >
              <Brush :size="14" class="inline mr-1" />
              Paint
            </button>
            <button
              @click="setMaskSubMode('polygon')"
              :class="[
                'p-1.5 rounded text-xs font-medium transition-all',
                maskSubMode === 'polygon' ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              ]"
            >
              <Pentagon :size="14" class="inline mr-1" />
              Polygon
            </button>
          </div>

          <!-- Instructions -->
          <div class="text-xs bg-pink-50 p-2 rounded border border-pink-200">
            <div v-if="maskSubMode === 'paint'" class="text-pink-700">
              <div class="font-medium mb-1">Paint Mode</div>
              <div>Click and drag to paint freely. Auto-creates bounding box.</div>
            </div>
            <div v-else-if="maskSubMode === 'polygon'" class="text-pink-700">
              <div class="font-medium mb-1">Polygon Mode</div>
              <div>Click to add points<br />Press Enter to finish<br />Press Escape to cancel</div>
            </div>
          </div>

          <!-- Action Buttons for Polygon Mode -->
          <div v-if="maskSubMode === 'polygon' && isDrawingMask" class="flex gap-2">
            <button
              @click="finishMaskPolygon"
              class="flex-1 p-2 rounded bg-green-100 hover:bg-green-200 transition-colors text-xs font-medium text-green-700"
              title="Finish Mask"
            >
              Done
            </button>
            <button
              @click="cancelMaskPolygon"
              class="flex-1 p-2 rounded bg-red-100 hover:bg-red-200 transition-colors text-xs font-medium text-red-700"
              title="Cancel Mask"
            >
              Cancel
            </button>
          </div>
        </div>

        <!-- Skeleton Instructions -->
        <div v-if="drawingMode === 'skeleton'" class="space-y-2">
          <!-- Phase Selection -->
          <div class="grid grid-cols-3 gap-1">
            <button
              @click="setSkeletonPhase('nodes')"
              :class="[
                'p-1.5 rounded text-xs font-medium transition-all',
                skeletonPhase === 'nodes' ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              ]"
            >
              1. Nodes
            </button>
            <button
              @click="setSkeletonPhase('edges')"
              :class="[
                'p-1.5 rounded text-xs font-medium transition-all',
                skeletonPhase === 'edges' ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              ]"
              :disabled="!currentSkeleton || currentSkeleton.keypoints.length < 2"
            >
              2. Edges
            </button>
            <button
              @click="setSkeletonPhase('labels')"
              :class="[
                'p-1.5 rounded text-xs font-medium transition-all',
                skeletonPhase === 'labels' ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              ]"
              :disabled="!currentSkeleton || currentSkeleton.keypoints.length === 0"
            >
              3. Labels
            </button>
          </div>

          <!-- Phase Instructions -->
          <div class="text-xs bg-purple-50 p-2 rounded border border-purple-200">
            <div v-if="skeletonPhase === 'nodes'" class="text-purple-700">
              <div class="font-medium mb-1">Phase 1: Place Nodes</div>
              <div>Click on the image to place keypoint nodes</div>
            </div>
            <div v-else-if="skeletonPhase === 'edges'" class="text-purple-700">
              <div class="font-medium mb-1">Phase 2: Draw Edges</div>
              <div>Click two nodes to connect them with an edge</div>
              <div v-if="selectedNodeForEdge !== null" class="mt-1 font-medium text-purple-900">
                Node {{ selectedNodeForEdge }} selected - click another node
              </div>
            </div>
            <div v-else-if="skeletonPhase === 'labels'" class="text-purple-700">
              <div class="font-medium mb-1">Phase 3: Assign Body Parts</div>
              <div>Click a node, then select a body part below</div>
              <div v-if="selectedNodeForLabel !== null" class="mt-1 font-medium text-purple-900">
                Node {{ selectedNodeForLabel }} selected
              </div>
            </div>
          </div>

          <!-- Body Part Selection (only in labels phase) -->
          <div v-if="skeletonPhase === 'labels' && selectedNodeForLabel !== null" class="max-h-32 overflow-y-auto">
            <div class="grid grid-cols-2 gap-1">
              <button
                v-for="part in availableBodyParts"
                :key="part"
                @click="assignBodyPartToNode(part)"
                class="p-1.5 text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 rounded transition-colors"
              >
                {{ part }}
              </button>
            </div>
          </div>

          <!-- Action Buttons -->
          <div v-if="currentSkeleton" class="flex gap-2">
            <button
              @click="finishSkeletonEarly"
              class="flex-1 p-2 rounded bg-green-100 hover:bg-green-200 transition-colors text-xs font-medium text-green-700"
              title="Finish Skeleton"
            >
              Done
            </button>
            <button
              @click="clearCurrentSkeleton"
              class="flex-1 p-2 rounded bg-red-100 hover:bg-red-200 transition-colors text-xs font-medium text-red-700"
              title="Cancel Skeleton"
            >
              Cancel
            </button>
          </div>
        </div>

        <!-- Edit Actions -->
        <div class="pt-2 border-t space-y-2">
          <div class="grid grid-cols-2 gap-2">
            <button
              @click="undo"
              :disabled="!canUndo"
              :class="[
                'flex items-center justify-center gap-1 p-2 rounded-lg transition-all text-sm',
                !canUndo
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
              ]"
              title="Undo (Ctrl+Z)"
            >
              <Undo :size="16" />
              <span>Undo</span>
            </button>
            <button
              @click="redo"
              :disabled="!canRedo"
              :class="[
                'flex items-center justify-center gap-1 p-2 rounded-lg transition-all text-sm',
                !canRedo
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
              ]"
              title="Redo (Ctrl+Y)"
            >
              <Redo :size="16" />
              <span>Redo</span>
            </button>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <button
              @click="copyShape"
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
              @click="exportAnnotations"
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
            @click="deleteSelectedShape"
            :disabled="!selectedShape"
            :class="[
              'w-full flex items-center justify-center gap-2 p-2 rounded-lg transition-all text-sm',
              !selectedShape
                ? 'bg-red-100 text-red-400 cursor-not-allowed'
                : 'bg-red-100 text-red-600 hover:bg-red-200',
            ]"
            title="Delete Selected (Delete)"
          >
            <Trash2 :size="16" />
            <span>Delete Selected</span>
          </button>
          <button
            v-if="selectedShape && selectedShape.masks && selectedShape.masks.length > 0"
            @click="clearMasksFromSelectedBox"
            class="w-full p-2 rounded-lg transition-all text-xs bg-purple-100 text-purple-600 hover:bg-purple-200"
            title="Clear Masks"
          >
            Clear Masks
          </button>
          <button
            @click="clearAllShapes"
            :disabled="shapes.length === 0"
            :class="[
              'w-full p-2 rounded-lg transition-all text-xs',
              shapes.length === 0
                ? 'bg-orange-100 text-orange-400 cursor-not-allowed'
                : 'bg-orange-100 text-orange-600 hover:bg-orange-200',
            ]"
            title="Clear All Annotations"
          >
            Clear All
          </button>
        </div>
      </div>

      <!-- Right Panel - Zoom and Image Controls -->
      <div class="absolute top-4 right-4 space-y-4 z-10">
        <!-- Zoom Indicator -->
        <div class="bg-white rounded-lg shadow-lg p-3">
          <div class="text-xs font-medium text-gray-600 mb-1">Zoom</div>
          <div class="text-lg font-bold text-gray-800">{{ Math.round(zoomLevel * 100) }}%</div>
          <button
            @click="resetZoom"
            class="mt-2 w-full px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs font-medium transition-colors"
            title="Reset Zoom (100%)"
          >
            Reset
          </button>
        </div>

        <!-- Image Adjustments -->
        <ImageAdjustments
          v-model:brightness="brightness"
          v-model:contrast="contrast"
          v-model:redChannel="redChannel"
          v-model:greenChannel="greenChannel"
          v-model:blueChannel="blueChannel"
          v-model:saturation="saturation"
          v-model:hue="hue"
          @update:brightness="applyImageFilters"
          @update:contrast="applyImageFilters"
          @update:redChannel="applyImageFilters"
          @update:greenChannel="applyImageFilters"
          @update:blueChannel="applyImageFilters"
          @update:saturation="applyImageFilters"
          @update:hue="applyImageFilters"
          @reset="resetImageFilters"
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

      <!-- Konva Container -->
      <div ref="konvaContainerRef" class="relative bg-white rounded-lg shadow-md w-full h-full"></div>

      <!-- Hidden image for reference -->
      <img ref="imageRef" :src="imageSrc" alt="Annotation image" class="hidden" />
    </div>

    <!-- Annotation Controls Panel -->
    <div class="bg-gray-50 border-t border-gray-200 p-4 space-y-4 max-h-[40%] overflow-y-auto">
      <!-- Description -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2">Description</label>
        <textarea
          v-model="description"
          placeholder="Add a description for this annotation..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
          rows="2"
        />
      </div>

      <!-- All Labels in Project -->
      <div v-if="availableLabels.length > 0">
        <label class="block text-sm font-semibold text-gray-700 mb-2">
          Project Labels <span class="text-xs font-normal text-gray-500">({{ availableLabels.length }} total)</span>
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="label in availableLabels"
            :key="label"
            @click="selectedLabel = label"
            :class="[
              'inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium transition-all',
              selectedLabel === label ? 'ring-2 ring-blue-500' : '',
            ]"
            :style="{ backgroundColor: getLabelColor(label) + '20', color: getLabelColor(label) }"
          >
            <div class="w-2 h-2 rounded-full" :style="{ backgroundColor: getLabelColor(label) }"></div>
            {{ label }}
          </button>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="grid grid-cols-3 gap-2">
        <button
          @click="saveAnnotation"
          :disabled="saving"
          class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-sm"
        >
          <Save :size="16" />
          <span>Save</span>
        </button>
        <button
          @click="acceptAnnotation"
          :disabled="saving"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-sm"
        >
          <Check :size="16" />
          <span>Accept</span>
        </button>
        <button
          @click="rejectAnnotation"
          :disabled="saving"
          class="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-sm"
        >
          <Trash2 :size="16" />
          <span>Reject</span>
        </button>
      </div>
    </div>
  </div>
</template>
