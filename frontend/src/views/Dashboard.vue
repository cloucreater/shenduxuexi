<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import * as echarts from 'echarts'

const router = useRouter()
const authStore = useAuthStore()

const currentTime = ref('')
const isLoading = ref(false)
let clockTimer: ReturnType<typeof setInterval>

// Real data from API
const statsData = ref<any>(null)
const trendData = ref<{ dates: string[]; values: number[] }>({ dates: [], values: [] })

const kpiStats = computed(() => {
  const s = statsData.value
  if (!s) return [
    { label: '今日检测次数', value: '—', icon: 'search', change: '加载中', changeType: 'up', bg: 'rgba(76,175,80,0.15)' },
    { label: '模型状态', value: '—', icon: 'brain', change: '加载中', changeType: 'up', bg: 'rgba(33,150,243,0.15)' },
    { label: '首要病害', value: '—', icon: 'alert', change: '加载中', changeType: 'neutral', bg: 'rgba(255,152,0,0.15)' },
    { label: '病害率', value: '—', icon: 'chart', change: '加载中', changeType: 'down', bg: 'rgba(244,67,54,0.15)' },
  ]
  return [
    { label: '今日检测次数', value: s.todayDetectCount, icon: 'search', change: '实时', changeType: 'up', bg: 'rgba(76,175,80,0.15)' },
    { label: '模型状态', value: s.modelStatus || '正常', icon: 'brain', change: '运行中', changeType: 'up', bg: 'rgba(33,150,243,0.15)' },
    { label: '首要病害', value: s.topDisease || '—', icon: 'alert', change: s.topDisease ? '主要' : '暂无', changeType: 'neutral', bg: 'rgba(255,152,0,0.15)' },
    { label: '病害率', value: `${s.diseaseRate || 0}%`, icon: 'chart', change: '统计', changeType: 'neutral', bg: 'rgba(244,67,54,0.15)' },
  ]
})

// Model info
const modelInfo = ref([
  { label: 'CNN准确率', value: '66.7%', icon: 'target', color: '#4caf50' },
  { label: 'R² Score', value: '0.977', icon: 'chart', color: '#2196f3' },
  { label: '训练数据', value: '5,802 张', icon: 'package', color: '#ff9800' },
  { label: '数据集划分', value: '7:1.5:1.5', icon: 'shuffle', color: '#9c27b0' },
])

let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

async function loadData() {
  isLoading.value = true
  try {
    const [statsRes, trendRes] = await Promise.all([
      api.get('/dashboard/stats'),
      api.get('/dashboard/trend')
    ])
    statsData.value = statsRes.data
    trendData.value = trendRes.data
  } catch {
    // Use fallback data
    statsData.value = { todayDetectCount: 0, modelStatus: '离线', topDisease: '无', diseaseRate: 0 }
    trendData.value = { dates: [], values: [] }
  } finally {
    isLoading.value = false
  }
}

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', weekday: 'long'
  })
}

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

function renderTrendChart() {
  const el = document.getElementById('trendChart')
  if (!el) return
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(el)

  const dates = trendData.value.dates.length > 0 ? trendData.value.dates : ['暂无数据']
  const values = trendData.value.values.length > 0 ? trendData.value.values : [0]

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 20, right: 20, bottom: 20, left: 45 },
    xAxis: {
      type: 'category', data: dates,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 }
    },
    yAxis: {
      type: 'value', name: '检测次数',
      nameTextStyle: { color: 'rgba(255,255,255,0.4)', fontSize: 11 },
      axisLine: { show: false }, axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 }
    },
    series: [{
      data: values, type: 'line', smooth: true,
      symbol: 'circle', symbolSize: 8,
      lineStyle: { color: '#66bb6a', width: 3, shadowBlur: 10, shadowColor: 'rgba(76,175,80,0.4)' },
      itemStyle: { color: '#66bb6a', borderColor: '#fff', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(76,175,80,0.25)' },
          { offset: 1, color: 'rgba(76,175,80,0)' }
        ])
      }
    }]
  })
}

function renderPieChart() {
  const el = document.getElementById('pieChart')
  if (!el) return
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(el)

  const data = [
    { name: '叶斑病', value: 32, color: '#f44336' },
    { name: '白粉病', value: 22, color: '#ff9800' },
    { name: '锈病', value: 18, color: '#ff5722' },
    { name: '早疫病', value: 14, color: '#2196f3' },
    { name: '晚疫病', value: 10, color: '#9c27b0' },
    { name: '健康', value: 4, color: '#4caf50' },
  ]

  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      bottom: 0,
      textStyle: { fontSize: 11, color: 'rgba(255,255,255,0.5)' },
      itemWidth: 10, itemHeight: 10, itemGap: 14
    },
    series: [{
      type: 'pie',
      radius: ['50%', '80%'],
      center: ['50%', '43%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: 'rgba(10,40,20,0.5)', borderWidth: 3 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' }, scaleSize: 8 },
      data: data.map(d => ({ name: d.name, value: d.value, itemStyle: { color: d.color } }))
    }]
  })
}

onMounted(async () => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)

  await loadData()
  setTimeout(() => {
    renderTrendChart()
    renderPieChart()
  }, 200)

  window.addEventListener('resize', () => {
    trendChart?.resize()
    pieChart?.resize()
  })
})

onUnmounted(() => {
  clearInterval(clockTimer)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<template>
  <div>
    <!-- Welcome Header -->
    <div class="page-header animate-fade-down">
      <h2>{{ greeting }}，{{ authStore.user?.username || '用户' }}</h2>
      <p>{{ currentTime }} · 智慧农业病害检测系统</p>
    </div>

    <!-- KPI Cards -->
    <div class="flex-card-row cols-4">
      <div
        v-for="(stat, idx) in kpiStats"
        :key="idx"
        class="glass stat-card animate-fade-up"
        :class="`stagger-${idx + 1}`"
      >
        <div class="stat-icon" :style="{ background: stat.bg }">
          <svg v-if="stat.icon === 'search'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <svg v-else-if="stat.icon === 'brain'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5z"/><path d="M14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z"/></svg>
          <svg v-else-if="stat.icon === 'alert'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <svg v-else-if="stat.icon === 'chart'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <span :class="['stat-change', stat.changeType]">{{ stat.change }}</span>
        </div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="content-grid mb-6">
      <div class="glass animate-fade-up stagger-2">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>近7天检测趋势</h3>
        <div id="trendChart" class="chart-container"></div>
      </div>
      <div class="glass animate-fade-up stagger-3">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>病害分布统计</h3>
        <div id="pieChart" class="chart-container"></div>
      </div>
    </div>

    <!-- Model Info Cards -->
    <div class="glass mb-6 animate-fade-up stagger-4">
      <h3 style="font-weight:700;margin-bottom:18px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5z"/><path d="M14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z"/></svg>模型信息</h3>
      <div class="flex-card-row cols-4" style="margin-bottom:0;">
        <div
          v-for="(info, idx) in modelInfo"
          :key="idx"
          class="section-card text-center"
          style="padding:18px 16px;"
        >
          <div style="margin-bottom:8px;display:flex;justify-content:center;">
            <svg v-if="info.icon === 'target'" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
            <svg v-else-if="info.icon === 'chart'" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="18" y="3" width="4" height="18"/><rect x="10" y="8" width="4" height="13"/><rect x="2" y="13" width="4" height="8"/></svg>
            <svg v-else-if="info.icon === 'package'" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
            <svg v-else-if="info.icon === 'shuffle'" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>
          </div>
          <div style="font-weight:800;font-size:1.3rem;color:var(--text-primary);">{{ info.value }}</div>
          <div style="font-size:0.8rem;color:var(--text-secondary);margin-top:4px;">{{ info.label }}</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="glass animate-fade-up stagger-5">
      <h3 style="font-weight:700;margin-bottom:18px;font-size:1.05rem;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>快捷操作</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <button class="btn btn-primary" @click="router.push('/image')">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
          图片检测
        </button>
        <button class="btn btn-outline" @click="router.push('/video')">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="4" width="16" height="16" rx="2"/><polygon points="22,7 18,10 18,14 22,17"/></svg>
          视频检测
        </button>
        <button class="btn btn-outline" @click="router.push('/treatment')">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L9 7l-5 1 4 4-1 5 5-2.5L17 17l-1-5 4-4-5-1-3-5z"/></svg>
          防治方案
        </button>
        <button class="btn btn-outline" @click="router.push('/evaluation')">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26"/></svg>
          效果评估
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flex-card-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}
/* 4 cards per row on desktop */
.flex-card-row.cols-4 > * {
  flex: 0 0 calc(25% - 9px);
}
.flex-card-row > .stat-card,
.flex-card-row > .section-card {
  min-width: 0;
}

.stat-card {
  height: 96px;
  padding: 12px 16px !important;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-card .stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.stat-card .stat-content {
  flex: 1;
  min-width: 0;
}

.stat-card .stat-value {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 2px;
}

.stat-card .stat-label {
  color: var(--text-secondary);
  font-size: 0.75rem;
  margin-top: 0;
}

.stat-card .stat-change {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.7rem;
  font-weight: 600;
  margin-top: 4px;
  padding: 2px 8px;
  border-radius: 12px;
}
.stat-change.up { color: var(--color-success); background: var(--color-success-bg); }
.stat-change.down { color: var(--color-danger); background: var(--color-danger-bg); }
.stat-change.neutral { color: var(--color-warning); background: var(--color-warning-bg); }

@media (max-width: 768px) {
  .flex-card-row {
    gap: 10px;
  }
  /* 2 per row on tablet */
  .flex-card-row.cols-4 > * {
    flex: 0 0 calc(50% - 5px);
  }
}

@media (max-width: 480px) {
  .flex-card-row.cols-4 > * {
    flex: 0 0 100%;
  }
}
</style>