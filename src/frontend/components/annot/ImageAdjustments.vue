<script setup>
import { ref } from 'vue'
import { Sun, Contrast } from 'lucide-vue-next'

const props = defineProps({
  brightness: {
    type: Number,
    default: 0,
  },
  contrast: {
    type: Number,
    default: 0,
  },
  redChannel: {
    type: Number,
    default: 0,
  },
  greenChannel: {
    type: Number,
    default: 0,
  },
  blueChannel: {
    type: Number,
    default: 0,
  },
  saturation: {
    type: Number,
    default: 0,
  },
  hue: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits([
  'update:brightness',
  'update:contrast',
  'update:redChannel',
  'update:greenChannel',
  'update:blueChannel',
  'update:saturation',
  'update:hue',
  'apply',
  'reset',
])

const showImageControls = ref(false)

const updateBrightness = (e) => {
  emit('update:brightness', Number(e.target.value))
}

const updateContrast = (e) => {
  emit('update:contrast', Number(e.target.value))
}

const updateRedChannel = (e) => {
  emit('update:redChannel', Number(e.target.value))
}

const updateGreenChannel = (e) => {
  emit('update:greenChannel', Number(e.target.value))
}

const updateBlueChannel = (e) => {
  emit('update:blueChannel', Number(e.target.value))
}

const updateSaturation = (e) => {
  emit('update:saturation', Number(e.target.value))
}

const updateHue = (e) => {
  emit('update:hue', Number(e.target.value))
}

const handleReset = () => {
  emit('reset')
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-lg p-3 max-h-[500px] overflow-y-auto">
    <button
      @click="showImageControls = !showImageControls"
      class="w-full flex items-center justify-between text-xs font-medium text-gray-700 mb-2 sticky top-0 bg-white z-10"
    >
      <span class="flex items-center gap-1">
        <Sun :size="14" />
        Image Controls
      </span>
      <span>{{ showImageControls ? '▼' : '▶' }}</span>
    </button>

    <div v-if="showImageControls" class="space-y-3">
      <!-- Basic Adjustments -->
      <div class="pb-2 border-b">
        <div class="text-xs font-medium text-gray-600 mb-2">Basic</div>

        <div class="space-y-2">
          <div>
            <label class="text-xs text-gray-600 flex items-center justify-between mb-1">
              <span class="flex items-center gap-1">
                <Sun :size="12" />
                Brightness
              </span>
              <span class="font-medium">{{ brightness }}</span>
            </label>
            <input
              type="range"
              :value="brightness"
              @input="updateBrightness"
              min="-100"
              max="100"
              class="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          <div>
            <label class="text-xs text-gray-600 flex items-center justify-between mb-1">
              <span class="flex items-center gap-1">
                <Contrast :size="12" />
                Contrast
              </span>
              <span class="font-medium">{{ contrast }}</span>
            </label>
            <input
              type="range"
              :value="contrast"
              @input="updateContrast"
              min="-100"
              max="100"
              class="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          <div>
            <label class="text-xs text-gray-600 flex items-center justify-between mb-1">
              <span>Saturation</span>
              <span class="font-medium">{{ saturation }}</span>
            </label>
            <input
              type="range"
              :value="saturation"
              @input="updateSaturation"
              min="-100"
              max="100"
              class="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          <div>
            <label class="text-xs text-gray-600 flex items-center justify-between mb-1">
              <span>Hue</span>
              <span class="font-medium">{{ hue }}°</span>
            </label>
            <input
              type="range"
              :value="hue"
              @input="updateHue"
              min="0"
              max="360"
              class="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      </div>

      <!-- RGB Channels -->
      <div class="pb-2">
        <div class="text-xs font-medium text-gray-600 mb-2">RGB Channels</div>

        <div class="space-y-2">
          <div>
            <label class="text-xs text-red-600 flex items-center justify-between mb-1">
              <span class="font-medium">Red</span>
              <span class="font-medium">{{ redChannel }}</span>
            </label>
            <input
              type="range"
              :value="redChannel"
              @input="updateRedChannel"
              min="-255"
              max="255"
              class="w-full h-1 bg-red-200 rounded-lg appearance-none cursor-pointer"
              style="accent-color: #ef4444"
            />
          </div>

          <div>
            <label class="text-xs text-green-600 flex items-center justify-between mb-1">
              <span class="font-medium">Green</span>
              <span class="font-medium">{{ greenChannel }}</span>
            </label>
            <input
              type="range"
              :value="greenChannel"
              @input="updateGreenChannel"
              min="-255"
              max="255"
              class="w-full h-1 bg-green-200 rounded-lg appearance-none cursor-pointer"
              style="accent-color: #22c55e"
            />
          </div>

          <div>
            <label class="text-xs text-blue-600 flex items-center justify-between mb-1">
              <span class="font-medium">Blue</span>
              <span class="font-medium">{{ blueChannel }}</span>
            </label>
            <input
              type="range"
              :value="blueChannel"
              @input="updateBlueChannel"
              min="-255"
              max="255"
              class="w-full h-1 bg-blue-200 rounded-lg appearance-none cursor-pointer"
              style="accent-color: #3b82f6"
            />
          </div>
        </div>
      </div>

      <button
        @click="handleReset"
        class="w-full px-2 py-1 bg-gray-500 hover:bg-gray-600 text-white rounded text-xs font-medium transition-colors"
      >
        Reset All
      </button>
    </div>
  </div>
</template>
