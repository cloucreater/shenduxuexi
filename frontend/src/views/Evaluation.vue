<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

const formData = ref({
  disease: '',
  medicine: '',
  beforeImage: null as File | null,
  afterImage: null as File | null,
  beforeImageUrl: '',
  afterImageUrl: '',
})
const submitting = ref(false)
const evaluations = ref<any[]>([])
const errorMsg = ref('')

const diseaseOptions = ['叶斑病', '锈病', '白粉病', '早疫病', '晚疫病']

const standards = [
  { range: '≥90%', label: '非常有效', desc: '病害基本消除，作物恢复正常生长', color: '#4caf50', bg: 'rgba(76,175,80,0.15)' },
  { range: '70-89%', label: '有效', desc: '病害明显减少，效果良好', color: '#2196f3', bg: 'rgba(33,150,243,0.15)' },
  { range: '40-69%', label: '待观察', desc: '有一定效果但不明显，需继续观察', color: '#ff9800', bg: 'rgba(255,152,0,0.15)' },
  { range: '<40%', label: '无效', desc: '效果不佳，需更换防治方案', color: '#f44336', bg: 'rgba(244,67,54,0.15)' },
]

function handleBeforeImageUpload(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    formData.value.beforeImage = target.files[0]
    formData.value.beforeImageUrl = URL.createObjectURL(target.files[0])
  }
}

function handleAfterImageUpload(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    formData.value.afterImage = target.files[0]
    formData.value.afterImageUrl = URL.createObjectURL(target.files[0])
  }
}

async function submitEvaluation() {
  if (!formData.value.disease || !formData.value.medicine) {
    alert('请填写病害类型和使用药剂')
    return
  }
  if (!formData.value.afterImage) {
    alert('请上传施药后图片')
    return
  }

  submitting.value = true
  errorMsg.value = ''

  try {
    const fd = new FormData()
    fd.append('file', formData.value.afterImage)
    if (formData.value.beforeImage) {
      fd.append('before_image', formData.value.beforeImage)
    }

    const res = await api.post('/evaluation/compare', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    const data = res.data
    const effectiveness = data.change <= -20 ? 100 + data.change : Math.max(0, 100 - Math.abs(data.change))

    evaluations.value.unshift({
      id: Date.now().toString(),
      date: new Date().toISOString().split('T')[0],
      disease: formData.value.disease,
      medicine: formData.value.medicine,
      effectiveness: Math.round(effectiveness),
      colonyBefore: data.previous_count,
      colonyAfter: data.current_count,
      healthyBefore: 0,
      healthyAfter: 0,
      totalDetections: data.previous_count + data.current_count,
      status: data.evaluation === '有效' ? '非常有效' : data.evaluation === '一般' ? '待观察' : '无效',
      statusColor: data.evaluation === '有效' ? '#4caf50' : data.evaluation === '一般' ? '#ff9800' : '#f44336',
      deepAnalysis: data.deep_analysis,
    })

    formData.value = { disease: '', medicine: '', beforeImage: null, afterImage: null, beforeImageUrl: '', afterImageUrl: '' }
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '评估失败，请重试'
  } finally {
    submitting.value = false
  }
}

async function loadHistory() {
  try {
    const res = await api.get('/history', { params: { limit: 50 } })
    const records = (res.data.records || []).filter((r: any) => r.type === 'evaluation' || r.detections?.length)
    evaluations.value = records.slice(0, 20).map((r: any) => {
      const diseaseDetections = (r.detections || []).filter((d: any) => d.label !== 'healthy')
      return {
        id: r.id,
        date: r.created_at?.split(' ')[0] || '—',
        disease: diseaseDetections[0]?.label || '—',
        medicine: '—',
        effectiveness: 50,
        colonyBefore: 0,
        colonyAfter: diseaseDetections.length,
        healthyBefore: 0,
        healthyAfter: (r.detections || []).length - diseaseDetections.length,
        totalDetections: (r.detections || []).length,
        status: diseaseDetections.length === 0 ? '非常有效' : '待观察',
        statusColor: diseaseDetections.length === 0 ? '#4caf50' : '#ff9800',
      }
    })
  } catch {
    evaluations.value = []
  }
}

function getLevelColor(pct: number): string {
  if (pct >= 90) return '#4caf50'
  if (pct >= 70) return '#2196f3'
  if (pct >= 40) return '#ff9800'
  return '#f44336'
}

function getLevelBg(pct: number): string {
  if (pct >= 90) return 'rgba(76,175,80,0.15)'
  if (pct >= 70) return 'rgba(33,150,243,0.15)'
  if (pct >= 40) return 'rgba(255,152,0,0.15)'
  return 'rgba(244,67,54,0.15)'
}

onMounted(() => {
  loadHistory()
})
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>效果评估</h2>
      <p>评估防治措施的实际效果，为科学用药提供数据支撑</p>
    </div>

    <div style="display:grid;grid-template-columns:45% 55%;gap:20px;">
      <!-- Left: Form -->
      <div class="glass animate-slide-left">
        <h3 style="font-weight:700;margin-bottom:20px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>提交新评估</h3>

        <div class="form-group">
          <label class="form-label">病害类型 <span class="required">*</span></label>
          <select v-model="formData.disease" class="form-select">
            <option value="">请选择病害类型</option>
            <option v-for="d in diseaseOptions" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">使用药剂 <span class="required">*</span></label>
          <input v-model="formData.medicine" type="text" placeholder="请输入使用的药剂名称" class="form-input" />
        </div>

        <div class="form-group">
          <label class="form-label">施药前图片 <span style="font-weight:400;color:var(--text-muted);">(可选)</span></label>
          <div class="upload-zone" @click="($refs.beforeInput as HTMLInputElement)?.click()">
            <input ref="beforeInput" type="file" accept="image/*" style="display:none" @change="handleBeforeImageUpload" />
            <div v-if="formData.beforeImageUrl">
              <img :src="formData.beforeImageUrl" alt="施药前" style="max-height:140px;margin:0 auto;border-radius:10px;" />
              <p style="color:#4caf50;font-size:0.85rem;margin-top:6px;display:flex;align-items:center;gap:4px;justify-content:center;"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>已上传施药前图片</p>
            </div>
            <div v-else>
              <div class="upload-icon"><svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg></div>
              <p style="font-weight:500;">点击上传施药前图片</p>
              <p style="font-size:0.8rem;color:var(--text-muted);">用于对比分析效果</p>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">施药后图片 <span class="required">*</span></label>
          <div class="upload-zone" @click="($refs.afterInput as HTMLInputElement)?.click()">
            <input ref="afterInput" type="file" accept="image/*" style="display:none" @change="handleAfterImageUpload" />
            <div v-if="formData.afterImageUrl">
              <img :src="formData.afterImageUrl" alt="施药后" style="max-height:140px;margin:0 auto;border-radius:10px;" />
              <p style="color:#4caf50;font-size:0.85rem;margin-top:6px;display:flex;align-items:center;gap:4px;justify-content:center;"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>已上传施药后图片</p>
            </div>
            <div v-else>
              <div class="upload-icon"><svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div>
              <p style="font-weight:500;">点击上传施药后图片</p>
              <p style="font-size:0.8rem;color:var(--text-muted);">用于对比分析效果</p>
            </div>
          </div>
        </div>

        <div v-if="errorMsg" style="padding:10px 14px;background:rgba(244,67,54,0.1);border-radius:8px;color:#f44336;font-size:0.85rem;margin-bottom:12px;">
          {{ errorMsg }}
        </div>

        <button @click="submitEvaluation" :disabled="submitting" class="btn btn-primary btn-lg" style="width:100%;">
          <template v-if="submitting">正在分析...</template>
          <template v-else>开始评估</template>
        </button>
      </div>

      <!-- Right: Records & Standards -->
      <div class="animate-slide-right">
        <div class="glass mb-4" style="max-height:400px;overflow-y:auto;">
          <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;display:flex;align-items:center;gap:8px;">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="18" y="3" width="4" height="18"/><rect x="10" y="8" width="4" height="13"/><rect x="2" y="13" width="4" height="8"/></svg>
            评估记录
            <span style="font-weight:400;font-size:0.8rem;color:var(--text-tertiary);margin-left:4px;">({{ evaluations.length }} 条)</span>
          </h3>

          <div v-if="evaluations.length === 0" style="text-align:center;padding:48px 20px;">
            <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="margin-bottom:12px;opacity:0.3;"><path d="M22 12h-6l-2 3H10l-2-3H2"/><path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/></svg>
            <p style="color:var(--text-secondary);">暂无评估记录</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="(record, idx) in evaluations"
              :key="record.id"
              class="section-card"
              :class="`animate-fade-up stagger-${Math.min(idx+1,8)}`"
              style="padding:16px 18px;"
            >
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div>
                  <span style="font-weight:700;">{{ record.disease }}</span>
                  <span
                    style="margin-left:8px;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:600;"
                    :style="{ background: getLevelBg(record.effectiveness), color: getLevelColor(record.effectiveness) }"
                  >
                    {{ record.status }} ({{ record.effectiveness }}%)
                  </span>
                </div>
                <span style="font-size:0.78rem;color:var(--text-tertiary);">{{ record.date }}</span>
              </div>

              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
                <div style="text-align:center;padding:8px;background:rgba(244,67,54,0.1);border-radius:10px;">
                  <p style="font-size:0.7rem;color:var(--text-tertiary);">当前菌落</p>
                  <p style="font-size:1.1rem;font-weight:800;color:#f44336;">{{ record.colonyAfter }}</p>
                </div>
                <div style="text-align:center;padding:8px;background:rgba(76,175,80,0.1);border-radius:10px;">
                  <p style="font-size:0.7rem;color:var(--text-tertiary);">之前菌落</p>
                  <p style="font-size:1.1rem;font-weight:800;color:#4caf50;">{{ record.colonyBefore }}</p>
                </div>
                <div style="text-align:center;padding:8px;background:rgba(33,150,243,0.1);border-radius:10px;">
                  <p style="font-size:0.7rem;color:var(--text-tertiary);">检测总数</p>
                  <p style="font-size:1.1rem;font-weight:800;color:#2196f3;">{{ record.totalDetections }}</p>
                </div>
              </div>

              <div style="margin-top:10px;">
                <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:4px;">
                  <span style="color:var(--text-secondary);">防治效果</span>
                  <span style="font-weight:700;" :style="{color:getLevelColor(record.effectiveness)}">{{ record.effectiveness }}%</span>
                </div>
                <div class="progress-track">
                  <div class="progress-fill" :style="{width:record.effectiveness+'%',background:getLevelColor(record.effectiveness)}"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="4" y1="20" x2="20" y2="20"/><polyline points="4 20 8 12 12 16 16 8 20 12"/></svg>效果评估标准</h3>
          <div class="space-y-3">
            <div v-for="std in standards" :key="std.range" class="section-card" style="display:flex;align-items:center;gap:16px;padding:18px;">
              <div
                style="width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.85rem;flex-shrink:0;"
                :style="{ background: std.bg, color: std.color }"
              >
                {{ std.range }}
              </div>
              <div style="flex:1;">
                <p style="font-weight:700;margin-bottom:2px;">{{ std.label }} <span style="font-weight:400;font-size:0.8rem;" :style="{color:std.color}">{{ std.range }}</span></p>
                <p style="font-size:0.82rem;color:var(--text-secondary);">{{ std.desc }}</p>
              </div>
              <div style="width:80px;text-align:right;">
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :style="{ width: std.range === '≥90%' ? '100%' : std.range === '70-89%' ? '80%' : std.range === '40-69%' ? '55%' : '25%', background: std.color }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
