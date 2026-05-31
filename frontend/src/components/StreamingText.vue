<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{
  text: string
  speed?: number
  enabled?: boolean
  markdown?: boolean
}>(), {
  speed: 30,
  enabled: true,
  markdown: false,
})

const emit = defineEmits<{ complete: [] }>()

const displayedText = ref('')
const isComplete = ref(false)
let timer: ReturnType<typeof setInterval> | null = null
let index = 0

function startStreaming() {
  if (!props.enabled || !props.text) {
    displayedText.value = props.text || ''
    isComplete.value = true
    return
  }
  displayedText.value = ''
  index = 0
  isComplete.value = false
  timer = setInterval(() => {
    if (index < props.text.length) {
      displayedText.value += props.text[index]
      index++
    } else {
      if (timer) clearInterval(timer)
      timer = null
      isComplete.value = true
      emit('complete')
    }
  }, props.speed)
}

function stop() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function skip() {
  if (timer) clearInterval(timer)
  timer = null
  displayedText.value = props.text
  isComplete.value = true
  emit('complete')
}

watch(() => props.text, () => {
  stop()
  startStreaming()
}, { immediate: true })

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

defineExpose({ stop, skip, isComplete })

// Simple markdown rendering
function renderMarkdown(content: string): string {
  return content
    .replace(/### (.+)/g, '<h3 style="margin:16px 0 8px;font-weight:700;font-size:1.05rem;">$1</h3>')
    .replace(/## (.+)/g, '<h2 style="margin:20px 0 10px;font-weight:700;font-size:1.15rem;">$1</h2>')
    .replace(/# (.+)/g, '<h1 style="margin:24px 0 12px;font-weight:800;font-size:1.3rem;">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong style="font-weight:700;">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/- (.+)/g, '<li style="margin:4px 0 4px 16px;list-style:disc;">$1</li>')
    .replace(/\n{2,}/g, '</p><p style="margin:8px 0;line-height:1.7;">')
    .replace(/\n/g, '<br/>')
}

const renderedContent = markdown ? renderMarkdown(displayedText.value) : displayedText.value
</script>

<template>
  <div class="streaming-text">
    <!-- Cursor blink -->
    <span v-if="markdown" v-html="renderedContent"></span>
    <span v-else>{{ displayedText }}</span>
    <span v-if="!isComplete" class="cursor">|</span>
    <span v-if="!isComplete && text.length > 0" class="skip-btn" @click="skip">跳过 »</span>
  </div>
</template>

<style scoped>
.streaming-text {
  position: relative;
  line-height: 1.8;
  color: var(--text-primary);
}

.cursor {
  display: inline-block;
  margin-left: 2px;
  font-weight: 700;
  color: #4caf50;
  animation: blink 0.7s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.skip-btn {
  display: inline-block;
  margin-left: 12px;
  padding: 2px 10px;
  font-size: 0.75rem;
  border-radius: 12px;
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
  cursor: pointer;
  font-weight: 600;
  vertical-align: middle;
  transition: all 0.2s;
}

.skip-btn:hover {
  background: rgba(76, 175, 80, 0.3);
}
</style>