<script setup>
import { ref } from 'vue'
import { Download, FileJson, Database } from 'lucide-vue-next'
import JSZip from 'jszip'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const api = useApi()
const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = runtimeConfig.public.apiBaseUrl || 'http://localhost:8000'
const exportFormat = ref('json')
const isExporting = ref(false)

const downloadFile = (content, filename, mimeType) => {
  const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(link)
}

const fetchAllRecords = async (pathBuilder, pageSize) => {
  const records = []
  let skip = 0

  while (true) {
    const response = await api.get(pathBuilder(skip, pageSize))
    const batch = Array.isArray(response) ? response : []
    if (batch.length === 0) {
      break
    }
    records.push(...batch)
    if (batch.length < pageSize) {
      break
    }
    skip += pageSize
  }

  return records
}

const sanitizeFileName = (value) => String(value || '').replace(/[^a-zA-Z0-9._-]/g, '_')

const extFromMimeType = (mimeType) => {
  if (!mimeType) return 'jpg'
  if (mimeType.includes('png')) return 'png'
  if (mimeType.includes('webp')) return 'webp'
  if (mimeType.includes('gif')) return 'gif'
  if (mimeType.includes('bmp')) return 'bmp'
  if (mimeType.includes('tiff')) return 'tiff'
  if (mimeType.includes('svg')) return 'svg'
  return 'jpg'
}

const extFromPath = (path) => {
  const clean = String(path || '').split('?')[0]
  const match = clean.match(/\.([a-zA-Z0-9]+)$/)
  return match ? match[1].toLowerCase() : ''
}

const resolveImageUrl = (image) => {
  const location = image?.location
  if (!location) return ''

  if (location.startsWith('minio://')) {
    const minioPath = location.replace('minio://', '')
    const projectId = image?.project_id || props.projectId
    return `${apiBaseUrl}/images/minio/${projectId}?object_path=${encodeURIComponent(minioPath)}`
  }

  if (location.startsWith('http://') || location.startsWith('https://')) {
    return location
  }

  if (location.startsWith('/')) {
    return `${apiBaseUrl}${location}`
  }

  return `${apiBaseUrl}/images/serve?path=${encodeURIComponent(location)}`
}

const handleExport = async () => {
  if (!props.projectId) {
    alert('No project selected')
    return
  }

  isExporting.value = true
  try {
    // Fetch all project data and annotations from database
    const [imagesResponse, annotationsResponse] = await Promise.all([
      fetchAllRecords((skip, limit) => `/data/?project_id=${props.projectId}&skip=${skip}&limit=${limit}`, 100),
      fetchAllRecords((skip, limit) => `/annotations/?project_id=${props.projectId}&skip=${skip}&limit=${limit}`, 1000),
    ])

    const images = imagesResponse || []
    const annotations = annotationsResponse || []

    console.log('Fetched images:', images.length)
    console.log('Fetched annotations:', annotations.length)

    const zip = new JSZip()
    const imagesFolder = zip.folder('images')
    const exportedImageNameById = new Map()
    const failedImages = []

    for (let index = 0; index < images.length; index += 1) {
      const image = images[index]
      const imageUrl = resolveImageUrl(image)

      if (!imageUrl) {
        failedImages.push({ id: image?.id, location: image?.location, reason: 'Missing image URL' })
        continue
      }

      try {
        const response = await fetch(imageUrl)
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const blob = await response.blob()
        const extFromOriginal = extFromPath(image.location)
        const extension = extFromOriginal || extFromMimeType(blob.type)
        const baseName = sanitizeFileName(image?.id ?? `image-${index + 1}`)
        const filename = `${String(index + 1).padStart(5, '0')}_${baseName}.${extension}`

        imagesFolder.file(filename, blob)
        exportedImageNameById.set(image.id, filename)
      } catch (error) {
        failedImages.push({
          id: image?.id,
          location: image?.location,
          reason: error?.message || 'Failed to fetch image',
        })
      }
    }

    if (exportFormat.value === 'json') {
      // Export as COCO format JSON
      const cocoData = {
        info: {
          description: `Depict-AI Project ${props.projectId}`,
          version: '1.0',
          year: new Date().getFullYear(),
          date_created: new Date().toISOString(),
        },
        images: images.map((img, idx) => ({
          id: img.id,
          file_name: exportedImageNameById.get(img.id)
            ? `images/${exportedImageNameById.get(img.id)}`
            : img.location || 'unknown',
          height: img.height || 0,
          width: img.width || 0,
          image_index: idx,
        })),
        annotations: annotations.map((ann) => ({
          id: ann.id,
          image_id: ann.data_id,
          category_id: 1,
          category_name: ann.label || 'unlabeled',
          iscrowd: 0,
          area: 0,
          bbox: [],
          segmentation: [],
          status: ann.status || 'unknown',
          created_at: ann.created_at,
        })),
        categories: [
          {
            id: 1,
            name: 'annotation',
            supercategory: 'object',
          },
        ],
      }

      const jsonContent = JSON.stringify(cocoData, null, 2)
      zip.file('annotations.json', jsonContent)
    } else if (exportFormat.value === 'csv') {
      // Export as CSV
      const csvHeaders = ['Image ID', 'File Name', 'Annotation ID', 'Label', 'Status', 'Created At']

      const csvRows = []
      images.forEach((img) => {
        const imgAnnotations = annotations.filter((ann) => ann.data_id === img.id)
        const exportedName = exportedImageNameById.get(img.id)
        const fileName = exportedName ? `images/${exportedName}` : img.location || 'unknown'

        if (imgAnnotations.length === 0) {
          // Row for image with no annotations
          csvRows.push([img.id, fileName, '', 'No annotation', '', ''])
        } else {
          // Row for each annotation
          imgAnnotations.forEach((ann) => {
            csvRows.push([img.id, fileName, ann.id, ann.label || '', ann.status || '', ann.created_at || ''])
          })
        }
      })

      // Convert to CSV string
      const csvContent = [
        csvHeaders.map((h) => `"${h}"`).join(','),
        csvRows.map((row) => row.map((cell) => `"${cell}"`).join(',')).join('\n'),
      ].join('\n')

      zip.file('annotations.csv', csvContent)
    }

    zip.file(
      'export-report.json',
      JSON.stringify(
        {
          project_id: props.projectId,
          format: exportFormat.value,
          image_count: images.length,
          annotation_count: annotations.length,
          downloaded_images: exportedImageNameById.size,
          failed_images: failedImages,
          generated_at: new Date().toISOString(),
        },
        null,
        2
      )
    )

    const zipBlob = await zip.generateAsync({ type: 'blob' })
    const filename = `project-${props.projectId}-${exportFormat.value}-with-images-${Date.now()}.zip`
    downloadFile(zipBlob, filename, 'application/zip')

    alert(
      `Export successful: ${exportedImageNameById.size}/${images.length} images downloaded. Metadata format: ${exportFormat.value.toUpperCase()}.`
    )
  } catch (error) {
    console.error('Export failed:', error)
    alert(`Export failed: ${error.message}`)
  } finally {
    isExporting.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Export Data</h2>

    <div class="space-y-4">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
          <Download :size="20" class="text-green-600" />
        </div>
        <p class="text-sm text-gray-600">Export project data, annotations, and images</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
        <div class="space-y-2">
          <label
            class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <input type="radio" v-model="exportFormat" value="json" class="w-4 h-4 text-blue-600" />
            <FileJson :size="18" class="text-gray-600" />
            <div class="flex-1">
              <div class="font-medium text-gray-900">JSON</div>
              <div class="text-xs text-gray-500">COCO format, annotations included</div>
            </div>
          </label>

          <label
            class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <input type="radio" v-model="exportFormat" value="csv" class="w-4 h-4 text-blue-600" />
            <Database :size="18" class="text-gray-600" />
            <div class="flex-1">
              <div class="font-medium text-gray-900">CSV</div>
              <div class="text-xs text-gray-500">Tabular metadata + bundled image files</div>
            </div>
          </label>
        </div>
      </div>

      <button
        @click="handleExport"
        :disabled="isExporting"
        class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Download :size="18" />
        <span v-if="!isExporting">Export ZIP (Data + Images)</span>
        <span v-else>Exporting ZIP...</span>
      </button>
    </div>
  </div>
</template>
