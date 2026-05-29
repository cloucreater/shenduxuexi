<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

// Real evaluation records from API
const evaluationRecords = ref<any[]>([])
const loading = ref(true)

// New evaluation form
const newEvaluation = ref({
  disease: '',
  medicine: '',
  beforeImage: null as File | null,
  afterImage: null as File | null,
  beforeImageUrl: '',
  afterImageUrl: ''
})
const submitting = ref(false)

// Evaluation standards
const standards = [
  { range: '90%+', label: '非常有效', desc: '病害基本消除', color: '#16a34a', bg: 'var(--color-success-bg)' },
  { range: '70-89%', label: '有效', desc: '病害明显减少', color: '#3b82f6', bg: 'var(--color-info-bg)' },
  { range: '40-69%', label: '待观察', desc: '效果不明显', color: '#f59e0b', bg: 'var(--color-warning-bg)' },
  { range: '<40%', label: '无效', desc: '需更换方案', color: '#ef4444', bg: 'var(--color-danger-bg)' },
]

// Load history evaluations
async function loadEvaluations() {
  try {
    // Get evaluation-type detections
    const res = await api.get('/history?limit=50')
    const records = res.data.records || []
    // Process into evaluation records
    const evals = []
    for (const record of records) {
      if (record.detections && record.detections.length > 0) {
        const diseaseDetections = record.detections.filter((d: any) => d.label !== 'Healthy' && d.label !== '健康')
        const healthyDetections = record.detections.filter((d: any) => d.label === 'Healthy' || d.label === '健康')
        evals.push({
          id: record.id,
          date: record.created_at?.split(' ')[0] || '--',
          disease: diseaseDetections[0]?.label || '健康',
          count: diseaseDetections.length,
          healthyCount: healthyDetections.length,
          totalDetections: record.detections.length,
          image: record.result_image || record.image_url,
          detections: record.detections
        })
      }
    }
    evaluationRecords.value = evals
  } catch {
    evaluationRecords.value = []
  } finally {
    loading.value = false
  }
}

async function submitEvaluation() {
  if (!newEvaluation.value.disease || !newEvaluation.value.medicine) {
    alert('请填写病害类型和使用药剂')
    return
  }
  if (!newEvaluation.value.beforeImage) {
    alert('请上传施药前图片')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('file', newEvaluation.value.beforeImage)
    if (newEvaluation.value.afterImage) {
      formData.append('after_file', newEvaluation.value.afterImage)
    }

    const res = await api.post('/evaluation/compare', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // Add the result to the list
    evaluationRecords.value.unshift({
      id: Date.now().toString(),
      date: new Date().toISOString().split('T')[0],
      disease: newEvaluation.value.disease,
      count: res.data.current_count || 0,
      change: res.data.change || 0,
      evaluation: res.data.evaluation || '--',
      deepAnalysis: res.data.deep_analysis
    })

    // Reset form
    newEvaluation.value = {
      disease: '',
      medicine: '',
      beforeImage: null,
      afterImage: null,
      beforeImageUrl: '',
      afterImageUrl: ''
    }

    alert('评估提交成功！')
  } catch (err) {
    console.error('评估失败:', err)
    alert('评估提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

function handleBeforeImageUpload(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    newEvaluation.value.beforeImage = target.files[0]
    newEvaluation.value.beforeImageUrl = URL.createObjectURL(target.files[0])
  }
}

function handleAfterImageUpload(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    newEvaluation.value.afterImage = target.files[0]
    newEvaluation.value.afterImageUrl = URL.createObjectURL(target.files[0])
  }
}

function getEffectivenessColor(pct: number): string {
  if (pct >= 70) return 'var(--color-success)'
  if (pct >= 40) return 'var(--color-warning)'
  return 'var(--color-danger)'
}

function getEffectivenessBg(pct: number): string {
  if (pct >= 70) return 'var(--color-success-bg)'
  if (pct >= 40) return 'var(--color-warning-bg)'
  return 'var(--color-danger-bg)'
}

function getStatusLabel(pct: number): string {
  if (pct >= 90) return '非常有效'
  if (pct >= 70) return '有效'
  if (pct >= 40) return '待观察'
  return '无效'
}

onMounted(() => {
  loadEvaluations()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="page-header animate-fade-down">
      <h2>📋 效果评估</h2>
      <p>评估农药和防治措施的实际效果，为科学决策提供依据</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- Submit Form - 2 cols -->
      <div class="lg:col-span-2">
        <div class="glass-card animate-fade-up stagger-1">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:20px;font-size:1.05rem;">
            📝 提交新评估
          </h3>

          <div class="space-y-5">
            <!-- Disease Type -->
            <div>
              <label class="form-label">病害类型 <span class="required">*</span></label>
              <select v-model="newEvaluation.disease" class="form-select">
                <option value="">请选择病害类型</option>
                <option value="白粉病">白粉病 / Powdery Mildew</option>
                <option value="叶斑病">叶斑病 / Leaf Spot</option>
                <option value="锈病">锈病 / Rust</option>
                <option value="早疫病">早疫病 / Early Blight</option>
                <option value="晚疫病">晚疫病 / Late Blight</option>
              </select>
            </div>

            <!-- Medicine -->
            <div>
              <label class="form-label">使用药剂 <span class="required">*</span></label>
              <input
                v-model="newEvaluation.medicine"
                type="text"
                placeholder="请输入使用的药剂名称"
                class="form-input"
              />
            </div>

            <!-- Before Image -->
            <div>
              <label class="form-label">施药前图片 <span class="required">*</span></label>
              <div
                class="upload-zone"
                @click="($refs.beforeInput as HTMLInputElement)?.click()"
              >
                <input
                  ref="beforeInput"
                  type="file"
                  accept="image/*"
                  style="display:none"
                  @change="handleBeforeImageUpload"
                />
                <div v-if="newEvaluation.beforeImageUrl" style="position:relative;">
                  <img :src="newEvaluation.beforeImageUrl" alt="施药前" style="max-height:160px;margin:0 auto;border-radius:8px;" />
                  <p style="color:var(--color-success);font-size:0.85rem;margin-top:6px;">✅ 已上传施药前图片</p>
                </div>
                <div v-else>
                  <div class="upload-icon">📸</div>
                  <p style="font-weight:500;">点击上传施药前图片</p>
                  <p style="font-size:0.8rem;color:var(--text-muted);">支持 JPG、PNG 格式</p>
                </div>
              </div>
            </div>

            <!-- After Image -->
            <div>
              <label class="form-label">施药后图片 <span style="color:var(--text-muted);font-weight:400;">(可选)</span></label>
              <div
                class="upload-zone"
                @click="($refs.afterInput as HTMLInputElement)?.click()"
              >
                <input
                  ref="afterInput"
                  type="file"
                  accept="image/*"
                  style="display:none"
                  @change="handleAfterImageUpload"
                />
                <div v-if="newEvaluation.afterImageUrl" style="position:relative;">
                  <img :src="newEvaluation.afterImageUrl" alt="施药后" style="max-height:160px;margin:0 auto;border-radius:8px;" />
                  <p style="color:var(--color-success);font-size:0.85rem;margin-top:6px;">✅ 已上传施药后图片</p>
                </div>
                <div v-else>
                  <div class="upload-icon">🔬</div>
                  <p style="font-weight:500;">点击上传施药后图片</p>
                  <p style="font-size:0.8rem;color:var(--text-muted);">用于对比分析</p>
                </div>
              </div>
            </div>

            <!-- Submit -->
            <button
              @click="submitEvaluation"
              :disabled="submitting"
              class="btn btn-primary btn-lg"
              style="width:100%;"
            >
              {{ submitting ? '⏳ 正在分析...' : '🚀 提交评估' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Evaluation History - 3 cols -->
      <div class="lg:col-span-3">
        <div class="glass-card animate-fade-up stagger-2" style="margin-bottom:20px;">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">
            📊 评估记录
            <span style="font-weight:400;font-size:0.8rem;color:var(--text-muted);margin-left:8px;">
              ({{ evaluationRecords.length }} 条)
            </span>
          </h3>

          <!-- Loading -->
          <div v-if="loading" style="text-align:center;padding:40px;">
            <div class="skeleton" style="height:80px;margin-bottom:12px;"></div>
            <div class="skeleton" style="height:80px;margin-bottom:12px;"></div>
            <div class="skeleton" style="height:80px;"></div>
          </div>

          <!-- Records -->
          <div v-else-if="evaluationRecords.length > 0" class="space-y-3" style="max-height:600px;overflow-y:auto;">
            <div
              v-for="(record, idx) in evaluationRecords"
              :key="record.id"
              class="section-card animate-fade-up"
              :class="'stagger-' + Math.min(idx + 1, 8)"
              style="cursor:pointer;padding:18px 20px;"
            >
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                <div>
                  <span style="font-weight:700;color:var(--text-primary);">{{ record.disease }}</span>
                  <span
                    style="margin-left:8px;padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;"
                    :style="{ background: getEffectivenessBg(record.change ? Math.abs(record.change) : record.effectiveness || 0), color: getEffectivenessColor(record.change ? Math.abs(record.change) : record.effectiveness || 0) }"
                  >
                    {{ record.evaluation || getStatusLabel(record.effectiveness || 0) }}
                  </span>
                </div>
                <span style="font-size:0.8rem;color:var(--text-muted);">{{ record.date }}</span>
              </div>

              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
                <div style="text-align:center;padding:10px;background:var(--color-danger-bg);border-radius:10px;">
                  <p style="font-size:0.75rem;color:var(--text-muted);">菌落数量</p>
                  <p style="font-size:1.3rem;font-weight:800;color:var(--color-danger);">{{ record.count || record.beforeCount || '--' }}</p>
                </div>
                <div style="text-align:center;padding:10px;background:var(--color-success-bg);border-radius:10px;">
                  <p style="font-size:0.75rem;color:var(--text-muted);">健康区域</p>
                  <p style="font-size:1.3rem;font-weight:800;color:var(--color-success);">{{ record.healthyCount || record.afterCount || '--' }}</p>
                </div>
                <div style="text-align:center;padding:10px;background:var(--color-info-bg);border-radius:10px;">
                  <p style="font-size:0.75rem;color:var(--text-muted);">检测总数</p>
                  <p style="font-size:1.3rem;font-weight:800;color:var(--color-info);">{{ record.totalDetections || record.beforeCount || '--' }}</p>
                </div>
              </div>

              <!-- Effect bar -->
              <div v-if="record.effectiveness !== undefined" style="margin-top:10px;">
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:4px;">
                  <span style="color:var(--text-secondary);">防治效果</span>
                  <span style="font-weight:700;" :style="{ color: getEffectivenessColor(record.effectiveness) }">
                    {{ record.effectiveness }}%
                  </span>
                </div>
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :style="{ width: record.effectiveness + '%', background: getEffectivenessColor(record.effectiveness) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty -->
          <div v-else style="text-align:center;padding:48px 20px;">
            <div style="font-size:3rem;margin-bottom:12px;">📭</div>
            <p style="color:var(--text-secondary);font-weight:500;">暂无评估记录</p>
            <p style="color:var(--text-muted);font-size:0.85rem;margin-top:4px;">提交新的评估后将在此显示</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Evaluation Standards -->
    <div class="glass-card animate-fade-up stagger-3">
      <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">📏 效果评估标准</h3>
      <div class="stats-grid" style="margin-bottom:0;">
        <div
          v-for="std in standards"
          :key="std.range"
          class="section-card"
          style="text-align:center;padding:24px 20px;cursor:default;"
        >
          <div
            style="width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-weight:800;font-size:1rem;"
            :style="{ background: std.bg, color: std.color }"
          >
            {{ std.range }}
          </div>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:4px;">{{ std.label }}</p>
          <p style="font-size:0.82rem;color:var(--text-secondary);">{{ std.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
