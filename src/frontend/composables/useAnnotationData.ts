import { ref } from 'vue'

interface LabelColors {
  [key: string]: string
}

export function useAnnotationData(projectId: number, imageId: string | number, userId: number) {
  const api = useApi()

  const description = ref('')
  const selectedLabel = ref('')
  const availableLabels = ref<string[]>([])
  const newLabel = ref('')
  const showLabelInput = ref(false)
  const saving = ref(false)

  const labelColors = ref<LabelColors>({
    person: '#FF6B6B',
    car: '#4ECDC4',
    dog: '#95E1D3',
    cat: '#F38181',
    default: '#00ff00',
  })

  const generateRandomColor = () => {
    const hue = Math.floor(Math.random() * 360)
    return `hsl(${hue}, 70%, 60%)`
  }

  const getLabelColor = (label: string) => {
    return labelColors.value[label] || labelColors.value['default']
  }

  const fetchLabels = async () => {
    try {
      const annotations = await api.get(`/annotations/?project_id=${projectId}`)
      const uniqueLabels = new Set<string>()
      annotations.forEach((annotation: any) => {
        if (annotation.label) {
          uniqueLabels.add(annotation.label)
        }
      })
      availableLabels.value = Array.from(uniqueLabels).sort()

      availableLabels.value.forEach((label) => {
        if (!labelColors.value[label]) {
          labelColors.value[label] = generateRandomColor()
        }
      })
    } catch (error) {
      console.error('Error fetching labels:', error)
    }
  }

  const loadExistingAnnotation = async () => {
    try {
      const annotations = await api.get(`/annotations/?project_id=${projectId}`)
      const existingAnnotation = annotations.find(
        (ann: any) => ann.data_id === imageId || ann.data_id === String(imageId)
      )

      if (existingAnnotation) {
        console.log('Found existing annotation:', existingAnnotation)
        description.value = existingAnnotation.description || ''
        selectedLabel.value = existingAnnotation.label || ''
      }
    } catch (error) {
      console.error('Error loading existing annotation:', error)
    }
  }

  const addLabel = async () => {
    if (!newLabel.value.trim()) return

    availableLabels.value.push(newLabel.value)
    selectedLabel.value = newLabel.value

    // Assign color to new label
    if (!labelColors.value[newLabel.value]) {
      labelColors.value[newLabel.value] = generateRandomColor()
    }

    const labelToSave = newLabel.value
    newLabel.value = ''
    showLabelInput.value = false

    try {
      await api.post('/annotations/labels', { name: labelToSave })
    } catch (error) {
      console.error('Failed to save label:', error)
    }
  }

  const saveAnnotation = async (emit: any) => {
    if (!selectedLabel.value) {
      alert('Please select or create a label')
      return
    }

    saving.value = true
    try {
      const existingAnnotations = await api.get(`/annotations/?project_id=${projectId}`)
      const existingAnnotation = existingAnnotations.find(
        (ann: any) => ann.data_id === imageId || ann.data_id === String(imageId)
      )

      if (existingAnnotation) {
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
        const annotationData = {
          data_id: imageId,
          project_id: projectId,
          author_id: userId,
          description: description.value,
          label: selectedLabel.value,
          status: 'human annotation',
        }

        const response = await api.post('/annotations/', annotationData)
        console.log('Annotation saved:', response)
        emit('save', response)
        alert('✓ Annotation saved successfully!')
      }
    } catch (error: any) {
      console.error('Failed to save annotation:', error)
      alert(`Failed to save annotation: ${error?.data?.detail || error?.message || 'Unknown error'}`)
    } finally {
      saving.value = false
    }
  }

  const acceptAnnotation = async (emit: any) => {
    saving.value = true
    try {
      const response = await api.post(`/annotations/update-status/${imageId}`, { status: 'certified' })
      emit('accept', response)
      alert('✓ Annotation accepted!')
    } catch (error: any) {
      console.error('Failed to accept annotation:', error)
      alert(`Failed to accept annotation: ${error?.data?.detail || error?.message || 'Unknown error'}`)
    } finally {
      saving.value = false
    }
  }

  const rejectAnnotation = async (emit: any) => {
    const confirmReject = confirm('Are you sure you want to reject this annotation?')
    if (!confirmReject) return

    saving.value = true
    try {
      const response = await api.post(`/annotations/update-status/${imageId}`, { status: 'rejected' })
      emit('reject', response)
      alert('✓ Annotation rejected!')
    } catch (error: any) {
      console.error('Failed to reject annotation:', error)
      alert(`Failed to reject annotation: ${error?.data?.detail || error?.message || 'Unknown error'}`)
    } finally {
      saving.value = false
    }
  }

  return {
    description,
    selectedLabel,
    availableLabels,
    newLabel,
    showLabelInput,
    saving,
    labelColors,
    getLabelColor,
    fetchLabels,
    loadExistingAnnotation,
    addLabel,
    saveAnnotation,
    acceptAnnotation,
    rejectAnnotation,
  }
}
