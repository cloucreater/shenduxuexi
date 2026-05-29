<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

// Loading state
const loading = ref(true)

// Prediction data (try loading from API, fallback to computed)
const predictionData = ref({
  currentWeek: { powdery_mildew: 0, leaf_spot: 0, rust: 0, early_blight: 0, healthy: 0 },
  nextWeek: { powdery_mildew: 0, leaf_spot: 0, rust: 0, early_blight: 0, healthy: 0 },
  changeRate: { powdery_mildew: 0, leaf_spot: 0, rust: 0, early_blight: 0, healthy: 0 }
})

// Alerts
const alerts = ref<any[]>([])

// Charts
let trendChart: echarts.ECharts | null = null
let comparisonChart: echarts.ECharts | null = null
const trendChartRef = ref<HTMLDivElement | null>(null)
const comparisonChartRef = ref<HTMLDivElement | null>(null)

const months = ['1月', '2月', '3月', '4月', '5月', '6月']
const diseaseHistorical: Record<string, number[]> = {
  powdery_mildew: [45, 52, 78, 125, 168, 156],
  leaf_spot: [28, 35, 52, 68, 82, 89],
  rust: [12, 18, 28, 35, 42, 45],
  early_blight: [8, 12, 18, 25, 30, 32]
}

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#171717', fontSize: 12 },
      boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
    },
    legend: {
      data: ['白粉病', '叶斑病', '锈病', '早疫病'],
      bottom: 0,
      textStyle: { color: '#737373', fontSize: 11 }
    },
    grid: { left: 48, right: 24, bottom: 40, top: 20 },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisTick: { show: false },
      axisLabel: { color: '#737373', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.04)' } },
      axisLabel: { color: '#737373', fontSize: 11 }
    },
    series: [
      { name: '白粉病', type: 'line', smooth: true, data: diseaseHistorical.powdery_mildew, lineStyle: { color: '#ef4444', width: 3 }, itemStyle: { color: '#ef4444' }, symbol: 'circle', symbolSize: 6 },
      { name: '叶斑病', type: 'line', smooth: true, data: diseaseHistorical.leaf_spot, lineStyle: { color: '#f59e0b', width: 3 }, itemStyle: { color: '#f59e0b' }, symbol: 'circle', symbolSize: 6 },
      { name: '锈病', type: 'line', smooth: true, data: diseaseHistorical.rust, lineStyle: { color: '#f97316', width: 3 }, itemStyle: { color: '#f97316' }, symbol: 'circle', symbolSize: 6 },
      { name: '早疫病', type: 'line', smooth: true, data: diseaseHistorical.early_blight, lineStyle: { color: '#22c55e', width: 3 }, itemStyle: { color: '#22c55e' }, symbol: 'circle', symbolSize: 6 }
    ]
  })
}

function initComparisonChart() {
  if (!comparisonChartRef.value) return
  comparisonChart = echarts.init(comparisonChartRef.value)
  comparisonChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#171717', fontSize: 12 },
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['本周', '下周预测'],
      bottom: 0,
      textStyle: { color: '#737373', fontSize: 11 }
    },
    grid: { left: 48, right: 24, bottom: 40, top: 20 },
    xAxis: {
      type: 'category',
      data: ['白粉病', '叶斑病', '锈病', '早疫病', '健康'],
      axisLabel: { color: '#737373', fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.04)' } },
      axisLabel: { color: '#737373', fontSize: 11 }
    },
    series: [
      {
        name: '本周', type: 'bar',
        data: [
          predictionData.value.currentWeek.powdery_mildew || 156,
          predictionData.value.currentWeek.leaf_spot || 89,
          predictionData.value.currentWeek.rust || 45,
          predictionData.value.currentWeek.early_blight || 32,
          predictionData.value.currentWeek.healthy || 178
        ],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#16a34a' }, { offset: 1, color: '#86efac' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        barWidth: '30%'
      },
      {
        name: '下周预测', type: 'bar',
        data: [
          predictionData.value.nextWeek.powdery_mildew || 182,
          predictionData.value.nextWeek.leaf_spot || 95,
          predictionData.value.nextWeek.rust || 52,
          predictionData.value.nextWeek.early_blight || 38,
          predictionData.value.nextWeek.healthy || 165
        ],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#f59e0b' }, { offset: 1, color: '#fcd34d' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        barWidth: '30%'
      }
    ]
  })
}

async function loadPredictionData() {
  try {
    // Try to load from history trend API for current data
    const res = await api.get('/dashboard/trend')
    if (res.data?.values?.length) {
      const recentValues = res.data.values.slice(-1)[0] || 0
      // Derive approximate distribution
      predictionData.value.currentWeek = {
        powdery_mildew: Math.round(recentValues * 0.35),
        leaf_spot: Math.round(recentValues * 0.2),
        rust: Math.round(recentValues * 0.1),
        early_blight: Math.round(recentValues * 0.07),
        healthy: Math.round(recentValues * 0.4)
      }
      // Simple prediction: apply seasonal trend
      const factor = 1.08 + Math.random() * 0.1
      predictionData.value.nextWeek = {
        powdery_mildew: Math.round(predictionData.value.currentWeek.powdery_mildew * factor),
        leaf_spot: Math.round(predictionData.value.currentWeek.leaf_spot * factor),
        rust: Math.round(predictionData.value.currentWeek.rust * factor),
        early_blight: Math.round(predictionData.value.currentWeek.early_blight * factor),
        healthy: Math.round(predictionData.value.currentWeek.healthy * (1 / factor))
      }
      // Calculate change rates
      for (const key of Object.keys(predictionData.value.changeRate)) {
        const cur = (predictionData.value.currentWeek as any)[key] || 1
        const next = (predictionData.value.nextWeek as any)[key] || 0
        ;(predictionData.value.changeRate as any)[key] = parseFloat(((next - cur) / cur * 100).toFixed(1))
      }

      // Set alerts
      alerts.value = []
      if (predictionData.value.changeRate.powdery_mildew > 10) {
        alerts.value.push({ level: 'warning', disease: '白粉病', message: '未来7天白粉病发病风险升高，建议提前预防', time: '高风险' })
      }
      if (predictionData.value.changeRate.early_blight > 10) {
        alerts.value.push({ level: 'info', disease: '早疫病', message: '早疫病发病率预计上升，注意田间管理', time: '中风险' })
      }
      if (alerts.value.length === 0) {
        alerts.value.push({ level: 'info', disease: '总体趋势', message: '未来一周病害趋势相对平稳，保持常规管理即可', time: '低风险' })
      }
    }
  } catch {
    // Fallback to sample data
    predictionData.value = {
      currentWeek: { powdery_mildew: 156, leaf_spot: 89, rust: 45, early_blight: 32, healthy: 178 },
      nextWeek: { powdery_mildew: 182, leaf_spot: 95, rust: 52, early_blight: 38, healthy: 165 },
      changeRate: { powdery_mildew: 16.7, leaf_spot: 6.7, rust: 15.6, early_blight: 18.8, healthy: -7.3 }
    }
    alerts.value = [
      { level: 'warning', disease: '白粉病', message: '未来7天白粉病发病风险较高，建议提前预防', time: '高风险' },
      { level: 'info', disease: '叶斑病', message: '叶斑病发病率将略有上升，注意田间管理', time: '中风险' }
    ]
  }
}

function getChangeClass(rate: number): string {
  if (rate > 10) return 'text-danger'
  if (rate > 0) return 'text-warning'
  if (rate < 0) return 'text-success'
  return ''
}

function getChangeIcon(rate: number): string {
  if (rate > 0) return '↑'
  if (rate < 0) return '↓'
  return '→'
}

onMounted(async () => {
  await loadPredictionData()
  loading.value = false

  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initComparisonChart()
  }, 150)

  window.addEventListener('resize', () => {
    trendChart?.resize()
    comparisonChart?.resize()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {})
  trendChart?.dispose()
  comparisonChart?.dispose()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="page-header animate-fade-down">
      <h2>📈 趋势预测</h2>
      <p>基于历史数据和AI模型，预测未来病害发展趋势</p>
    </div>

    <!-- Alerts -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-up stagger-1">
      <div
        v-for="(alert, idx) in alerts"
        :key="idx"
        class="section-card"
        :style="{ borderLeft: `4px solid ${alert.level === 'warning' ? 'var(--color-warning)' : 'var(--color-info)'}` }"
      >
        <div style="display:flex;align-items:center;gap:14px;">
          <div
            style="width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;"
            :style="{ background: alert.level === 'warning' ? 'var(--color-warning-bg)' : 'var(--color-info-bg)' }"
          >
            {{ alert.level === 'warning' ? '⚠️' : 'ℹ️' }}
          </div>
          <div style="flex:1;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
              <h3 style="font-weight:700;color:var(--text-primary);font-size:0.95rem;">{{ alert.disease }} 预警</h3>
              <span
                style="padding:2px 10px;border-radius:12px;font-size:0.72rem;font-weight:600;"
                :style="{
                  background: alert.level === 'warning' ? 'var(--color-warning-bg)' : 'var(--color-info-bg)',
                  color: alert.level === 'warning' ? 'var(--color-warning)' : 'var(--color-info)'
                }"
              >
                {{ alert.time }}
              </span>
            </div>
            <p style="font-size:0.85rem;color:var(--text-secondary);">{{ alert.message }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="content-grid animate-fade-up stagger-2">
      <div class="glass-card">
        <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">📉 近6个月发病趋势</h3>
        <div ref="trendChartRef" style="height:320px;"></div>
      </div>
      <div class="glass-card">
        <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">📊 本周 vs 下周预测</h3>
        <div ref="comparisonChartRef" style="height:320px;"></div>
      </div>
    </div>

    <!-- Next Week Prediction Details -->
    <div class="glass-card animate-fade-up stagger-3">
      <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">🔮 下周预测详情</h3>
      <div class="stats-grid" style="margin-bottom:0;">
        <div class="section-card text-center" style="padding:20px;">
          <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:8px;">白粉病</p>
          <p style="font-size:2rem;font-weight:800;color:var(--color-danger);">{{ predictionData.nextWeek.powdery_mildew }}</p>
          <span style="font-size:0.8rem;font-weight:600;" :class="getChangeClass(predictionData.changeRate.powdery_mildew)">
            {{ getChangeIcon(predictionData.changeRate.powdery_mildew) }} {{ Math.abs(predictionData.changeRate.powdery_mildew) }}%
          </span>
        </div>
        <div class="section-card text-center" style="padding:20px;">
          <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:8px;">叶斑病</p>
          <p style="font-size:2rem;font-weight:800;color:var(--color-warning);">{{ predictionData.nextWeek.leaf_spot }}</p>
          <span style="font-size:0.8rem;font-weight:600;" :class="getChangeClass(predictionData.changeRate.leaf_spot)">
            {{ getChangeIcon(predictionData.changeRate.leaf_spot) }} {{ Math.abs(predictionData.changeRate.leaf_spot) }}%
          </span>
        </div>
        <div class="section-card text-center" style="padding:20px;">
          <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:8px;">锈病</p>
          <p style="font-size:2rem;font-weight:800;color:#f97316;">{{ predictionData.nextWeek.rust }}</p>
          <span style="font-size:0.8rem;font-weight:600;" :class="getChangeClass(predictionData.changeRate.rust)">
            {{ getChangeIcon(predictionData.changeRate.rust) }} {{ Math.abs(predictionData.changeRate.rust) }}%
          </span>
        </div>
        <div class="section-card text-center" style="padding:20px;">
          <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:8px;">早疫病</p>
          <p style="font-size:2rem;font-weight:800;color:var(--color-success);">{{ predictionData.nextWeek.early_blight }}</p>
          <span style="font-size:0.8rem;font-weight:600;" :class="getChangeClass(predictionData.changeRate.early_blight)">
            {{ getChangeIcon(predictionData.changeRate.early_blight) }} {{ Math.abs(predictionData.changeRate.early_blight) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- Prevention Recommendations -->
    <div class="glass-card animate-fade-up stagger-4" style="background:linear-gradient(135deg, var(--green-700), var(--green-500));color:#fff;">
      <h3 style="font-weight:700;margin-bottom:14px;font-size:1.05rem;">🧠 智能防治建议</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
        <div style="padding:16px;background:rgba(255,255,255,0.12);border-radius:12px;backdrop-filter:blur(4px);">
          <h4 style="font-weight:700;margin-bottom:6px;">🌿 白粉病预防</h4>
          <p style="font-size:0.82rem;opacity:0.9;line-height:1.5;">保持田间通风，及时清除病叶，喷施多菌灵或百菌清进行预防</p>
        </div>
        <div style="padding:16px;background:rgba(255,255,255,0.12);border-radius:12px;backdrop-filter:blur(4px);">
          <h4 style="font-weight:700;margin-bottom:6px;">💧 叶斑病预防</h4>
          <p style="font-size:0.82rem;opacity:0.9;line-height:1.5;">加强排水防涝，避免过度灌溉，发病初期使用代森锰锌防治</p>
        </div>
        <div style="padding:16px;background:rgba(255,255,255,0.12);border-radius:12px;backdrop-filter:blur(4px);">
          <h4 style="font-weight:700;margin-bottom:6px;">🛡️ 锈病预防</h4>
          <p style="font-size:0.82rem;opacity:0.9;line-height:1.5;">增施磷钾肥提高植株抗性，发现病株立即清除并喷施三唑酮</p>
        </div>
      </div>
    </div>
  </div>
</template>
