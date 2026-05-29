<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isStreaming = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const error = ref('')

const stats = ref({
  fps: 0, totalFrames: 0, diseaseFrames: 0, healthFrames: 0,
  diseaseRate: 0, runtime: '00:00:00'
})

const recentRecords = ref<Array<{ label: string; confidence: number; timestamp: string }>>([])

const mockDetections = [
  { label: '白粉病 / Powdery Mildew', confidence: 0.92 },
  { label: '叶斑病 / Leaf Spot', confidence: 0.87 },
  { label: '健康 / Healthy', confidence: 0.95 },
  { label: '锈病 / Rust', confidence: 0.78 },
  { label: '早疫病 / Early Blight', confidence: 0.81 },
]

let startTime: Date | null = null
let statsInterval: number | null = null
let detectionInterval: number | null = null
let fpsInterval: number | null = null
let frameCount = 0

function getLabelColor(label: string): string {
  if (label.includes('白粉病')) return '#ef4444'
  if (label.includes('叶斑病')) return '#f59e0b'
  if (label.includes('锈病')) return '#f97316'
  if (label.includes('早疫病')) return '#22c55e'
  return '#16a34a'
}

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [h, m, s].map(v => String(v).padStart(2, '0')).join(':')
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 } }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
      isStreaming.value = true
      error.value = ''
      startTime = new Date()

      statsInterval = window.setInterval(() => {
        if (!startTime) return
        stats.value.runtime = formatTime(Math.floor((Date.now() - startTime.getTime()) / 1000))
      }, 1000)

      detectionInterval = window.setInterval(() => {
        if (!isStreaming.value) return
        frameCount++; stats.value.totalFrames++
        const det = mockDetections[Math.floor(Math.random() * mockDetections.length)]
        recentRecords.value.unshift({ ...det, timestamp: new Date().toLocaleTimeString('zh-CN') })
        if (recentRecords.value.length > 10) recentRecords.value.pop()
        if (det.label.includes('健康')) stats.value.healthFrames++
        else stats.value.diseaseFrames++
        stats.value.diseaseRate = stats.value.totalFrames > 0
          ? parseFloat((stats.value.diseaseFrames / stats.value.totalFrames * 100).toFixed(1))
          : 0
      }, 2000)

      fpsInterval = window.setInterval(() => { stats.value.fps = frameCount; frameCount = 0 }, 1000)
    }
  } catch (err: any) {
    error.value = '无法访问摄像头: ' + (err.message || '未知错误')
  }
}

function stopCamera() {
  if (videoRef.value?.srcObject) {
    (videoRef.value.srcObject as MediaStream).getTracks().forEach(t => t.stop())
    videoRef.value.srcObject = null
  }
  isStreaming.value = false
  if (statsInterval) clearInterval(statsInterval)
  if (detectionInterval) clearInterval(detectionInterval)
  if (fpsInterval) clearInterval(fpsInterval)
  stats.value = { fps: 0, totalFrames: 0, diseaseFrames: 0, healthFrames: 0, diseaseRate: 0, runtime: '00:00:00' }
  recentRecords.value = []
  startTime = null
}

onMounted(() => { startCamera() })
onUnmounted(() => { stopCamera() })
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div style="display:flex;justify-content:space-between;align-items:center;" class="animate-fade-down">
      <div class="page-header" style="margin-bottom:0;">
        <h2>📷 实时摄像头检测</h2>
        <p>实时视频流病害检测与统计</p>
      </div>
      <button @click="router.push('/detect/camera/history')" class="btn btn-outline">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        历史记录
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Camera Feed -->
      <div class="lg:col-span-2">
        <div class="glass-card animate-fade-up stagger-1">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-weight:700;color:var(--text-primary);font-size:1.05rem;">📹 摄像头画面</h3>
            <span v-if="isStreaming" class="tag tag-success" style="display:flex;align-items:center;gap:6px;">
              <span style="width:8px;height:8px;border-radius:50%;background:var(--color-success);animation:pulse-green 2s infinite;"></span>
              直播中
            </span>
            <span v-else class="tag" style="background:rgba(0,0,0,0.04);color:var(--text-muted);">已停止</span>
          </div>

          <div class="relative bg-black rounded-xl overflow-hidden" style="min-height:380px;">
            <video v-show="isStreaming" ref="videoRef" class="w-full h-full object-cover" playsinline muted />
            <canvas ref="canvasRef" class="hidden" />

            <!-- Error -->
            <div v-if="error" class="absolute inset-0 flex items-center justify-center" style="background:rgba(0,0,0,0.85);">
              <div class="text-center" style="color:#fff;padding:24px;">
                <div style="font-size:3rem;margin-bottom:12px;">⚠️</div>
                <p style="font-weight:600;">{{ error }}</p>
              </div>
            </div>

            <!-- Not started -->
            <div v-if="!isStreaming && !error" class="absolute inset-0 flex items-center justify-center" style="background:rgba(0,0,0,0.75);">
              <div class="text-center" style="color:#fff;">
                <div style="font-size:3rem;margin-bottom:12px;">📷</div>
                <p style="font-weight:600;font-size:1.05rem;margin-bottom:16px;">摄像头未启动</p>
                <button @click="startCamera" class="btn btn-primary">启动摄像头</button>
              </div>
            </div>
          </div>

          <div style="display:flex;gap:12px;margin-top:14px;">
            <button v-if="!isStreaming" @click="startCamera" class="btn btn-primary btn-lg" style="flex:1;">
              ▶️ 启动摄像头
            </button>
            <button v-else @click="stopCamera" class="btn btn-danger btn-lg" style="flex:1;">
              ⏹️ 停止检测
            </button>
          </div>
        </div>
      </div>

      <!-- Stats Panel -->
      <div class="space-y-4 animate-fade-up stagger-2">
        <div class="glass-card">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:14px;font-size:1rem;">📊 实时统计</h3>
          <div class="space-y-2">
            <div style="display:flex;justify-content:space-between;padding:10px 12px;border-radius:10px;background:var(--color-info-bg);">
              <span style="color:var(--text-secondary);font-size:0.85rem;">FPS</span>
              <span style="font-weight:800;color:var(--color-info);font-size:1.2rem;">{{ stats.fps }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:10px 12px;border-radius:10px;background:rgba(0,0,0,0.015);">
              <span style="color:var(--text-secondary);font-size:0.85rem;">检测帧数</span>
              <span style="font-weight:800;color:var(--text-primary);font-size:1.2rem;">{{ stats.totalFrames }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:10px 12px;border-radius:10px;background:var(--color-danger-bg);">
              <span style="color:var(--text-secondary);font-size:0.85rem;">病害帧数</span>
              <span style="font-weight:800;color:var(--color-danger);font-size:1.2rem;">{{ stats.diseaseFrames }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:10px 12px;border-radius:10px;background:var(--color-success-bg);">
              <span style="color:var(--text-secondary);font-size:0.85rem;">健康帧数</span>
              <span style="font-weight:800;color:var(--color-success);font-size:1.2rem;">{{ stats.healthFrames }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:10px 12px;border-radius:10px;background:var(--color-warning-bg);">
              <span style="color:var(--text-secondary);font-size:0.85rem;">病害率</span>
              <span style="font-weight:800;color:var(--color-warning);font-size:1.2rem;">{{ stats.diseaseRate }}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:10px 12px;border-radius:10px;background:rgba(0,0,0,0.015);">
              <span style="color:var(--text-secondary);font-size:0.85rem;">运行时间</span>
              <span style="font-weight:700;color:var(--text-secondary);">{{ stats.runtime }}</span>
            </div>
          </div>
        </div>

        <!-- Recent Records -->
        <div class="glass-card">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:14px;font-size:1rem;">🕐 最近检测</h3>
          <div v-if="recentRecords.length === 0" style="text-align:center;padding:24px;color:var(--text-muted);">
            暂无记录
          </div>
          <div v-else class="space-y-2" style="max-height:280px;overflow-y:auto;">
            <div
              v-for="(record, idx) in recentRecords"
              :key="idx"
              style="display:flex;align-items:center;justify-content:space-between;padding:8px 10px;border-radius:8px;background:rgba(0,0,0,0.012);"
            >
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:8px;height:8px;border-radius:50%;" :style="{ background: getLabelColor(record.label) }"></div>
                <span style="font-size:0.82rem;font-weight:500;color:var(--text-primary);">{{ record.label.split(' / ')[0] }}</span>
              </div>
              <span style="font-weight:700;font-size:0.82rem;" :style="{ color: getLabelColor(record.label) }">
                {{ (record.confidence * 100).toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
