<script setup>
import { ref } from 'vue'

const emit = defineEmits(['select-category'])

const selectedCategory = ref(null)

const categories = [
  {
    key: 'satellite',
    label: 'Satellite',
    image: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
  },
  {
    key: 'hugging-face-dataset',
    label: 'Hugging Face Dataset',
    image: 'https://images.unsplash.com/photo-1516110833967-0b5716ca1387?auto=format&fit=crop&w=800&q=80',
  },
  {
    key: 'aws-open-data',
    label: 'AWS Open Data',
    image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80',
  },
]

const handleSelect = (category) => {
  if (category.key === 'hugging-face-dataset') {
    window.open(
      'https://huggingface.co/datasets?modality=modality:image&sort=trending',
      '_blank',
      'noopener,noreferrer'
    )
    return
  }

  selectedCategory.value = category.key
  emit('select-category', category)
}
</script>

<template>
  <div>
    <h3 class="text-lg font-semibold text-gray-900 mb-2">Data acquisition</h3>
    <p class="text-sm text-gray-500 mb-4">Choose a data source category:</p>

    <div class="grid grid-cols-2 gap-3">
      <button
        v-for="category in categories"
        :key="category.key"
        type="button"
        class="group rounded-lg overflow-hidden border transition-all text-left"
        :class="
          selectedCategory === category.key
            ? 'border-blue-950 ring-2 ring-blue-200'
            : 'border-gray-200 hover:border-blue-300'
        "
        @click="handleSelect(category)"
      >
        <div class="h-24 bg-gray-100 overflow-hidden">
          <img
            :src="category.image"
            :alt="category.label"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
        </div>
        <div class="px-2 py-2">
          <p class="text-xs font-medium text-gray-800 leading-tight">{{ category.label }}</p>
        </div>
      </button>
    </div>
  </div>
</template>
