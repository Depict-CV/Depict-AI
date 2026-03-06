<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const { user } = useAuth()
const api = useApi()

const loading = ref(false)
const errorMessage = ref('')
const stacItems = ref([])
const previewImageUrl = ref('')
const previewImageTitle = ref('')
const mapElement = ref(null)
const isDrawMode = ref(false)
const bboxInput = ref('')
const selectedItemIds = ref(new Set())
const lastSelectedItemId = ref(null)
const isImporting = ref(false)
const importMessage = ref('')
const nextPageRequest = ref(null)
const resultsSentinel = ref(null)

let mapInstance = null
let drawModeButton = null
let boxStart = null
let bboxRectangle = null
let L = null
let resultsObserver = null
let imageClickTimeout = null

const PAGE_SIZE = 20
const JSON_HEADERS = { 'Content-Type': 'application/json' }
const DEFAULT_ERROR_MESSAGE = {
  page: 'Failed to load STAC page data',
  stac: 'Failed to load STAC data',
}

const collectionOptions = ['sentinel-2-l2a', 'landsat-c2-l2', 'naip', 'modis-13Q1-061']

const sortFieldOptions = [
  { value: 'datetime', label: 'Date' },
  { value: 'cloudCover', label: 'Cloud Cover' },
]

const form = ref({
  collection: 'sentinel-2-l2a',
  bbox: null,
  startDate: '2025-01-01',
  endDate: '2025-01-31',
  maxCloudCover: 20,
  sortField: 'datetime',
})

const filteredStacItems = computed(() => {
  let items = [...stacItems.value]

  items.sort((a, b) => {
    if (form.value.sortField === 'cloudCover') {
      const aVal = typeof a.cloudCover === 'number' ? a.cloudCover : Number.POSITIVE_INFINITY
      const bVal = typeof b.cloudCover === 'number' ? b.cloudCover : Number.POSITIVE_INFINITY
      return bVal - aVal
    }

    const aDate = a.datetime ? new Date(a.datetime).getTime() : 0
    const bDate = b.datetime ? new Date(b.datetime).getTime() : 0
    return bDate - aDate
  })

  return items
})

const selectedCount = computed(() => selectedItemIds.value.size)

const canImport = computed(() => selectedCount.value > 0 && !!props.projectId)

const canLoadMoreChunks = computed(() => !!nextPageRequest.value && !loading.value)

const getErrorMessage = (error, fallback) => error?.data?.detail || error?.message || fallback

const pickFirstUrl = (item, candidates) => {
  for (const key of candidates) {
    const value = key.split('.').reduce((acc, part) => acc?.[part], item)
    if (typeof value === 'string' && value.length > 0) {
      return value
    }
  }

  return ''
}

const updateDrawButtonUi = () => {
  if (!drawModeButton) {
    return
  }

  drawModeButton.textContent = isDrawMode.value ? '▣' : '□'
  drawModeButton.title = isDrawMode.value ? 'Disable bbox draw mode' : 'Enable bbox draw mode'
  drawModeButton.setAttribute('aria-label', drawModeButton.title)
  drawModeButton.style.background = isDrawMode.value ? '#059669' : '#ffffff'
  drawModeButton.style.color = isDrawMode.value ? '#ffffff' : '#111827'
}

const setDrawMode = (enabled) => {
  isDrawMode.value = enabled

  if (mapInstance) {
    if (enabled) {
      mapInstance.dragging.disable()
    } else {
      mapInstance.dragging.enable()
    }
  }

  updateDrawButtonUi()
}

const toggleDrawMode = () => setDrawMode(!isDrawMode.value)

const updateRectangle = (bounds) => {
  if (!L || !mapInstance) {
    return
  }

  if (!bboxRectangle) {
    bboxRectangle = L.rectangle(bounds).addTo(mapInstance)
    return
  }

  bboxRectangle.setBounds(bounds)
}

const applyBboxOnMap = (bbox, { fit = true } = {}) => {
  if (!L || !mapInstance || !Array.isArray(bbox) || bbox.length !== 4) {
    return
  }

  const bounds = L.latLngBounds([bbox[1], bbox[0]], [bbox[3], bbox[2]])
  updateRectangle(bounds)

  if (fit) {
    mapInstance.fitBounds(bounds, { padding: [20, 20] })
  }
}

const clearRectangle = () => {
  boxStart = null
  if (bboxRectangle && mapInstance) {
    mapInstance.removeLayer(bboxRectangle)
  }
  bboxRectangle = null
}

const initInteractiveMap = async () => {
  if (!mapElement.value || typeof window === 'undefined') {
    return
  }

  const leafletModule = await import('leaflet')
  L = leafletModule.default || leafletModule

  const map = L.map(mapElement.value).setView([20, 0], 2)
  mapInstance = map

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  const DrawModeControl = L.Control.extend({
    onAdd: () => {
      const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control')
      const button = L.DomUtil.create('button', '', container)

      button.type = 'button'
      button.style.width = '30px'
      button.style.height = '30px'
      button.style.border = '0'
      button.style.cursor = 'pointer'
      button.style.fontSize = '17px'
      button.style.fontWeight = '700'
      button.style.lineHeight = '1'

      drawModeButton = button
      updateDrawButtonUi()

      L.DomEvent.disableClickPropagation(container)
      L.DomEvent.on(button, 'click', (event) => {
        L.DomEvent.stop(event)
        toggleDrawMode()
      })

      return container
    },
  })

  map.addControl(new DrawModeControl({ position: 'topleft' }))

  map.on('mousedown', (event) => {
    if (!isDrawMode.value) {
      return
    }

    boxStart = event.latlng
    updateRectangle(L.latLngBounds(boxStart, boxStart))
  })

  map.on('mousemove', (event) => {
    if (!isDrawMode.value || !boxStart) {
      return
    }

    updateRectangle(L.latLngBounds(boxStart, event.latlng))
  })

  map.on('mouseup', (event) => {
    if (!isDrawMode.value || !boxStart) {
      return
    }

    const bounds = L.latLngBounds(boxStart, event.latlng)
    updateRectangle(bounds)
    form.value.bbox = [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()]
    bboxInput.value = form.value.bbox.map((value) => Number(value).toFixed(6)).join(', ')
    boxStart = null
  })

  setDrawMode(false)

  if (form.value.bbox) {
    applyBboxOnMap(form.value.bbox)
  }
}

const toggleItemSelection = (itemId) => {
  selectedItemIds.value.has(itemId) ? selectedItemIds.value.delete(itemId) : selectedItemIds.value.add(itemId)
}

const selectRangeFromLastSelection = (itemId) => {
  if (!lastSelectedItemId.value) {
    toggleItemSelection(itemId)
    lastSelectedItemId.value = itemId
    return
  }

  const items = filteredStacItems.value
  const lastIndex = items.findIndex((item) => item.id === lastSelectedItemId.value)
  const currentIndex = items.findIndex((item) => item.id === itemId)

  if (lastIndex === -1 || currentIndex === -1) {
    toggleItemSelection(itemId)
    lastSelectedItemId.value = itemId
    return
  }

  const start = Math.min(lastIndex, currentIndex)
  const end = Math.max(lastIndex, currentIndex)

  for (let index = start; index <= end; index += 1) {
    selectedItemIds.value.add(items[index].id)
  }

  lastSelectedItemId.value = itemId
}

const handleImageSingleClick = (itemId, event) => {
  const isShiftClick = event?.shiftKey === true

  if (imageClickTimeout) {
    clearTimeout(imageClickTimeout)
  }

  imageClickTimeout = setTimeout(() => {
    const action = isShiftClick ? selectRangeFromLastSelection : handleCheckboxToggle
    action(itemId)
    imageClickTimeout = null
  }, 220)
}

const handleImageDoubleClick = (item) => {
  if (imageClickTimeout) {
    clearTimeout(imageClickTimeout)
    imageClickTimeout = null
  }

  openImagePreview(item)
}

const toggleSelectAllVisible = () => {
  const visibleIds = filteredStacItems.value.map((item) => item.id)
  const allVisibleSelected = visibleIds.length > 0 && visibleIds.every((id) => selectedItemIds.value.has(id))

  if (allVisibleSelected) {
    visibleIds.forEach((id) => selectedItemIds.value.delete(id))
    return
  }

  visibleIds.forEach((id) => selectedItemIds.value.add(id))
}

const handleCheckboxToggle = (itemId) => {
  toggleItemSelection(itemId)
  lastSelectedItemId.value = itemId
}

const importSelectedItems = async () => {
  if (!props.projectId) {
    importMessage.value = 'Select a project first before importing.'
    return
  }

  if (!user?.value?.id) {
    importMessage.value = 'User is not available. Please refresh and try again.'
    return
  }

  const selectedItems = filteredStacItems.value.filter((item) => selectedItemIds.value.has(item.id))
  if (selectedItems.length === 0) {
    importMessage.value = 'Select at least one item to import.'
    return
  }

  isImporting.value = true
  importMessage.value = ''

  try {
    const payload = selectedItems
      .map((item) => ({
        location: item.previewUrl || item.primaryAssetUrl,
        user_id: user.value.id,
        project_id: props.projectId,
        type: 'image',
      }))
      .filter((entry) => !!entry.location)

    if (payload.length === 0) {
      importMessage.value = 'Selected items do not have importable image URLs.'
      return
    }

    const response = await api.post('/data/add_batch', payload)
    importMessage.value = `Import complete: ${response.created || 0} created, ${response.skipped || 0} skipped.`
  } catch (error) {
    importMessage.value = error?.data?.detail || error?.message || 'Failed to import selected items.'
  } finally {
    isImporting.value = false
  }
}

const mapIncomingItems = (incomingItems) => {
  return incomingItems
    .map((item) => ({
      id: item.id,
      collection: item.collection,
      datetime: item.properties?.datetime,
      cloudCover: item.properties?.['eo:cloud_cover'],
      platform: item.properties?.platform || item.properties?.constellation || '',
      instrument: item.properties?.instruments?.[0] || item.properties?.instrument || '',
      provider: item.properties?.providers?.[0]?.name || '',
      previewUrl: getPreviewUrl(item),
      primaryAssetUrl: getPrimaryAssetUrl(item),
      raw: item,
    }))
    .filter((item) => item.id)
}

const buildRequestFromLink = (link, basePayload) => {
  if (!link?.href) return null

  const method = (link.method || 'GET').toUpperCase()
  let body

  if (method !== 'GET') {
    if (link.merge) {
      body = {
        ...(basePayload || {}),
        ...(link.body || {}),
      }
    } else {
      body = link.body || undefined
    }
  }

  return {
    href: link.href,
    method,
    body,
  }
}

const appendUniqueItems = (incomingItems, { reset = false } = {}) => {
  if (reset) {
    stacItems.value = []
  }

  const existingIds = new Set(stacItems.value.map((item) => item.id))
  const uniqueIncoming = incomingItems.filter((item) => item?.id && !existingIds.has(item.id))
  stacItems.value = [...stacItems.value, ...uniqueIncoming]
}

const applyResponsePage = (response, basePayload, { reset = false } = {}) => {
  const mappedItems = mapIncomingItems(response?.features || [])
  appendUniqueItems(mappedItems, { reset })

  const nextLink = (response?.links || []).find((link) => link?.rel === 'next' && link?.href)
  nextPageRequest.value = buildRequestFromLink(nextLink, basePayload)
}

const executePageRequest = async (requestConfig, { reset = false } = {}) => {
  if (!requestConfig?.href) {
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    const response = await $fetch(requestConfig.href, {
      method: requestConfig.method || 'GET',
      body: requestConfig.body,
      headers: JSON_HEADERS,
    })

    applyResponsePage(response, requestConfig.body, { reset })
  } catch (error) {
    errorMessage.value = getErrorMessage(error, DEFAULT_ERROR_MESSAGE.page)
  } finally {
    loading.value = false
  }
}

const loadNextChunk = async () => {
  if (!canLoadMoreChunks.value || !nextPageRequest.value) {
    return
  }

  await executePageRequest(nextPageRequest.value)
}

const getPreviewUrl = (item) => {
  return (
    pickFirstUrl(item, [
      'assets.thumbnail.href',
      'assets.preview.href',
      'assets.rendered_preview.href',
      'assets.visual.href',
    ]) || ''
  )
}

const getPrimaryAssetUrl = (item) => {
  return (
    pickFirstUrl(item, [
      'assets.visual.href',
      'assets.analytic.href',
      'assets.image.href',
      'assets.thumbnail.href',
      'assets.preview.href',
    ]) || ''
  )
}

const loadStacData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    if (!form.value.bbox) {
      throw new Error('Please draw a BBOX on the map or enter coordinates manually')
    }

    const datetime = `${form.value.startDate}/${form.value.endDate}`

    const payload = {
      collections: [form.value.collection],
      bbox: form.value.bbox,
      datetime,
      limit: PAGE_SIZE,
      query: {
        'eo:cloud_cover': {
          lte: Number(form.value.maxCloudCover),
        },
      },
    }

    const response = await $fetch('https://planetarycomputer.microsoft.com/api/stac/v1/search', {
      method: 'POST',
      body: payload,
      headers: JSON_HEADERS,
    })

    applyResponsePage(response, payload, { reset: true })
    selectedItemIds.value = new Set()
    lastSelectedItemId.value = null
    importMessage.value = ''
  } catch (error) {
    errorMessage.value = getErrorMessage(error, DEFAULT_ERROR_MESSAGE.stac)
    stacItems.value = []
  } finally {
    loading.value = false
  }
}

const openImagePreview = (item) => {
  if (!item?.previewUrl) {
    return
  }

  previewImageUrl.value = item.previewUrl
  previewImageTitle.value = item.id || 'STAC preview'
}

const closeImagePreview = () => {
  previewImageUrl.value = ''
  previewImageTitle.value = ''
}

const observeSentinel = () => {
  if (resultsObserver) {
    resultsObserver.disconnect()
    resultsObserver = null
  }

  if (!resultsSentinel.value || typeof window === 'undefined') {
    return
  }

  resultsObserver = new window.IntersectionObserver(
    (entries) => {
      const [entry] = entries
      if (entry?.isIntersecting) {
        loadNextChunk()
      }
    },
    {
      root: null,
      rootMargin: '250px 0px',
      threshold: 0,
    }
  )

  resultsObserver.observe(resultsSentinel.value)
}

watch(resultsSentinel, () => {
  observeSentinel()
})

onMounted(() => {
  observeSentinel()
  initInteractiveMap().catch((error) => {
    errorMessage.value = error?.message || 'Failed to initialize map'
  })
})

onUnmounted(() => {
  if (imageClickTimeout) {
    clearTimeout(imageClickTimeout)
    imageClickTimeout = null
  }

  if (resultsObserver) {
    resultsObserver.disconnect()
    resultsObserver = null
  }

  clearRectangle()

  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }

  drawModeButton = null
  boxStart = null
  L = null
})
</script>

<template>
  <div class="w-full">
    <div class="bg-white border border-gray-200 rounded-lg p-3 mb-4">
      <h2 class="text-lg font-semibold text-gray-900 mb-1">Satellite Data (Microsoft Planetary Computer)</h2>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-3 items-start">
        <div class="lg:col-span-1">
          <label class="block text-sm text-gray-700 mb-1">Draw BBOX on map</label>
          <div class="space-y-2">
            <div ref="mapElement" class="w-full aspect-square overflow-hidden rounded border border-gray-300"></div>
          </div>
        </div>

        <div class="lg:col-span-2">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div>
              <label class="block text-sm text-gray-700 mb-1">Collection</label>
              <select
                v-model="form.collection"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
              >
                <option v-for="collection in collectionOptions" :key="collection" :value="collection">
                  {{ collection }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm text-gray-700 mb-1">Start Date</label>
              <input
                v-model="form.startDate"
                type="date"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label class="block text-sm text-gray-700 mb-1">End Date</label>
              <input
                v-model="form.endDate"
                type="date"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label class="block text-sm text-gray-700 mb-1">Max Cloud Cover (%)</label>
              <input
                v-model.number="form.maxCloudCover"
                type="number"
                min="0"
                max="100"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label class="block text-sm text-gray-700 mb-1">Sort by</label>
              <select
                v-model="form.sortField"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
              >
                <option v-for="option in sortFieldOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm text-gray-700 mb-1"
                >Or edit BBOX manually (minLon,minLat,maxLon,maxLat)</label
              >
              <div class="flex gap-2">
                <input
                  v-model="bboxInput"
                  type="text"
                  class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
                  placeholder="-122.600000, 37.600000, -122.300000, 37.900000"
                />
              </div>
            </div>
          </div>

          <div class="mt-3 flex justify-end">
            <button
              type="button"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
              :disabled="loading"
              @click="loadStacData"
            >
              {{ loading ? 'Loading...' : 'Load as STAC' }}
            </button>
          </div>
        </div>
      </div>

      <p v-if="errorMessage" class="mt-3 text-sm text-red-600">{{ errorMessage }}</p>
    </div>

    <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
      <h3 class="text-base font-semibold text-gray-900">STAC Results</h3>
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-500">Loaded {{ filteredStacItems.length }} item(s)</span>
        <button
          type="button"
          class="px-2.5 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded"
          @click="toggleSelectAllVisible"
        >
          Toggle Select Visible
        </button>
        <button
          type="button"
          class="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
          :disabled="isImporting || !canImport"
          @click="importSelectedItems"
        >
          {{ isImporting ? 'Importing...' : `Import Selected (${selectedCount})` }}
        </button>
      </div>
    </div>

    <p v-if="!projectId" class="mb-3 text-xs text-amber-700">Select a project to enable import.</p>
    <p v-if="importMessage" class="mb-3 text-sm text-gray-700">{{ importMessage }}</p>

    <div
      v-if="filteredStacItems.length > 0"
      class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-2"
    >
      <div
        v-for="item in filteredStacItems"
        :key="item.id"
        class="border rounded-lg overflow-hidden bg-white"
        :class="selectedItemIds.has(item.id) ? 'border-blue-300 ring-2 ring-blue-100' : 'border-gray-200'"
      >
        <div class="aspect-square bg-gray-100">
          <img
            v-if="item.previewUrl"
            :src="item.previewUrl"
            :alt="item.id"
            class="w-full h-full object-contain cursor-zoom-in"
            title="Double click to enlarge"
            @click="handleImageSingleClick(item.id, $event)"
            @dblclick="handleImageDoubleClick(item)"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-xs text-gray-500">No preview</div>
        </div>
        <div class="p-2">
          <label class="inline-flex items-center gap-2 text-xs text-gray-700 mb-2">
            <input
              type="checkbox"
              class="rounded border-gray-300"
              :checked="selectedItemIds.has(item.id)"
              @change="handleCheckboxToggle(item.id)"
            />
            Select item
          </label>
          <p class="text-sm font-medium text-gray-900 truncate">{{ item.id }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ item.collection }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ item.datetime || 'No datetime' }}</p>
        </div>
      </div>
    </div>

    <div v-if="filteredStacItems.length > 0" ref="resultsSentinel" class="h-6 mt-2 flex items-center justify-center">
      <p v-if="loading" class="text-xs text-gray-500">Loading next chunk...</p>
      <p v-else-if="!nextPageRequest" class="text-xs text-gray-500">No more results available.</p>
    </div>

    <div v-else class="text-sm text-gray-500 py-6 text-center border border-dashed border-gray-300 rounded-lg bg-white">
      No STAC items loaded yet.
    </div>

    <div
      v-if="previewImageUrl"
      class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
      @click="closeImagePreview"
    >
      <div class="relative max-w-6xl max-h-[90vh] w-full" @click.stop>
        <button
          type="button"
          class="absolute -top-10 right-0 px-3 py-1.5 text-sm bg-white/90 hover:bg-white text-gray-900 rounded"
          @click="closeImagePreview"
        >
          Close
        </button>
        <img :src="previewImageUrl" :alt="previewImageTitle" class="w-full max-h-[90vh] object-contain rounded" />
      </div>
    </div>
  </div>
</template>
