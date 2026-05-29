<script setup lang="ts">
import { ref, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const videoUrl = ref<string | null>(null)
const isLoading = ref(false)
const uploadProgress = ref(0)
const result = ref<any>(null)

let pieChart: echarts.ECharts | null = null

function handleDragOver(e: DragEvent) { e.preventDefault(); isDragging.value = true }
function handleDragLeave() { isDragging.value = false }

function handleDrop(e: DragEvent) {
  e.preventDefault(); isDragging.value = false
  const files = e.dataTransfer?.files
  if (files?.[0]?.type.match(/^video\//)) { handleFileSelect(files[0]) }
  else { alert('请上传视频文件') }
}

function handleFileInput(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) handleFileSelect(target.files[0])
}

function handleFileSelect(file: File) {
  if (!file.type.match(/^video\//)) { alert('请上传视频文件（MP4/AVI/MOV）'); return }
  selectedFile.value = file
  videoUrl.value = URL.createObjectURL(file)
  result.value = null
}

function resetDetection() {
  selectedFile.value = null
  if (videoUrl.value) URL.revokeObjectURL(videoUrl.value)
  videoUrl.value = null
  result.value = null
  uploadProgress.value = 0
}

async function startDetection() {
  if (!selectedFile.value) return
  isLoading.value = true; uploadProgress.value = 0

  for (let i = 0; i <= 100; i += 5) {
    await new Promise(resolve => setTimeout(resolve, 80))
    uploadProgress.value = i
  }

  result.value = {
    totalFrames: 480,
    diseaseFrames: 356,
    healthFrames: 124,
    diseaseRate: 74.2,
    categories: [
      { name: '叶斑病', enName: 'Leaf Spot', count: 178, percentage: 50.0, avgConfidence: 0.91, color: '#f44336' },
      { name: '白粉病', enName: 'Powdery Mildew', count: 112, percentage: 31.5, avgConfidence: 0.87, color: '#ff9800' },
      { name: '锈病', enName: 'Rust', count: 66, percentage: 18.5, avgConfidence: 0.82, color: '#ff5722' },
    ],
    timeline: [
      { frameId: 15, label: '叶斑病', confidence: 0.94, time: '00:00:15', timeSec: 0.5 },
      { frameId: 32, label: '叶斑病', confidence: 0.91, time: '00:00:32', timeSec: 1.1 },
      { frameId: 48, label: '白粉病', confidence: 0.93, time: '00:00:48', timeSec: 1.6 },
      { frameId: 67, label: '白粉病', confidence: 0.88, time: '00:01:07', timeSec: 2.2 },
      { frameId: 89, label: '叶斑病', confidence: 0.92, time: '00:01:29', timeSec: 3.0 },
      { frameId: 112, label: '锈病', confidence: 0.85, time: '00:01:52', timeSec: 3.7 },
      { frameId: 135, label: '白粉病', confidence: 0.90, time: '00:02:15', timeSec: 4.5 },
      { frameId: 158, label: '叶斑病', confidence: 0.87, time: '00:02:38', timeSec: 5.3 },
      { frameId: 181, label: '锈病', confidence: 0.91, time: '00:03:01', timeSec: 6.0 },
      { frameId: 204, label: '白粉病', confidence: 0.86, time: '00:03:24', timeSec: 6.8 },
      { frameId: 227, label: '叶斑病', confidence: 0.89, time: '00:03:47', timeSec: 7.6 },
      { frameId: 250, label: '锈病', confidence: 0.83, time: '00:04:10', timeSec: 8.3 },
    ],
    sliderValue: 0,
  }

  isLoading.value = false

  await nextTick()
  setTimeout(renderPieChart, 200)
}

function renderPieChart() {
  const el = document.getElementById('videoPieChart')
  if (!el || !result.value) return
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(el)

  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c} 帧 ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['45%', '72%'],
      center: ['50%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: 'rgba(10,40,20,0.5)', borderWidth: 3 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
      data: result.value.categories.map((c: any) => ({
        name: c.name, value: c.count, itemStyle: { color: c.color }
      }))
    }]
  })
}

function getLabelColor(label: string): string {
  if (label.includes('叶斑病')) return '#f44336'
  if (label.includes('白粉病')) return '#ff9800'
  if (label.includes('锈病')) return '#ff5722'
  return '#4caf50'
}

onUnmounted(() => { pieChart?.dispose() })
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>🎥 视频检测</h2>
      <p>上传田间视频，逐帧分析病害发生情况与分布</p>
    </div>

    <!-- Upload -->
    <div v-if="!selectedFile" class="glass animate-scale-in" style="padding:48px 32px;">
      <div
        :class="['upload-zone', { dragover: isDragging }]"
        style="border-style:dashed;padding:60px 40px;"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="($refs.videoFileInput as HTMLInputElement)?.click()"
      >
        <input ref="videoFileInput" type="file" accept="video/*" style="display:none" @change="handleFileInput" />
        <div class="upload-icon">🎬</div>
        <p style="font-weight:600;font-size:1.1rem;">拖拽视频到此处</p>
        <p style="color:var(--text-tertiary);">或点击选择文件 · 支持 MP4、AVI、MOV 格式</p>
      </div>
    </div>

    <div v-else class="space-y-6">
      <!-- Video Preview -->
      <div class="glass animate-fade-up">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <h3 style="font-weight:700;">🎬 视频预览</h3>
          <button class="btn btn-outline btn-sm" @click="resetDetection">重新选择</button>
        </div>
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;">
          <div style="font-size:2rem;">🎬</div>
          <div>
            <p style="font-weight:600;">{{ selectedFile.name }}</p>
            <p style="font-size:0.82rem;color:var(--text-tertiary);">{{ (selectedFile.size/1024/1024).toFixed(2) }} MB</p>
          </div>
        </div>
        <div v-if="videoUrl" style="border-radius:12px;overflow:hidden;background:#000;">
          <video :src="videoUrl" style="width:100%;max-height:360px;" controls />
        </div>
      </div>

      <!-- Progress -->
      <div v-if="isLoading" class="glass animate-fade-up">
        <h3 style="font-weight:700;margin-bottom:14px;">⏳ 检测进度</h3>
        <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:8px;">
          <span style="color:var(--text-secondary);">正在逐帧分析...</span>
          <span style="font-weight:700;color:#4caf50;">{{ uploadProgress }}%</span>
        </div>
        <div class="progress-track" style="height:10px;">
          <div class="progress-fill" :style="{width:uploadProgress+'%'}"></div>
        </div>
        <p style="text-align:center;color:var(--text-muted);font-size:0.82rem;margin-top:10px;">正在进行逐帧检测，请稍候...</p>
      </div>

      <!-- Start Button -->
      <button
        v-if="!result && !isLoading"
        @click="startDetection"
        class="btn btn-primary btn-lg"
        style="width:100%;"
      >
        🚀 开始逐帧检测
      </button>

      <!-- Results -->
      <div v-if="result" class="space-y-6">
        <!-- Stats Cards -->
        <div class="stats-grid animate-fade-up">
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(33,150,243,0.15);">📊</div>
            <div class="stat-value">{{ result.totalFrames }}</div>
            <div class="stat-label">总帧数</div>
          </div>
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(244,67,54,0.15);">🦠</div>
            <div class="stat-value">{{ result.diseaseFrames }}</div>
            <div class="stat-label">病害帧数</div>
          </div>
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(255,152,0,0.15);">📈</div>
            <div class="stat-value">{{ result.diseaseRate }}%</div>
            <div class="stat-label">病害率</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
          <!-- Category Distribution -->
          <div class="glass animate-fade-up stagger-1">
            <h3 style="font-weight:700;margin-bottom:14px;">📊 病害类别分布</h3>
            <div id="videoPieChart" style="width:100%;height:280px;"></div>
            <div class="space-y-2" style="margin-top:10px;">
              <div v-for="cat in result.categories" :key="cat.name"
                style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <div style="width:8px;height:8px;border-radius:50%;" :style="{background:cat.color}"></div>
                  <span style="font-size:0.85rem;">{{ cat.name }}</span>
                </div>
                <div style="text-align:right;">
                  <span style="font-weight:700;">{{ cat.count }}帧</span>
                  <span style="margin-left:8px;font-size:0.78rem;color:var(--text-tertiary);">{{ cat.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Timeline -->
          <div class="glass animate-fade-up stagger-2">
            <h3 style="font-weight:700;margin-bottom:14px;">📍 病害时间轴</h3>
            <p style="font-size:0.8rem;color:var(--text-tertiary);margin-bottom:12px;">拖动滑块查看不同时间点的检测结果</p>

            <!-- Slider -->
            <input
              type="range" min="0" :max="result.timeline.length-1" step="1"
              v-model="result.sliderValue"
              style="width:100%;height:6px;-webkit-appearance:none;appearance:none;background:rgba(255,255,255,0.1);border-radius:3px;outline:none;margin-bottom:16px;"
            />

            <!-- Current Frame Info -->
            <div v-if="result.timeline[result.sliderValue]"
              style="padding:14px;background:rgba(255,255,255,0.04);border-radius:12px;text-align:center;margin-bottom:12px;"
            >
              <p style="font-size:0.82rem;color:var(--text-tertiary);">
                Frame #{{ result.timeline[result.sliderValue].frameId }} · {{ result.timeline[result.sliderValue].time }}
              </p>
              <p style="font-weight:700;font-size:1.1rem;margin-top:4px;" :style="{color:getLabelColor(result.timeline[result.sliderValue].label)}">
                {{ result.timeline[result.sliderValue].label }}
                <span style="margin-left:6px;font-size:0.9rem;">
                  {{ (result.timeline[result.sliderValue].confidence*100).toFixed(0) }}%
                </span>
              </p>
            </div>

            <!-- Timeline dots -->
            <div class="space-y-1" style="max-height:180px;overflow-y:auto;">
              <div
                v-for="(frame, idx) in result.timeline" :key="idx"
                class="section-card"
                style="padding:8px 12px;display:flex;align-items:center;gap:10px;cursor:pointer;"
                :style="{ borderColor: result.sliderValue === idx ? getLabelColor(frame.label) : 'rgba(255,255,255,0.06)' }"
                @click="result.sliderValue = idx"
              >
                <div style="width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;color:#fff;flex-shrink:0;" :style="{background:getLabelColor(frame.label)}">
                  {{ frame.frameId }}
                </div>
                <div style="flex:1;">
                  <div style="display:flex;justify-content:space-between;">
                    <span style="font-size:0.82rem;font-weight:600;">{{ frame.label }}</span>
                    <span style="font-size:0.75rem;color:var(--text-muted);">{{ frame.time }}</span>
                  </div>
                  <div class="progress-track" style="height:4px;margin-top:4px;">
                    <div class="progress-fill" :style="{width:(frame.confidence*100)+'%',background:getLabelColor(frame.label)}"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
