<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Annotorious } from '@recogito/annotorious'
import '@recogito/annotorious/dist/annotorious.min.css'
import { Save, X, Check, Trash2, Plus, Undo2 } from 'lucide-vue-next'

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
const annoRef = ref(null)
const drawingMode = ref(false)
const annotations = ref([])

// Annotation state
const description = ref('')
const selectedLabel = ref('')
const availableLabels = ref([])
const newLabel = ref('')
const showLabelInput = ref(false)
const saving = ref(false)
const currentAnnotation = ref(null)

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
  } catch (error) {
    console.error('Error fetching labels:', error)
  }
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

  // Initialize Annotorious after image loads
  await nextTick()
  initializeAnnotorious()
})

const initializeAnnotorious = () => {
  if (!imageRef.value) return

  // Create Annotorious instance
  annoRef.value = new Annotorious({
    image: imageRef.value,
    readOnly: false,
  })

  // Event listeners
  annoRef.value.on('createAnnotation', (annotation) => {
    console.log('Annotation created:', annotation)
    annotations.value.push(annotation)
    currentAnnotation.value = annotation
  })

  annoRef.value.on('updateAnnotation', (annotation) => {
    console.log('Annotation updated:', annotation)
    const index = annotations.value.findIndex((a) => a.id === annotation.id)
    if (index !== -1) {
      annotations.value[index] = annotation
    }
    currentAnnotation.value = annotation
  })

  annoRef.value.on('deleteAnnotation', (annotation) => {
    console.log('Annotation deleted:', annotation)
    const index = annotations.value.findIndex((a) => a.id === annotation.id)
    if (index !== -1) {
      annotations.value.splice(index, 1)
    }
    if (currentAnnotation.value?.id === annotation.id) {
      currentAnnotation.value = null
      description.value = ''
      selectedLabel.value = ''
    }
  })

  annoRef.value.on('selectAnnotation', (annotation) => {
    console.log('Annotation selected:', annotation)
    currentAnnotation.value = annotation
    // Load annotation details if they exist
    if (annotation.body && annotation.body.length > 0) {
      const body = annotation.body[0]
      description.value = body.value || ''
      selectedLabel.value = body.purpose || ''
    }
  })
}

const toggleDrawingMode = () => {
  drawingMode.value = !drawingMode.value
  if (annoRef.value) {
    annoRef.value.setReadOnly(!drawingMode.value)
  }
}

const clearAllAnnotations = () => {
  if (annoRef.value && annotations.value.length > 0) {
    annotations.value.forEach((annotation) => {
      annoRef.value.removeAnnotation(annotation)
    })
    annotations.value = []
    currentAnnotation.value = null
    description.value = ''
    selectedLabel.value = ''
  }
}

const undoLastAnnotation = () => {
  if (annotations.value.length > 0) {
    const lastAnnotation = annotations.value[annotations.value.length - 1]
    annoRef.value.removeAnnotation(lastAnnotation)
    annotations.value.pop()
    currentAnnotation.value = null
    description.value = ''
    selectedLabel.value = ''
  }
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
  if (!selectedLabel.value) {
    alert('Please select or create a label')
    return
  }

  if (!currentAnnotation.value) {
    alert('Please create an annotation on the image first')
    return
  }

  saving.value = true
  try {
    // Update current annotation with label and description
    const annotationBody = [
      {
        type: 'TextualBody',
        purpose: selectedLabel.value,
        value: description.value,
      },
    ]

    currentAnnotation.value.body = annotationBody
    annoRef.value.updateAnnotation(currentAnnotation.value)

    // Get canvas as PNG for mask
    const canvas = document.querySelector('.a9s-annotationlayer canvas')
    const maskData = canvas?.toDataURL('image/png') || null

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
        mask: maskData,
        annotation_data: JSON.stringify(currentAnnotation.value),
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
    <!-- Annotorious Drawing Area -->
    <div class="flex-1 flex flex-col items-center justify-center p-4 bg-gray-100 relative overflow-auto">
      <div class="relative bg-white rounded-lg shadow-md">
        <img ref="imageRef" :src="imageSrc" alt="Annotation image" class="max-w-full max-h-[600px] object-contain" />
      </div>

      <!-- Drawing Mode Info -->
      <div
        v-if="drawingMode"
        class="absolute top-4 right-4 bg-white p-4 rounded-lg shadow-lg border border-gray-200 space-y-3 max-w-xs"
      >
        <div class="text-xs text-center text-gray-700 font-semibold">📍 Drawing Mode Active</div>
        <div class="text-xs text-gray-600 text-center">Draw shapes or rectangles on the image</div>
        <div class="text-xs text-gray-500 text-center">{{ annotations.length }} annotation(s) created</div>

        <div class="flex gap-2">
          <button
            @click="undoLastAnnotation"
            :disabled="annotations.length === 0"
            class="flex-1 px-3 py-2 text-sm bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-300 text-white rounded transition-colors flex items-center justify-center gap-1"
          >
            <Undo2 :size="14" />
            Undo
          </button>
          <button
            @click="clearAllAnnotations"
            :disabled="annotations.length === 0"
            class="flex-1 px-3 py-2 text-sm bg-red-500 hover:bg-red-600 disabled:bg-gray-300 text-white rounded transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>
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

      <!-- Label Selection -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2">Label</label>
        <div class="flex gap-2">
          <select
            v-model="selectedLabel"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="">Select a label...</option>
            <option v-for="label in availableLabels" :key="label" :value="label">
              {{ label }}
            </option>
          </select>
          <button
            @click="showLabelInput = !showLabelInput"
            class="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center gap-1"
            title="Add new label"
          >
            <Plus :size="16" />
          </button>
        </div>

        <!-- Add New Label Input -->
        <div v-if="showLabelInput" class="mt-2 flex gap-2">
          <input
            v-model="newLabel"
            type="text"
            placeholder="New label name..."
            class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <button
            @click="addLabel"
            class="px-3 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors text-sm"
          >
            Add
          </button>
          <button
            @click="showLabelInput = false"
            class="px-3 py-2 bg-gray-400 hover:bg-gray-500 text-white rounded-lg transition-colors text-sm"
          >
            Cancel
          </button>
        </div>
      </div>

      <!-- Drawing Mode Toggle -->
      <div>
        <button
          @click="toggleDrawingMode"
          :class="[
            'w-full px-4 py-2 rounded-lg font-medium transition-colors text-sm',
            drawingMode
              ? 'bg-purple-600 hover:bg-purple-700 text-white'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-800',
          ]"
        >
          {{ drawingMode ? '✓ Drawing Mode Active' : 'Draw Annotation' }}
        </button>
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
