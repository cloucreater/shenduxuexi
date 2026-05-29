<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const selectedCrop = ref('番茄')
const cropOptions = ['番茄', '黄瓜', '辣椒', '土豆', '小麦', '水稻']

// 7-day forecast
const forecastDays = ['5/30', '5/31', '6/1', '6/2', '6/3', '6/4', '6/5']

const diseaseConfig: Record<string, { name: string; color: string; risk: number[]; baseline: number }> = {
  '叶斑病': { name: '叶斑病', color: '#f44336', risk: [3, 4, 5, 4, 3, 2, 2], baseline: 30 },
  '白粉病': { name: '白粉病', color: '#ff9800', risk: [2, 2, 3, 4, 3, 2, 1], baseline: 22 },
  '锈病': { name: '锈病', color: '#ff5722', risk: [1, 2, 2, 3, 2, 1, 1], baseline: 14 },
  '早疫病': { name: '早疫病', color: '#2196f3', risk: [2, 1, 2, 2, 3, 2, 1], baseline: 10 },
}

const dailyRisks = ref([
  { day: '5/30', weekday: '周五', risk: '中', riskLevel: 2, desc: '温湿度适宜，需关注叶斑病', color: '#ff9800' },
  { day: '5/31', weekday: '周六', risk: '中', riskLevel: 2, desc: '湿度略升，白粉病风险增加', color: '#ff9800' },
  { day: '6/1', weekday: '周日', risk: '高', riskLevel: 3, desc: '预计降雨，叶斑病高发风险', color: '#f44336' },
  { day: '6/2', weekday: '周一', risk: '高', riskLevel: 3, desc: '持续高温高湿，多种病害风险', color: '#f44336' },
  { day: '6/3', weekday: '周二', risk: '中', riskLevel: 2, desc: '雨后转晴，注意锈病防控', color: '#ff9800' },
  { day: '6/4', weekday: '周三', risk: '低', riskLevel: 1, desc: '天气晴好，保持常规管理', color: '#4caf50' },
  { day: '6/5', weekday: '周四', risk: '低', riskLevel: 1, desc: '环境适宜，病害风险较低', color: '#4caf50' },
])

let forecastChart: echarts.ECharts | null = null

function renderForecastChart() {
  const el = document.getElementById('forecastChart')
  if (!el) return
  if (forecastChart) forecastChart.dispose()
  forecastChart = echarts.init(el)

  forecastChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff', fontSize: 13 },
    },
    legend: {
      data: Object.keys(diseaseConfig),
      bottom: 0,
      textStyle: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
    },
    grid: { left: 48, right: 20, bottom: 40, top: 20 },
    xAxis: {
      type: 'category', data: forecastDays,
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
    series: Object.entries(diseaseConfig).map(([name, cfg]) => ({
      name, type: 'line', smooth: true,
      data: cfg.risk,
      symbol: 'circle', symbolSize: 6,
      lineStyle: { color: cfg.color, width: 2.5 },
      itemStyle: { color: cfg.color },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: cfg.color + '30' },
          { offset: 1, color: cfg.color + '00' },
        ])
      },
    }))
  })
}

const preventionAdvices = [
  { title: '叶斑病防控', desc: '提前喷施代森锰锌预防，发病初期使用多菌灵治疗。注意排水防涝，降低田间湿度。', icon: '🍂', color: '#f44336' },
  { title: '白粉病防控', desc: '保持田间通风透光，使用硫磺制剂进行预防性喷施。增施磷钾肥提高植株抗性。', icon: '🌿', color: '#ff9800' },
  { title: '锈病防控', desc: '选用抗锈病品种，发病初期喷施三唑酮。及时清除田间病残体，减少菌源。', icon: '🦠', color: '#ff5722' },
]

onMounted(() => {
  setTimeout(renderForecastChart, 200)
  window.addEventListener('resize', () => forecastChart?.resize())
})

onUnmounted(() => { forecastChart?.dispose() })
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>📈 趋势预测</h2>
      <p>基于历史数据和气象信息，预测未来7天病害发生趋势</p>
    </div>

    <!-- Crop Select -->
    <div class="glass animate-fade-up">
      <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-weight:600;white-space:nowrap;">🌱 选择作物：</span>
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

    <!-- Forecast Chart -->
    <div class="glass animate-fade-up stagger-1">
      <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">
        📉 {{ selectedCrop }}未来7天病害风险预测
      </h3>
      <div id="forecastChart" class="chart-container" style="height:340px;"></div>
    </div>

    <!-- Daily Risk Cards -->
    <div class="glass animate-fade-up stagger-2">
      <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">📅 每日风险等级</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;">
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
    </div>

    <!-- Prevention Advices -->
    <div class="glass animate-fade-up stagger-3" style="background:linear-gradient(135deg,rgba(46,125,50,0.5),rgba(76,175,80,0.3));">
      <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">🧠 智能防治建议</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;">
        <div
          v-for="advice in preventionAdvices" :key="advice.title"
          style="padding:18px;background:rgba(255,255,255,0.08);border-radius:14px;"
        >
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <span style="font-size:1.5rem;">{{ advice.icon }}</span>
            <h4 style="font-weight:700;">{{ advice.title }}</h4>
          </div>
          <p style="font-size:0.82rem;color:rgba(255,255,255,0.7);line-height:1.6;">{{ advice.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
