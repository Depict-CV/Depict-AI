import { ref, type Ref } from 'vue'
import Konva from 'konva'

// Skeleton structure constants
export const SKELETON_STRUCTURE = [
  [0, 1],
  [0, 2], // nose to eyes
  [1, 3],
  [2, 4], // eyes to ears
  [0, 5],
  [0, 6], // nose to shoulders
  [5, 7],
  [7, 9], // left arm
  [6, 8],
  [8, 10], // right arm
  [5, 11],
  [6, 12], // shoulders to hips
  [11, 13],
  [13, 15], // left leg
  [12, 14],
  [14, 16], // right leg
]

export const KEYPOINT_NAMES = [
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
]

interface SkeletonType {
  keypoints: Array<{ circle: Konva.Circle; label: Konva.Text; pos: { x: number; y: number } }>
  connections: Konva.Line[]
  group: Konva.Group
}

export function useShapeDrawing(
  stage: Ref<Konva.Stage | null>,
  layer: Ref<Konva.Layer | null>,
  drawingMode: Ref<string>,
  selectedLabel: Ref<string>,
  getLabelColor: (label: string) => string
) {
  const isDrawing = ref(false)
  const currentShape = ref<any>(null)
  const shapes = ref<any[]>([])

  // Mask state
  const currentMask = ref<Konva.Line | null>(null)
  const maskPoints = ref<number[]>([])
  const isDrawingMask = ref(false)

  // Polygon state
  const polygonPoints = ref<number[]>([])
  const currentPolygon = ref<Konva.Line | null>(null)
  const isDrawingPolygon = ref(false)

  // Skeleton state
  const currentSkeleton = ref<SkeletonType | null>(null)

  const setupDrawingEvents = (onShapeClick: (shape: any) => void, onSaveHistory: () => void) => {
    if (!stage.value) return

    let startPos: { x: number; y: number } | null = null

    stage.value.on('mousedown touchstart', (e) => {
      if (drawingMode.value === 'pan' || drawingMode.value === 'select') return

      const pos = stage.value!.getRelativePointerPosition()!

      // Handle mask mode
      if (drawingMode.value === 'mask') {
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

        layer.value?.add(currentMask.value)
        return
      }

      // Handle skeleton mode
      if (drawingMode.value === 'skeleton') {
        addKeypoint(pos)
        return
      }

      // Handle polygon mode
      if (drawingMode.value === 'polygon') {
        addPolygonPoint(pos, onShapeClick, onSaveHistory)
        return
      }

      isDrawing.value = true
      startPos = pos

      // Handle rectangle mode
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

        currentShape.value.metadata = {
          type: 'rectangle',
          label: selectedLabel.value || '',
          createdAt: new Date().toISOString(),
        }

        const shapeRef = currentShape.value
        shapeRef.on('click tap', (e: any) => {
          if (drawingMode.value === 'select') {
            e.cancelBubble = true
            onShapeClick(shapeRef)
          }
        })

        shapeRef.on('mouseenter', () => {
          if (drawingMode.value === 'select') {
            stage.value!.container().style.cursor = 'pointer'
          }
        })

        shapeRef.on('mouseleave', () => {
          if (drawingMode.value === 'select') {
            stage.value!.container().style.cursor = 'default'
          }
        })
      }

      if (currentShape.value) {
        layer.value?.add(currentShape.value)
        layer.value?.draw()
      }
    })

    stage.value.on('mousemove touchmove', (e) => {
      // Handle mask drawing
      if (isDrawingMask.value && currentMask.value) {
        const pos = stage.value!.getRelativePointerPosition()!
        maskPoints.value.push(pos.x, pos.y)
        currentMask.value.points(maskPoints.value)
        layer.value?.batchDraw()
        return
      }

      if (!isDrawing.value || !currentShape.value || drawingMode.value === 'pan' || drawingMode.value === 'select')
        return

      const pos = stage.value!.getRelativePointerPosition()!

      if (drawingMode.value === 'rectangle' && startPos) {
        currentShape.value.width(pos.x - startPos.x)
        currentShape.value.height(pos.y - startPos.y)
      }

      layer.value?.batchDraw()
    })

    stage.value.on('mouseup touchend', () => {
      // Handle mask completion
      if (isDrawingMask.value) {
        finishMask(onShapeClick, onSaveHistory)
        return
      }

      if (!isDrawing.value) return

      isDrawing.value = false

      if (currentShape.value) {
        currentShape.value.masks = []
        shapes.value.push(currentShape.value)
        onSaveHistory()
        currentShape.value = null
      }
    })
  }

  const finishMask = (onShapeClick: (shape: any) => void, onSaveHistory: () => void) => {
    isDrawingMask.value = false

    if (currentMask.value && maskPoints.value.length >= 6) {
      currentMask.value.closed(true)
      const maskColor = currentMask.value.stroke()
      currentMask.value.fill(maskColor + '30')

      // Calculate bounding box
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

      boundingBox.metadata = {
        type: 'rectangle',
        label: selectedLabel.value || '',
        createdAt: new Date().toISOString(),
        hasMask: true,
      }

      boundingBox.masks = [currentMask.value]

      boundingBox.on('click tap', (e: any) => {
        if (drawingMode.value === 'select') {
          e.cancelBubble = true
          onShapeClick(boundingBox)
        }
      })

      boundingBox.on('mouseenter', () => {
        if (drawingMode.value === 'select') {
          stage.value!.container().style.cursor = 'pointer'
        }
      })

      boundingBox.on('mouseleave', () => {
        if (drawingMode.value === 'select') {
          stage.value!.container().style.cursor = 'default'
        }
      })

      layer.value?.add(boundingBox)
      boundingBox.moveToTop()
      currentMask.value.moveToTop()
      shapes.value.push(boundingBox)
      onSaveHistory()

      currentMask.value = null
      maskPoints.value = []
      layer.value?.draw()
    }
  }

  const addPolygonPoint = (
    pos: { x: number; y: number },
    onShapeClick: (shape: any) => void,
    onSaveHistory: () => void
  ) => {
    if (!isDrawingPolygon.value) {
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

      layer.value?.add(currentPolygon.value)
    } else {
      polygonPoints.value.push(pos.x, pos.y)
      currentPolygon.value!.points(polygonPoints.value)
    }

    const point = new Konva.Circle({
      x: pos.x,
      y: pos.y,
      radius: 4,
      fill: '#ffffff',
      stroke: '#ff0000',
      strokeWidth: 2,
    })
    layer.value?.add(point)
    layer.value?.draw()
  }

  const finishPolygon = (onShapeClick: (shape: any) => void, onSaveHistory: () => void) => {
    if (!currentPolygon.value || polygonPoints.value.length < 6) return

    currentPolygon.value.closed(true)
    currentPolygon.value.fill(currentPolygon.value.stroke() + '20')

    currentPolygon.value.on('click tap', (e: any) => {
      if (drawingMode.value === 'select') {
        e.cancelBubble = true
        onShapeClick(currentPolygon.value)
      }
    })

    shapes.value.push(currentPolygon.value)
    onSaveHistory()

    isDrawingPolygon.value = false
    currentPolygon.value = null
    polygonPoints.value = []
    layer.value?.draw()
  }

  const cancelPolygon = () => {
    if (currentPolygon.value) {
      currentPolygon.value.destroy()
      currentPolygon.value = null
    }
    isDrawingPolygon.value = false
    polygonPoints.value = []
    layer.value?.draw()
  }

  const addKeypoint = (pos: { x: number; y: number }) => {
    if (!currentSkeleton.value) {
      currentSkeleton.value = {
        keypoints: [],
        connections: [],
        group: new Konva.Group({
          draggable: false,
        }),
      }
      layer.value?.add(currentSkeleton.value.group)
    }

    const skeleton = currentSkeleton.value
    const keypointIndex = skeleton.keypoints.length

    const keypoint = new Konva.Circle({
      x: pos.x,
      y: pos.y,
      radius: 5,
      fill: '#ff0000',
      stroke: '#ffffff',
      strokeWidth: 2,
      draggable: false,
    })

    const label = new Konva.Text({
      x: pos.x + 8,
      y: pos.y - 8,
      text: `${keypointIndex}: ${KEYPOINT_NAMES[keypointIndex] || 'point'}`,
      fontSize: 12,
      fill: '#ffffff',
      stroke: '#000000',
      strokeWidth: 0.5,
    })

    keypoint.on('dragmove', () => {
      label.x(keypoint.x() + 8)
      label.y(keypoint.y() - 8)
      updateSkeletonConnections(skeleton)
    })

    skeleton.keypoints.push({ circle: keypoint, label, pos: { x: pos.x, y: pos.y } })
    skeleton.group.add(keypoint)
    skeleton.group.add(label)

    if (keypointIndex > 0) {
      updateSkeletonConnections(skeleton)
    }

    layer.value?.draw()

    if (skeleton.keypoints.length >= KEYPOINT_NAMES.length) {
      finishSkeleton()
    }
  }

  const updateSkeletonConnections = (skeleton: SkeletonType) => {
    skeleton.connections.forEach((line) => line.destroy())
    skeleton.connections = []

    SKELETON_STRUCTURE.forEach(([startIdx, endIdx]) => {
      if (startIdx < skeleton.keypoints.length && endIdx < skeleton.keypoints.length) {
        const startKp = skeleton.keypoints[startIdx]
        const endKp = skeleton.keypoints[endIdx]

        const line = new Konva.Line({
          points: [startKp.circle.x(), startKp.circle.y(), endKp.circle.x(), endKp.circle.y()],
          stroke: '#00ff00',
          strokeWidth: 2,
          lineCap: 'round',
          lineJoin: 'round',
        })

        skeleton.group.add(line)
        line.moveToBottom()
        skeleton.connections.push(line)
      }
    })

    layer.value?.draw()
  }

  const finishSkeleton = () => {
    if (currentSkeleton.value) {
      currentSkeleton.value.group.on('click tap', () => {
        // Will be handled by parent
      })

      shapes.value.push(currentSkeleton.value)
      currentSkeleton.value = null
    }
  }

  const clearCurrentSkeleton = () => {
    if (currentSkeleton.value) {
      currentSkeleton.value.group.destroy()
      currentSkeleton.value = null
      layer.value?.draw()
    }
  }

  const finishSkeletonEarly = () => {
    if (currentSkeleton.value && currentSkeleton.value.keypoints.length > 0) {
      finishSkeleton()
      return currentSkeleton.value?.keypoints.length || 0
    }
    return 0
  }

  return {
    shapes,
    isDrawing,
    isDrawingPolygon,
    currentSkeleton,
    setupDrawingEvents,
    finishPolygon,
    cancelPolygon,
    finishSkeletonEarly,
    clearCurrentSkeleton,
  }
}
