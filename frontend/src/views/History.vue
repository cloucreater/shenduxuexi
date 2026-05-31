<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

// ── Types ──
interface HistoryRecord {
  id: string
  created_at: string
  result_image: string | null
  image_url: string | null
  detections: Array<{ label: string; label_en: string; confidence: number; bbox: number[] }>
  _diseaseLabel: string
  _diseaseCount: number
  _healthyCount: number
  _severity: string
  _imageUrl: string | null
  _date: string
}

// ── State ──
const historyRecords = ref<HistoryRecord[]>([])
const loading = ref(true)
const selectedRecords = ref<number[]>([])
const comparisonResult = ref<any>(null)
const comparing = ref(false)
const timeFilter = ref<'all' | 'today' | 'week' | 'month' | 'custom'>('all')
const customStart = ref('')
const customEnd = ref('')
const searchQuery = ref('')
const showExportMenu = ref(false)

// ── Charts ──
let comparisonChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let severityChart: echarts.ECharts | null = null

// ── Constants ──

const DISEASE_LABELS: Record<string, string> = {
  healthy: '健康', leaf_spot: '叶斑病', rust: '锈病',
  powdery_mildew: '白粉病', early_blight: '早疫病', late_blight: '晚疫病',
  bacterial_spot: '细菌性斑点病', leaf_mold: '叶霉病', septoria: '斑枯病',
  Bacterial_spot: '细菌性斑点病',
}

function getDisplayLabel(key: string): string {
  return DISEASE_LABELS[key] || key
}

function getSeverityColor(severity: string): string {
  const map: Record<string, string> = { '严重': '#f44336', '中等': '#ff9800', '轻度': '#2196f3', '健康': '#4caf50' }
  return map[severity] || '#888'
}

function getSeverityBg(severity: string): string {
  const map: Record<string, string> = { '严重': 'rgba(244,67,54,0.15)', '中等': 'rgba(255,152,0,0.15)', '轻度': 'rgba(33,150,243,0.15)', '健康': 'rgba(76,175,80,0.15)' }
  return map[severity] || 'rgba(255,255,255,0.05)'
}

function getEffectivenessTag(effectiveness: string) {
  const map: Record<string, { color: string; bg: string }> = {
    '有效': { color: '#4caf50', bg: 'rgba(76,175,80,0.15)' },
    '一般': { color: '#ff9800', bg: 'rgba(255,152,0,0.15)' },
    '无效': { color: '#f44336', bg: 'rgba(244,67,54,0.15)' },
    '持平': { color: '#2196f3', bg: 'rgba(33,150,243,0.15)' },
  }
  return map[effectiveness] || map['持平']
}

// ── Computed ──

const filteredRecords = computed(() => {
  let records = historyRecords.value

  // Time filter
  if (timeFilter.value === 'custom') {
    if (customStart.value && customEnd.value) {
      records = records.filter(r => {
        const d = r._date
        return d >= customStart.value && d <= customEnd.value
      })
    }
  } else if (timeFilter.value !== 'all') {
    const now = new Date()
    const start = timeFilter.value === 'today'
      ? new Date(now.getFullYear(), now.getMonth(), now.getDate())
      : timeFilter.value === 'week'
      ? new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      : new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
    records = records.filter(r => new Date(r._date) >= start)
  }

  // Search filter
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    records = records.filter(r =>
      r._diseaseLabel.toLowerCase().includes(q) ||
      getDisplayLabel(r._diseaseLabel).includes(q)
    )
  }

  return records
})

const canCompare = computed(() => selectedRecords.value.length === 2)

const trendPrediction = computed(() => {
  if (!comparisonResult.value?.changes) return null
  const cr = comparisonResult.value
  const changeRate = parseFloat(cr.changes.changePercent) || 0
  // Simple linear projection for next period
  const current = cr.record2.diseaseCount
  const predicted = Math.max(0, Math.round(current * (1 + changeRate / 100)))
  const direction = changeRate > 0 ? '上升' : changeRate < 0 ? '下降' : '持平'
  const riskLevel = changeRate > 30 ? '高风险' : changeRate > 10 ? '中风险' : changeRate < -10 ? '改善' : '稳定'

  return {
    predicted,
    direction,
    riskLevel,
    suggestion: changeRate > 20
      ? '病害呈显著上升趋势，建议立即采取综合防治措施'
      : changeRate > 0
      ? '病害有轻微上升趋势，建议加强监测并预防性施药'
      : changeRate < -20
      ? '防治效果显著，建议维持当前方案并定期监测'
      : changeRate < 0
      ? '病害有所下降，继续观察即可'
      : '病害无明显变化，建议优化防治策略',
  }
})

// ── API ──

async function loadHistory() {
  loading.value = true
  try {
    const res = await api.get('/history', { params: { limit: 50 } })
    const records = res.data.records || []
    historyRecords.value = records.map((r: any) => {
      const diseaseDetections = (r.detections || []).filter((d: any) =>
        d.label !== '健康' && d.label_en !== 'healthy'
      )
      const mainDisease = diseaseDetections.length > 0
        ? diseaseDetections.sort((a: any, b: any) => b.confidence - a.confidence)[0]
        : null

      return {
        ...r,
        _diseaseLabel: mainDisease ? mainDisease.label : '健康',
        _diseaseCount: diseaseDetections.length,
        _healthyCount: (r.detections || []).length - diseaseDetections.length,
        _severity: diseaseDetections.length > 3 ? '严重' : diseaseDetections.length > 1 ? '中等' : diseaseDetections.length > 0 ? '轻度' : '健康',
        _imageUrl: r.result_image || r.image_url,
        _date: r.created_at?.split(' ')[0] || '',
      }
    })
  } catch {
    historyRecords.value = []
  } finally {
    loading.value = false
  }
}

function toggleSelect(id: number) {
  const idx = selectedRecords.value.indexOf(id)
  if (idx > -1) {
    selectedRecords.value.splice(idx, 1)
  } else if (selectedRecords.value.length < 2) {
    selectedRecords.value.push(id)
  }
}

function isSelected(id: number): boolean {
  return selectedRecords.value.includes(id)
}

function selectionOrder(id: number): number {
  return selectedRecords.value.indexOf(id)
}

async function compareRecords() {
  if (!canCompare.value) return

  const r1 = historyRecords.value.find(r => r.id === selectedRecords.value[0] as any)
  const r2 = historyRecords.value.find(r => r.id === selectedRecords.value[1] as any)
  if (!r1 || !r2) return

  comparing.value = true

  try {
    const res = await api.post('/history/compare', {
      period1: { start: r1._date, end: r1._date },
      period2: { start: r2._date, end: r2._date },
      comparison_type: 'disease',
    })

    const data = res.data
    const details: any[] = data.details || []

    // Severity breakdowns
    const sev1 = computeSeverity(r1)
    const sev2 = computeSeverity(r2)

    comparisonResult.value = {
      record1: {
        date: r1._date,
        disease: r1._diseaseLabel,
        diseaseCount: r1._diseaseCount,
        healthyCount: r1._healthyCount,
        severity: r1._severity,
        image: r1._imageUrl,
        severityBreakdown: sev1,
      },
      record2: {
        date: r2._date,
        disease: r2._diseaseLabel,
        diseaseCount: r2._diseaseCount,
        healthyCount: r2._healthyCount,
        severity: r2._severity,
        image: r2._imageUrl,
        severityBreakdown: sev2,
      },
      categories: data.categories || [],
      period1Values: data.period1_values || [],
      period2Values: data.period2_values || [],
      details,
      deepAnalysis: data.deep_analysis,
      changes: {
        diseaseChange: r2._diseaseCount - r1._diseaseCount,
        changePercent: r1._diseaseCount > 0
          ? ((r2._diseaseCount - r1._diseaseCount) / r1._diseaseCount * 100).toFixed(1)
          : '0',
        effectiveness: r2._diseaseCount < r1._diseaseCount
          ? '有效' : r2._diseaseCount === r1._diseaseCount ? '持平' : '无效',
        healthChange: r2._healthyCount - r1._healthyCount,
        severityChange: {
          serious: (sev2.serious || 0) - (sev1.serious || 0),
          moderate: (sev2.moderate || 0) - (sev1.moderate || 0),
          mild: (sev2.mild || 0) - (sev1.mild || 0),
        },
      },
    }

    await nextTick()
    renderAllCharts()
  } catch {
    // Fallback with local comparison
    comparisonResult.value = {
      record1: {
        date: r1._date, disease: r1._diseaseLabel,
        diseaseCount: r1._diseaseCount, healthyCount: r1._healthyCount,
        severity: r1._severity, image: r1._imageUrl,
        severityBreakdown: computeSeverity(r1),
      },
      record2: {
        date: r2._date, disease: r2._diseaseLabel,
        diseaseCount: r2._diseaseCount, healthyCount: r2._healthyCount,
        severity: r2._severity, image: r2._imageUrl,
        severityBreakdown: computeSeverity(r2),
      },
      categories: [r1._diseaseLabel, r2._diseaseLabel],
      period1Values: [r1._diseaseCount, 0],
      period2Values: [0, r2._diseaseCount],
      details: [],
      changes: {
        diseaseChange: r2._diseaseCount - r1._diseaseCount,
        changePercent: r1._diseaseCount > 0
          ? ((r2._diseaseCount - r1._diseaseCount) / r1._diseaseCount * 100).toFixed(1)
          : '0',
        effectiveness: r2._diseaseCount < r1._diseaseCount
          ? '有效' : r2._diseaseCount === r1._diseaseCount ? '持平' : '无效',
        healthChange: r2._healthyCount - r1._healthyCount,
        severityChange: { serious: 0, moderate: 0, mild: 0 },
      },
    }
    await nextTick()
    renderAllCharts()
  } finally {
    comparing.value = false
  }
}

function computeSeverity(record: HistoryRecord) {
  const dets = record.detections || []
  let serious = 0, moderate = 0, mild = 0, healthy = 0
  for (const d of dets) {
    if (d.label === '健康' || d.label_en === 'healthy') {
      healthy++
    } else if (d.confidence > 0.85) {
      serious++
    } else if (d.confidence > 0.6) {
      moderate++
    } else {
      mild++
    }
  }
  return { serious, moderate, mild, healthy }
}

function clearSelection() {
  selectedRecords.value = []
  comparisonResult.value = null
  disposeAllCharts()
}

function disposeAllCharts() {
  comparisonChart?.dispose(); comparisonChart = null
  trendChart?.dispose(); trendChart = null
  severityChart?.dispose(); severityChart = null
}

// ── Charts ──

function renderAllCharts() {
  renderComparisonChart()
  renderTrendChart()
  renderSeverityChart()
}

function renderComparisonChart() {
  const el = document.getElementById('comparisonChart')
  if (!el) return
  if (comparisonChart) comparisonChart.dispose()
  comparisonChart = echarts.init(el)

  const cr = comparisonResult.value
  if (!cr?.categories?.length) {
    el.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);">暂无对比数据</div>'
    return
  }

  comparisonChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff', fontSize: 12 },
    },
    legend: {
      data: [cr.record1?.date || '时期1', cr.record2?.date || '时期2'],
      bottom: 0,
      textStyle: { fontSize: 11, color: 'rgba(255,255,255,0.5)' },
      itemWidth: 12, itemHeight: 12,
    },
    grid: { left: 44, right: 20, bottom: 44, top: 16 },
    xAxis: {
      type: 'category',
      data: cr.categories.map((c: string) => getDisplayLabel(c)),
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10, rotate: cr.categories.length > 4 ? 25 : 0 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    yAxis: {
      type: 'value', minInterval: 1,
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
    },
    series: [
      {
        name: cr.record1?.date || '时期1', type: 'bar',
        data: cr.period1Values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b82f6' }, { offset: 1, color: '#93c5fd' },
          ]),
          borderRadius: [6, 6, 0, 0],
        },
        barWidth: '35%', barGap: '20%',
      },
      {
        name: cr.record2?.date || '时期2', type: 'bar',
        data: cr.period2Values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#16a34a' }, { offset: 1, color: '#86efac' },
          ]),
          borderRadius: [6, 6, 0, 0],
        },
        barWidth: '35%',
      },
    ],
  })
}

function renderTrendChart() {
  const el = document.getElementById('trendChart')
  if (!el) return
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(el)

  const cr = comparisonResult.value
  if (!cr) return

  const p1Total = cr.record1.diseaseCount + cr.record1.healthyCount
  const p2Total = cr.record2.diseaseCount + cr.record2.healthyCount
  const healthRate1 = p1Total > 0 ? (cr.record1.healthyCount / p1Total * 100).toFixed(1) : 0
  const healthRate2 = p2Total > 0 ? (cr.record2.healthyCount / p2Total * 100).toFixed(1) : 0
  // Project next
  const hr1 = Number(healthRate1)
  const hr2 = Number(healthRate2)
  const projected = Math.min(100, Math.max(0, hr2 + (hr2 - hr1)))

  trendChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff' },
    },
    grid: { left: 50, right: 20, bottom: 30, top: 20 },
    xAxis: {
      type: 'category',
      data: [cr.record1.date, cr.record2.date, '预测趋势'],
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10 },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    yAxis: {
      type: 'value', min: 0, max: 100,
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11, formatter: '{value}%' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
    },
    series: [
      {
        name: '健康率', type: 'line', smooth: true,
        data: [healthRate1, healthRate2, projected],
        symbol: 'circle', symbolSize: 8,
        lineStyle: { color: '#4caf50', width: 3 },
        itemStyle: { color: '#4caf50' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(76,175,80,0.25)' },
            { offset: 1, color: 'rgba(76,175,80,0)' },
          ]),
        },
        markLine: {
          silent: true,
          data: [{ yAxis: 70, label: { formatter: '警戒线', fontSize: 11 } }],
          lineStyle: { color: '#f44336', type: 'dashed' },
        },
      },
    ],
  })
}

function renderSeverityChart() {
  const el = document.getElementById('severityChart')
  if (!el) return
  if (severityChart) severityChart.dispose()
  severityChart = echarts.init(el)

  const cr = comparisonResult.value
  if (!cr) return

  const sev1 = cr.record1.severityBreakdown || { mild: 0, moderate: 0, serious: 0 }
  const sev2 = cr.record2.severityBreakdown || { mild: 0, moderate: 0, serious: 0 }

  severityChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff' },
    },
    legend: {
      data: [cr.record1.date, cr.record2.date],
      bottom: 0,
      textStyle: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
    },
    grid: { left: 44, right: 20, bottom: 44, top: 16 },
    xAxis: {
      type: 'category',
      data: ['轻度', '中度', '重度'],
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    yAxis: {
      type: 'value', minInterval: 1,
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
    },
    series: [
      {
        name: cr.record1.date, type: 'bar',
        data: [sev1.mild, sev1.moderate, sev1.serious],
        itemStyle: { color: '#3b82f6', borderRadius: [6, 6, 0, 0] },
        barWidth: '35%', barGap: '20%',
      },
      {
        name: cr.record2.date, type: 'bar',
        data: [sev2.mild, sev2.moderate, sev2.serious],
        itemStyle: { color: '#16a34a', borderRadius: [6, 6, 0, 0] },
        barWidth: '35%',
      },
    ],
  })
}

// ── Export ──

function exportJSON() {
  if (!comparisonResult.value) return
  const data = {
    exportTime: new Date().toISOString(),
    comparison: comparisonResult.value,
    prediction: trendPrediction.value,
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `history-comparison-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  showExportMenu.value = false
}

function exportReport() {
  if (!comparisonResult.value) return
  const cr = comparisonResult.value
  const changes = cr.changes
  const pred = trendPrediction.value

  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>病害对比报告</title>
<style>
  body { font-family: 'Inter', 'Noto Sans SC', sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #0a3520; color: #e0e0e0; }
  h1 { color: #4caf50; border-bottom: 2px solid rgba(76,175,80,0.3); padding-bottom: 12px; }
  h2 { color: #66bb6a; margin-top: 28px; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.08); }
  th { color: rgba(255,255,255,0.5); font-size: 0.85rem; }
  .tag { padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; display: inline-block; }
  .tag-success { background: rgba(76,175,80,0.2); color: #4caf50; }
  .tag-warning { background: rgba(255,152,0,0.2); color: #ff9800; }
  .tag-danger { background: rgba(244,67,54,0.2); color: #f44336; }
  .footer { margin-top: 40px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); color: rgba(255,255,255,0.3); font-size: 0.8rem; text-align: center; }
</style></head>
<body>
  <h1>病害检测对比报告</h1>
  <p>生成时间: ${new Date().toLocaleString('zh-CN')}</p>
  <h2>对比记录</h2>
  <table>
    <tr><th></th><th>时期 1: ${cr.record1.date}</th><th>时期 2: ${cr.record2.date}</th></tr>
    <tr><td>主要病害</td><td>${cr.record1.disease}</td><td>${cr.record2.disease}</td></tr>
    <tr><td>病害数量</td><td style="color:#f44336;font-weight:700;">${cr.record1.diseaseCount}</td><td style="color:#f44336;font-weight:700;">${cr.record2.diseaseCount}</td></tr>
    <tr><td>健康数量</td><td style="color:#4caf50;font-weight:700;">${cr.record1.healthyCount}</td><td style="color:#4caf50;font-weight:700;">${cr.record2.healthyCount}</td></tr>
    <tr><td>严重程度</td><td>${cr.record1.severity}</td><td>${cr.record2.severity}</td></tr>
  </table>
  <h2>变化分析</h2>
  <table>
    <tr><td>数量变化</td><td style="color:${changes.diseaseChange > 0 ? '#f44336' : '#4caf50'}">${changes.diseaseChange > 0 ? '+' : ''}${changes.diseaseChange}</td></tr>
    <tr><td>变化率</td><td>${changes.changePercent}%</td></tr>
    <tr><td>效果评估</td><td><span class="tag ${changes.effectiveness === '有效' ? 'tag-success' : changes.effectiveness === '无效' ? 'tag-danger' : 'tag-warning'}">${changes.effectiveness}</span></td></tr>
  </table>
  ${pred ? `
  <h2>趋势预测</h2>
  <table>
    <tr><td>预测方向</td><td>${pred.direction}</td></tr>
    <tr><td>风险等级</td><td><span class="tag ${pred.riskLevel === '高风险' ? 'tag-danger' : pred.riskLevel === '中风险' ? 'tag-warning' : 'tag-success'}">${pred.riskLevel}</span></td></tr>
    <tr><td>建议</td><td>${pred.suggestion}</td></tr>
  </table>` : ''}
  <div class="footer">智慧农业病害检测系统 - 自动生成报告</div>
</body></html>`

  const blob = new Blob([html], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `comparison-report-${Date.now()}.html`
  a.click()
  URL.revokeObjectURL(url)
  showExportMenu.value = false
}

// ── Lifecycle ──

function handleResize() {
  comparisonChart?.resize()
  trendChart?.resize()
  severityChart?.resize()
}

watch([timeFilter, searchQuery], () => {
  selectedRecords.value = []
  comparisonResult.value = null
  disposeAllCharts()
})

onMounted(() => {
  loadHistory()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  disposeAllCharts()
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>历史对比</h2>
      <p>对比不同时期的检测结果，分析病害变化趋势和防治效果</p>
    </div>

    <div class="history-layout">
      <!-- ═══════ Left Panel (35%) ═══════ -->
      <div class="left-panel animate-fade-up">
        <div class="glass" style="display:flex;flex-direction:column;height:100%;">
          <!-- Header -->
          <div style="padding:18px 20px;border-bottom:1px solid rgba(255,255,255,0.06);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
              <h3 style="font-weight:700;font-size:1rem;display:flex;align-items:center;gap:8px;">
                <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
                检测记录
              </h3>
              <span style="font-size:0.75rem;color:var(--text-muted);">
                已选 {{ selectedRecords.length }}/2
              </span>
            </div>

            <!-- Search -->
            <div class="search-wrap" style="margin-bottom:10px;">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
              <input v-model="searchQuery" placeholder="搜索病害名称..." class="search-input" style="flex:1;" />
            </div>

            <!-- Time filters -->
            <div class="time-filters">
              <button v-for="opt in [
                { value: 'all', label: '全部' },
                { value: 'today', label: '今日' },
                { value: 'week', label: '本周' },
                { value: 'month', label: '本月' },
                { value: 'custom', label: '自定义' },
              ]" :key="opt.value"
                @click="timeFilter = opt.value as any"
                :class="['time-filter-btn', { active: timeFilter === opt.value }]"
              >{{ opt.label }}</button>
            </div>

            <!-- Custom date range -->
            <div v-if="timeFilter === 'custom'" style="display:flex;gap:8px;margin-top:10px;">
              <input v-model="customStart" type="date" class="date-input" />
              <span style="color:var(--text-muted);align-self:center;">至</span>
              <input v-model="customEnd" type="date" class="date-input" />
            </div>
          </div>

          <!-- Record list -->
          <div style="flex:1;overflow-y:auto;padding:12px 16px;">
            <!-- Loading -->
            <div v-if="loading" style="display:flex;flex-direction:column;gap:10px;padding:8px 0;">
              <div v-for="i in 4" :key="i" class="skeleton" style="height:80px;border-radius:14px;"></div>
            </div>

            <!-- Empty -->
            <div v-else-if="filteredRecords.length === 0" style="text-align:center;padding:40px 20px;">
              <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="opacity:0.25;margin-bottom:12px;"><path d="M22 12h-6l-2 3H10l-2-3H2"/><path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/></svg>
              <p style="color:var(--text-secondary);font-size:0.9rem;">{{ searchQuery ? '未找到匹配记录' : '暂无检测记录' }}</p>
              <p style="color:var(--text-muted);font-size:0.8rem;margin-top:4px;">{{ searchQuery ? '尝试其他关键词' : '请先进行图片检测' }}</p>
            </div>

            <!-- List -->
            <div v-else class="record-list">
              <div
                v-for="record in filteredRecords"
                :key="record.id"
                @click="toggleSelect(record.id as any)"
                :class="['record-card', { selected: isSelected(record.id as any) }]"
              >
                <!-- Selection order badge -->
                <div v-if="isSelected(record.id as any)" class="selection-badge">
                  {{ selectionOrder(record.id as any) + 1 }}
                </div>

                <div class="record-card-inner">
                  <!-- Thumbnail -->
                  <div class="record-thumb">
                    <img
                      v-if="record._imageUrl"
                      :src="'data:image/jpeg;base64,' + record._imageUrl"
                      alt="检测图片"
                      @error="($event.target as HTMLImageElement).style.display='none'"
                    />
                    <svg v-else width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" style="opacity:0.4;"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                  </div>

                  <!-- Info -->
                  <div class="record-info">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
                      <span style="font-weight:600;font-size:0.9rem;">{{ record._diseaseLabel }}</span>
                      <span
                        class="severity-tag"
                        :style="{ background: getSeverityBg(record._severity), color: getSeverityColor(record._severity) }"
                      >{{ record._severity }}</span>
                    </div>
                    <p style="font-size:0.78rem;color:var(--text-muted);">{{ record.created_at }}</p>
                    <div style="display:flex;gap:14px;margin-top:3px;">
                      <span style="font-size:0.76rem;color:var(--text-secondary);">
                        病害: <strong style="color:#f44336;">{{ record._diseaseCount }}</strong>
                      </span>
                      <span style="font-size:0.76rem;color:var(--text-secondary);">
                        健康: <strong style="color:#4caf50;">{{ record._healthyCount }}</strong>
                      </span>
                    </div>
                  </div>

                  <!-- Check circle -->
                  <div :class="['check-circle', { checked: isSelected(record.id as any) }]">
                    <svg v-if="isSelected(record.id as any)" width="14" height="14" fill="none" stroke="#fff" stroke-width="3" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"/></svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div style="padding:14px 20px;border-top:1px solid rgba(255,255,255,0.06);display:flex;gap:10px;">
            <button
              @click="compareRecords"
              :disabled="!canCompare || comparing"
              class="btn btn-primary"
              style="flex:1;"
            >
              <svg v-if="comparing" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" class="spin-icon"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0118.8-4.3M22 12.5a10 10 0 01-18.8 4.2"/></svg>
              <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              {{ comparing ? '分析中...' : '对比分析' }}
            </button>
            <button @click="clearSelection" class="btn btn-outline" :disabled="selectedRecords.length === 0 && !comparisonResult">
              清除
            </button>
          </div>
        </div>
      </div>

      <!-- ═══════ Right Panel (65%) ═══════ -->
      <div class="right-panel animate-fade-up stagger-1">
        <!-- Empty state -->
        <div v-if="!comparisonResult" class="glass empty-state">
          <svg width="64" height="64" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="opacity:0.2;margin-bottom:16px;"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
          <p style="font-weight:600;font-size:1.05rem;">选择记录进行对比</p>
          <p style="color:var(--text-muted);font-size:0.85rem;margin-top:6px;max-width:280px;">
            从左侧选择两条历史检测记录，点击"对比分析"查看详细对比结果
          </p>
        </div>

        <!-- Comparison results -->
        <div v-else class="comparison-results">
          <!-- Export button -->
          <div style="display:flex;justify-content:flex-end;margin-bottom:12px;position:relative;">
            <div style="position:relative;">
              <button @click="showExportMenu = !showExportMenu" class="btn btn-outline btn-sm" style="gap:6px;">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                导出报告
              </button>
              <div v-if="showExportMenu" class="export-dropdown glass" style="position:absolute;top:38px;right:0;z-index:10;min-width:160px;padding:6px;">
                <button @click="exportJSON" class="export-option">JSON 格式</button>
                <button @click="exportReport" class="export-option">HTML 报告</button>
              </div>
            </div>
          </div>

          <!-- Record cards -->
          <div class="record-cards">
            <div class="glass record-detail-card" style="border-left:3px solid #3b82f6;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#3b82f6;"></div>
                <span style="font-weight:600;font-size:0.9rem;">记录 1</span>
                <span style="font-size:0.78rem;color:var(--text-muted);">{{ comparisonResult.record1.date }}</span>
              </div>
              <div style="display:flex;align-items:center;gap:12px;">
                <div class="record-thumb-sm">
                  <img
                    v-if="comparisonResult.record1.image"
                    :src="'data:image/jpeg;base64,' + comparisonResult.record1.image"
                    @error="($event.target as HTMLImageElement).style.display='none'"
                  />
                  <svg v-else width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" style="opacity:0.3;"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                </div>
                <div style="flex:1;">
                  <div style="display:flex;gap:16px;">
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">主要病害</span><p style="font-weight:700;font-size:0.95rem;">{{ comparisonResult.record1.disease }}</p></div>
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">病害数</span><p style="font-weight:700;color:#f44336;font-size:1.1rem;">{{ comparisonResult.record1.diseaseCount }}</p></div>
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">健康数</span><p style="font-weight:700;color:#4caf50;font-size:1.1rem;">{{ comparisonResult.record1.healthyCount }}</p></div>
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">程度</span><span class="severity-tag" :style="{background:getSeverityBg(comparisonResult.record1.severity),color:getSeverityColor(comparisonResult.record1.severity),marginTop:'2px',display:'inline-block'}">{{ comparisonResult.record1.severity }}</span></div>
                  </div>
                </div>
              </div>
            </div>

            <div style="display:flex;align-items:center;justify-content:center;padding:0 4px;">
              <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="color:var(--text-muted);"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </div>

            <div class="glass record-detail-card" style="border-left:3px solid #16a34a;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#16a34a;"></div>
                <span style="font-weight:600;font-size:0.9rem;">记录 2</span>
                <span style="font-size:0.78rem;color:var(--text-muted);">{{ comparisonResult.record2.date }}</span>
              </div>
              <div style="display:flex;align-items:center;gap:12px;">
                <div class="record-thumb-sm">
                  <img
                    v-if="comparisonResult.record2.image"
                    :src="'data:image/jpeg;base64,' + comparisonResult.record2.image"
                    @error="($event.target as HTMLImageElement).style.display='none'"
                  />
                  <svg v-else width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" style="opacity:0.3;"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                </div>
                <div style="flex:1;">
                  <div style="display:flex;gap:16px;">
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">主要病害</span><p style="font-weight:700;font-size:0.95rem;">{{ comparisonResult.record2.disease }}</p></div>
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">病害数</span><p style="font-weight:700;color:#f44336;font-size:1.1rem;">{{ comparisonResult.record2.diseaseCount }}</p></div>
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">健康数</span><p style="font-weight:700;color:#4caf50;font-size:1.1rem;">{{ comparisonResult.record2.healthyCount }}</p></div>
                    <div><span style="font-size:0.72rem;color:var(--text-muted);">程度</span><span class="severity-tag" :style="{background:getSeverityBg(comparisonResult.record2.severity),color:getSeverityColor(comparisonResult.record2.severity),marginTop:'2px',display:'inline-block'}">{{ comparisonResult.record2.severity }}</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Changes analysis -->
          <div v-if="comparisonResult.changes" class="glass changes-card">
            <h4 style="font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px;font-size:0.95rem;">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
              变化分析
            </h4>
            <div class="changes-grid">
              <div class="change-item">
                <span class="change-label">病害数量变化</span>
                <span class="change-value" :style="{color: comparisonResult.changes.diseaseChange > 0 ? '#f44336' : '#4caf50'}">
                  {{ comparisonResult.changes.diseaseChange > 0 ? '+' : '' }}{{ comparisonResult.changes.diseaseChange }}
                </span>
              </div>
              <div class="change-item">
                <span class="change-label">变化率</span>
                <span class="change-value" :style="{color: parseFloat(comparisonResult.changes.changePercent) > 0 ? '#f44336' : '#4caf50'}">
                  {{ parseFloat(comparisonResult.changes.changePercent) > 0 ? '+' : '' }}{{ comparisonResult.changes.changePercent }}%
                </span>
              </div>
              <div class="change-item">
                <span class="change-label">健康数量变化</span>
                <span class="change-value" :style="{color: comparisonResult.changes.healthChange > 0 ? '#4caf50' : '#f44336'}">
                  {{ comparisonResult.changes.healthChange > 0 ? '+' : '' }}{{ comparisonResult.changes.healthChange }}
                </span>
              </div>
              <div class="change-item">
                <span class="change-label">防治效果</span>
                <span class="change-value">
                  <span class="tag" :style="{background:getEffectivenessTag(comparisonResult.changes.effectiveness).bg,color:getEffectivenessTag(comparisonResult.changes.effectiveness).color}">{{ comparisonResult.changes.effectiveness }}</span>
                </span>
              </div>
            </div>

            <!-- Detail breakdown if available -->
            <div v-if="comparisonResult.details.length > 0" style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.05);">
              <div v-for="d in comparisonResult.details.slice(0, 5)" :key="d.category" class="change-detail-row">
                <span style="font-size:0.83rem;color:var(--text-secondary);">{{ getDisplayLabel(d.category) }}</span>
                <span style="font-size:0.85rem;font-weight:600;">{{ d.period1_count }} &rarr; {{ d.period2_count }}</span>
                <span :style="{color: d.change > 0 ? '#f44336' : d.change < 0 ? '#4caf50' : 'var(--text-muted)',fontSize:'0.8rem'}">
                  {{ d.change > 0 ? '+' : '' }}{{ d.change }} ({{ d.change_rate }}%)
                </span>
              </div>
            </div>
          </div>

          <!-- Charts -->
          <div class="glass" style="margin-top:16px;">
            <h4 style="font-weight:700;margin-bottom:16px;font-size:0.95rem;display:flex;align-items:center;gap:8px;">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="18" y="3" width="4" height="18"/><rect x="10" y="8" width="4" height="13"/><rect x="2" y="13" width="4" height="8"/></svg>
              病害分布对比
            </h4>
            <div id="comparisonChart" style="height:280px;"></div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;">
            <div class="glass">
              <h4 style="font-weight:700;margin-bottom:14px;font-size:0.9rem;display:flex;align-items:center;gap:8px;">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                健康率趋势
              </h4>
              <div id="trendChart" style="height:240px;"></div>
            </div>
            <div class="glass">
              <h4 style="font-weight:700;margin-bottom:14px;font-size:0.9rem;display:flex;align-items:center;gap:8px;">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                严重程度对比
              </h4>
              <div id="severityChart" style="height:240px;"></div>
            </div>
          </div>

          <!-- Trend prediction -->
          <div v-if="trendPrediction" class="glass prediction-card" style="margin-top:16px;">
            <h4 style="font-weight:700;margin-bottom:12px;font-size:0.95rem;display:flex;align-items:center;gap:8px;">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
              趋势预测
            </h4>
            <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
              <div style="text-align:center;min-width:80px;">
                <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">方向</p>
                <p style="font-weight:700;font-size:1.1rem;" :style="{color:trendPrediction.direction==='上升'?'#f44336':trendPrediction.direction==='下降'?'#4caf50':'#2196f3'}">{{ trendPrediction.direction }}</p>
              </div>
              <div style="text-align:center;min-width:80px;">
                <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">风险等级</p>
                <span class="tag" :style="{
                  background: trendPrediction.riskLevel === '高风险' ? 'rgba(244,67,54,0.15)' : trendPrediction.riskLevel === '中风险' ? 'rgba(255,152,0,0.15)' : trendPrediction.riskLevel === '改善' ? 'rgba(76,175,80,0.15)' : 'rgba(33,150,243,0.15)',
                  color: trendPrediction.riskLevel === '高风险' ? '#f44336' : trendPrediction.riskLevel === '中风险' ? '#ff9800' : trendPrediction.riskLevel === '改善' ? '#4caf50' : '#2196f3',
                  fontSize:'0.85rem',fontWeight:'600',padding:'4px 12px'
                }">{{ trendPrediction.riskLevel }}</span>
              </div>
              <div style="text-align:center;min-width:80px;">
                <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">预测下期病害数</p>
                <p style="font-weight:700;font-size:1.1rem;color:#ff9800;">{{ trendPrediction.predicted }}</p>
              </div>
            </div>
            <div style="margin-top:12px;padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;font-size:0.84rem;color:var(--text-secondary);line-height:1.6;">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="margin-right:6px;vertical-align:-3px;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
              {{ trendPrediction.suggestion }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Layout ── */
.history-layout {
  display: grid;
  grid-template-columns: 35% 65%;
  gap: 20px;
}

.left-panel { min-width: 0; display: flex; }
.left-panel > .glass { flex: 1; }

.right-panel { min-width: 0; }

/* ── Search ── */
.search-wrap {
  display: flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; padding: 7px 12px; transition: border-color 0.2s;
}
.search-wrap:focus-within { border-color: rgba(76,175,80,0.3); }
.search-input {
  background: transparent; border: none; outline: none;
  color: var(--text-primary); font-size: 0.82rem; font-family: inherit;
  min-width: 0;
}
.search-input::placeholder { color: var(--text-muted); }

/* ── Time filters ── */
.time-filters { display: flex; gap: 4px; flex-wrap: wrap; }
.time-filter-btn {
  padding: 5px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);
  background: transparent; color: var(--text-muted); cursor: pointer;
  font-size: 0.76rem; font-family: inherit; transition: all 0.15s; white-space: nowrap;
}
.time-filter-btn:hover { border-color: rgba(255,255,255,0.15); color: var(--text-primary); }
.time-filter-btn.active {
  background: rgba(76,175,80,0.15); border-color: rgba(76,175,80,0.3);
  color: #4caf50; font-weight: 600;
}

.date-input {
  flex: 1; min-width: 0;
  padding: 6px 10px; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
  background: rgba(255,255,255,0.04); color: var(--text-primary);
  font-size: 0.8rem; font-family: inherit; outline: none;
}
.date-input:focus { border-color: rgba(76,175,80,0.3); }

/* ── Record list ── */
.record-list { display: flex; flex-direction: column; gap: 8px; }

.record-card {
  position: relative;
  padding: 14px;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255,255,255,0.02);
}
.record-card:hover { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.12); }
.record-card.selected {
  background: rgba(76,175,80,0.06);
  border-color: rgba(76,175,80,0.35);
}

.selection-badge {
  position: absolute; top: -6px; right: -6px;
  width: 22px; height: 22px; border-radius: 50%;
  background: #4caf50; color: #fff;
  font-size: 0.7rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  z-index: 2;
}

.record-card-inner {
  display: flex; align-items: center; gap: 12px;
}

.record-thumb {
  width: 56px; height: 56px; border-radius: 10px; overflow: hidden;
  flex-shrink: 0; background: rgba(0,0,0,0.2);
  display: flex; align-items: center; justify-content: center;
}
.record-thumb img { width: 100%; height: 100%; object-fit: cover; }

.record-info { flex: 1; min-width: 0; }

.severity-tag {
  padding: 2px 8px; border-radius: 12px;
  font-size: 0.7rem; font-weight: 600; white-space: nowrap;
}

.check-circle {
  width: 22px; height: 22px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.12); flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.check-circle.checked {
  background: #4caf50; border-color: #4caf50;
}

/* ── Empty state ── */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 32px; text-align: center; min-height: 400px;
}

/* ── Export ── */
.export-option {
  display: block; width: 100%; padding: 10px 14px;
  border: none; border-radius: 8px; background: transparent;
  color: var(--text-primary); cursor: pointer; font-size: 0.84rem;
  font-family: inherit; text-align: left; transition: background 0.15s;
}
.export-option:hover { background: rgba(255,255,255,0.06); }

/* ── Record detail cards ── */
.record-cards { display: flex; flex-direction: column; gap: 8px; }
.record-detail-card { padding: 16px 18px; }
.record-thumb-sm {
  width: 56px; height: 56px; border-radius: 10px; overflow: hidden;
  flex-shrink: 0; background: rgba(0,0,0,0.2);
  display: flex; align-items: center; justify-content: center;
}
.record-thumb-sm img { width: 100%; height: 100%; object-fit: cover; }

/* ── Changes ── */
.changes-card { padding: 18px 20px; margin-top: 16px; }
.changes-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;
}
.change-item {
  padding: 14px 16px; background: rgba(255,255,255,0.02);
  border-radius: 12px; border: 1px solid rgba(255,255,255,0.04);
  display: flex; flex-direction: column; gap: 6px;
}
.change-label { font-size: 0.76rem; color: var(--text-muted); }
.change-value { font-weight: 700; font-size: 1rem; }

.change-detail-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.03);
}

.prediction-card { padding: 18px 20px; }

/* ── Spinner ── */
.spin-icon { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ── */
@media (max-width: 900px) {
  .history-layout {
    grid-template-columns: 1fr;
  }
  .left-panel > .glass { max-height: none; }
  .record-cards { gap: 10px; }
  .changes-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 600px) {
  .changes-grid { grid-template-columns: 1fr; }
  .record-thumb-sm { width: 44px; height: 44px; }
  .record-detail-card .record-detail-card-inner { flex-direction: column; }
}
</style>
