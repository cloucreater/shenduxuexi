<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api'
import StreamingText from '@/components/StreamingText.vue'

const formData = ref({ disease: '', severity: '', crop: '' })
const result = ref<any>(null)
const isGenerating = ref(false)
const errorMsg = ref('')
const streamMode = ref(false)
const streamContent = ref('')

const diseaseOptions = [
  { value: 'leaf_spot', label: '叶斑病 / Leaf Spot' },
  { value: 'rust', label: '锈病 / Rust' },
  { value: 'powdery_mildew', label: '白粉病 / Powdery Mildew' },
  { value: 'early_blight', label: '早疫病 / Early Blight' },
  { value: 'late_blight', label: '晚疫病 / Late Blight' },
]

const severityOptions = [
  { value: '轻度', label: '轻度 / Light', color: '#ff9800' },
  { value: '中度', label: '中度 / Medium', color: '#f44336' },
  { value: '重度', label: '重度 / Severe', color: '#b71c1c' },
]

const cropOptions = [
  { value: '番茄', label: '番茄 / Tomato' },
  { value: '黄瓜', label: '黄瓜 / Cucumber' },
  { value: '辣椒', label: '辣椒 / Pepper' },
]

const farmingAdvices = [
  { title: '及时清除病叶', desc: '发现病叶立即摘除，带出田外销毁，减少病原传播', icon: 'leaf' },
  { title: '加强通风透光', desc: '合理密植，保持田间通风透光，降低田间湿度', icon: 'wind' },
  { title: '控制灌溉方式', desc: '避免大水漫灌，采用滴灌或渗灌方式，保持土壤适度干燥', icon: 'water' },
  { title: '增施有机肥料', desc: '适当增施磷钾肥，提高植株抗病能力，避免偏施氮肥', icon: 'sprout' },
  { title: '合理轮作制度', desc: '实行3年以上轮作，避免连作障碍加重病害', icon: 'cycle' },
  { title: '种子消毒处理', desc: '播种前进行温汤浸种或药剂拌种，杀灭种子携带病菌', icon: 'flask' },
]

const preventionTips = [
  '选择抗病品种进行种植，从源头降低病害风险',
  '实行合理的轮作制度，避免连作导致土传病害积累',
  '播种前进行种子消毒处理，杀灭种传病原菌',
  '加强田间管理，及时清除杂草和病残体',
  '关注天气预报，在病害高发期前7-10天进行预防性施药',
  '合理施肥，增施有机肥和磷钾肥，控制氮肥用量',
  '保持合理的种植密度，确保田间通风透光',
]

async function generateTreatment() {
  if (!formData.value.disease || !formData.value.severity || !formData.value.crop) {
    alert('请填写完整的病害信息')
    return
  }

  isGenerating.value = true
  errorMsg.value = ''

  try {
    const res = await api.post('/treatment/generate', {
      disease_name: formData.value.disease,
      severity: formData.value.severity,
      crop_type: formData.value.crop,
    })

    const data = res.data
    const severityIdx = severityOptions.findIndex(s => s.value === formData.value.severity)

    result.value = {
      disease: data.disease || formData.value.disease,
      severity: data.severity || formData.value.severity,
      severityColor: severityOptions[severityIdx]?.color || '#ff9800',
      crop: formData.value.crop,
      timestamp: new Date().toLocaleString('zh-CN'),
      medicines: (data.recommendations?.pesticides || []).map((p: any) => ({
        name: p.name,
        usage: p.method || '叶面喷施',
        dosage: p.concentration || '按说明使用',
        adjustedDosage: p.concentration || '按说明使用',
        frequency: '每7-14天一次',
        precautions: '按推荐剂量使用，注意安全间隔期',
      })),
      farmingAdvices,
      preventionTips,
      safetyInterval: data.recommendations?.safety_interval || '7天',
      aiInsights: data.ai_insights || [],
      aiAnalysis: (data.ai_insights || []).join('；') || `根据AI综合分析，${formData.value.crop}病害目前处于${formData.value.severity}阶段。建议立即采取综合防治措施。`,
      weatherAnalysis: data.weather_analysis,
      environmentAnalysis: data.environment_analysis,
    }
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '方案生成失败，请重试'
  } finally {
    isGenerating.value = false
  }
}

function resetForm() {
  formData.value = { disease: '', severity: '', crop: '' }
  result.value = null
  errorMsg.value = ''
  streamContent.value = ''
}

async function generateStream() {
  if (!formData.value.disease || !formData.value.severity || !formData.value.crop) {
    alert('请填写完整的病害信息')
    return
  }
  isGenerating.value = true
  errorMsg.value = ''
  streamContent.value = ''

  try {
    const res = await fetch('/api/treatment/generate/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({
        disease_name: formData.value.disease,
        severity: formData.value.severity,
        crop_type: formData.value.crop,
      })
    })

    const reader = res.body?.getReader()
    const decoder = new TextDecoder()

    while (reader) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value)
      const lines = text.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'text') {
            streamContent.value += data.content
          }
        }
      }
    }
  } catch (e: any) {
    errorMsg.value = '流式生成失败: ' + (e.message || '未知错误')
  } finally {
    isGenerating.value = false
  }
}

function toggleStreamMode() {
  streamMode.value = !streamMode.value
  streamContent.value = ''
  result.value = null
}
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>防治方案</h2>
      <p>基于AI智能分析，为您生成个性化的病害防治方案</p>
    </div>

    <div style="display:grid;grid-template-columns:40% 60%;gap:20px;">
      <div class="glass animate-slide-left">
        <h3 style="font-weight:700;margin-bottom:20px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>病害信息</h3>

        <div class="form-group">
          <label class="form-label">病害类型 <span class="required">*</span></label>
          <select v-model="formData.disease" class="form-select">
            <option value="">请选择病害类型</option>
            <option v-for="opt in diseaseOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">严重程度 <span class="required">*</span></label>
          <select v-model="formData.severity" class="form-select">
            <option value="">请选择严重程度</option>
            <option v-for="opt in severityOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
          <div v-if="formData.severity" style="display:flex;gap:4px;margin-top:6px;">
            <span
              v-for="opt in severityOptions"
              :key="opt.value"
              style="padding:2px 10px;border-radius:10px;font-size:0.72rem;font-weight:600;"
              :style="{
                background: formData.severity === opt.value ? opt.color : 'transparent',
                color: formData.severity === opt.value ? '#fff' : 'rgba(255,255,255,0.4)',
                border: `1px solid ${formData.severity === opt.value ? opt.color : 'rgba(255,255,255,0.1)'}`,
              }"
            >
              {{ opt.label.split(' / ')[0] }}
            </span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">作物种类 <span class="required">*</span></label>
          <select v-model="formData.crop" class="form-select">
            <option value="">请选择作物种类</option>
            <option v-for="opt in cropOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>

        <div style="display:flex;gap:12px;align-items:center;margin-bottom:16px;">
          <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:0.82rem;color:var(--text-secondary);">
            <input type="checkbox" v-model="streamMode" @change="toggleStreamMode" style="accent-color:#4caf50;" />
            流式AI生成
          </label>
          <span v-if="streamMode" style="font-size:0.72rem;color:#4caf50;background:rgba(76,175,80,0.1);padding:2px 10px;border-radius:10px;">打字机效果</span>
        </div>

        <div v-if="errorMsg" style="padding:10px 14px;background:rgba(244,67,54,0.1);border-radius:8px;color:#f44336;font-size:0.85rem;margin-bottom:12px;">
          {{ errorMsg }}
        </div>

        <div style="display:flex;gap:12px;">
          <button @click="streamMode ? generateStream() : generateTreatment()" :disabled="isGenerating" class="btn btn-primary btn-lg" style="flex:1;">
            {{ isGenerating ? (streamMode ? 'AI流式生成中...' : '正在生成...') : (streamMode ? 'AI流式生成方案' : '生成防治方案') }}
          </button>
          <button @click="resetForm" class="btn btn-outline">重置</button>
        </div>
      </div>

      <div class="animate-slide-right">
        <div v-if="isGenerating" class="glass text-center" style="padding:60px 32px;">
          <div style="width:50px;height:50px;border:3px solid rgba(255,255,255,0.1);border-top-color:#4caf50;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px;"></div>
          <p style="font-weight:600;">正在基于AI生成个性化防治方案...</p>
          <p style="font-size:0.85rem;color:var(--text-tertiary);margin-top:6px;">综合分析病害特征和防治经验</p>
        </div>

        <div v-else-if="streamContent" class="space-y-4">
          <div class="glass" style="background:linear-gradient(135deg,rgba(46,125,50,0.6),rgba(76,175,80,0.4));padding:20px 24px;">
            <h3 style="font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>AI流式防治方案</h3>
            <div style="background:rgba(0,0,0,0.15);border-radius:12px;padding:16px;max-height:500px;overflow-y:auto;">
              <StreamingText :text="streamContent" :speed="20" markdown />
            </div>
          </div>
        </div>

        <div v-else-if="result" class="space-y-4">
          <div class="glass" style="background:linear-gradient(135deg,rgba(46,125,50,0.6),rgba(76,175,80,0.4));padding:20px 24px;">
            <h3 style="font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>防治方案已生成</h3>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;text-align:center;">
              <div>
                <p style="font-size:0.72rem;opacity:0.7;">病害类型</p>
                <p style="font-weight:700;">{{ result.disease }}</p>
              </div>
              <div>
                <p style="font-size:0.72rem;opacity:0.7;">严重程度</p>
                <p style="font-weight:700;" :style="{color:result.severityColor}">{{ result.severity }}</p>
              </div>
              <div>
                <p style="font-size:0.72rem;opacity:0.7;">作物种类</p>
                <p style="font-weight:700;">{{ result.crop }}</p>
              </div>
            </div>
          </div>

          <div v-if="result.medicines.length > 0" class="glass">
            <h3 style="font-weight:700;margin-bottom:14px;font-size:1rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>推荐药剂</h3>
            <div class="space-y-3">
              <div v-for="(med, idx) in result.medicines" :key="idx" class="section-card" style="padding:16px 18px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                  <h4 style="font-weight:700;">{{ med.name }}</h4>
                  <span class="tag tag-info">{{ med.usage }}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.82rem;color:var(--text-secondary);">
                  <div>用量：<strong>{{ med.adjustedDosage || med.dosage }}</strong></div>
                  <div>频率：<strong>{{ med.frequency }}</strong></div>
                </div>
                <p style="margin-top:8px;font-size:0.76rem;color:#ff9800;background:rgba(255,152,0,0.1);padding:6px 10px;border-radius:8px;">
                  <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="flex-shrink:0;margin-top:2px;"><path d="M12 2L2 22h20L12 2z"/><path d="M12 14v4"/><circle cx="12" cy="16.5" r="0.5" fill="currentColor"/></svg> {{ med.precautions }}
                </p>
              </div>
            </div>
          </div>

          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:14px;font-size:1rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>农事管理建议</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
              <div v-for="(advice, idx) in result.farmingAdvices" :key="idx" class="section-card" style="padding:12px;display:flex;align-items:flex-start;gap:10px;">
                <div style="flex-shrink:0;width:28px;height:28px;display:flex;align-items:center;justify-content:center;">
                  <svg v-if="advice.icon === 'leaf'" width="22" height="22" fill="none" stroke="#4caf50" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12c0 5.5 4.5 10 10 10"/><path d="M12 2c5.5 0 10 4.5 10 10"/><path d="M12 14a2 2 0 100-4 2 2 0 000 4z"/></svg>
                  <svg v-else-if="advice.icon === 'wind'" width="22" height="22" fill="none" stroke="#2196f3" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.59 4.59A2 2 0 1111 8H2m10.59 11.41A2 2 0 1014 16H2m15.73-8.27A2.5 2.5 0 1119.5 12H2"/></svg>
                  <svg v-else-if="advice.icon === 'water'" width="22" height="22" fill="none" stroke="#03a9f4" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z"/></svg>
                  <svg v-else-if="advice.icon === 'sprout'" width="22" height="22" fill="none" stroke="#ff9800" stroke-width="1.5" viewBox="0 0 24 24"><path d="M7 17h10"/><path d="M12 7v10"/><circle cx="12" cy="5" r="3"/></svg>
                  <svg v-else-if="advice.icon === 'cycle'" width="22" height="22" fill="none" stroke="#9c27b0" stroke-width="1.5" viewBox="0 0 24 24"><polyline points="1 4 1 10 7 10"/><path d="M3.5 17.5A9 9 0 102 12"/></svg>
                  <svg v-else-if="advice.icon === 'flask'" width="22" height="22" fill="none" stroke="#e91e63" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 3h6M10 3v4.5L6 19.1A2 2 0 007.8 22h8.4a2 2 0 001.8-2.9L14 7.5V3"/></svg>
                </div>
                <div>
                  <h4 style="font-weight:600;font-size:0.85rem;margin-bottom:2px;">{{ advice.title }}</h4>
                  <p style="font-size:0.75rem;color:var(--text-secondary);line-height:1.4;">{{ advice.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:12px;font-size:1rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5z"/><path d="M14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z"/></svg>AI智能分析</h3>
            <p style="font-size:0.88rem;color:rgba(255,255,255,0.7);line-height:1.7;">{{ result.aiAnalysis }}</p>
            <div v-if="result.safetyInterval" style="margin-top:12px;padding:12px 16px;background:rgba(76,175,80,0.1);border-radius:10px;border:1px solid rgba(76,175,80,0.2);">
              <span style="font-weight:600;color:#4caf50;display:inline-flex;align-items:center;gap:4px;"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>安全间隔期：</span>
              <span>收前{{ result.safetyInterval }}</span>
            </div>
          </div>

          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:12px;font-size:1rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>预防措施</h3>
            <div class="space-y-2">
              <div v-for="(tip, idx) in result.preventionTips" :key="idx" style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;">
                <span style="color:#4caf50;font-weight:700;flex-shrink:0;">✓</span>
                <span style="font-size:0.85rem;color:var(--text-secondary);">{{ tip }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="glass text-center" style="padding:80px 32px;">
          <div style="margin-bottom:16px;opacity:0.3;"><svg width="64" height="64" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path d="M9 3h6M10 3v4.5L6 19.1A2 2 0 007.8 22h8.4a2 2 0 001.8-2.9L14 7.5V3"/></svg></div>
          <p style="font-weight:600;font-size:1.05rem;">选择病害信息后生成方案</p>
          <p style="color:var(--text-tertiary);font-size:0.85rem;margin-top:8px;line-height:1.6;">
            请选择病害类型、严重程度和作物种类<br>系统将为您生成个性化的防治方案
          </p>
        </div>
      </div>
    </div>
  </div>
</template>