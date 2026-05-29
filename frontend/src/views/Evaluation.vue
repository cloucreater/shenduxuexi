<script setup lang="ts">
import { ref, onMounted } from 'vue'

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
  if (!formData.value.beforeImage) {
    alert('请上传施药前图片')
    return
  }

  submitting.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Generate simulated result
  const effectiveness = 40 + Math.floor(Math.random() * 55)
  const colonyBefore = 50 + Math.floor(Math.random() * 200)
  const colonyAfter = Math.max(5, colonyBefore - Math.floor(colonyBefore * effectiveness / 100))
  const healthyBefore = 100 + Math.floor(Math.random() * 100)
  const healthyAfter = healthyBefore + Math.floor((colonyBefore - colonyAfter) * 0.8)

  evaluations.value.unshift({
    id: Date.now().toString(),
    date: new Date().toISOString().split('T')[0],
    disease: formData.value.disease,
    medicine: formData.value.medicine,
    effectiveness,
    colonyBefore,
    colonyAfter,
    healthyBefore,
    healthyAfter,
    totalDetections: colonyBefore + healthyBefore,
    status: effectiveness >= 90 ? '非常有效' : effectiveness >= 70 ? '有效' : effectiveness >= 40 ? '待观察' : '无效',
    statusColor: effectiveness >= 90 ? '#4caf50' : effectiveness >= 70 ? '#2196f3' : effectiveness >= 40 ? '#ff9800' : '#f44336',
  })

  formData.value = { disease: '', medicine: '', beforeImage: null, afterImage: null, beforeImageUrl: '', afterImageUrl: '' }
  submitting.value = false
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

// Pre-populate some demo records
const demoNames = [
  { disease: '叶斑病', medicine: '多菌灵悬浮剂', effectiveness: 92, colonyBefore: 156, colonyAfter: 12, healthyBefore: 89, healthyAfter: 168 },
  { disease: '白粉病', medicine: '氟硅唑乳油', effectiveness: 78, colonyBefore: 134, colonyAfter: 29, healthyBefore: 102, healthyAfter: 145 },
  { disease: '锈病', medicine: '三唑酮乳油', effectiveness: 45, colonyBefore: 98, colonyAfter: 54, healthyBefore: 76, healthyAfter: 82 },
]

onMounted(() => {
  evaluations.value = demoNames.map((d, i) => ({
    id: `demo-${i}`,
    date: new Date(Date.now() - (i + 1) * 86400000).toISOString().split('T')[0],
    disease: d.disease,
    medicine: d.medicine,
    effectiveness: d.effectiveness,
    colonyBefore: d.colonyBefore,
    colonyAfter: d.colonyAfter,
    healthyBefore: d.healthyBefore,
    healthyAfter: d.healthyAfter,
    totalDetections: d.colonyBefore + d.healthyBefore,
    status: d.effectiveness >= 90 ? '非常有效' : d.effectiveness >= 70 ? '有效' : '待观察',
    statusColor: d.effectiveness >= 90 ? '#4caf50' : d.effectiveness >= 70 ? '#2196f3' : '#ff9800',
  }))
})
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>⭐ 效果评估</h2>
      <p>评估防治措施的实际效果，为科学用药提供数据支撑</p>
    </div>

    <div style="display:grid;grid-template-columns:45% 55%;gap:20px;">
      <!-- Left: Form -->
      <div class="glass animate-slide-left">
        <h3 style="font-weight:700;margin-bottom:20px;font-size:1.05rem;">📝 提交新评估</h3>

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
          <label class="form-label">施药前图片 <span class="required">*</span></label>
          <div class="upload-zone" @click="($refs.beforeInput as HTMLInputElement)?.click()">
            <input ref="beforeInput" type="file" accept="image/*" style="display:none" @change="handleBeforeImageUpload" />
            <div v-if="formData.beforeImageUrl">
              <img :src="formData.beforeImageUrl" alt="施药前" style="max-height:140px;margin:0 auto;border-radius:10px;" />
              <p style="color:#4caf50;font-size:0.85rem;margin-top:6px;">✅ 已上传施药前图片</p>
            </div>
            <div v-else>
              <div class="upload-icon">📸</div>
              <p style="font-weight:500;">点击上传施药前图片</p>
              <p style="font-size:0.8rem;color:var(--text-muted);">支持 JPG、PNG 格式</p>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">施药后图片 <span style="font-weight:400;color:var(--text-muted);">(可选)</span></label>
          <div class="upload-zone" @click="($refs.afterInput as HTMLInputElement)?.click()">
            <input ref="afterInput" type="file" accept="image/*" style="display:none" @change="handleAfterImageUpload" />
            <div v-if="formData.afterImageUrl">
              <img :src="formData.afterImageUrl" alt="施药后" style="max-height:140px;margin:0 auto;border-radius:10px;" />
              <p style="color:#4caf50;font-size:0.85rem;margin-top:6px;">✅ 已上传施药后图片</p>
            </div>
            <div v-else>
              <div class="upload-icon">🔬</div>
              <p style="font-weight:500;">点击上传施药后图片</p>
              <p style="font-size:0.8rem;color:var(--text-muted);">用于对比分析效果</p>
            </div>
          </div>
        </div>

        <button @click="submitEvaluation" :disabled="submitting" class="btn btn-primary btn-lg" style="width:100%;">
          {{ submitting ? '⏳ 正在分析...' : '🚀 开始评估' }}
        </button>
      </div>

      <!-- Right: Records & Standards -->
      <div class="animate-slide-right">
        <!-- Evaluation Records -->
        <div class="glass mb-4" style="max-height:400px;overflow-y:auto;">
          <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">
            📊 评估记录
            <span style="font-weight:400;font-size:0.8rem;color:var(--text-tertiary);margin-left:8px;">({{ evaluations.length }} 条)</span>
          </h3>

          <div v-if="evaluations.length === 0" style="text-align:center;padding:48px 20px;">
            <div style="font-size:3rem;margin-bottom:12px;">📭</div>
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
                  <p style="font-size:0.7rem;color:var(--text-tertiary);">菌落数量</p>
                  <p style="font-size:1.1rem;font-weight:800;color:#f44336;">{{ record.colonyAfter }} <span style="font-size:0.7rem;opacity:0.6;">/ {{ record.colonyBefore }}</span></p>
                </div>
                <div style="text-align:center;padding:8px;background:rgba(76,175,80,0.1);border-radius:10px;">
                  <p style="font-size:0.7rem;color:var(--text-tertiary);">健康区域</p>
                  <p style="font-size:1.1rem;font-weight:800;color:#4caf50;">{{ record.healthyAfter }} <span style="font-size:0.7rem;opacity:0.6;">/ {{ record.healthyBefore }}</span></p>
                </div>
                <div style="text-align:center;padding:8px;background:rgba(33,150,243,0.1);border-radius:10px;">
                  <p style="font-size:0.7rem;color:var(--text-tertiary);">检测总数</p>
                  <p style="font-size:1.1rem;font-weight:800;color:#2196f3;">{{ record.totalDetections }}</p>
                </div>
              </div>

              <!-- Effect bar -->
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

        <!-- Evaluation Standards -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">📏 效果评估标准</h3>
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
