<script setup lang="ts">
import { ref } from 'vue'

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const imageUrl = ref<string | null>(null)
const result = ref<any>(null)
const isDetecting = ref(false)
const showDetail = ref(false)
const selectedDisease = ref<any>(null)

const diseaseInfoDB: Record<string, any> = {
  'leaf_spot': {
    name: '叶斑病', enName: 'Leaf Spot',
    desc: '叶斑病是一类常见的植物病害，由多种真菌或细菌引起，主要危害叶片，严重时可导致叶片枯死脱落。',
    symptoms: ['叶片出现圆形或不规则形褐色斑点', '斑点边缘有黄色晕圈', '严重时斑点连片导致叶片枯死', '湿度大时斑点表面出现霉层'],
    causes: '温暖潮湿环境、植株过密、通风不良、偏施氮肥等',
    recommendations: ['及时清除病叶并销毁', '使用代森锰锌或多菌灵喷施', '加强通风降低田间湿度', '合理施肥增强植株抗性'],
  },
  'powdery_mildew': {
    name: '白粉病', enName: 'Powdery Mildew',
    desc: '白粉病是由白粉菌科真菌引起的植物病害，在叶片、茎秆和果实表面形成白色粉状物。',
    symptoms: ['叶片表面出现白色粉状斑点', '斑点逐渐扩大覆盖整个叶片', '叶片变黄卷曲', '严重时植株矮化、果实畸形'],
    causes: '高湿度、通风不良、光照不足、氮肥过多等',
    recommendations: ['使用硫磺悬浮剂喷施', '保持植株间距确保通风', '及时摘除病叶', '增施磷钾肥提高抗性'],
  },
  'rust': {
    name: '锈病', enName: 'Rust',
    desc: '锈病是由锈菌引起的植物病害，因在叶片上形成铁锈色的孢子堆而得名，危害多种作物。',
    symptoms: ['叶片出现黄色或橙色锈斑', '叶背形成疱状孢子堆', '后期病斑变为深褐色', '严重时叶片提前脱落'],
    causes: '温暖潮湿气候、植株密度过大、氮肥过量等',
    recommendations: ['使用三唑酮或戊唑醇喷施', '清除病株残体', '选用抗病品种', '合理密植改善通风'],
  },
  'early_blight': {
    name: '早疫病', enName: 'Early Blight',
    desc: '早疫病又称轮纹病，由链格孢菌引起，主要危害番茄、马铃薯等茄科作物。',
    symptoms: ['叶片出现同心轮纹状褐色病斑', '病斑周围有明显黄色晕圈', '下部叶片先发病向上蔓延', '茎部和果实也可受害'],
    causes: '高温高湿环境、连作种植、植株长势弱等',
    recommendations: ['实行轮作避免连作', '使用代森锌或百菌清防治', '及时摘除下部老叶病叶', '加强水肥管理壮苗'],
  },
  'late_blight': {
    name: '晚疫病', enName: 'Late Blight',
    desc: '晚疫病是一种毁灭性病害，由疫霉菌引起，历史上曾导致爱尔兰马铃薯大饥荒。',
    symptoms: ['叶片出现暗绿色水渍状病斑', '病斑迅速扩大变为褐色', '叶背出现白色霉层', '块茎出现褐色腐烂'],
    causes: '低温高湿环境、连续阴雨、田间积水等',
    recommendations: ['使用甲霜灵锰锌或霜霉威', '及时清除并销毁病株', '加强田间排水', '关注天气提前预防'],
  },
}

const simDetections = [
  { class: 'leaf_spot', confidence: 0.92, bbox: { x: 120, y: 80, w: 180, h: 140 } },
  { class: 'powdery_mildew', confidence: 0.85, bbox: { x: 320, y: 150, w: 160, h: 120 } },
  { class: 'leaf_spot', confidence: 0.73, bbox: { x: 200, y: 250, w: 140, h: 100 } },
  { class: 'healthy', confidence: 0.96, bbox: { x: 50, y: 300, w: 200, h: 150 } },
]

function handleDragOver(e: DragEvent) { e.preventDefault(); isDragging.value = true }
function handleDragLeave() { isDragging.value = false }

function handleDrop(e: DragEvent) {
  e.preventDefault(); isDragging.value = false
  const files = e.dataTransfer?.files
  if (files?.[0]?.type.match(/^image\//)) { handleFileSelect(files[0]) }
  else { alert('请上传图片文件（JPG/PNG）') }
}

function handleFileInput(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) handleFileSelect(target.files[0])
}

function handleFileSelect(file: File) {
  if (!file.type.match(/^image\/(jpeg|png|jpg)$/)) { alert('请上传 JPG 或 PNG 格式的图片'); return }
  selectedFile.value = file
  imageUrl.value = URL.createObjectURL(file)
  result.value = null
}

async function startDetection() {
  if (!selectedFile.value) return
  isDetecting.value = true
  await new Promise(resolve => setTimeout(resolve, 1800))

  const detections = simDetections.map(d => ({
    ...d,
    label: diseaseInfoDB[d.class]?.name || '健康',
    enLabel: diseaseInfoDB[d.class]?.enName || 'Healthy',
    info: diseaseInfoDB[d.class],
  }))
  const diseaseCount = detections.filter(d => d.class !== 'healthy').length
  const healthCount = detections.filter(d => d.class === 'healthy').length

  result.value = {
    imageId: Math.random().toString(36).slice(2, 10).toUpperCase(),
    timestamp: new Date().toLocaleString('zh-CN'),
    fileName: selectedFile.value.name,
    fileSize: (selectedFile.value.size / 1024).toFixed(2) + ' KB',
    detectionTime: '1,247ms',
    totalDetections: detections.length,
    diseaseCount,
    healthCount,
    severity: diseaseCount >= 3 ? '严重' : diseaseCount >= 2 ? '中等' : diseaseCount >= 1 ? '轻微' : '健康',
    detections,
    summary: detections.find(d => d.class !== 'healthy')?.info?.recommendations?.[0] || '作物生长状况良好',
  }

  isDetecting.value = false
}

function resetDetection() {
  selectedFile.value = null
  if (imageUrl.value) URL.revokeObjectURL(imageUrl.value)
  imageUrl.value = null
  result.value = null
}

function showDiseaseDetail(det: any) {
  selectedDisease.value = det
  showDetail.value = true
}

function getBoxColor(cls: string): string {
  const colors: Record<string, string> = { leaf_spot: '#f44336', powdery_mildew: '#ff9800', rust: '#ff5722', early_blight: '#2196f3', late_blight: '#9c27b0', healthy: '#4caf50' }
  return colors[cls] || '#4caf50'
}
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>📷 图片检测</h2>
      <p>上传作物叶片图片，AI自动识别病害类型与严重程度</p>
    </div>

    <!-- Upload Zone -->
    <div v-if="!selectedFile" class="glass animate-scale-in" style="padding:48px 32px;">
      <div
        :class="['upload-zone', { dragover: isDragging }]"
        style="border-style:dashed;padding:60px 40px;"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="($refs.fileInput as HTMLInputElement)?.click()"
      >
        <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/jpg" style="display:none" @change="handleFileInput" />
        <div class="upload-icon">🖼️</div>
        <p style="font-weight:600;font-size:1.1rem;">拖拽图片到此处</p>
        <p style="color:var(--text-tertiary);">或点击选择文件 · 支持 JPG、PNG 格式</p>
      </div>
    </div>

    <!-- Detection Result -->
    <div v-else style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <!-- Left: Image -->
      <div class="glass animate-slide-left">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <h3 style="font-weight:700;">📸 图片预览</h3>
          <button class="btn btn-outline btn-sm" @click="resetDetection">重新上传</button>
        </div>

        <div v-if="selectedFile" style="margin-bottom:12px;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:10px;font-size:0.82rem;">
          <span style="color:var(--text-secondary);">文件名：</span>{{ selectedFile.name }}
          <span style="margin-left:16px;color:var(--text-secondary);">大小：</span>{{ (selectedFile.size/1024).toFixed(2) }} KB
        </div>

        <div style="position:relative;background:rgba(0,0,0,0.2);border-radius:12px;overflow:hidden;min-height:300px;">
          <img :src="imageUrl!" alt="预览" style="width:100%;display:block;" />

          <!-- Detection Boxes -->
          <div v-if="result" v-for="(det, idx) in result.detections" :key="idx"
            class="detection-box"
            :style="{
              left: det.bbox.x + 'px', top: det.bbox.y + 'px',
              width: det.bbox.w + 'px', height: det.bbox.h + 'px',
              borderColor: getBoxColor(det.class),
              background: getBoxColor(det.class) + '15'
            }"
            @click.stop="showDiseaseDetail(det)"
          >
            <span class="det-label" :style="{background:getBoxColor(det.class)}">
              {{ det.label }} {{ (det.confidence*100).toFixed(0) }}%
            </span>
          </div>

          <!-- Loading overlay -->
          <div v-if="isDetecting" style="position:absolute;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;flex-direction:column;">
            <div style="width:48px;height:48px;border:3px solid rgba(255,255,255,0.2);border-top-color:#4caf50;border-radius:50%;animation:spin 0.8s linear infinite;margin-bottom:14px;"></div>
            <p style="font-weight:600;">AI正在分析中...</p>
          </div>
        </div>

        <button v-if="!result && !isDetecting" @click="startDetection" class="btn btn-primary btn-lg" style="width:100%;margin-top:14px;">
          🔍 开始检测
        </button>
      </div>

      <!-- Right: Results -->
      <div class="animate-slide-right">
        <!-- Empty -->
        <div v-if="!result && !isDetecting" class="glass text-center" style="padding:60px 32px;">
          <div style="font-size:3rem;margin-bottom:12px;">🔍</div>
          <p style="font-weight:600;">点击"开始检测"进行分析</p>
          <p style="color:var(--text-tertiary);font-size:0.85rem;margin-top:6px;">AI将自动识别图片中的病害区域</p>
        </div>

        <!-- Results -->
        <div v-if="result" class="space-y-4">
          <!-- Stats -->
          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:14px;">📊 检测统计</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
              <div style="text-align:center;padding:14px;background:rgba(33,150,243,0.1);border-radius:12px;">
                <p style="font-size:1.6rem;font-weight:800;color:#2196f3;">{{ result.totalDetections }}</p>
                <p style="font-size:0.75rem;color:var(--text-secondary);">检测总数</p>
              </div>
              <div style="text-align:center;padding:14px;background:rgba(76,175,80,0.1);border-radius:12px;">
                <p style="font-size:1.6rem;font-weight:800;color:#4caf50;">{{ result.healthCount }}</p>
                <p style="font-size:0.75rem;color:var(--text-secondary);">健康区域</p>
              </div>
              <div style="text-align:center;padding:14px;background:rgba(244,67,54,0.1);border-radius:12px;">
                <p style="font-size:1.6rem;font-weight:800;color:#f44336;">{{ result.diseaseCount }}</p>
                <p style="font-size:0.75rem;color:var(--text-secondary);">病害区域</p>
              </div>
              <div style="text-align:center;padding:14px;background:rgba(255,152,0,0.1);border-radius:12px;">
                <p style="font-size:1.3rem;font-weight:800;color:#ff9800;">{{ result.severity }}</p>
                <p style="font-size:0.75rem;color:var(--text-secondary);">严重程度</p>
              </div>
            </div>
          </div>

          <!-- Detection List -->
          <div class="glass" style="max-height:350px;overflow-y:auto;">
            <h3 style="font-weight:700;margin-bottom:14px;">🔍 检测详情</h3>
            <div class="space-y-2">
              <div
                v-for="(det, idx) in result.detections" :key="idx"
                class="section-card" style="cursor:pointer;padding:14px;"
                @click="showDiseaseDetail(det)"
              >
                <div style="display:flex;align-items:center;justify-content:space-between;">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:10px;height:10px;border-radius:50%;" :style="{background:getBoxColor(det.class)}"></div>
                    <div>
                      <p style="font-weight:700;font-size:0.9rem;">{{ det.label }}</p>
                      <p style="font-size:0.75rem;color:var(--text-tertiary);">{{ det.enLabel }}</p>
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <p style="font-size:1.2rem;font-weight:800;" :style="{color:getBoxColor(det.class)}">{{ (det.confidence*100).toFixed(0) }}%</p>
                    <p style="font-size:0.68rem;color:var(--text-muted);">置信度</p>
                  </div>
                </div>
                <div class="progress-track" style="margin-top:8px;">
                  <div class="progress-fill" :style="{width:(det.confidence*100)+'%',background:getBoxColor(det.class)}"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Disease Detail Modal -->
    <div v-if="showDetail && selectedDisease" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal-content animate-scale-in">
        <div style="padding:24px 28px;border-bottom:1px solid rgba(255,255,255,0.06);">
          <div style="display:flex;justify-content:space-between;align-items:start;">
            <div>
              <h2 style="font-weight:700;font-size:1.3rem;">{{ selectedDisease.label }}</h2>
              <p style="color:var(--text-tertiary);font-size:0.85rem;">{{ selectedDisease.enLabel }}</p>
            </div>
            <button @click="showDetail = false" style="padding:6px;border-radius:8px;border:none;background:rgba(255,255,255,0.08);color:#fff;cursor:pointer;font-size:1.2rem;">✕</button>
          </div>
        </div>

        <div v-if="selectedDisease.info" style="padding:20px 28px 28px;" class="space-y-4">
          <div>
            <h4 style="font-weight:700;margin-bottom:8px;">📋 病害描述</h4>
            <p style="color:var(--text-secondary);line-height:1.7;">{{ selectedDisease.info.desc }}</p>
          </div>
          <div style="padding:14px;background:rgba(244,67,54,0.08);border-radius:12px;border-left:3px solid #f44336;">
            <h4 style="font-weight:700;margin-bottom:8px;">🔍 症状表现</h4>
            <ul style="list-style:disc;padding-left:18px;color:var(--text-secondary);line-height:1.8;">
              <li v-for="s in selectedDisease.info.symptoms" :key="s">{{ s }}</li>
            </ul>
          </div>
          <div style="padding:14px;background:rgba(255,152,0,0.08);border-radius:12px;border-left:3px solid #ff9800;">
            <h4 style="font-weight:700;margin-bottom:8px;">🌱 诱因分析</h4>
            <p style="color:var(--text-secondary);">{{ selectedDisease.info.causes }}</p>
          </div>
          <div style="padding:14px;background:rgba(76,175,80,0.08);border-radius:12px;border-left:3px solid #4caf50;">
            <h4 style="font-weight:700;margin-bottom:8px;">💊 防治建议</h4>
            <ul style="list-style:disc;padding-left:18px;color:var(--text-secondary);line-height:1.8;">
              <li v-for="r in selectedDisease.info.recommendations" :key="r">{{ r }}</li>
            </ul>
          </div>
        </div>
        <div v-else style="padding:28px;text-align:center;">
          <div style="font-size:3rem;margin-bottom:12px;">✅</div>
          <p style="font-weight:600;color:#4caf50;">健康植株</p>
          <p style="color:var(--text-tertiary);margin-top:4px;">未检测到病害症状</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detection-box {
  position: absolute;
  border: 3px solid;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.detection-box:hover { transform: scale(1.03); z-index: 2; box-shadow: 0 0 20px rgba(0,0,0,0.4); }
.det-label {
  position: absolute;
  top: -28px;
  left: 0;
  padding: 2px 8px;
  border-radius: 4px 4px 0 0;
  font-size: 0.72rem;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
}
</style>
