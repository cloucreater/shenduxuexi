<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as echarts from 'echarts'

const router = useRouter()
const authStore = useAuthStore()

const currentTime = ref('')
let clockTimer: ReturnType<typeof setInterval>

// KPI stats
const kpiStats = ref([
  { label: '今日检测次数', value: 25, icon: '🔍', change: '+12%', changeType: 'up', bg: 'rgba(76,175,80,0.15)' },
  { label: '模型状态', value: '66.7%', icon: '🧠', change: '运行中', changeType: 'up', bg: 'rgba(33,150,243,0.15)' },
  { label: '首要病害', value: '叶斑病', icon: '⚠️', change: '高风险', changeType: 'neutral', bg: 'rgba(255,152,0,0.15)' },
  { label: '需关注病害', value: '晚疫病', icon: '📈', change: '上升趋势', changeType: 'down', bg: 'rgba(244,67,54,0.15)' },
])

// Model info
const modelInfo = ref([
  { label: 'CNN准确率', value: '66.7%', icon: '🎯', color: '#4caf50' },
  { label: 'R² Score', value: '0.977', icon: '📊', color: '#2196f3' },
  { label: '训练数据', value: '5,802 张', icon: '📦', color: '#ff9800' },
  { label: '数据集划分', value: '7:1.5:1.5', icon: '🔀', color: '#9c27b0' },
])

let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', weekday: 'long'
  })
}

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了 🌙'
  if (h < 9) return '早上好 ☀️'
  if (h < 12) return '上午好 🌤️'
  if (h < 14) return '中午好 ☀️'
  if (h < 18) return '下午好 🌿'
  return '晚上好 🌆'
})

function renderTrendChart() {
  const el = document.getElementById('trendChart')
  if (!el) return
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(el)

  const dates = ['05-23', '05-24', '05-25', '05-26', '05-27', '05-28', '05-29']
  const values = [8, 12, 15, 10, 18, 14, 25]

  trendChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff', fontSize: 13 },
      boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
    },
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

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)

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
          {{ stat.icon }}
        </div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
        <span :class="['stat-change', stat.changeType]">{{ stat.change }}</span>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="content-grid mb-6">
      <div class="glass animate-fade-up stagger-2">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">📈 近7天检测趋势</h3>
        <div id="trendChart" class="chart-container"></div>
      </div>
      <div class="glass animate-fade-up stagger-3">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">🍅 病害分布统计</h3>
        <div id="pieChart" class="chart-container"></div>
      </div>
    </div>

    <!-- Model Info Cards -->
    <div class="glass mb-6 animate-fade-up stagger-4">
      <h3 style="font-weight:700;margin-bottom:18px;font-size:1.05rem;">🧠 模型信息</h3>
      <div class="flex-card-row cols-4" style="margin-bottom:0;">
        <div
          v-for="(info, idx) in modelInfo"
          :key="idx"
          class="section-card text-center"
          style="padding:18px 16px;"
        >
          <div style="font-size:1.5rem;margin-bottom:8px;">{{ info.icon }}</div>
          <div style="font-weight:800;font-size:1.3rem;color:var(--text-primary);">{{ info.value }}</div>
          <div style="font-size:0.8rem;color:var(--text-secondary);margin-top:4px;">{{ info.label }}</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="glass animate-fade-up stagger-5">
      <h3 style="font-weight:700;margin-bottom:18px;font-size:1.05rem;">⚡ 快捷操作</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <button class="btn btn-primary" @click="router.push('/image')">
          📷 图片检测
        </button>
        <button class="btn btn-outline" @click="router.push('/video')">
          🎥 视频检测
        </button>
        <button class="btn btn-outline" @click="router.push('/treatment')">
          💊 防治方案
        </button>
        <button class="btn btn-outline" @click="router.push('/evaluation')">
          ⭐ 效果评估
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flex-card-row {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin-bottom: 24px;
}
/* 4 cards per row on desktop */
.flex-card-row.cols-4 > * {
  flex: 0 0 calc(25% - 13.5px);
}
.flex-card-row > .stat-card,
.flex-card-row > .section-card {
  min-width: 0;
}

@media (max-width: 768px) {
  .flex-card-row {
    gap: 12px;
  }
  /* 2 per row on tablet */
  .flex-card-row.cols-4 > * {
    flex: 0 0 calc(50% - 6px);
  }
}

@media (max-width: 480px) {
  .flex-card-row.cols-4 > * {
    flex: 0 0 100%;
  }
}
</style>
