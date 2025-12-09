<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { Square, Circle, Save, Check, X, ArrowLeft, Trash2, History, Clock, Plus, Undo, Pencil, Palette, Pentagon, Paintbrush, Eraser, Pipette } from 'lucide-vue-next'
import Konva from 'konva'

const route = useRoute()
const router = useRouter()
const api = useApi()

// Image data
const image = ref(null)
const loading = ref(true)

// Konva stage and layer
const stageContainer = ref(null)
const stage = ref(null)
const layer = ref(null)
const imageNode = ref(null)
const drawingLayer = ref(null)

// Drawing state
const activeTool = ref('bbox') // 'bbox', 'polygon', 'keypoint', 'segmentation', 'skeleton', 'cuboid', 'line', 'point', 'eraser'
const isDrawing = ref(false)
const annotations = ref([])
const currentShape = ref(null)

// Advanced drawing state
const polygonPoints = ref([])
const freehandPoints = ref([])
const brushSize = ref(10)
const selectedColor = ref('#3498db')
const maskOpacity = ref(0.5)
const eraserSize = ref(20)
const showColorPicker = ref(false)

// Annotation task settings
const annotationTask = ref('object-detection') // 'object-detection', 'segmentation', 'keypoints', 'pose', 'lanes'
const currentLabel = ref('person')
const labels = ref(['person', 'car', 'bicycle', 'dog', 'cat', 'background', 'road', 'building'])
const showLabelDialog = ref(false)
const newLabelInput = ref('')

// Keypoint/Skeleton configuration
const keypointConnections = ref([
  [0, 1], [1, 2], [2, 3], [3, 4], // head to torso
  [1, 5], [5, 6], [6, 7], // left arm
  [1, 8], [8, 9], [9, 10], // right arm
  [1, 11], [11, 12], [12, 13], // left leg
  [1, 14], [14, 15], [15, 16], // right leg
])
const keypointLabels = ref([
  'nose', 'neck', 'right_shoulder', 'right_elbow', 'right_wrist',
  'left_shoulder', 'left_elbow', 'left_wrist',
  'right_hip', 'right_knee', 'right_ankle',
  'left_hip', 'left_knee', 'left_ankle',
  'right_eye', 'left_eye'
])
const currentKeypoints = ref([])

// Cuboid state for 3D bounding boxes
const cuboidPoints = ref([])
const cuboidStep = ref(0) // 0: front face, 1: back face

// Predefined colors
const colors = [
  '#3498db', '#e74c3c', '#27ae60', '#f39c12', 
  '#9b59b6', '#1abc9c', '#e67e22', '#34495e',
  '#f1c40f', '#16a085', '#c0392b', '#8e44ad'
]

// History tracking
const history = ref([])
const showHistory = ref(false)

// Canvas dimensions
const canvasWidth = ref(800)
const canvasHeight = ref(600)

// Fetch image data
const fetchImage = async () => {
  try {
    // TODO: Replace with actual API call
    // const response = await api.get(`/images/${route.params.id}`)
    // image.value = response
    
    // Mock data for now
    image.value = {
      id: route.params.id,
      location: `https://picsum.photos/800/600?random=${route.params.id}`,
      type: 'landscape'
    }
  } catch (error) {
    console.error('Failed to fetch image:', error)
  } finally {
    loading.value = false
  }
}

// Add history entry
const addHistoryEntry = (action, details) => {
  const entry = {
    id: Date.now(),
    action,
    details,
    timestamp: new Date().toISOString(),
    annotationCount: annotations.value.length
  }
  history.value.unshift(entry)
}

const setupKonva = (img) => {
  // Get container dimensions
  const container = stageContainer.value
  if (!container) return
  
  // Wait for DOM to fully render
  const containerWidth = container.parentElement?.clientWidth || window.innerWidth - 350
  const containerHeight = container.parentElement?.clientHeight || window.innerHeight - 100
  
  // Calculate scaling to fit image
  const scale = Math.min(
    containerWidth / img.width,
    containerHeight / img.height,
    1 // Don't scale up
  )
  
  canvasWidth.value = img.width * scale
  canvasHeight.value = img.height * scale
  
  // Create Konva stage
  stage.value = new Konva.Stage({
    container: stageContainer.value,
    width: canvasWidth.value,
    height: canvasHeight.value,
  })
  
  // Create image layer
  layer.value = new Konva.Layer()
  stage.value.add(layer.value)
  
  // Create drawing layer (for annotations)
  drawingLayer.value = new Konva.Layer()
  stage.value.add(drawingLayer.value)
  
  // Add image to layer
  imageNode.value = new Konva.Image({
    image: img,
    width: canvasWidth.value,
    height: canvasHeight.value,
  })
  layer.value.add(imageNode.value)
  layer.value.batchDraw()
  
  // Setup mouse events
  setupMouseEvents()
}

// Setup mouse events for Konva
const setupMouseEvents = () => {
  if (!stage.value) return
  
  stage.value.on('mousedown touchstart', handleMouseDown)
  stage.value.on('mousemove touchmove', handleMouseMove)
  stage.value.on('mouseup touchend', handleMouseUp)
  stage.value.on('contextmenu', handleContextMenu)
}

const handleMouseDown = (e) => {
  const pos = stage.value.getPointerPosition()
  
  // Polygon tool - add points on click
  if (activeTool.value === 'polygon') {
    polygonPoints.value.push(pos)
    drawPolygonPreview()
    return
  }
  
  // Keypoint tool - place keypoints
  if (activeTool.value === 'keypoint') {
    placeKeypoint(pos)
    return
  }
  
  // Point tool - single point annotation
  if (activeTool.value === 'point') {
    createPointAnnotation(pos)
    return
  }
  
  // Cuboid tool - 3D bounding box
  if (activeTool.value === 'cuboid') {
    handleCuboidClick(pos)
    return
  }
  
  // Eraser tool
  if (activeTool.value === 'eraser') {
    eraseAtPoint(pos.x, pos.y)
    return
  }
  
  isDrawing.value = true
  
  // Segmentation tool (brush-based mask painting)
  if (activeTool.value === 'segmentation') {
    freehandPoints.value = [pos.x, pos.y]
    currentShape.value = new Konva.Line({
      points: freehandPoints.value,
      stroke: selectedColor.value,
      strokeWidth: brushSize.value,
      lineCap: 'round',
      lineJoin: 'round',
      opacity: maskOpacity.value,
    })
    drawingLayer.value.add(currentShape.value)
    return
  }
  
  // Line tool - for lane detection, etc.
  if (activeTool.value === 'line') {
    currentShape.value = new Konva.Line({
      points: [pos.x, pos.y, pos.x, pos.y],
      stroke: selectedColor.value,
      strokeWidth: 3,
      lineCap: 'round',
      dash: [5, 5],
    })
    drawingLayer.value.add(currentShape.value)
    return
  }
  
  // Bounding Box tool (bbox)
  if (activeTool.value === 'bbox') {
    currentShape.value = new Konva.Rect({
      x: pos.x,
      y: pos.y,
      width: 0,
      height: 0,
      stroke: selectedColor.value,
      strokeWidth: 2,
      fill: selectedColor.value,
      opacity: 0.2,
      dash: [5, 5],
    })
    drawingLayer.value.add(currentShape.value)
  }
}

const handleMouseMove = (e) => {
  if (!isDrawing.value || !currentShape.value) return
  
  const pos = stage.value.getPointerPosition()
  
  // Segmentation tool (brush painting)
  if (activeTool.value === 'segmentation') {
    freehandPoints.value.push(pos.x, pos.y)
    currentShape.value.points(freehandPoints.value)
    drawingLayer.value.batchDraw()
    return
  }
  
  // Line tool
  if (activeTool.value === 'line') {
    const points = currentShape.value.points()
    currentShape.value.points([points[0], points[1], pos.x, pos.y])
    drawingLayer.value.batchDraw()
    return
  }
  
  // Bounding Box tool
  if (activeTool.value === 'bbox') {
    const startPos = { x: currentShape.value.x(), y: currentShape.value.y() }
    currentShape.value.width(pos.x - startPos.x)
    currentShape.value.height(pos.y - startPos.y)
    drawingLayer.value.batchDraw()
  }
}

const handleMouseUp = (e) => {
  if (!isDrawing.value || !currentShape.value) return
  
  isDrawing.value = false
  
  // Finalize the shape
  const annotation = {
    id: Date.now(),
    type: activeTool.value,
    color: selectedColor.value,
    label: currentLabel.value,
    created: new Date().toISOString(),
    shape: currentShape.value,
  }
  
  // Remove dash effect
  currentShape.value.dash([])
  
  if (activeTool.value === 'bbox') {
    const width = Math.abs(currentShape.value.width())
    const height = Math.abs(currentShape.value.height())
    
    if (width < 5 || height < 5) {
      currentShape.value.destroy()
      currentShape.value = null
      drawingLayer.value.batchDraw()
      return
    }
    
    // Normalize negative dimensions
    if (currentShape.value.width() < 0) {
      currentShape.value.x(currentShape.value.x() + currentShape.value.width())
      currentShape.value.width(Math.abs(currentShape.value.width()))
    }
    if (currentShape.value.height() < 0) {
      currentShape.value.y(currentShape.value.y() + currentShape.value.height())
      currentShape.value.height(Math.abs(currentShape.value.height()))
    }
    
    annotation.x = currentShape.value.x()
    annotation.y = currentShape.value.y()
    annotation.width = currentShape.value.width()
    annotation.height = currentShape.value.height()
    
    // Add label text
    addBBoxLabel(currentShape.value, annotation)
  } else if (activeTool.value === 'line') {
    const points = currentShape.value.points()
    const distance = Math.sqrt(
      Math.pow(points[2] - points[0], 2) + Math.pow(points[3] - points[1], 2)
    )
    
    if (distance < 5) {
      currentShape.value.destroy()
      currentShape.value = null
      drawingLayer.value.batchDraw()
      return
    }
    
    currentShape.value.opacity(1)
    annotation.points = points
    annotation.startX = points[0]
    annotation.startY = points[1]
    annotation.endX = points[2]
    annotation.endY = points[3]
  } else if (activeTool.value === 'segmentation') {
    if (freehandPoints.value.length < 4) {
      currentShape.value.destroy()
      currentShape.value = null
      freehandPoints.value = []
      drawingLayer.value.batchDraw()
      return
    }
    
    annotation.points = [...freehandPoints.value]
    annotation.brushSize = brushSize.value
    annotation.opacity = maskOpacity.value
  }
  
  // Make shape interactive
  makeShapeInteractive(currentShape.value, annotation)
  
  annotations.value.push(annotation)
  addHistoryEntry('added', `${annotation.type} annotation: ${annotation.label}`)
  
  currentShape.value = null
  freehandPoints.value = []
  drawingLayer.value.batchDraw()
}

// Make shapes interactive (draggable, selectable, deletable)
const makeShapeInteractive = (shape, annotation) => {
  if (!shape) return
  
  shape.draggable(true)
  
  // Hover effects
  shape.on('mouseenter', () => {
    stage.value.container().style.cursor = 'move'
    shape.strokeWidth(3)
    drawingLayer.value.batchDraw()
  })
  
  shape.on('mouseleave', () => {
    stage.value.container().style.cursor = 'crosshair'
    shape.strokeWidth(2)
    drawingLayer.value.batchDraw()
  })
  
  // Click to select
  shape.on('click', () => {
    // Highlight selected shape
    drawingLayer.value.children.forEach(child => {
      if (child !== shape) {
        child.strokeWidth(2)
      }
    })
    shape.strokeWidth(4)
    drawingLayer.value.batchDraw()
  })
}

const deleteAnnotation = (id) => {
  const annotation = annotations.value.find(ann => ann.id === id)
  if (!annotation) return
  
  annotations.value = annotations.value.filter(ann => ann.id !== id)
  
  // Remove shape from layer
  if (annotation.shape) {
    annotation.shape.destroy()
    drawingLayer.value.batchDraw()
  }
  
  // Add history entry
  addHistoryEntry('deleted', `${annotation.type} annotation removed`)
}

const clearAllAnnotations = () => {
  const count = annotations.value.length
  
  // Remove all shapes from layer
  drawingLayer.value.destroyChildren()
  drawingLayer.value.batchDraw()
  
  annotations.value = []
  
  // Add history entry
  if (count > 0) {
    addHistoryEntry('cleared', `All ${count} annotations cleared`)
  }
}

// Add label to bounding box
const addBBoxLabel = (shape, annotation) => {
  if (!shape || !annotation.label) return
  
  const labelText = new Konva.Text({
    x: shape.x(),
    y: shape.y() - 22,
    text: annotation.label,
    fontSize: 14,
    fontFamily: 'Arial',
    fill: 'white',
    padding: 5,
  })
  
  const labelBg = new Konva.Rect({
    x: shape.x(),
    y: shape.y() - 22,
    width: labelText.width(),
    height: labelText.height(),
    fill: selectedColor.value,
    cornerRadius: 3,
  })
  
  const labelGroup = new Konva.Group()
  labelGroup.add(labelBg)
  labelGroup.add(labelText)
  
  drawingLayer.value.add(labelGroup)
  annotation.labelShape = labelGroup
  
  // Make label follow bbox when dragged
  shape.on('dragmove', () => {
    labelGroup.x(shape.x())
    labelGroup.y(shape.y() - 22)
  })
}

// Keypoint annotation
const placeKeypoint = (pos) => {
  const keypoint = new Konva.Circle({
    x: pos.x,
    y: pos.y,
    radius: 6,
    fill: selectedColor.value,
    stroke: 'white',
    strokeWidth: 2,
    draggable: true,
  })
  
  drawingLayer.value.add(keypoint)
  
  const annotation = {
    id: Date.now(),
    type: 'keypoint',
    color: selectedColor.value,
    label: keypointLabels.value[currentKeypoints.value.length % keypointLabels.value.length],
    x: pos.x,
    y: pos.y,
    created: new Date().toISOString(),
    shape: keypoint,
  }
  
  // Add label
  const label = new Konva.Text({
    x: pos.x + 10,
    y: pos.y - 10,
    text: annotation.label,
    fontSize: 12,
    fill: selectedColor.value,
    fontStyle: 'bold',
  })
  drawingLayer.value.add(label)
  annotation.labelShape = label
  
  keypoint.on('dragmove', () => {
    label.x(keypoint.x() + 10)
    label.y(keypoint.y() - 10)
    annotation.x = keypoint.x()
    annotation.y = keypoint.y()
  })
  
  makeShapeInteractive(keypoint, annotation)
  annotations.value.push(annotation)
  currentKeypoints.value.push(annotation)
  addHistoryEntry('added', `Keypoint: ${annotation.label}`)
  
  drawingLayer.value.batchDraw()
}

// Point annotation (for counting, localization)
const createPointAnnotation = (pos) => {
  const point = new Konva.Circle({
    x: pos.x,
    y: pos.y,
    radius: 5,
    fill: selectedColor.value,
    stroke: 'white',
    strokeWidth: 2,
    draggable: true,
  })
  
  drawingLayer.value.add(point)
  
  const annotation = {
    id: Date.now(),
    type: 'point',
    color: selectedColor.value,
    label: currentLabel.value,
    x: pos.x,
    y: pos.y,
    created: new Date().toISOString(),
    shape: point,
  }
  
  point.on('dragmove', () => {
    annotation.x = point.x()
    annotation.y = point.y()
  })
  
  makeShapeInteractive(point, annotation)
  annotations.value.push(annotation)
  addHistoryEntry('added', `Point: ${annotation.label}`)
  
  drawingLayer.value.batchDraw()
}

// Cuboid annotation (3D bounding box)
const handleCuboidClick = (pos) => {
  cuboidPoints.value.push(pos)
  
  if (cuboidPoints.value.length === 4 && cuboidStep.value === 0) {
    // Front face complete, draw it
    drawCuboidPreview()
    cuboidStep.value = 1
  } else if (cuboidPoints.value.length === 8) {
    // Both faces complete, create cuboid
    completeCuboid()
  } else {
    drawCuboidPreview()
  }
}

const drawCuboidPreview = () => {
  // Remove old preview
  const oldPreview = drawingLayer.value.find('.cuboid-preview')
  oldPreview.forEach(p => p.destroy())
  
  if (cuboidPoints.value.length >= 4) {
    // Draw front face
    const frontFace = new Konva.Line({
      points: [
        cuboidPoints.value[0].x, cuboidPoints.value[0].y,
        cuboidPoints.value[1].x, cuboidPoints.value[1].y,
        cuboidPoints.value[2].x, cuboidPoints.value[2].y,
        cuboidPoints.value[3].x, cuboidPoints.value[3].y,
      ],
      stroke: selectedColor.value,
      strokeWidth: 2,
      closed: true,
      dash: [5, 5],
      name: 'cuboid-preview',
    })
    drawingLayer.value.add(frontFace)
  }
  
  if (cuboidPoints.value.length > 4) {
    // Draw back face and connections
    const backPoints = cuboidPoints.value.slice(4)
    if (backPoints.length > 1) {
      const backLine = new Konva.Line({
        points: backPoints.flatMap(p => [p.x, p.y]),
        stroke: selectedColor.value,
        strokeWidth: 2,
        dash: [5, 5],
        name: 'cuboid-preview',
      })
      drawingLayer.value.add(backLine)
    }
    
    // Draw connecting lines
    for (let i = 0; i < Math.min(4, backPoints.length); i++) {
      const line = new Konva.Line({
        points: [cuboidPoints.value[i].x, cuboidPoints.value[i].y, backPoints[i].x, backPoints[i].y],
        stroke: selectedColor.value,
        strokeWidth: 2,
        dash: [5, 5],
        name: 'cuboid-preview',
      })
      drawingLayer.value.add(line)
    }
  }
  
  // Draw points
  cuboidPoints.value.forEach((point, i) => {
    const circle = new Konva.Circle({
      x: point.x,
      y: point.y,
      radius: 4,
      fill: i < 4 ? selectedColor.value : '#ff6b6b',
      name: 'cuboid-preview',
    })
    drawingLayer.value.add(circle)
  })
  
  drawingLayer.value.batchDraw()
}

const completeCuboid = () => {
  if (cuboidPoints.value.length !== 8) return
  
  // Remove preview
  const oldPreview = drawingLayer.value.find('.cuboid-preview')
  oldPreview.forEach(p => p.destroy())
  
  // Create cuboid group
  const group = new Konva.Group({ draggable: true })
  
  // Draw front face
  const frontFace = new Konva.Line({
    points: [
      cuboidPoints.value[0].x, cuboidPoints.value[0].y,
      cuboidPoints.value[1].x, cuboidPoints.value[1].y,
      cuboidPoints.value[2].x, cuboidPoints.value[2].y,
      cuboidPoints.value[3].x, cuboidPoints.value[3].y,
    ],
    stroke: selectedColor.value,
    strokeWidth: 2,
    closed: true,
  })
  
  // Draw back face
  const backFace = new Konva.Line({
    points: [
      cuboidPoints.value[4].x, cuboidPoints.value[4].y,
      cuboidPoints.value[5].x, cuboidPoints.value[5].y,
      cuboidPoints.value[6].x, cuboidPoints.value[6].y,
      cuboidPoints.value[7].x, cuboidPoints.value[7].y,
    ],
    stroke: selectedColor.value,
    strokeWidth: 2,
    closed: true,
    opacity: 0.6,
  })
  
  // Draw connecting lines
  for (let i = 0; i < 4; i++) {
    const line = new Konva.Line({
      points: [
        cuboidPoints.value[i].x, cuboidPoints.value[i].y,
        cuboidPoints.value[i + 4].x, cuboidPoints.value[i + 4].y,
      ],
      stroke: selectedColor.value,
      strokeWidth: 2,
      dash: [5, 3],
    })
    group.add(line)
  }
  
  group.add(backFace)
  group.add(frontFace)
  drawingLayer.value.add(group)
  
  const annotation = {
    id: Date.now(),
    type: 'cuboid',
    color: selectedColor.value,
    label: currentLabel.value,
    points: [...cuboidPoints.value],
    created: new Date().toISOString(),
    shape: group,
  }
  
  makeShapeInteractive(group, annotation)
  annotations.value.push(annotation)
  addHistoryEntry('added', `3D BBox: ${annotation.label}`)
  
  cuboidPoints.value = []
  cuboidStep.value = 0
  drawingLayer.value.batchDraw()
}

const cancelCuboid = () => {
  const oldPreview = drawingLayer.value.find('.cuboid-preview')
  oldPreview.forEach(p => p.destroy())
  cuboidPoints.value = []
  cuboidStep.value = 0
  drawingLayer.value.batchDraw()
}

// Draw skeleton connections
const drawSkeleton = () => {
  // Remove old skeleton lines
  const oldLines = drawingLayer.value.find('.skeleton-line')
  oldLines.forEach(l => l.destroy())
  
  if (currentKeypoints.value.length < 2) return
  
  keypointConnections.value.forEach(([start, end]) => {
    if (start < currentKeypoints.value.length && end < currentKeypoints.value.length) {
      const startKp = currentKeypoints.value[start]
      const endKp = currentKeypoints.value[end]
      
      const line = new Konva.Line({
        points: [startKp.x, startKp.y, endKp.x, endKp.y],
        stroke: selectedColor.value,
        strokeWidth: 3,
        opacity: 0.6,
        name: 'skeleton-line',
      })
      drawingLayer.value.add(line)
      line.moveToBottom()
    }
  })
  
  drawingLayer.value.batchDraw()
}

const drawPolygonPreview = () => {
  if (!drawingLayer.value || polygonPoints.value.length === 0) return
  
  // Remove old preview if exists
  const oldPreview = drawingLayer.value.findOne('.polygon-preview')
  if (oldPreview) oldPreview.destroy()
  
  const oldPoints = drawingLayer.value.find('.polygon-point')
  oldPoints.forEach(p => p.destroy())
  
  // Draw lines
  if (polygonPoints.value.length > 1) {
    const points = []
    polygonPoints.value.forEach(p => {
      points.push(p.x, p.y)
    })
    
    const line = new Konva.Line({
      points: points,
      stroke: selectedColor.value,
      strokeWidth: 2,
      dash: [5, 5],
      name: 'polygon-preview',
    })
    drawingLayer.value.add(line)
  }
  
  // Draw vertex points
  polygonPoints.value.forEach(point => {
    const circle = new Konva.Circle({
      x: point.x,
      y: point.y,
      radius: 4,
      fill: selectedColor.value,
      name: 'polygon-point',
    })
    drawingLayer.value.add(circle)
  })
  
  drawingLayer.value.batchDraw()
}

const completePolygon = () => {
  if (polygonPoints.value.length < 3) return
  
  // Convert points to flat array
  const points = []
  polygonPoints.value.forEach(p => {
    points.push(p.x, p.y)
  })
  
  // Create polygon shape
  const polygon = new Konva.Line({
    points: points,
    stroke: selectedColor.value,
    strokeWidth: 2,
    fill: selectedColor.value,
    opacity: 0.2,
    closed: true,
  })
  
  drawingLayer.value.add(polygon)
  
  const annotation = {
    id: Date.now(),
    type: 'polygon',
    color: selectedColor.value,
    points: [...polygonPoints.value],
    created: new Date().toISOString(),
    shape: polygon,
  }
  
  makeShapeInteractive(polygon, annotation)
  annotations.value.push(annotation)
  addHistoryEntry('added', `Polygon with ${polygonPoints.value.length} vertices added`)
  
  // Clear preview and points
  const oldPreview = drawingLayer.value.findOne('.polygon-preview')
  if (oldPreview) oldPreview.destroy()
  const oldPoints = drawingLayer.value.find('.polygon-point')
  oldPoints.forEach(p => p.destroy())
  
  polygonPoints.value = []
  drawingLayer.value.batchDraw()
}

const cancelPolygon = () => {
  // Clear preview and points
  const oldPreview = drawingLayer.value.findOne('.polygon-preview')
  if (oldPreview) oldPreview.destroy()
  const oldPoints = drawingLayer.value.find('.polygon-point')
  oldPoints.forEach(p => p.destroy())
  
  polygonPoints.value = []
  drawingLayer.value.batchDraw()
}

const eraseAtPoint = (x, y) => {
  let erasedCount = 0
  
  annotations.value = annotations.value.filter(ann => {
    let shouldKeep = true
    
    if (ann.type === 'rectangle') {
      if (x >= ann.x && x <= ann.x + ann.width && y >= ann.y && y <= ann.y + ann.height) {
        shouldKeep = false
      }
    } else if (ann.type === 'circle') {
      const dist = Math.sqrt(Math.pow(x - ann.centerX, 2) + Math.pow(y - ann.centerY, 2))
      if (dist <= ann.radius) {
        shouldKeep = false
      }
    } else if (ann.points) {
      // Check if any point is within eraser radius
      for (let i = 0; i < ann.points.length; i += 2) {
        const px = ann.points[i]
        const py = ann.points[i + 1]
        const dist = Math.sqrt(Math.pow(x - px, 2) + Math.pow(y - py, 2))
        if (dist <= eraserSize.value) {
          shouldKeep = false
          break
        }
      }
    }
    
    if (!shouldKeep) {
      erasedCount++
      if (ann.shape) {
        ann.shape.destroy()
      }
    }
    
    return shouldKeep
  })
  
  if (erasedCount > 0) {
    drawingLayer.value.batchDraw()
    addHistoryEntry('deleted', `Erased ${erasedCount} annotation(s)`)
  }
}

const undoLastAnnotation = () => {
  if (annotations.value.length > 0) {
    const removed = annotations.value.pop()
    if (removed.shape) {
      removed.shape.destroy()
      drawingLayer.value.batchDraw()
    }
    addHistoryEntry('deleted', `Undid ${removed.type} annotation`)
  }
}

const handleKeyDown = (e) => {
  if (e.ctrlKey && e.key === 'z') {
    e.preventDefault()
    undoLastAnnotation()
  } else if (e.key === 'Enter' && activeTool.value === 'polygon') {
    e.preventDefault()
    completePolygon()
  } else if (e.key === 'Escape' && activeTool.value === 'polygon') {
    e.preventDefault()
    cancelPolygon()
  }
}

const handleContextMenu = (e) => {
  e.evt.preventDefault()
  if (activeTool.value === 'polygon' && polygonPoints.value.length > 0) {
    completePolygon()
  }
}

const saveAnnotations = async () => {
  try {
    // TODO: Implement API call to save annotations
    // await api.post(`/images/${route.params.id}/annotations`, { annotations: annotations.value })
    console.log('Saving annotations:', annotations.value)
    addHistoryEntry('saved', `${annotations.value.length} annotations saved`)
    alert('Annotations saved! (Currently console.log only)')
  } catch (error) {
    console.error('Failed to save annotations:', error)
  }
}

const approveAnnotations = async () => {
  try {
    // TODO: Implement API call to approve annotations
    // await api.post(`/images/${route.params.id}/approve`)
    console.log('Approving annotations:', annotations.value)
    addHistoryEntry('approved', `${annotations.value.length} annotations approved`)
    alert('Annotations approved! (Currently console.log only)')
  } catch (error) {
    console.error('Failed to approve annotations:', error)
  }
}

const toggleHistory = () => {
  showHistory.value = !showHistory.value
}

const getActionIcon = (action) => {
  switch(action) {
    case 'opened': return Clock
    case 'added': return Plus
    case 'deleted': return Trash2
    case 'cleared': return X
    case 'saved': return Save
    case 'approved': return Check
    default: return History
  }
}

const getActionColor = (action) => {
  switch(action) {
    case 'opened': return '#3498db'
    case 'added': return '#27ae60'
    case 'deleted': return '#e74c3c'
    case 'cleared': return '#e67e22'
    case 'saved': return '#3498db'
    case 'approved': return '#27ae60'
    default: return '#95a5a6'
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  
  if (diffSecs < 60) return `${diffSecs}s ago`
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  
  return date.toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const handleClose = () => {
  router.push('/')
}

const addNewLabel = () => {
  if (newLabelInput.value.trim() && !labels.value.includes(newLabelInput.value.trim())) {
    labels.value.push(newLabelInput.value.trim())
    currentLabel.value = newLabelInput.value.trim()
    newLabelInput.value = ''
    showLabelDialog.value = false
  }
}

const formatCoords = (annotation) => {
  if (annotation.type === 'bbox') {
    return `(${Math.round(annotation.x)}, ${Math.round(annotation.y)}) ${Math.round(annotation.width)}×${Math.round(annotation.height)}`
  } else if (annotation.type === 'polygon' && annotation.points) {
    return `${annotation.points.length} vertices`
  } else if (annotation.type === 'segmentation' && annotation.points) {
    return `${Math.floor(annotation.points.length / 2)} points • ${annotation.brushSize}px brush`
  } else if (annotation.type === 'keypoint') {
    return `(${Math.round(annotation.x)}, ${Math.round(annotation.y)})`
  } else if (annotation.type === 'point') {
    return `(${Math.round(annotation.x)}, ${Math.round(annotation.y)})`
  } else if (annotation.type === 'line') {
    const length = Math.sqrt(
      Math.pow(annotation.endX - annotation.startX, 2) + 
      Math.pow(annotation.endY - annotation.startY, 2)
    )
    return `Length: ${Math.round(length)}px`
  } else if (annotation.type === 'cuboid') {
    return `8 vertices (3D)`
  }
  return ''
}

// Initialize
onMounted(async () => {
  await fetchImage()
  
  if (stageContainer.value && image.value) {
    const img = new Image()
    img.crossOrigin = 'Anonymous'
    img.onload = () => {
      setupKonva(img)
      addHistoryEntry('opened', 'Image opened for annotation')
    }
    img.src = image.value.location
  }
  
  // Add keyboard event listener
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  // Cleanup keyboard event listener
  window.removeEventListener('keydown', handleKeyDown)
  
  // Cleanup Konva
  if (stage.value) {
    stage.value.destroy()
  }
})
</script>

<template>
  <div class="annotation-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading image...</p>
    </div>
    
    <!-- Main Content -->
    <template v-else-if="image">
      <!-- Left Sidebar -->
      <div class="annotation-sidebar">
        <div class="sidebar-header">
          <h2>Annotations</h2>
          <span class="annotation-count">{{ annotations.length }}</span>
        </div>
        
        <!-- Annotation Task Selector -->
        <div class="task-section">
          <h3>Annotation Task</h3>
          <select v-model="annotationTask" class="task-select">
            <option value="object-detection">Object Detection</option>
            <option value="segmentation">Instance Segmentation</option>
            <option value="keypoints">Keypoint Detection</option>
            <option value="pose">Pose Estimation</option>
            <option value="lanes">Lane Detection</option>
            <option value="3d-bbox">3D Bounding Box</option>
          </select>
        </div>
        
        <!-- Drawing Tools -->
        <div class="tools-section">
          <h3>Drawing Tools</h3>
          <div class="tool-buttons">
            <button 
              :class="['tool-btn', { active: activeTool === 'bbox' }]"
              @click="activeTool = 'bbox'; cancelPolygon(); cancelCuboid()"
              title="Bounding Box"
            >
              <Square :size="18" />
              <span>BBox</span>
            </button>
            <button 
              :class="['tool-btn', { active: activeTool === 'polygon' }]"
              @click="activeTool = 'polygon'; cancelCuboid()"
              title="Polygon Segmentation"
            >
              <Pentagon :size="18" />
              <span>Polygon</span>
            </button>
            <button 
              :class="['tool-btn', { active: activeTool === 'segmentation' }]"
              @click="activeTool = 'segmentation'; cancelPolygon(); cancelCuboid()"
              title="Brush Segmentation"
            >
              <Paintbrush :size="18" />
              <span>Segment</span>
            </button>
            <button 
              :class="['tool-btn', { active: activeTool === 'keypoint' }]"
              @click="activeTool = 'keypoint'; cancelPolygon(); cancelCuboid()"
              title="Keypoint"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 3v6M12 15v6M3 12h6M15 12h6" />
              </svg>
              <span>Keypoint</span>
            </button>
            <button 
              :class="['tool-btn', { active: activeTool === 'point' }]"
              @click="activeTool = 'point'; cancelPolygon(); cancelCuboid()"
              title="Point Annotation"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="4" />
              </svg>
              <span>Point</span>
            </button>
            <button 
              :class="['tool-btn', { active: activeTool === 'line' }]"
              @click="activeTool = 'line'; cancelPolygon(); cancelCuboid()"
              title="Line"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="19" x2="19" y2="5" />
              </svg>
              <span>Line</span>
            </button>
            <button 
              :class="['tool-btn', { active: activeTool === 'cuboid' }]"
              @click="activeTool = 'cuboid'; cancelPolygon()"
              title="3D Bounding Box"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                <line x1="12" y1="22.08" x2="12" y2="12" />
              </svg>
              <span>3D Box</span>
            </button>
            <button 
              :class="['tool-btn', { active: activeTool === 'eraser' }]"
              @click="activeTool = 'eraser'; cancelPolygon(); cancelCuboid()"
              title="Eraser"
            >
              <Eraser :size="18" />
              <span>Erase</span>
            </button>
          </div>
          
          <!-- Polygon Controls -->
          <div v-if="activeTool === 'polygon' && polygonPoints.length > 0" class="polygon-controls">
            <div class="control-hint">
              {{ polygonPoints.length }} points • Right-click or press Enter to complete
            </div>
            <div class="control-buttons">
              <button class="complete-btn" @click="completePolygon">Complete</button>
              <button class="cancel-btn" @click="cancelPolygon">Cancel</button>
            </div>
          </div>
          
          <!-- Cuboid Controls -->
          <div v-if="activeTool === 'cuboid' && cuboidPoints.length > 0" class="polygon-controls">
            <div class="control-hint">
              {{ cuboidStep === 0 ? 'Front face' : 'Back face' }}: {{ cuboidPoints.length - (cuboidStep * 4) }}/4 points
            </div>
            <div class="control-buttons">
              <button class="cancel-btn" @click="cancelCuboid">Cancel</button>
            </div>
          </div>
          
          <!-- Keypoint Progress -->
          <div v-if="activeTool === 'keypoint' && currentKeypoints.length > 0" class="control-group">
            <div class="keypoint-progress">
              <span>{{ currentKeypoints.length }} keypoints placed</span>
              <button class="clear-keypoints-btn" @click="currentKeypoints = []; drawSkeleton()">
                Clear All
              </button>
            </div>
            <button v-if="currentKeypoints.length >= 2" class="skeleton-btn" @click="drawSkeleton">
              Draw Skeleton
            </button>
          </div>
          
          <!-- Label Selector -->
          <div class="control-group">
            <label>Current Label</label>
            <select v-model="currentLabel" class="label-select">
              <option v-for="label in labels" :key="label" :value="label">
                {{ label }}
              </option>
            </select>
            <button class="add-label-btn" @click="showLabelDialog = true">
              <Plus :size="16" />
              Add Label
            </button>
          </div>
          
          <!-- Brush Size Slider -->
          <div v-if="activeTool === 'segmentation'" class="control-group">
            <label>Brush Size: {{ brushSize }}px</label>
            <input 
              v-model.number="brushSize" 
              type="range" 
              min="1" 
              max="50" 
              class="slider"
            />
          </div>
          
          <!-- Eraser Size Slider -->
          <div v-if="activeTool === 'eraser'" class="control-group">
            <label>Eraser Size: {{ eraserSize }}px</label>
            <input 
              v-model.number="eraserSize" 
              type="range" 
              min="5" 
              max="100" 
              class="slider"
            />
          </div>
          
          <!-- Mask Opacity Slider -->
          <div v-if="activeTool === 'segmentation'" class="control-group">
            <label>Opacity: {{ Math.round(maskOpacity * 100) }}%</label>
            <input 
              v-model.number="maskOpacity" 
              type="range" 
              min="0.1" 
              max="1" 
              step="0.1" 
              class="slider"
            />
          </div>
          
          <!-- Color Selector -->
          <div class="control-group">
            <label>Color</label>
            <div class="color-selector">
              <div class="color-grid">
                <button 
                  v-for="color in colors" 
                  :key="color"
                  :class="['color-btn', { active: selectedColor === color }]"
                  :style="{ backgroundColor: color }"
                  @click="selectedColor = color"
                  :title="color"
                ></button>
              </div>
              <div class="custom-color">
                <input 
                  v-model="selectedColor" 
                  type="color" 
                  class="color-input"
                />
                <span class="color-value">{{ selectedColor }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Annotations List -->
        <div class="annotations-list">
          <h3>Shapes ({{ annotations.length }})</h3>
          <div v-if="annotations.length === 0" class="empty-state">
            <p>No annotations yet</p>
            <p class="hint">Draw on the image to create annotations</p>
          </div>
          <div v-else class="annotation-items">
            <div 
              v-for="annotation in annotations" 
              :key="annotation.id" 
              class="annotation-item"
            >
              <div class="annotation-info">
                <div class="annotation-type">
                  <Square v-if="annotation.type === 'bbox'" :size="16" />
                  <Pentagon v-if="annotation.type === 'polygon'" :size="16" />
                  <Paintbrush v-if="annotation.type === 'segmentation'" :size="16" />
                  <svg v-if="annotation.type === 'keypoint'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <svg v-if="annotation.type === 'point'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="4" />
                  </svg>
                  <svg v-if="annotation.type === 'line'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="5" y1="19" x2="19" y2="5" />
                  </svg>
                  <svg v-if="annotation.type === 'cuboid'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                  </svg>
                  <span 
                    class="color-dot" 
                    :style="{ backgroundColor: annotation.color }"
                  ></span>
                  <span class="annotation-label">{{ annotation.label }}</span>
                </div>
                <div class="annotation-coords">
                  {{ formatCoords(annotation) }}
                </div>
              </div>
              <button 
                class="delete-btn" 
                @click="deleteAnnotation(annotation.id)"
                title="Delete annotation"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="action-buttons">
          <button class="action-btn save-btn" @click="saveAnnotations">
            <Save :size="20" />
            <span>Save</span>
          </button>
          <button class="action-btn approve-btn" @click="approveAnnotations">
            <Check :size="20" />
            <span>Approve</span>
          </button>
          <button class="action-btn clear-btn" @click="clearAllAnnotations">
            <Trash2 :size="20" />
            <span>Clear All</span>
          </button>
          <button class="action-btn history-btn" @click="toggleHistory">
            <History :size="20" />
            <span>History ({{ history.length }})</span>
          </button>
        </div>
      </div>
      
      <!-- History Panel -->
      <div v-if="showHistory" class="history-panel">
        <div class="history-header">
          <div class="history-title">
            <History :size="20" />
            <h2>Modification History</h2>
          </div>
          <button class="close-history-btn" @click="showHistory = false">
            <X :size="20" />
          </button>
        </div>
        
        <div class="history-content">
          <div v-if="history.length === 0" class="history-empty">
            <History :size="48" />
            <p>No history yet</p>
          </div>
          
          <div v-else class="history-timeline">
            <div 
              v-for="entry in history" 
              :key="entry.id" 
              class="history-entry"
            >
              <div class="history-icon" :style="{ background: getActionColor(entry.action) + '20', color: getActionColor(entry.action) }">
                <component :is="getActionIcon(entry.action)" :size="16" />
              </div>
              <div class="history-details">
                <div class="history-action">{{ entry.action }}</div>
                <div class="history-description">{{ entry.details }}</div>
                <div class="history-meta">
                  <span class="history-time">{{ formatTime(entry.timestamp) }}</span>
                  <span class="history-count">{{ entry.annotationCount }} annotations</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Main Canvas Area -->
      <div class="annotation-main">
        <div class="main-header">
          <button class="back-btn" @click="handleClose">
            <ArrowLeft :size="20" />
            <span>Back to Gallery</span>
          </button>
          <div class="image-info">
            <h2>Image #{{ image.id }}</h2>
            <span class="image-meta">{{ image.type }} | Active tool: {{ activeTool }}</span>
          </div>
        </div>
        
        <div class="canvas-container">
          <div ref="stageContainer" class="konva-container"></div>
          
          <!-- Canvas Hints -->
          <div v-if="activeTool === 'polygon' && polygonPoints.length > 0" class="canvas-hint">
            Click to add points • Right-click or Enter to complete • Esc to cancel
          </div>
          <div v-else-if="activeTool === 'cuboid' && cuboidPoints.length > 0" class="canvas-hint">
            {{ cuboidStep === 0 ? 'Click to draw front face (4 corners)' : 'Click to draw back face (4 corners)' }}
          </div>
          <div v-else-if="activeTool === 'keypoint'" class="canvas-hint">
            Click to place keypoints • {{ keypointLabels[currentKeypoints.length % keypointLabels.length] }}
          </div>
          <div v-else-if="activeTool === 'segmentation'" class="canvas-hint">
            Click and drag to paint segmentation mask
          </div>
          <div v-else-if="activeTool === 'eraser'" class="canvas-hint">
            Click and drag to erase annotations
          </div>
          <div v-else-if="activeTool === 'line'" class="canvas-hint">
            Click and drag to draw line
          </div>
          <div v-else-if="activeTool === 'point'" class="canvas-hint">
            Click to place point annotation
          </div>
          <div v-else-if="activeTool === 'bbox'" class="canvas-hint">
            Click and drag to draw bounding box
          </div>
        </div>
      </div>
    </template>
  </div>
  
  <!-- Label Dialog -->
  <div v-if="showLabelDialog" class="label-dialog-overlay" @click="showLabelDialog = false">
    <div class="label-dialog" @click.stop>
      <div class="dialog-header">
        <h3>Add New Label</h3>
        <button @click="showLabelDialog = false">
          <X :size="20" />
        </button>
      </div>
      <div class="dialog-content">
        <input 
          v-model="newLabelInput" 
          type="text" 
          placeholder="Enter label name..."
          @keyup.enter="addNewLabel"
          class="label-input"
        />
      </div>
      <div class="dialog-actions">
        <button @click="showLabelDialog = false" class="cancel-btn">Cancel</button>
        <button @click="addNewLabel" class="complete-btn">Add Label</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.annotation-page {
  display: flex;
  height: 100vh;
  background: #f5f6fa;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.spinner {
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Sidebar */
.annotation-sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #e1e8ed;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.annotation-count {
  background: #3498db;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

/* Task Section */
.task-section {
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.task-section h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.task-select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  background: white;
  color: #2c3e50;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.task-select:hover {
  border-color: #3498db;
}

.task-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* Tools Section */
.tools-section {
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.tools-section h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tool-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

.tool-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 4px;
  border: 2px solid #e1e8ed;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #2c3e50;
}

.tool-btn:hover {
  border-color: #3498db;
  background: #f8f9fa;
}

.tool-btn.active {
  border-color: #3498db;
  background: #3498db;
  color: white;
}

.tool-btn span {
  font-size: 10px;
  font-weight: 600;
}

.tool-btn svg {
  flex-shrink: 0;
}

/* Polygon Controls */
.polygon-controls {
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px solid #3498db;
}

.control-hint {
  font-size: 12px;
  color: #2c3e50;
  margin-bottom: 8px;
  text-align: center;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

.complete-btn, .cancel-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.complete-btn {
  background: #27ae60;
  color: white;
}

.complete-btn:hover {
  background: #229954;
}

.cancel-btn {
  background: #e74c3c;
  color: white;
}

.cancel-btn:hover {
  background: #c0392b;
}

/* Control Groups */
.control-group {
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.control-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e1e8ed;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3498db;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3498db;
  cursor: pointer;
  border: none;
}

/* Color Selector */
.color-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.color-btn {
  width: 100%;
  aspect-ratio: 1;
  border: 3px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.color-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.color-btn.active {
  border-color: white;
  box-shadow: 0 0 0 2px #3498db;
}

.custom-color {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border-radius: 6px;
}

.color-input {
  width: 40px;
  height: 40px;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  cursor: pointer;
}

.color-value {
  font-size: 12px;
  font-family: 'Courier New', monospace;
  color: #7f8c8d;
  font-weight: 600;
}

/* Label Selector */
.label-select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  background: white;
  color: #2c3e50;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
}

.label-select:hover {
  border-color: #3498db;
}

.label-select:focus {
  outline: none;
  border-color: #3498db;
}

.add-label-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
  border: 2px dashed #e1e8ed;
  background: white;
  border-radius: 6px;
  color: #7f8c8d;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-label-btn:hover {
  border-color: #3498db;
  color: #3498db;
  background: #f8f9fa;
}

/* Keypoint Progress */
.keypoint-progress {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
}

.clear-keypoints-btn {
  padding: 4px 8px;
  border: none;
  background: #e74c3c;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-keypoints-btn:hover {
  background: #c0392b;
}

.skeleton-btn {
  width: 100%;
  padding: 8px;
  border: none;
  background: #9b59b6;
  color: white;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.skeleton-btn:hover {
  background: #8e44ad;
}

.annotation-label {
  font-weight: 700;
  color: #3498db;
}

/* Annotations List */
.annotations-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.annotations-list h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #95a5a6;
}

.empty-state p {
  margin: 0 0 8px 0;
}

.empty-state .hint {
  font-size: 12px;
  color: #bdc3c7;
}

.annotation-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.annotation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
  transition: all 0.2s;
}

.annotation-item:hover {
  background: #ecf0f1;
  border-color: #bdc3c7;
}

.annotation-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.annotation-type {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 14px;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 1px #e1e8ed;
  flex-shrink: 0;
}

.annotation-coords {
  font-size: 11px;
  color: #7f8c8d;
  font-family: 'Courier New', monospace;
}

.delete-btn {
  padding: 6px;
  border: none;
  background: transparent;
  color: #95a5a6;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: #e74c3c;
  color: white;
}

/* Action Buttons */
.action-buttons {
  padding: 20px;
  border-top: 1px solid #e1e8ed;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.save-btn {
  background: #3498db;
  color: white;
}

.save-btn:hover {
  background: #2980b9;
}

.approve-btn {
  background: #27ae60;
  color: white;
}

.approve-btn:hover {
  background: #229954;
}

.clear-btn {
  background: #e74c3c;
  color: white;
}

.clear-btn:hover {
  background: #c0392b;
}

.history-btn {
  background: #9b59b6;
  color: white;
}

.history-btn:hover {
  background: #8e44ad;
}

/* History Panel */
.history-panel {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  height: 100vh;
  background: white;
  border-left: 1px solid #e1e8ed;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.history-header {
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #2c3e50;
}

.history-title h2 {
  margin: 0;
  font-size: 18px;
}

.close-history-btn {
  padding: 8px;
  border: none;
  background: transparent;
  color: #7f8c8d;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-history-btn:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.history-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #bdc3c7;
  text-align: center;
}

.history-empty p {
  margin: 16px 0 0 0;
  font-size: 14px;
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-entry {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.history-entry:hover {
  background: #ecf0f1;
  transform: translateX(4px);
}

.history-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.history-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-action {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  text-transform: capitalize;
}

.history-description {
  font-size: 13px;
  color: #7f8c8d;
  line-height: 1.4;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.history-time {
  font-size: 11px;
  color: #95a5a6;
}

.history-count {
  font-size: 11px;
  color: #95a5a6;
  padding: 2px 8px;
  background: white;
  border-radius: 10px;
}

/* Main Area */
.annotation-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-header {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #e1e8ed;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f8f9fa;
  border-color: #bdc3c7;
}

.image-info h2 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #2c3e50;
}

.image-meta {
  font-size: 13px;
  color: #7f8c8d;
}

.canvas-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: auto;
  position: relative;
}

.konva-container {
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  cursor: crosshair;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: white;
  max-width: 100%;
  max-height: 100%;
}

/* Canvas Hints */
.canvas-hint {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(52, 152, 219, 0.95);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.3s ease;
  pointer-events: none;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Label Dialog */
.label-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

.label-dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.dialog-header button {
  padding: 6px;
  border: none;
  background: transparent;
  color: #7f8c8d;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-header button:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.dialog-content {
  padding: 20px;
}

.label-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  font-size: 14px;
  color: #2c3e50;
  transition: all 0.2s;
}

.label-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.dialog-actions {
  display: flex;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e1e8ed;
}

.dialog-actions button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
</style>
