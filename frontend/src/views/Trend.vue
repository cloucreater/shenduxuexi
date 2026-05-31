<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const selectedCrop = ref('番茄')
const cropOptions = ['番茄', '黄瓜', '辣椒', '土豆', '小麦', '水稻']

const isLoading = ref(false)
const forecastDays = ref<string[]>([])
const trendValues = ref<number[]>([])

const diseaseConfig: Record<string, { name: string; color: string; baseline: number }> = {
  '叶斑病': { name: '叶斑病', color: '#f44336', baseline: 30 },
  '白粉病': { name: '白粉病', color: '#ff9800', baseline: 22 },
  '锈病': { name: '锈病', color: '#ff5722', baseline: 14 },
  '早疫病': { name: '早疫病', color: '#2196f3', baseline: 10 },
}

const dailyRisks = ref<any[]>([])

function computeDailyRisks(dates: string[], values: number[]) {
  const maxVal = Math.max(...values, 1)
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

  dailyRisks.value = dates.map((date, i) => {
    const val = values[i] || 0
    const ratio = val / maxVal
    let riskLevel: number, risk: string, color: string
    if (ratio >= 0.7) { riskLevel = 3; risk = '高'; color = '#f44336' }
    else if (ratio >= 0.3) { riskLevel = 2; risk = '中'; color = '#ff9800' }
    else { riskLevel = 1; risk = '低'; color = '#4caf50' }

    const now = new Date()
    const d = new Date(now.getFullYear(), parseInt(date.split('-')[0]) - 1, parseInt(date.split('-')[1]))
    const weekday = weekdays[d.getDay()] || ''

    return {
      day: date, weekday, risk, riskLevel,
      desc: riskLevel === 3 ? '病害高发，需重点关注' : riskLevel === 2 ? '注意监测，保持预防' : '风险较低，常规管理',
      color,
    }
  })
}

async function loadTrendData() {
  isLoading.value = true
  try {
    const res = await api.get('/dashboard/trend')
    forecastDays.value = res.data.dates || []
    trendValues.value = res.data.values || []
    computeDailyRisks(forecastDays.value, trendValues.value)
  } catch {
    forecastDays.value = []
    trendValues.value = []
  } finally {
    isLoading.value = false
    setTimeout(renderForecastChart, 200)
  }
}

let forecastChart: echarts.ECharts | null = null

function renderForecastChart() {
  const el = document.getElementById('forecastChart')
  if (!el) return
  if (forecastChart) forecastChart.dispose()
  forecastChart = echarts.init(el)

  const dates = forecastDays.value.length > 0 ? forecastDays.value : ['暂无数据']
  const maxVal = Math.max(...trendValues.value, 1)

  const diseaseNames = Object.keys(diseaseConfig)
  const seriesData = diseaseNames.map(name => {
    const cfg = diseaseConfig[name]
    const risk = dates.map((_, i) => {
      const val = trendValues.value[i] || 0
      const ratio = val / maxVal
      return Math.min(5, Math.round(ratio * cfg.baseline / 20) + 1)
    })
    const { name: _cfgName, ...restCfg } = cfg
    return { name, risk, ...restCfg }
  })

  forecastChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff', fontSize: 13 },
    },
    legend: {
      data: diseaseNames,
      bottom: 0,
      textStyle: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
    },
    grid: { left: 48, right: 20, bottom: 40, top: 20 },
    xAxis: {
      type: 'category', data: dates,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
    },
    yAxis: {
      type: 'value', name: '风险指数',
      nameTextStyle: { color: 'rgba(255,255,255,0.4)', fontSize: 11 },
      axisLine: { show: false }, axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
      min: 0, max: 6,
    },
    series: seriesData.map(s => ({
      name: s.name, type: 'line', smooth: true,
      data: s.risk,
      symbol: 'circle', symbolSize: 6,
      lineStyle: { color: s.color, width: 2.5 },
      itemStyle: { color: s.color },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: s.color + '30' },
          { offset: 1, color: s.color + '00' },
        ])
      },
    }))
  })
}

const preventionAdvices = [
  { title: '叶斑病防控', desc: '提前喷施代森锰锌预防，发病初期使用多菌灵治疗。注意排水防涝，降低田间湿度。', icon: 'leaf', color: '#f44336' },
  { title: '白粉病防控', desc: '保持田间通风透光，使用硫磺制剂进行预防性喷施。增施磷钾肥提高植株抗性。', icon: 'sprout', color: '#ff9800' },
  { title: '锈病防控', desc: '选用抗锈病品种，发病初期喷施三唑酮。及时清除田间病残体，减少菌源。', icon: 'bacteria', color: '#ff5722' },
]

onMounted(() => {
  loadTrendData()
  window.addEventListener('resize', () => forecastChart?.resize())
})

onUnmounted(() => { forecastChart?.dispose() })
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>趋势预测</h2>
      <p>基于历史数据和气象信息，预测未来7天病害发生趋势</p>
    </div>

    <div class="glass animate-fade-up">
      <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-weight:600;white-space:nowrap;display:inline-flex;align-items:center;gap:6px;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>选择作物：</span>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button
            v-for="crop in cropOptions" :key="crop"
            :class="['btn', selectedCrop === crop ? 'btn-primary' : 'btn-outline', 'btn-sm']"
            @click="selectedCrop = crop"
          >
            {{ crop }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="glass text-center" style="padding:48px;">
      <div style="width:40px;height:40px;border:3px solid rgba(255,255,255,0.1);border-top-color:#4caf50;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px;"></div>
      <p style="color:var(--text-secondary);">正在加载趋势数据...</p>
    </div>

    <template v-else>
      <div class="glass animate-fade-up stagger-1">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>{{ selectedCrop }}近7天病害风险预测
        </h3>
        <div id="forecastChart" class="chart-container" style="height:340px;"></div>
        <div v-if="forecastDays.length === 0" style="text-align:center;padding:32px;color:var(--text-muted);">
          暂无检测数据，完成检测后可查看趋势分析
        </div>
      </div>

      <div class="glass animate-fade-up stagger-2">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>每日风险等级</h3>
        <div v-if="dailyRisks.length > 0" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;">
          <div
            v-for="day in dailyRisks" :key="day.day"
            class="section-card text-center"
            style="padding:18px 14px;"
          >
            <p style="font-size:0.85rem;font-weight:600;">{{ day.day }}</p>
            <p style="font-size:0.75rem;color:var(--text-muted);">{{ day.weekday }}</p>
            <div
              style="width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:10px auto;font-weight:800;font-size:1rem;"
              :style="{background:day.riskLevel===3?'rgba(244,67,54,0.2)':day.riskLevel===2?'rgba(255,152,0,0.2)':'rgba(76,175,80,0.2)',color:day.color}"
            >
              {{ day.risk }}
            </div>
            <p style="font-size:0.75rem;color:var(--text-secondary);line-height:1.4;">{{ day.desc }}</p>
          </div>
        </div>
        <div v-else style="text-align:center;padding:32px;color:var(--text-muted);">
          暂无数据
        </div>
      </div>

      <div class="glass animate-fade-up stagger-3" style="background:linear-gradient(135deg,rgba(46,125,50,0.5),rgba(76,175,80,0.3));">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5z"/><path d="M14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z"/></svg>智能防治建议</h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;">
          <div
            v-for="advice in preventionAdvices" :key="advice.title"
            style="padding:18px;background:rgba(255,255,255,0.08);border-radius:14px;"
          >
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
              <span style="display:flex;align-items:center;">
                <svg v-if="advice.icon === 'leaf'" width="22" height="22" fill="none" stroke="#f44336" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12c0 5.5 4.5 10 10 10"/><path d="M12 2c5.5 0 10 4.5 10 10"/></svg>
                <svg v-else-if="advice.icon === 'sprout'" width="22" height="22" fill="none" stroke="#ff9800" stroke-width="1.5" viewBox="0 0 24 24"><path d="M7 17h10"/><path d="M12 7v10"/><circle cx="12" cy="5" r="3"/></svg>
                <svg v-else-if="advice.icon === 'bacteria'" width="22" height="22" fill="none" stroke="#ff5722" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M8 12h8M12 8v8"/></svg>
              </span>
              <h4 style="font-weight:700;">{{ advice.title }}</h4>
            </div>
            <p style="font-size:0.82rem;color:rgba(255,255,255,0.7);line-height:1.6;">{{ advice.desc }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
