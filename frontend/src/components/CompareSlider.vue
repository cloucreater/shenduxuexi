<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = withDefaults(defineProps<{
  beforeImage?: string
  afterImage?: string
  beforeLabel?: string
  afterLabel?: string
  width?: number
  height?: number
}>(), {
  beforeLabel: '施药前',
  afterLabel: '施药后',
  width: 600,
  height: 400,
})

const emit = defineEmits<{ change: [position: number] }>()

const containerRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const sliderPos = ref(50) // percentage

const sliderStyle = computed(() => ({
  left: `${sliderPos.value}%`,
}))

const clipStyle = computed(() => ({
  clipPath: `inset(0 ${100 - sliderPos.value}% 0 0)`,
}))

function onPointerDown(e: PointerEvent) {
  isDragging.value = true
  e.preventDefault()
  ;(e.target as HTMLElement).setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!isDragging.value || !containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width))
  sliderPos.value = (x / rect.width) * 100
  emit('change', sliderPos.value)
}

function onPointerUp() {
  isDragging.value = false
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowLeft') sliderPos.value = Math.max(0, sliderPos.value - 5)
  if (e.key === 'ArrowRight') sliderPos.value = Math.min(100, sliderPos.value + 5)
  emit('change', sliderPos.value)
}
</script>

<template>
  <div
    ref="containerRef"
    class="compare-slider"
    :style="{ maxWidth: width + 'px', height: height + 'px' }"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
    role="slider"
    :aria-valuenow="sliderPos"
    tabindex="0"
    @keydown="handleKeydown"
  >
    <!-- After image (full) -->
    <div v-if="afterImage" class="cs-image cs-after">
      <img :src="afterImage" :alt="afterLabel" />
      <span class="cs-label cs-label-right">{{ afterLabel }}</span>
    </div>

    <!-- Before image (clipped) -->
    <div v-if="beforeImage" class="cs-image cs-before" :style="clipStyle">
      <img :src="beforeImage" :alt="beforeLabel" />
      <span class="cs-label cs-label-left">{{ beforeLabel }}</span>
    </div>

    <!-- Slider handle -->
    <div
      class="cs-handle"
      :class="{ active: isDragging }"
      :style="sliderStyle"
      @pointerdown="onPointerDown"
    >
      <div class="cs-handle-circle">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        <div class="cs-handle-line"></div>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="9 6 15 12 9 18" />
        </svg>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!beforeImage && !afterImage" class="cs-empty">
      <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="opacity:0.3;">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <path d="M21 15l-5-5L5 21" />
      </svg>
      <p>暂无对比图片</p>
    </div>
  </div>
</template>

<style scoped>
.compare-slider {
  position: relative;
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  user-select: none;
  touch-action: none;
  background: rgba(0,0,0,0.05);
}

.cs-image {
  position: absolute;
  inset: 0;
}

.cs-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  pointer-events: none;
}

.cs-before {
  z-index: 2;
}

.cs-after {
  z-index: 1;
}

.cs-label {
  position: absolute;
  bottom: 14px;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  backdrop-filter: blur(8px);
  z-index: 5;
  pointer-events: none;
}

.cs-label-left {
  left: 14px;
  background: rgba(76, 175, 80, 0.8);
  color: #fff;
}

.cs-label-right {
  right: 14px;
  background: rgba(33, 150, 243, 0.8);
  color: #fff;
}

.cs-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 3px;
  background: rgba(255, 255, 255, 0.8);
  z-index: 10;
  cursor: ew-resize;
  transform: translateX(-50%);
  transition: background 0.2s;
}

.cs-handle.active {
  background: #4caf50;
}

.cs-handle-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 12px rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: #333;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cs-handle.active .cs-handle-circle {
  transform: translate(-50%, -50%) scale(1.1);
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4);
  background: #fff;
}

.cs-handle-line {
  width: 2px;
  height: 20px;
  background: rgba(0,0,0,0.15);
  border-radius: 1px;
}

.cs-empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.9rem;
}
</style>