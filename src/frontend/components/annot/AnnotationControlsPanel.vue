<script setup lang="ts">
import { Save, Check, Trash2, Plus } from 'lucide-vue-next'

interface Props {
  description: string
  selectedLabel: string
  availableLabels: string[]
  newLabel: string
  showLabelInput: boolean
  saving: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:description': [value: string]
  'update:selectedLabel': [value: string]
  'update:newLabel': [value: string]
  'update:showLabelInput': [value: boolean]
  addLabel: []
  save: []
  accept: []
  reject: []
}>()
</script>

<template>
  <div class="bg-gray-50 border-t border-gray-200 p-4 space-y-4 max-h-[40%] overflow-y-auto">
    <!-- Description -->
    <div>
      <label class="block text-sm font-semibold text-gray-700 mb-2">Description</label>
      <textarea
        :value="description"
        @input="emit('update:description', ($event.target as HTMLTextAreaElement).value)"
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
          :value="selectedLabel"
          @input="emit('update:selectedLabel', ($event.target as HTMLSelectElement).value)"
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        >
          <option value="">Select a label...</option>
          <option v-for="label in availableLabels" :key="label" :value="label">
            {{ label }}
          </option>
        </select>
        <button
          @click="emit('update:showLabelInput', !showLabelInput)"
          class="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center gap-1"
          title="Add new label"
        >
          <Plus :size="16" />
        </button>
      </div>

      <!-- Add New Label Input -->
      <div v-if="showLabelInput" class="mt-2 flex gap-2">
        <input
          :value="newLabel"
          @input="emit('update:newLabel', ($event.target as HTMLInputElement).value)"
          type="text"
          placeholder="New label name..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
        <button
          @click="emit('addLabel')"
          class="px-3 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors text-sm"
        >
          Add
        </button>
        <button
          @click="emit('update:showLabelInput', false)"
          class="px-3 py-2 bg-gray-400 hover:bg-gray-500 text-white rounded-lg transition-colors text-sm"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="grid grid-cols-3 gap-2">
      <button
        @click="emit('save')"
        :disabled="saving"
        class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-sm"
      >
        <Save :size="16" />
        <span>Save</span>
      </button>
      <button
        @click="emit('accept')"
        :disabled="saving"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-sm"
      >
        <Check :size="16" />
        <span>Accept</span>
      </button>
      <button
        @click="emit('reject')"
        :disabled="saving"
        class="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1 text-sm"
      >
        <Trash2 :size="16" />
        <span>Reject</span>
      </button>
    </div>
  </div>
</template>
