<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isStreaming = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const error = ref('')

const stats = ref({
  fps: 0, totalFrames: 0, diseaseFrames: 0, healthFrames: 0,
  diseaseRate: 0, runtime: '00:00:00'
})

const recentRecords = ref<Array<{ label: string; confidence: number; timestamp: string; color: string }>>([])

const mockDetections = [
  { label: '叶斑病', confidence: 0.92, color: '#f44336' },
  { label: '白粉病', confidence: 0.87, color: '#ff9800' },
  { label: '健康', confidence: 0.95, color: '#4caf50' },
  { label: '锈病', confidence: 0.78, color: '#ff5722' },
  { label: '早疫病', confidence: 0.81, color: '#2196f3' },
]

let startTime: Date | null = null
let statsInterval: number | null = null
let detectionInterval: number | null = null
let fpsInterval: number | null = null
let frameCount = 0

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [h, m, s].map(v => String(v).padStart(2, '0')).join(':')
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'environment' }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
      isStreaming.value = true
      error.value = ''
      startTime = new Date()

      statsInterval = window.setInterval(() => {
        if (!startTime) return
        stats.value.runtime = formatTime(Math.floor((Date.now() - startTime!.getTime()) / 1000))
      }, 1000)

      detectionInterval = window.setInterval(() => {
        if (!isStreaming.value) return
        frameCount++; stats.value.totalFrames++
        const det = mockDetections[Math.floor(Math.random() * mockDetections.length)]
        recentRecords.value.unshift({ ...det, timestamp: new Date().toLocaleTimeString('zh-CN') })
        if (recentRecords.value.length > 12) recentRecords.value.pop()
        if (det.label === '健康') stats.value.healthFrames++
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
    <div class="page-header animate-fade-down">
      <h2>📡 实时摄像头</h2>
      <p>实时视频流AI病害检测 · 毫秒级推理响应</p>
    </div>

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;">
      <!-- Camera Feed -->
      <div class="glass animate-fade-up">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <h3 style="font-weight:700;">📹 摄像头画面</h3>
          <span v-if="isStreaming" class="tag tag-success" style="display:flex;align-items:center;gap:6px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#4caf50;animation:pulse-green 2s infinite;"></span>
            直播中
          </span>
        </div>

        <div class="relative" style="background:#000;border-radius:12px;overflow:hidden;min-height:380px;">
          <video v-show="isStreaming" ref="videoRef" style="width:100%;height:100%;object-fit:cover;" playsinline muted autoplay />

          <div v-if="error" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.85);">
            <div style="text-align:center;padding:24px;color:#fff;">
              <div style="font-size:3rem;margin-bottom:12px;">⚠️</div>
              <p style="font-weight:600;">{{ error }}</p>
            </div>
          </div>

          <div v-if="!isStreaming && !error" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.75);">
            <div style="text-align:center;color:#fff;">
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

      <!-- Stats & Records -->
      <div class="space-y-4 animate-fade-up stagger-2">
        <!-- Stats -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:14px;">📊 实时统计</h3>
          <div class="space-y-2">
            <div style="display:flex;justify-content:space-between;padding:8px 12px;border-radius:8px;background:rgba(33,150,243,0.1);">
              <span style="font-size:0.85rem;color:var(--text-secondary);">FPS</span>
              <span style="font-weight:800;color:#2196f3;font-size:1.1rem;">{{ stats.fps }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.03);">
              <span style="font-size:0.85rem;color:var(--text-secondary);">检测帧数</span>
              <span style="font-weight:800;">{{ stats.totalFrames }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 12px;border-radius:8px;background:rgba(244,67,54,0.08);">
              <span style="font-size:0.85rem;color:var(--text-secondary);">病害帧数</span>
              <span style="font-weight:800;color:#f44336;font-size:1.1rem;">{{ stats.diseaseFrames }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 12px;border-radius:8px;background:rgba(76,175,80,0.08);">
              <span style="font-size:0.85rem;color:var(--text-secondary);">健康帧数</span>
              <span style="font-weight:800;color:#4caf50;font-size:1.1rem;">{{ stats.healthFrames }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 12px;border-radius:8px;background:rgba(255,152,0,0.08);">
              <span style="font-size:0.85rem;color:var(--text-secondary);">病害率</span>
              <span style="font-weight:800;color:#ff9800;font-size:1.1rem;">{{ stats.diseaseRate }}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.03);">
              <span style="font-size:0.85rem;color:var(--text-secondary);">运行时间</span>
              <span style="font-weight:700;color:var(--text-secondary);">{{ stats.runtime }}</span>
            </div>
          </div>
        </div>

        <!-- Recent Detections -->
        <div class="glass" style="max-height:320px;overflow-y:auto;">
          <h3 style="font-weight:700;margin-bottom:14px;">🕐 最近检测</h3>
          <div v-if="recentRecords.length === 0" style="text-align:center;padding:24px;color:var(--text-muted);">
            暂无记录
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="(record, idx) in recentRecords"
              :key="idx"
              style="display:flex;align-items:center;justify-content:space-between;padding:8px 10px;border-radius:8px;background:rgba(255,255,255,0.02);"
            >
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:8px;height:8px;border-radius:50%;" :style="{background:record.color}"></div>
                <span style="font-size:0.82rem;font-weight:500;">{{ record.label }}</span>
              </div>
              <span style="font-weight:700;font-size:0.82rem;" :style="{color:record.color}">
                {{ (record.confidence*100).toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
