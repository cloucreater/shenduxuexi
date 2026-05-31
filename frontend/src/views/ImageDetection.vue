<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDetectionStore } from '@/stores/detection'
import api from '@/api'

const router = useRouter()
const detectionStore = useDetectionStore()

// ── State ──
const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const imageUrl = ref<string | null>(null)
const resultImageUrl = ref<string | null>(null)
const result = ref<any>(null)
const isDetecting = ref(false)
const showDetail = ref(false)
const selectedDisease = ref<any>(null)
const errorMsg = ref('')
const imageScale = ref({ x: 1, y: 1 })
const imageDisplayWidth = ref(0)
const imageDisplayHeight = ref(0)
const imageNaturalWidth = ref(0)
const imageNaturalHeight = ref(0)
const previewZoom = ref(false)

// ── Batch Mode ──
const batchMode = ref(false)
const batchFiles = ref<File[]>([])
const batchResults = ref<any[]>([])
const batchDetecting = ref(false)
const batchProgress = ref(0)

function toggleBatchMode() {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    batchFiles.value = []
    batchResults.value = []
    batchProgress.value = 0
  }
}

function handleBatchFileInput(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files) {
    const allowed = Array.from(target.files).filter(f => f.type.match(/^image\/(jpeg|png|jpg)$/))
    batchFiles.value = [...batchFiles.value, ...allowed].slice(0, 20)
  }
}

function removeBatchFile(idx: number) {
  batchFiles.value.splice(idx, 1)
}

async function submitBatchDetect() {
  if (batchFiles.value.length === 0) return
  batchDetecting.value = true
  batchResults.value = []
  batchProgress.value = 0

  try {
    const fd = new FormData()
    batchFiles.value.forEach(f => fd.append('files', f))
    const res = await api.post('/detect/batch', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => { batchProgress.value = Math.round((e.loaded / (e.total || 1)) * 30) }
    })
    batchResults.value = res.data.results || []
    batchProgress.value = 100
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '批量检测失败'
  } finally {
    batchDetecting.value = false
  }
}

// ── Disease Info Database ──
const diseaseInfoDB: Record<string, any> = {
  '叶斑病': {
    name: '叶斑病', enName: 'Leaf Spot',
    desc: '叶斑病是一类常见的植物病害，由多种真菌或细菌引起，主要危害叶片，严重时可导致叶片枯死脱落。',
    symptoms: ['叶片出现圆形或不规则形褐色斑点', '斑点边缘有黄色晕圈', '严重时斑点连片导致叶片枯死', '湿度大时斑点表面出现霉层'],
    causes: '温暖潮湿环境、植株过密、通风不良、偏施氮肥等',
    recommendations: ['及时清除病叶并销毁', '使用代森锰锌或多菌灵喷施', '加强通风降低田间湿度', '合理施肥增强植株抗性'],
    medicines: ['代森锰锌 WP 70% 稀释500倍', '多菌灵 WP 50% 稀释800倍', '苯醚甲环唑 EC 10% 稀释1500倍'],
  },
  '白粉病': {
    name: '白粉病', enName: 'Powdery Mildew',
    desc: '白粉病是由白粉菌科真菌引起的植物病害，在叶片、茎秆和果实表面形成白色粉状物。',
    symptoms: ['叶片表面出现白色粉状斑点', '斑点逐渐扩大覆盖整个叶片', '叶片变黄卷曲', '严重时植株矮化、果实畸形'],
    causes: '高湿度、通风不良、光照不足、氮肥过多等',
    recommendations: ['使用硫磺悬浮剂喷施', '保持植株间距确保通风', '及时摘除病叶', '增施磷钾肥提高抗性'],
    medicines: ['硫磺悬浮剂 SC 50% 稀释600倍', '三唑酮 WP 25% 稀释1000倍', '嘧菌酯 SC 25% 稀释1500倍'],
  },
  '锈病': {
    name: '锈病', enName: 'Rust',
    desc: '锈病是由锈菌引起的植物病害，因在叶片上形成铁锈色的孢子堆而得名，危害多种作物。',
    symptoms: ['叶片出现黄色或橙色锈斑', '叶背形成疱状孢子堆', '后期病斑变为深褐色', '严重时叶片提前脱落'],
    causes: '温暖潮湿气候、植株密度过大、氮肥过量等',
    recommendations: ['使用三唑酮或戊唑醇喷施', '清除病株残体', '选用抗病品种', '合理密植改善通风'],
    medicines: ['三唑酮 EC 20% 稀释1000倍', '戊唑醇 SC 43% 稀释3000倍', '吡唑醚菌酯 EC 25% 稀释2000倍'],
  },
  '早疫病': {
    name: '早疫病', enName: 'Early Blight',
    desc: '早疫病又称轮纹病，由链格孢菌引起，主要危害番茄、马铃薯等茄科作物。',
    symptoms: ['叶片出现同心轮纹状褐色病斑', '病斑周围有明显黄色晕圈', '下部叶片先发病向上蔓延', '茎部和果实也可受害'],
    causes: '高温高湿环境、连作种植、植株长势弱等',
    recommendations: ['实行轮作避免连作', '使用代森锌或百菌清防治', '及时摘除下部老叶病叶', '加强水肥管理壮苗'],
    medicines: ['代森锌 WP 80% 稀释600倍', '百菌清 SC 40% 稀释800倍', '氢氧化铜 WP 77% 稀释500倍'],
  },
  '晚疫病': {
    name: '晚疫病', enName: 'Late Blight',
    desc: '晚疫病是一种毁灭性病害，由疫霉菌引起，历史上曾导致爱尔兰马铃薯大饥荒。',
    symptoms: ['叶片出现暗绿色水渍状病斑', '病斑迅速扩大变为褐色', '叶背出现白色霉层', '块茎出现褐色腐烂'],
    causes: '低温高湿环境、连续阴雨、田间积水等',
    recommendations: ['使用甲霜灵锰锌或霜霉威', '及时清除并销毁病株', '加强田间排水', '关注天气提前预防'],
    medicines: ['甲霜灵锰锌 WP 58% 稀释600倍', '霜霉威 SC 72.2% 稀释800倍', '烯酰吗啉 WP 50% 稀释1500倍'],
  },
  '细菌性斑点病': {
    name: '细菌性斑点病', enName: 'Bacterial Spot',
    desc: '由黄单胞杆菌引起的细菌性病害，危害叶片和果实，潮湿季节发病严重。',
    symptoms: ['叶片出现水渍状小斑点', '斑点扩大为不规则形褐色坏死斑', '病斑周围有明显黄色晕圈', '严重时叶片黄化脱落'],
    causes: '高温多雨、灌溉水飞溅、植株伤口等',
    recommendations: ['使用铜制剂喷施', '避免雨淋灌溉', '及时清除病残体', '选用无病种苗'],
    medicines: ['氢氧化铜 WP 77% 稀释500倍', '春雷霉素 WP 2% 稀释500倍', '中生菌素 WP 3% 稀释1000倍'],
  },
}

const labelEnToCn: Record<string, string> = {
  'leaf_spot': '叶斑病', 'rust': '锈病', 'powdery_mildew': '白粉病',
  'early_blight': '早疫病', 'late_blight': '晚疫病', 'healthy': '健康',
  'bacterial_spot': '细菌性斑点病', 'leaf_mold': '叶霉病', 'septoria': '斑枯病',
  'Bacterial_spot': '细菌性斑点病',
}

const severityLevels = computed(() => {
  if (!result.value) return null
  const d = result.value.diseaseCount
  if (d === 0) return { label: '健康', color: '#4caf50', bg: 'rgba(76,175,80,0.15)' }
  if (d <= 2) return { label: '轻微', color: '#2196f3', bg: 'rgba(33,150,243,0.15)' }
  if (d <= 5) return { label: '中等', color: '#ff9800', bg: 'rgba(255,152,0,0.15)' }
  return { label: '严重', color: '#f44336', bg: 'rgba(244,67,54,0.15)' }
})

// ── File Handling ──
function handleDragOver(e: DragEvent) { e.preventDefault(); isDragging.value = true }
function handleDragLeave() { isDragging.value = false }

function handleDrop(e: DragEvent) {
  e.preventDefault(); isDragging.value = false
  const files = e.dataTransfer?.files
  if (files?.[0]?.type.match(/^image\//)) handleFileSelect(files[0])
  else errorMsg.value = '请上传图片文件（JPG/PNG）'
}

function handleFileInput(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) handleFileSelect(target.files[0])
}

function handleFileSelect(file: File) {
  if (!file.type.match(/^image\/(jpeg|png|jpg)$/)) {
    errorMsg.value = '请上传 JPG 或 PNG 格式的图片'
    return
  }
  selectedFile.value = file
  imageUrl.value = URL.createObjectURL(file)
  result.value = null
  resultImageUrl.value = null
  errorMsg.value = ''
  imageScale.value = { x: 1, y: 1 }
  previewZoom.value = false
}

function onImageLoad(e: Event) {
  const img = e.target as HTMLImageElement
  imageNaturalWidth.value = img.naturalWidth
  imageNaturalHeight.value = img.naturalHeight
  imageDisplayWidth.value = img.clientWidth
  imageDisplayHeight.value = img.clientHeight
  imageScale.value = {
    x: img.clientWidth / img.naturalWidth,
    y: img.clientHeight / img.naturalHeight,
  }
}

// ── Detection ──
async function startDetection() {
  if (!selectedFile.value) return
  isDetecting.value = true
  errorMsg.value = ''

  try {
    const data = await detectionStore.detectImage(selectedFile.value)

    const detections = (data.detections || []).map((d: any) => {
      const labelCn = d.label || labelEnToCn[d.label_en] || d.label_en
      return {
        ...d,
        label: labelCn,
        enLabel: d.label_en || d.label,
        info: diseaseInfoDB[labelCn] || null,
        bboxPixels: Array.isArray(d.bbox) && d.bbox.length === 4
          ? { x1: d.bbox[0], y1: d.bbox[1], x2: d.bbox[2], y2: d.bbox[3] }
          : null,
      }
    })

    const diseaseDetections = detections.filter((d: any) =>
      d.label !== '健康' && d.class !== 'healthy' && d.label_en !== 'healthy')
    const healthDetections = detections.filter((d: any) =>
      d.label === '健康' || d.class === 'healthy' || d.label_en === 'healthy')
    const diseaseCount = diseaseDetections.length
    const healthCount = healthDetections.length
    const avgConfidence = detections.length > 0
      ? detections.reduce((s: number, d: any) => s + d.confidence, 0) / detections.length
      : 0

    if (data.result_image) {
      resultImageUrl.value = 'data:image/jpeg;base64,' + data.result_image
    }

    result.value = {
      imageId: (data as any).image_id || data.id || '—',
      timestamp: new Date().toLocaleString('zh-CN'),
      fileName: selectedFile.value.name,
      fileSize: (selectedFile.value.size / 1024).toFixed(2) + ' KB',
      detectionTime: (data.detection_time || 0).toFixed(0) + 'ms',
      totalDetections: detections.length,
      diseaseCount,
      healthCount,
      avgConfidence: (avgConfidence * 100).toFixed(1),
      detections,
      summary: diseaseDetections[0]?.info?.recommendations?.[0] || '作物生长状况良好',
    }

    await nextTick()
    // Recalculate scale after result image loads
    const previewImg = document.querySelector('.preview-image') as HTMLImageElement
    if (previewImg && previewImg.complete) {
      onImageLoad({ target: previewImg } as any)
    }
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '检测失败，请重试'
  } finally {
    isDetecting.value = false
  }
}

function resetDetection() {
  selectedFile.value = null
  if (imageUrl.value) URL.revokeObjectURL(imageUrl.value)
  imageUrl.value = null
  resultImageUrl.value = null
  result.value = null
  errorMsg.value = ''
  imageScale.value = { x: 1, y: 1 }
  previewZoom.value = false
}

function showDiseaseDetail(det: any) {
  selectedDisease.value = det
  showDetail.value = true
}

function getBoxColor(cls: string): string {
  const colors: Record<string, string> = {
    leaf_spot: '#f44336', powdery_mildew: '#ff9800', rust: '#ff5722',
    early_blight: '#2196f3', late_blight: '#9c27b0', healthy: '#4caf50',
    bacterial_spot: '#e91e63', leaf_mold: '#795548', septoria: '#607d8b',
    Bacterial_spot: '#e91e63',
  }
  return colors[cls] || colors[cls?.toLowerCase()] || '#4caf50'
}

function goHistory() {
  router.push('/history')
}

// ── Computed bbox styles (scaled to displayed image size) ──
function getBBoxStyle(det: any) {
  if (!det.bboxPixels || imageScale.value.x === 0) return { display: 'none' }
  const { x1, y1, x2, y2 } = det.bboxPixels
  const sx = imageScale.value.x
  const sy = imageScale.value.y
  return {
    left: (x1 * sx) + 'px',
    top: (y1 * sy) + 'px',
    width: ((x2 - x1) * sx) + 'px',
    height: ((y2 - y1) * sy) + 'px',
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Top Bar -->
    <div class="page-header animate-fade-down" style="display:flex;justify-content:space-between;align-items:flex-start;">
      <div>
        <h2>图片检测</h2>
        <p>上传作物叶片图片，AI 自动识别病害类型与严重程度</p>
      </div>
      <button @click="goHistory" class="btn btn-outline btn-sm" style="gap:6px;white-space:nowrap;">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        检测历史
      </button>
    </div>

    <!-- Upload Zone (before file selected) -->
    <div v-if="!selectedFile" class="glass upload-hero animate-scale-in">
      <div
        :class="['upload-dropzone', { dragover: isDragging }]"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="($refs.fileInput as HTMLInputElement)?.click()"
      >
        <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/jpg" style="display:none" @change="handleFileInput" />
        <div class="upload-hero-icon">
          <svg width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.2" viewBox="0 0 24 24">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
        </div>
        <p class="upload-hero-title">拖拽图片到此处</p>
        <p class="upload-hero-sub">或点击选择文件 · 支持 JPG、PNG 格式 · 最大 50MB</p>
        <div class="upload-hero-formats">
          <span class="format-badge">JPG</span>
          <span class="format-badge">PNG</span>
          <span class="format-badge">JPEG</span>
        </div>
      </div>

      <div style="margin-top:28px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">
        <div class="feature-hint">
          <svg width="20" height="20" fill="none" stroke="#4caf50" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5zM14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z"/></svg>
          <span>YOLO + CNN 双模型</span>
        </div>
        <div class="feature-hint">
          <svg width="20" height="20" fill="none" stroke="#4caf50" stroke-width="1.5" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          <span>毫秒级响应</span>
        </div>
        <div class="feature-hint">
          <svg width="20" height="20" fill="none" stroke="#4caf50" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          <span>8种病害识别</span>
        </div>
      </div>
    </div>

    <!-- Main Content (after file selected) -->
    <div v-else class="detection-layout">
      <!-- ═══════ Left: Image Preview ═══════ -->
      <div class="left-panel animate-slide-left">
        <div class="glass" style="height:100%;display:flex;flex-direction:column;">
          <!-- Header -->
          <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.06);">
            <h3 style="font-weight:700;font-size:0.95rem;display:flex;align-items:center;gap:8px;">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
              图片预览
            </h3>
            <button v-if="result" class="btn btn-outline btn-sm" @click="resetDetection">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
              重新上传
            </button>
          </div>

          <!-- File info -->
          <div style="padding:10px 20px;font-size:0.8rem;color:var(--text-muted);border-bottom:1px solid rgba(255,255,255,0.04);display:flex;gap:20px;">
            <span>{{ selectedFile.name }}</span>
            <span>{{ (selectedFile.size/1024).toFixed(1) }} KB</span>
          </div>

          <!-- Image with detection boxes -->
          <div
            :class="['image-container', { zoomed: previewZoom }]"
            @click="previewZoom = !previewZoom"
          >
            <img
              :src="resultImageUrl || imageUrl!"
              alt="预览"
              class="preview-image"
              @load="onImageLoad"
            />

            <!-- Detection bounding boxes -->
            <template v-if="result && !isDetecting">
              <div
                v-for="(det, idx) in result.detections.filter((d: any) => d.bboxPixels)"
                :key="idx"
                class="detection-box"
                :style="{
                  ...getBBoxStyle(det),
                  borderColor: getBoxColor(det.label_en || det.class),
                  background: getBoxColor(det.label_en || det.class) + '18',
                }"
                @click.stop="showDiseaseDetail(det)"
              >
                <span class="box-label" :style="{ background: getBoxColor(det.label_en || det.class) }">
                  {{ det.label }} {{ (det.confidence * 100).toFixed(0) }}%
                </span>
              </div>
            </template>

            <!-- Loading overlay -->
            <div v-if="isDetecting" class="detecting-overlay">
              <div class="detecting-spinner"></div>
              <p class="detecting-text">AI 正在分析中...</p>
              <p class="detecting-sub">正在使用 YOLOv11 + CNN 双模型检测</p>
            </div>

            <!-- Zoom hint -->
            <div v-if="result && !isDetecting" class="zoom-hint">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
              点击图片{{ previewZoom ? '缩小' : '放大' }}
            </div>
          </div>

          <!-- Error message -->
          <div v-if="errorMsg" class="error-msg">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ errorMsg }}
          </div>

          <!-- Detect button -->
          <div style="padding:16px 20px;border-top:1px solid rgba(255,255,255,0.06);">
            <button
              v-if="!result"
              @click="startDetection"
              :disabled="isDetecting"
              class="detect-btn"
            >
              <template v-if="isDetecting">
                <span class="spinner-sm"></span>
                检测中...
              </template>
              <template v-else>
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                开始检测
              </template>
            </button>
            <div v-else style="display:flex;gap:10px;">
              <div style="flex:1;text-align:center;padding:10px;background:rgba(76,175,80,0.1);border-radius:10px;font-size:0.8rem;color:#4caf50;font-weight:600;">
                检测完成 · 耗时 {{ result.detectionTime }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════ Right: Results ═══════ -->
      <div class="right-panel animate-slide-right">
        <!-- Empty state -->
        <div v-if="!result && !isDetecting" class="glass empty-state">
          <svg width="56" height="56" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="opacity:0.2;margin-bottom:16px;">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <p style="font-weight:600;font-size:1rem;">点击"开始检测"进行分析</p>
          <p style="color:var(--text-muted);font-size:0.85rem;margin-top:6px;">AI 将自动识别图片中的病害区域并生成详细报告</p>
        </div>

        <!-- Results -->
        <div v-if="result" class="results-stack">
          <!-- Stats grid -->
          <div class="glass stats-section">
            <h4 style="font-weight:700;margin-bottom:14px;font-size:0.9rem;display:flex;align-items:center;gap:8px;">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
              检测统计
            </h4>
            <div class="stats-grid-4">
              <div class="stat-mini" style="--accent:#2196f3;">
                <p class="stat-mini-value">{{ result.totalDetections }}</p>
                <p class="stat-mini-label">检测总数</p>
              </div>
              <div class="stat-mini" style="--accent:#f44336;">
                <p class="stat-mini-value">{{ result.diseaseCount }}</p>
                <p class="stat-mini-label">病害区域</p>
              </div>
              <div class="stat-mini" style="--accent:#4caf50;">
                <p class="stat-mini-value">{{ result.healthCount }}</p>
                <p class="stat-mini-label">健康区域</p>
              </div>
              <div class="stat-mini" style="--accent:#ff9800;">
                <p class="stat-mini-value">{{ result.avgConfidence }}%</p>
                <p class="stat-mini-label">平均置信度</p>
              </div>
            </div>
            <div v-if="severityLevels" style="margin-top:12px;display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-radius:10px;" :style="{background:severityLevels.bg}">
              <span style="font-size:0.82rem;font-weight:600;">严重程度评估</span>
              <span style="font-weight:700;font-size:1rem;" :style="{color:severityLevels.color}">{{ severityLevels.label }}</span>
            </div>
          </div>

          <!-- Detection list -->
          <div class="glass detection-list-section">
            <h4 style="font-weight:700;margin-bottom:14px;font-size:0.9rem;display:flex;align-items:center;gap:8px;">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              检测详情
              <span style="font-weight:400;font-size:0.75rem;color:var(--text-muted);">{{ result.detections.length }} 项</span>
            </h4>
            <div class="detection-items">
              <div
                v-for="(det, idx) in result.detections"
                :key="idx"
                class="detection-item"
                @click="showDiseaseDetail(det)"
              >
                <div class="detection-item-top">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div class="color-dot" :style="{ background: getBoxColor(det.label_en || det.class) }"></div>
                    <div>
                      <p class="detection-item-name">{{ det.label }}</p>
                      <p class="detection-item-en">{{ det.enLabel }}</p>
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <p class="detection-item-conf" :style="{ color: getBoxColor(det.label_en || det.class) }">
                      {{ (det.confidence * 100).toFixed(1) }}%
                    </p>
                    <p class="detection-item-conf-label">置信度</p>
                  </div>
                </div>
                <div class="confidence-bar">
                  <div
                    class="confidence-fill"
                    :style="{
                      width: (det.confidence * 100) + '%',
                      background: 'linear-gradient(90deg, ' + getBoxColor(det.label_en || det.class) + ', ' + getBoxColor(det.label_en || det.class) + '88)',
                    }"
                  ></div>
                </div>
                <div style="display:flex;justify-content:flex-end;margin-top:6px;">
                  <span class="detail-link">
                    查看详情
                    <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick summary -->
          <div class="glass summary-bar">
            <svg width="18" height="18" fill="none" stroke="#4caf50" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <span>{{ result.summary }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════ Disease Detail Modal ═══════ -->
    <Teleport to="body">
      <div v-if="showDetail && selectedDisease" class="modal-overlay" @click.self="showDetail = false">
        <div class="detail-modal animate-scale-in">
          <!-- Header -->
          <div class="detail-header" :style="{ borderTop: '3px solid ' + getBoxColor(selectedDisease.label_en || selectedDisease.class) }">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
              <div>
                <h2 class="detail-title">{{ selectedDisease.label }}</h2>
                <p class="detail-en">{{ selectedDisease.enLabel }}</p>
              </div>
              <button @click="showDetail = false" class="modal-close-btn">&times;</button>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-top:12px;">
              <div style="flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
                <div
                  style="height:100%;border-radius:3px;transition:width 0.6s ease;"
                  :style="{ width: (selectedDisease.confidence * 100) + '%', background: getBoxColor(selectedDisease.label_en || selectedDisease.class) }"
                ></div>
              </div>
              <span style="font-weight:700;font-size:1.1rem;" :style="{color:getBoxColor(selectedDisease.label_en || selectedDisease.class)}">
                {{ (selectedDisease.confidence * 100).toFixed(1) }}%
              </span>
            </div>
          </div>

          <!-- Body -->
          <div class="detail-body">
            <template v-if="selectedDisease.info">
              <!-- Description -->
              <div class="detail-block">
                <h4 class="detail-block-title">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                  病害描述
                </h4>
                <p class="detail-block-text">{{ selectedDisease.info.desc }}</p>
              </div>

              <!-- Symptoms -->
              <div class="detail-block detail-block-red">
                <h4 class="detail-block-title">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                  症状表现
                </h4>
                <ul class="detail-list">
                  <li v-for="s in selectedDisease.info.symptoms" :key="s">{{ s }}</li>
                </ul>
              </div>

              <!-- Causes -->
              <div class="detail-block detail-block-orange">
                <h4 class="detail-block-title">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                  诱因分析
                </h4>
                <p class="detail-block-text">{{ selectedDisease.info.causes }}</p>
              </div>

              <!-- Recommendations -->
              <div class="detail-block detail-block-green">
                <h4 class="detail-block-title">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                  防治建议
                </h4>
                <ul class="detail-list">
                  <li v-for="r in selectedDisease.info.recommendations" :key="r">{{ r }}</li>
                </ul>
              </div>

              <!-- Medicines -->
              <div v-if="selectedDisease.info.medicines" class="detail-block detail-block-purple">
                <h4 class="detail-block-title">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L9 7l-5 1 4 4-1 5 5-2.5L17 17l-1-5 4-4-5-1-3-5z"/></svg>
                  推荐药剂
                </h4>
                <ul class="detail-list">
                  <li v-for="m in selectedDisease.info.medicines" :key="m">{{ m }}</li>
                </ul>
              </div>
            </template>

            <!-- Healthy plant -->
            <div v-else style="text-align:center;padding:32px 20px;">
              <svg width="48" height="48" fill="none" stroke="#4caf50" stroke-width="1.5" viewBox="0 0 24 24" style="margin-bottom:12px;"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
              <p style="font-weight:600;color:#4caf50;font-size:1.05rem;">健康植株</p>
              <p style="color:var(--text-muted);margin-top:4px;">未检测到病害症状，作物生长状况良好</p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* ── Upload Hero ── */
.upload-hero { padding: 36px 32px; text-align: center; }

.upload-dropzone {
  border: 2px dashed rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 56px 40px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255,255,255,0.01);
}
.upload-dropzone:hover { border-color: rgba(76,175,80,0.25); background: rgba(76,175,80,0.03); }
.upload-dropzone.dragover {
  border-color: #4caf50;
  background: rgba(76,175,80,0.08);
  transform: scale(1.01);
}

.upload-hero-icon { margin-bottom: 16px; opacity: 0.45; color: #4caf50; }
.upload-hero-title { font-weight: 700; font-size: 1.15rem; margin-bottom: 6px; }
.upload-hero-sub { color: var(--text-muted); font-size: 0.88rem; }
.upload-hero-formats { display: flex; gap: 8px; justify-content: center; margin-top: 16px; }

.format-badge {
  padding: 4px 14px; border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 0.75rem; color: var(--text-muted);
  font-weight: 500;
}

.feature-hint {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px;
  background: rgba(255,255,255,0.02);
  border-radius: 12px;
  font-size: 0.82rem; color: var(--text-secondary);
  justify-content: center;
}

/* ── Layout ── */
.detection-layout {
  display: grid;
  grid-template-columns: 45% 55%;
  gap: 20px;
  align-items: start;
}

.left-panel { min-width: 0; }
.right-panel { min-width: 0; }

/* ── Image Container ── */
.image-container {
  position: relative;
  flex: 1;
  min-height: 300px;
  background: rgba(0,0,0,0.25);
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  cursor: pointer;
}
.preview-image {
  width: 100%;
  display: block;
  transition: transform 0.3s ease;
}
.image-container.zoomed .preview-image {
  transform: scale(1.8);
  transform-origin: center center;
}

/* ── Detection Boxes ── */
.detection-box {
  position: absolute;
  border: 2.5px solid;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
  z-index: 2;
}
.detection-box:hover {
  transform: scale(1.04);
  z-index: 3;
  box-shadow: 0 0 16px rgba(0,0,0,0.35);
}
.box-label {
  position: absolute;
  top: -26px;
  left: -1px;
  padding: 3px 8px;
  border-radius: 4px 4px 0 0;
  font-size: 0.7rem;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  pointer-events: none;
}

/* ── Detecting overlay ── */
.detecting-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(4px);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  z-index: 10;
}
.detecting-spinner {
  width: 44px; height: 44px;
  border: 3px solid rgba(255,255,255,0.15);
  border-top-color: #4caf50;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.detecting-text { font-weight: 700; font-size: 1rem; color: #fff; }
.detecting-sub { font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 4px; }

.zoom-hint {
  position: absolute; bottom: 10px; right: 10px;
  display: flex; align-items: center; gap: 4px;
  padding: 5px 10px; border-radius: 8px;
  background: rgba(0,0,0,0.55); color: rgba(255,255,255,0.6);
  font-size: 0.72rem; pointer-events: none; z-index: 5;
}

/* ── Error ── */
.error-msg {
  display: flex; align-items: center; gap: 8px;
  margin: 10px 20px; padding: 10px 14px;
  background: rgba(244,67,54,0.08); border: 1px solid rgba(244,67,54,0.2);
  border-radius: 10px; color: #ef5350; font-size: 0.85rem;
}

/* ── Detect button ── */
.detect-btn {
  width: 100%; padding: 14px 20px;
  border: none; border-radius: 14px;
  background: linear-gradient(135deg, #2e7d32, #4caf50);
  color: #fff; font-size: 1rem; font-weight: 700;
  cursor: pointer; font-family: inherit;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  transition: all 0.25s;
  box-shadow: 0 4px 20px rgba(76,175,80,0.25);
}
.detect-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 28px rgba(76,175,80,0.35);
}
.detect-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.spinner-sm {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* ── Empty state ── */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 72px 32px; text-align: center; min-height: 400px;
}

/* ── Results ── */
.results-stack { display: flex; flex-direction: column; gap: 16px; }

.stats-section { padding: 18px 20px; }
.stats-grid-4 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.stat-mini {
  text-align: center;
  padding: 14px 10px;
  border-radius: 12px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04);
}
.stat-mini-value { font-size: 1.5rem; font-weight: 800; color: var(--accent); }
.stat-mini-label { font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; }

/* ── Detection list ── */
.detection-list-section { padding: 18px 20px; }
.detection-items { display: flex; flex-direction: column; gap: 8px; }

.detection-item {
  padding: 14px 16px;
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: 13px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255,255,255,0.01);
}
.detection-item:hover {
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.1);
}
.detection-item-top {
  display: flex; align-items: center; justify-content: space-between;
}
.color-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.detection-item-name { font-weight: 700; font-size: 0.88rem; }
.detection-item-en { font-size: 0.72rem; color: var(--text-muted); }
.detection-item-conf { font-size: 1.15rem; font-weight: 800; line-height: 1; }
.detection-item-conf-label { font-size: 0.65rem; color: var(--text-muted); }

.confidence-bar {
  height: 5px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  margin-top: 10px;
  overflow: hidden;
}
.confidence-fill {
  height: 100%; border-radius: 3px;
  transition: width 0.6s ease;
}
.detail-link {
  font-size: 0.75rem; color: var(--color-accent);
  display: flex; align-items: center; gap: 4px;
  font-weight: 600;
}
.detail-link:hover { text-decoration: underline; }

.summary-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px; font-size: 0.85rem; color: var(--text-secondary);
}

/* ── Detail Modal ── */
.modal-overlay {
  position: fixed; inset: 0; z-index: 300;
  background: rgba(0,0,0,0.55); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.detail-modal {
  width: 560px; max-width: 92vw; max-height: 88vh; overflow-y: auto;
  background: rgba(15,38,20,0.98);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
}
.detail-header { padding: 24px 28px; border-radius: 20px 20px 0 0; }
.detail-title { font-weight: 800; font-size: 1.25rem; }
.detail-en { font-size: 0.85rem; color: var(--text-muted); }
.modal-close-btn {
  width: 32px; height: 32px; border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04); color: var(--text-muted);
  cursor: pointer; font-size: 1.2rem; display: flex;
  align-items: center; justify-content: center; transition: all 0.15s;
}
.modal-close-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }

.detail-body { padding: 20px 28px 28px; display: flex; flex-direction: column; gap: 14px; }

.detail-block {
  padding: 16px 18px;
  background: rgba(255,255,255,0.02);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.04);
}
.detail-block-red { border-left: 3px solid #f44336; }
.detail-block-orange { border-left: 3px solid #ff9800; }
.detail-block-green { border-left: 3px solid #4caf50; }
.detail-block-purple { border-left: 3px solid #9c27b0; }

.detail-block-title {
  font-weight: 700; font-size: 0.88rem;
  display: flex; align-items: center; gap: 6px;
  margin-bottom: 8px;
}
.detail-block-text { font-size: 0.86rem; color: var(--text-secondary); line-height: 1.7; }
.detail-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 6px; }
.detail-list li {
  font-size: 0.85rem; color: var(--text-secondary);
  padding-left: 18px; position: relative; line-height: 1.6;
}
.detail-list li::before {
  content: ''; position: absolute; left: 0; top: 9px;
  width: 5px; height: 5px; border-radius: 50%;
  background: currentColor; opacity: 0.5;
}

/* ── Responsive ── */
@media (max-width: 860px) {
  .detection-layout {
    grid-template-columns: 1fr;
  }
  .image-container { min-height: 240px; }
}

@media (max-width: 480px) {
  .upload-hero { padding: 24px 16px; }
  .upload-dropzone { padding: 36px 20px; }
  .stats-grid-4 { grid-template-columns: 1fr 1fr; }
  .detail-modal { border-radius: 16px; }
}
</style>
