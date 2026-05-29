<script setup lang="ts">
import { ref } from 'vue'

const formData = ref({ disease: '', severity: '', crop: '' })
const result = ref<any>(null)
const isGenerating = ref(false)

const diseaseOptions = [
  { value: '叶斑病', label: '叶斑病 / Leaf Spot' },
  { value: '锈病', label: '锈病 / Rust' },
  { value: '白粉病', label: '白粉病 / Powdery Mildew' },
  { value: '早疫病', label: '早疫病 / Early Blight' },
  { value: '晚疫病', label: '晚疫病 / Late Blight' },
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

const medicineDB: Record<string, any[]> = {
  '叶斑病': [
    { name: '多菌灵悬浮剂', usage: '叶面喷施', dosage: '稀释1000-1500倍', frequency: '每7-10天一次', precautions: '避免高温时段使用，建议早晨或傍晚施药' },
    { name: '百菌清可湿性粉剂', usage: '叶面喷施', dosage: '稀释600-800倍', frequency: '每10-15天一次', precautions: '与其他农药混用时需先进行兼容性试验' },
    { name: '代森锰锌可湿性粉剂', usage: '叶面喷施', dosage: '稀释500-700倍', frequency: '每7-10天一次', precautions: '不能与铜制剂或碱性农药混用' },
  ],
  '锈病': [
    { name: '三唑酮乳油', usage: '叶面喷施', dosage: '稀释800-1000倍', frequency: '每10-14天一次', precautions: '施药后6小时内遇雨应补喷' },
    { name: '戊唑醇悬浮剂', usage: '叶面喷施', dosage: '稀释2000-3000倍', frequency: '每10-15天一次', precautions: '不可与强碱性农药混用' },
    { name: '嘧菌酯水分散粒剂', usage: '叶面喷施', dosage: '稀释1500-2000倍', frequency: '每7-14天一次', precautions: '避免与乳油类农药混合使用' },
  ],
  '白粉病': [
    { name: '硫磺悬浮剂', usage: '叶面喷施', dosage: '稀释500-800倍', frequency: '每7天一次', precautions: '高温(>32℃)时禁止使用，避免药害' },
    { name: '氟硅唑乳油', usage: '叶面喷施', dosage: '稀释3000-5000倍', frequency: '每10-14天一次', precautions: '施药时注意防护，避免接触皮肤' },
    { name: '嘧菌酯+苯醚甲环唑', usage: '叶面喷施', dosage: '稀释1500倍', frequency: '每10-15天一次', precautions: '采收前7天停止用药' },
  ],
  '早疫病': [
    { name: '代森锌可湿性粉剂', usage: '叶面喷施', dosage: '稀释500-600倍', frequency: '每7-10天一次', precautions: '不能与铜制剂或碱性农药混用' },
    { name: '嘧菌酯悬浮剂', usage: '叶面喷施', dosage: '稀释1500-2000倍', frequency: '每10-14天一次', precautions: '每季最多使用3次' },
    { name: '霜脲·锰锌可湿性粉剂', usage: '叶面喷施', dosage: '稀释600-800倍', frequency: '每7-10天一次', precautions: '注意轮换用药，避免产生抗药性' },
  ],
  '晚疫病': [
    { name: '甲霜灵锰锌可湿性粉剂', usage: '叶面喷施', dosage: '稀释500-800倍', frequency: '每7-10天一次', precautions: '发病初期使用效果最佳' },
    { name: '霜霉威水剂', usage: '叶面喷施+灌根', dosage: '稀释600-800倍', frequency: '每7-10天一次', precautions: '灌根时注意用药量，避免药害' },
    { name: '烯酰吗啉悬浮剂', usage: '叶面喷施', dosage: '稀释1500-2000倍', frequency: '每10-14天一次', precautions: '不可与强碱性农药混用' },
  ],
}

const farmingAdvices = [
  { title: '及时清除病叶', desc: '发现病叶立即摘除，带出田外销毁，减少病原传播', icon: '🍂' },
  { title: '加强通风透光', desc: '合理密植，保持田间通风透光，降低田间湿度', icon: '💨' },
  { title: '控制灌溉方式', desc: '避免大水漫灌，采用滴灌或渗灌方式，保持土壤适度干燥', icon: '💧' },
  { title: '增施有机肥料', desc: '适当增施磷钾肥，提高植株抗病能力，避免偏施氮肥', icon: '🌱' },
  { title: '合理轮作制度', desc: '实行3年以上轮作，避免连作障碍加重病害', icon: '🔄' },
  { title: '种子消毒处理', desc: '播种前进行温汤浸种或药剂拌种，杀灭种子携带病菌', icon: '🧪' },
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
  await new Promise(resolve => setTimeout(resolve, 1200))

  const medicines = medicineDB[formData.value.disease] || medicineDB['叶斑病']
  const severityIndex = severityOptions.findIndex(s => s.value === formData.value.severity)
  const safetyInterval = ['7天', '10天', '14天'][severityIndex] || '7天'

  result.value = {
    disease: formData.value.disease,
    severity: formData.value.severity,
    severityColor: severityOptions[severityIndex]?.color || '#ff9800',
    crop: formData.value.crop,
    timestamp: new Date().toLocaleString('zh-CN'),
    medicines: medicines.map((m, _i) => ({
      ...m,
      adjustedDosage: severityIndex === 0 ? m.dosage : severityIndex === 1 ? m.dosage.replace('稀释', '浓').replace(/倍$/, '') + '（适当增加浓度）' : '加大浓度，' + m.dosage,
    })),
    farmingAdvices,
    preventionTips,
    safetyInterval,
    aiAnalysis: `根据AI综合分析，${formData.value.crop}${formData.value.disease}目前处于${formData.value.severity}阶段。建议立即采取综合防治措施：优先使用推荐药剂进行化学防治，同时结合农事管理措施进行综合防控。预计正确用药后${safetyInterval}可观察到明显效果。安全间隔期为收前${safetyInterval}。请严格按照推荐剂量使用，注意药剂轮换以避免抗药性产生。`,
  }

  isGenerating.value = false
}

function resetForm() {
  formData.value = { disease: '', severity: '', crop: '' }
  result.value = null
}
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>💊 防治方案</h2>
      <p>基于AI智能分析，为您生成个性化的病害防治方案</p>
    </div>

    <div style="display:grid;grid-template-columns:40% 60%;gap:20px;">
      <!-- Left: Form -->
      <div class="glass animate-slide-left">
        <h3 style="font-weight:700;margin-bottom:20px;font-size:1.05rem;">📝 病害信息</h3>

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
            <option v-for="opt in severityOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
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

        <div style="display:flex;gap:12px;">
          <button @click="generateTreatment" :disabled="isGenerating" class="btn btn-primary btn-lg" style="flex:1;">
            {{ isGenerating ? '⏳ 正在生成...' : '🧬 生成防治方案' }}
          </button>
          <button @click="resetForm" class="btn btn-outline">重置</button>
        </div>
      </div>

      <!-- Right: Results -->
      <div class="animate-slide-right">
        <!-- Loading -->
        <div v-if="isGenerating" class="glass text-center" style="padding:60px 32px;">
          <div style="width:50px;height:50px;border:3px solid rgba(255,255,255,0.1);border-top-color:#4caf50;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px;"></div>
          <p style="font-weight:600;">正在基于AI生成个性化防治方案...</p>
          <p style="font-size:0.85rem;color:var(--text-tertiary);margin-top:6px;">综合分析病害特征和防治经验</p>
        </div>

        <!-- Results -->
        <div v-else-if="result" class="space-y-4">
          <!-- Summary -->
          <div class="glass" style="background:linear-gradient(135deg,rgba(46,125,50,0.6),rgba(76,175,80,0.4));padding:20px 24px;">
            <h3 style="font-weight:700;margin-bottom:12px;">✅ 防治方案已生成</h3>
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

          <!-- Medicine Recommendations -->
          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:14px;font-size:1rem;">💊 推荐药剂</h3>
            <div class="space-y-3">
              <div v-for="(med, idx) in result.medicines" :key="idx" class="section-card" style="padding:16px 18px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                  <h4 style="font-weight:700;">{{ med.name }}</h4>
                  <span class="tag tag-info">{{ med.usage }}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.82rem;color:var(--text-secondary);">
                  <div>📏 用量：<strong style="color:#fff;">{{ med.adjustedDosage || med.dosage }}</strong></div>
                  <div>🕐 频率：<strong style="color:#fff;">{{ med.frequency }}</strong></div>
                </div>
                <p style="margin-top:8px;font-size:0.76rem;color:#ff9800;background:rgba(255,152,0,0.1);padding:6px 10px;border-radius:8px;">
                  ⚠️ {{ med.precautions }}
                </p>
              </div>
            </div>
          </div>

          <!-- Farming Advice -->
          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:14px;font-size:1rem;">🌱 农事管理建议</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
              <div v-for="(advice, idx) in result.farmingAdvices" :key="idx" class="section-card" style="padding:12px;display:flex;align-items:flex-start;gap:10px;">
                <div style="font-size:1.5rem;flex-shrink:0;">{{ advice.icon }}</div>
                <div>
                  <h4 style="font-weight:600;font-size:0.85rem;margin-bottom:2px;">{{ advice.title }}</h4>
                  <p style="font-size:0.75rem;color:var(--text-secondary);line-height:1.4;">{{ advice.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Analysis -->
          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:12px;font-size:1rem;">🧠 AI智能分析</h3>
            <p style="font-size:0.88rem;color:rgba(255,255,255,0.7);line-height:1.7;">{{ result.aiAnalysis }}</p>
            <div style="margin-top:12px;padding:12px 16px;background:rgba(76,175,80,0.1);border-radius:10px;border:1px solid rgba(76,175,80,0.2);">
              <span style="font-weight:600;color:#4caf50;">⏱ 安全间隔期：</span>
              <span style="color:rgba(255,255,255,0.7);">收前{{ result.safetyInterval }}</span>
            </div>
          </div>

          <!-- Prevention Tips -->
          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:12px;font-size:1rem;">🛡️ 预防措施</h3>
            <div class="space-y-2">
              <div v-for="(tip, idx) in result.preventionTips" :key="idx" style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;">
                <span style="color:#4caf50;font-weight:700;flex-shrink:0;">✓</span>
                <span style="font-size:0.85rem;color:var(--text-secondary);">{{ tip }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="glass text-center" style="padding:80px 32px;">
          <div style="font-size:4rem;margin-bottom:16px;">🧪</div>
          <p style="font-weight:600;font-size:1.05rem;">选择病害信息后生成方案</p>
          <p style="color:var(--text-tertiary);font-size:0.85rem;margin-top:8px;line-height:1.6;">
            请选择病害类型、严重程度和作物种类<br>系统将为您生成个性化的防治方案
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
