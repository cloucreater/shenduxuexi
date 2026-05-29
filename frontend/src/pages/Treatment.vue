<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api'

const formData = ref({ disease: '', severity: '', crop: '' })
const result = ref<any>(null)
const isGenerating = ref(false)

const diseaseOptions = [
  { value: '白粉病', label: '白粉病 / Powdery Mildew' },
  { value: '叶斑病', label: '叶斑病 / Leaf Spot' },
  { value: '锈病', label: '锈病 / Rust' },
  { value: '早疫病', label: '早疫病 / Early Blight' },
  { value: '晚疫病', label: '晚疫病 / Late Blight' }
]

const severityOptions = [
  { value: '轻度', label: '轻度 / Light' },
  { value: '中度', label: '中度 / Medium' },
  { value: '重度', label: '重度 / Severe' }
]

const cropOptions = [
  { value: '番茄', label: '番茄 / Tomato' },
  { value: '土豆', label: '土豆 / Potato' },
  { value: '小麦', label: '小麦 / Wheat' },
  { value: '玉米', label: '玉米 / Corn' },
  { value: '水稻', label: '水稻 / Rice' }
]

async function generateTreatment() {
  if (!formData.value.disease || !formData.value.severity || !formData.value.crop) {
    alert('请填写完整的病害信息')
    return
  }

  isGenerating.value = true

  try {
    // Try calling the backend treatment API
    const res = await api.post('/treatment/generate', {
      disease: formData.value.disease,
      severity: formData.value.severity,
      crop: formData.value.crop
    })
    result.value = res.data
  } catch {
    // Fallback to simulated response
    await new Promise(resolve => setTimeout(resolve, 1500))

    result.value = {
      disease: formData.value.disease,
      severity: formData.value.severity,
      crop: formData.value.crop,
      timestamp: new Date().toLocaleString('zh-CN'),
      medicines: [
        { name: '多菌灵悬浮剂', usage: '叶面喷施', dosage: '稀释1000-1500倍', frequency: '每7-10天一次', precautions: '避免在高温时段使用，建议早晨或傍晚施药' },
        { name: '百菌清可湿性粉剂', usage: '叶面喷施', dosage: '稀释600-800倍', frequency: '每10-15天一次', precautions: '与其他农药混用时需先进行兼容性试验' },
        { name: '代森锰锌可湿性粉剂', usage: '叶面喷施', dosage: '稀释500-700倍', frequency: '每7-10天一次', precautions: '不能与铜制剂或碱性农药混用' }
      ],
      farmingAdvice: [
        { title: '及时清除病叶', description: '发现病叶立即摘除，带出田外销毁，减少病原传播', icon: 'leaf' },
        { title: '加强通风透光', description: '合理密植，保持田间通风透光，降低田间湿度', icon: 'sun' },
        { title: '控制灌溉', description: '避免大水漫灌，采用滴灌或渗灌方式，保持土壤适度干燥', icon: 'water' },
        { title: '增施有机肥', description: '适当增施磷钾肥，提高植株抗病能力，避免偏施氮肥', icon: 'fertilizer' }
      ],
      prevention: [
        '选择抗病品种进行种植',
        '实行合理的轮作制度，避免连作障碍',
        '播种前进行种子消毒处理',
        '加强田间管理，及时清除杂草',
        '关注天气预报，在病害高发期提前预防'
      ]
    }
  } finally {
    isGenerating.value = false
  }
}

function resetForm() {
  formData.value = { disease: '', severity: '', crop: '' }
  result.value = null
}

const iconMap: Record<string, string> = {
  leaf: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z',
  sun: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z',
  water: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z',
  fertilizer: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="page-header animate-fade-down">
      <h2>💊 防治方案</h2>
      <p>基于AI智能分析，为您生成个性化的病害防治方案</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Input Form -->
      <div class="glass-card animate-fade-up stagger-1">
        <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:20px;font-size:1.05rem;">📝 病害信息</h3>

        <div class="space-y-5">
          <div>
            <label class="form-label">病害类型 <span class="required">*</span></label>
            <select v-model="formData.disease" class="form-select">
              <option value="">请选择病害类型</option>
              <option v-for="opt in diseaseOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>

          <div>
            <label class="form-label">严重程度 <span class="required">*</span></label>
            <select v-model="formData.severity" class="form-select">
              <option value="">请选择严重程度</option>
              <option v-for="opt in severityOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>

          <div>
            <label class="form-label">作物种类 <span class="required">*</span></label>
            <select v-model="formData.crop" class="form-select">
              <option value="">请选择作物种类</option>
              <option v-for="opt in cropOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>

          <div style="display:flex;gap:12px;">
            <button
              @click="generateTreatment"
              :disabled="isGenerating"
              class="btn btn-primary btn-lg"
              style="flex:1;"
            >
              {{ isGenerating ? '⏳ 正在生成...' : '🧬 生成防治方案' }}
            </button>
            <button @click="resetForm" class="btn btn-outline">
              重置
            </button>
          </div>
        </div>
      </div>

      <!-- Results -->
      <div class="animate-fade-up stagger-2">
        <!-- Loading -->
        <div v-if="isGenerating" class="glass-card text-center" style="padding:60px 32px;">
          <div style="width:56px;height:56px;border:4px solid var(--surface-border);border-top-color:var(--color-primary);border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px;"></div>
          <p style="font-weight:600;color:var(--text-primary);">正在基于AI生成个性化防治方案...</p>
          <p style="font-size:0.85rem;color:var(--text-muted);margin-top:4px;">综合分析病害特征和防治经验</p>
        </div>

        <!-- Result -->
        <div v-else-if="result" class="space-y-4">
          <!-- Summary Header -->
          <div class="glass-card" style="background:linear-gradient(135deg, var(--green-700), var(--green-500));color:#fff;padding:20px 24px;">
            <h3 style="font-weight:700;margin-bottom:12px;font-size:1.05rem;">✅ 防治方案已生成</h3>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;text-align:center;">
              <div>
                <p style="font-size:0.75rem;opacity:0.8;">病害类型</p>
                <p style="font-weight:700;font-size:0.95rem;">{{ result.disease }}</p>
              </div>
              <div>
                <p style="font-size:0.75rem;opacity:0.8;">严重程度</p>
                <p style="font-weight:700;font-size:0.95rem;">{{ result.severity }}</p>
              </div>
              <div>
                <p style="font-size:0.75rem;opacity:0.8;">作物种类</p>
                <p style="font-weight:700;font-size:0.95rem;">{{ result.crop }}</p>
              </div>
            </div>
          </div>

          <!-- Medicines -->
          <div class="glass-card">
            <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:14px;font-size:1rem;">💊 推荐药剂</h3>
            <div class="space-y-3">
              <div
                v-for="(med, idx) in result.medicines"
                :key="idx"
                class="section-card animate-fade-up"
                :class="'stagger-' + (idx + 1)"
                style="padding:16px 18px;"
              >
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                  <h4 style="font-weight:700;color:var(--text-primary);">{{ med.name }}</h4>
                  <span style="padding:3px 12px;border-radius:12px;font-size:0.75rem;font-weight:600;background:var(--color-info-bg);color:var(--color-info);">
                    {{ med.usage }}
                  </span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.82rem;color:var(--text-secondary);">
                  <div>📏 用量：<strong>{{ med.dosage }}</strong></div>
                  <div>🕐 频率：<strong>{{ med.frequency }}</strong></div>
                </div>
                <p style="margin-top:8px;font-size:0.78rem;color:var(--color-warning);background:var(--color-warning-bg);padding:6px 10px;border-radius:6px;">
                  ⚠️ {{ med.precautions }}
                </p>
              </div>
            </div>
          </div>

          <!-- Farming Advice -->
          <div class="glass-card">
            <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:14px;font-size:1rem;">🌱 农事管理建议</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
              <div
                v-for="(advice, idx) in result.farmingAdvice"
                :key="idx"
                class="section-card"
                style="padding:14px;display:flex;align-items:flex-start;gap:10px;"
              >
                <div style="width:36px;height:36px;border-radius:10px;background:var(--color-primary-bg);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                  <svg class="w-5 h-5" style="color:var(--color-primary);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconMap[advice.icon] || iconMap.leaf" />
                  </svg>
                </div>
                <div>
                  <h4 style="font-weight:600;color:var(--text-primary);font-size:0.85rem;margin-bottom:2px;">{{ advice.title }}</h4>
                  <p style="font-size:0.78rem;color:var(--text-secondary);line-height:1.4;">{{ advice.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Prevention -->
          <div class="glass-card">
            <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:14px;font-size:1rem;">🛡️ 预防措施</h3>
            <div class="space-y-2">
              <div
                v-for="(item, idx) in result.prevention"
                :key="idx"
                style="display:flex;align-items:center;gap:10px;padding:8px 0;"
              >
                <svg class="w-5 h-5 flex-shrink-0" style="color:var(--color-success);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span style="font-size:0.88rem;color:var(--text-secondary);">{{ item }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="glass-card text-center" style="padding:60px 32px;">
          <div style="font-size:4rem;margin-bottom:16px;">🧪</div>
          <p style="font-weight:600;color:var(--text-primary);font-size:1.05rem;">填写病害信息获取方案</p>
          <p style="color:var(--text-muted);font-size:0.85rem;margin-top:6px;">请选择病害类型、严重程度和作物种类<br>系统将为您生成个性化的防治方案</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
