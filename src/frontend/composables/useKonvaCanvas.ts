import { ref, type Ref } from 'vue'
import Konva from 'konva'

export function useKonvaCanvas() {
  const stage = ref<Konva.Stage | null>(null)
  const layer = ref<Konva.Layer | null>(null)
  const imageNode = ref<Konva.Image | null>(null)
  const transformer = ref<Konva.Transformer | null>(null)
  const zoomLevel = ref(1)

  const initCanvas = (
    container: HTMLDivElement,
    imageElement: HTMLImageElement,
    imageFilters: {
      brightness: number
      contrast: number
      redChannel: number
      greenChannel: number
      blueChannel: number
      saturation: number
      hue: number
    }
  ) => {
    const containerWidth = container.offsetWidth
    const containerHeight = container.offsetHeight

    // Create stage
    stage.value = new Konva.Stage({
      container,
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
    img.src = imageElement.src
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
        brightness: imageFilters.brightness / 100,
        contrast: imageFilters.contrast,
        red: imageFilters.redChannel,
        green: imageFilters.greenChannel,
        blue: imageFilters.blueChannel,
        saturation: imageFilters.saturation / 100,
        hue: imageFilters.hue,
      })

      layer.value?.add(imageNode.value)
      imageNode.value.moveToBottom()
      layer.value?.draw()
    }
  }

  const setupZoomAndPan = (drawingMode: Ref<string>, onBackgroundClick: () => void) => {
    if (!stage.value) return

    const scaleBy = 1.1
    const minScale = 0.1
    const maxScale = 10

    // Click on background to deselect
    stage.value.on('click tap', (e) => {
      if (e.target === stage.value) {
        onBackgroundClick()
      }
    })

    // Zoom with mouse wheel
    stage.value.on('wheel', (e) => {
      e.evt.preventDefault()

      const oldScale = stage.value!.scaleX()
      const pointer = stage.value!.getPointerPosition()!

      const mousePointTo = {
        x: (pointer.x - stage.value!.x()) / oldScale,
        y: (pointer.y - stage.value!.y()) / oldScale,
      }

      let newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy

      // Limit zoom level
      if (newScale < minScale) newScale = minScale
      if (newScale > maxScale) newScale = maxScale

      stage.value!.scale({ x: newScale, y: newScale })
      zoomLevel.value = newScale

      const newPos = {
        x: pointer.x - mousePointTo.x * newScale,
        y: pointer.y - mousePointTo.y * newScale,
      }

      stage.value!.position(newPos)
      layer.value?.batchDraw()
    })

    // Pan with drag in pan mode
    let isPanning = false
    let lastPos: { x: number; y: number } | null = null

    stage.value.on('mousedown touchstart', (e) => {
      if (drawingMode.value === 'pan') {
        isPanning = true
        lastPos = stage.value!.getPointerPosition()
        stage.value!.container().style.cursor = 'grabbing'
        e.cancelBubble = true
      }
    })

    stage.value.on('mousemove touchmove', (e) => {
      if (isPanning && drawingMode.value === 'pan') {
        e.evt.preventDefault()
        const pos = stage.value!.getPointerPosition()!
        if (!lastPos) {
          lastPos = pos
          return
        }

        const dx = pos.x - lastPos.x
        const dy = pos.y - lastPos.y

        stage.value!.x(stage.value!.x() + dx)
        stage.value!.y(stage.value!.y() + dy)

        lastPos = pos
        layer.value?.batchDraw()
      }
    })

    stage.value.on('mouseup touchend', () => {
      if (isPanning) {
        isPanning = false
        lastPos = null
        if (drawingMode.value === 'pan') {
          stage.value!.container().style.cursor = 'grab'
        }
      }
    })

    // Update cursor based on mode
    stage.value.on('mouseover', () => {
      if (drawingMode.value === 'pan') {
        stage.value!.container().style.cursor = 'grab'
      } else {
        stage.value!.container().style.cursor = 'default'
      }
    })
  }

  const resetZoom = () => {
    if (!stage.value) return
    stage.value.scale({ x: 1, y: 1 })
    stage.value.position({ x: 0, y: 0 })
    zoomLevel.value = 1
    layer.value?.batchDraw()
  }

  const applyImageFilters = (filters: {
    brightness: number
    contrast: number
    redChannel: number
    greenChannel: number
    blueChannel: number
    saturation: number
    hue: number
  }) => {
    if (!imageNode.value) return
    imageNode.value.brightness(filters.brightness / 100)
    imageNode.value.contrast(filters.contrast)
    imageNode.value.red(filters.redChannel)
    imageNode.value.green(filters.greenChannel)
    imageNode.value.blue(filters.blueChannel)
    imageNode.value.saturation(filters.saturation / 100)
    imageNode.value.hue(filters.hue)
    imageNode.value.cache()
    layer.value?.batchDraw()
  }

  return {
    stage,
    layer,
    imageNode,
    transformer,
    zoomLevel,
    initCanvas,
    setupZoomAndPan,
    resetZoom,
    applyImageFilters,
  }
}
