<script setup lang="ts">
import { ref, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useDetectionStore } from '@/stores/detection'

const detectionStore = useDetectionStore()

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const videoUrl = ref<string | null>(null)
const isLoading = ref(false)
const uploadProgress = ref(0)
const result = ref<any>(null)
const errorMsg = ref('')

let pieChart: echarts.ECharts | null = null

const labelEnToCn: Record<string, string> = {
  'leaf_spot': '叶斑病', 'rust': '锈病', 'powdery_mildew': '白粉病',
  'early_blight': '早疫病', 'late_blight': '晚疫病', 'healthy': '健康',
}

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
  errorMsg.value = ''
}

function resetDetection() {
  selectedFile.value = null
  if (videoUrl.value) URL.revokeObjectURL(videoUrl.value)
  videoUrl.value = null
  result.value = null
  uploadProgress.value = 0
  errorMsg.value = ''
}

async function startDetection() {
  if (!selectedFile.value) return
  isLoading.value = true
  uploadProgress.value = 0
  errorMsg.value = ''

  try {
    const data = await detectionStore.detectVideo(selectedFile.value, (progress) => {
      uploadProgress.value = progress
    })

    const categoriesRaw = data.categories || []
    const categories = categoriesRaw.map((c: any) => ({
      name: c.label || labelEnToCn[c.label_en] || c.label_en,
      enName: c.label_en || c.name,
      count: c.count || 0,
      percentage: categoriesRaw.length > 0
        ? (c.count / categoriesRaw.reduce((s: number, x: any) => s + (x.count || 0), 0) * 100).toFixed(1)
        : 0,
      avgConfidence: c.avg_confidence || c.confidence || 0,
      color: getLabelColor(c.label || labelEnToCn[c.label_en] || ''),
    }))

    const topFrames = (data.top_frames || []).map((f: any) => ({
      frameId: f.frame_id,
      label: f.label || labelEnToCn[f.label_en] || f.label_en,
      confidence: f.confidence,
      time: f.frame_id ? `Frame #${f.frame_id}` : '',
      timeSec: 0,
    }))

    result.value = {
      totalFrames: data.total_frames || 0,
      diseaseFrames: data.disease_frames || 0,
      healthFrames: (data.total_frames || 0) - (data.disease_frames || 0),
      diseaseRate: data.disease_rate || 0,
      categories,
      timeline: topFrames,
      sliderValue: 0,
      deepAnalysis: data.deep_analysis,
    }

    await nextTick()
    setTimeout(renderPieChart, 200)
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '视频检测失败，请重试'
  } finally {
    isLoading.value = false
  }
}

function renderPieChart() {
  const el = document.getElementById('videoPieChart')
  if (!el || !result.value?.categories?.length) return
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
  if (label.includes('早疫病')) return '#2196f3'
  if (label.includes('晚疫病')) return '#9c27b0'
  return '#4caf50'
}

onUnmounted(() => { pieChart?.dispose() })
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>视频检测</h2>
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
        <div class="upload-icon"><svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><polygon points="10,8 16,12 10,16"/></svg></div>
        <p style="font-weight:600;font-size:1.1rem;">拖拽视频到此处</p>
        <p style="color:var(--text-tertiary);">或点击选择文件 · 支持 MP4、AVI、MOV 格式</p>
      </div>
    </div>

    <div v-else class="space-y-6">
      <div class="glass animate-fade-up">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <h3 style="font-weight:700;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><polygon points="10,8 16,12 10,16"/></svg>视频预览</h3>
          <button class="btn btn-outline btn-sm" @click="resetDetection">重新选择</button>
        </div>
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;">
          <div style="font-size:2rem;display:flex;align-items:center;justify-content:center;"><svg width="36" height="36" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><polygon points="10,8 16,12 10,16"/></svg></div>
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
        <h3 style="font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>检测进度</h3>
        <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:8px;">
          <span style="color:var(--text-secondary);">正在逐帧分析...</span>
          <span style="font-weight:700;color:#4caf50;">{{ uploadProgress }}%</span>
        </div>
        <div class="progress-track" style="height:10px;">
          <div class="progress-fill" :style="{width:uploadProgress+'%'}"></div>
        </div>
        <p style="text-align:center;color:var(--text-muted);font-size:0.82rem;margin-top:10px;">正在进行逐帧检测，请稍候...</p>
      </div>

      <div v-if="errorMsg" class="glass" style="padding:12px 16px;background:rgba(244,67,54,0.1);border-radius:8px;color:#f44336;font-size:0.85rem;">
        {{ errorMsg }}
      </div>

      <button
        v-if="!result && !isLoading"
        @click="startDetection"
        class="btn btn-primary btn-lg"
        style="width:100%;"
      >
        开始逐帧检测
      </button>

      <!-- Results -->
      <div v-if="result" class="space-y-6">
        <div class="stats-grid animate-fade-up">
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(33,150,243,0.15);"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg></div>
            <div class="stat-value">{{ result.totalFrames }}</div>
            <div class="stat-label">总帧数</div>
          </div>
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(244,67,54,0.15);"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M8 12h8M12 8v8"/></svg></div>
            <div class="stat-value">{{ result.diseaseFrames }}</div>
            <div class="stat-label">病害帧数</div>
          </div>
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(255,152,0,0.15);"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg></div>
            <div class="stat-value">{{ result.diseaseRate }}%</div>
            <div class="stat-label">病害率</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
          <div class="glass animate-fade-up stagger-1">
            <h3 style="font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>病害类别分布</h3>
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

          <div class="glass animate-fade-up stagger-2">
            <h3 style="font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>病害时间轴</h3>
            <p style="font-size:0.8rem;color:var(--text-tertiary);margin-bottom:12px;">拖动滑块查看不同时间点的检测结果</p>

            <input
              v-if="result.timeline.length > 1"
              type="range" min="0" :max="result.timeline.length-1" step="1"
              v-model="result.sliderValue"
              style="width:100%;height:6px;-webkit-appearance:none;appearance:none;background:rgba(255,255,255,0.1);border-radius:3px;outline:none;margin-bottom:16px;"
            />

            <div v-if="result.timeline[result.sliderValue]"
              style="padding:14px;background:rgba(255,255,255,0.04);border-radius:12px;text-align:center;margin-bottom:12px;"
            >
              <p style="font-size:0.82rem;color:var(--text-tertiary);">
                {{ result.timeline[result.sliderValue].time }}
              </p>
              <p style="font-weight:700;font-size:1.1rem;margin-top:4px;" :style="{color:getLabelColor(result.timeline[result.sliderValue].label)}">
                {{ result.timeline[result.sliderValue].label }}
                <span style="margin-left:6px;font-size:0.9rem;">
                  {{ (result.timeline[result.sliderValue].confidence*100).toFixed(0) }}%
                </span>
              </p>
            </div>

            <div v-if="result.timeline.length === 0" style="text-align:center;padding:32px;color:var(--text-muted);">
              未检测到病害帧
            </div>

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
