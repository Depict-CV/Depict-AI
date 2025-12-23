<script setup>
import { ref } from 'vue'
import { Download, FileJson, Database } from 'lucide-vue-next'
import { useApi } from '~/composables/useApi'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const api = useApi()
const exportFormat = ref('json')
const isExporting = ref(false)

const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(link)
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
      api.get(`/data/?project_id=${props.projectId}&limit=100`),
      api.get(`/annotations/?project_id=${props.projectId}&limit=10000`),
    ])

    const images = imagesResponse || []
    const annotations = annotationsResponse || []

    console.log('Fetched images:', images.length)
    console.log('Fetched annotations:', annotations.length)

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
          file_name: img.location || 'unknown',
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
      const filename = `project-${props.projectId}-${Date.now()}.json`
      downloadFile(jsonContent, filename, 'application/json')
    } else if (exportFormat.value === 'csv') {
      // Export as CSV
      const csvHeaders = ['Image ID', 'File Name', 'Annotation ID', 'Label', 'Status', 'Created At']

      const csvRows = []
      images.forEach((img) => {
        const imgAnnotations = annotations.filter((ann) => ann.data_id === img.id)

        if (imgAnnotations.length === 0) {
          // Row for image with no annotations
          csvRows.push([img.id, img.location || 'unknown', '', 'No annotation', '', ''])
        } else {
          // Row for each annotation
          imgAnnotations.forEach((ann) => {
            csvRows.push([
              img.id,
              img.location || 'unknown',
              ann.id,
              ann.label || '',
              ann.status || '',
              ann.created_at || '',
            ])
          })
        }
      })

      // Convert to CSV string
      const csvContent = [
        csvHeaders.map((h) => `"${h}"`).join(','),
        csvRows.map((row) => row.map((cell) => `"${cell}"`).join(',')).join('\n'),
      ].join('\n')

      const filename = `project-${props.projectId}-${Date.now()}.csv`
      downloadFile(csvContent, filename, 'text/csv')
    }

    alert(`Export ${exportFormat.value.toUpperCase()} successful!`)
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
        <p class="text-sm text-gray-600">Export project data and annotations</p>
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
              <div class="text-xs text-gray-500">Tabular data, metadata only</div>
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
        <span v-if="!isExporting">Export Data</span>
        <span v-else>Exporting...</span>
      </button>
    </div>
  </div>
</template>
