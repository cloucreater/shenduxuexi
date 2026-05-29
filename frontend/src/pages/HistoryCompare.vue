<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

// History records from API
const historyRecords = ref<any[]>([])
const loading = ref(true)

// Selection
const selectedRecords = ref<number[]>([])
const comparisonResult = ref<any>(null)
const comparing = ref(false)

// Charts
let comparisonChart: echarts.ECharts | null = null

// Disease labels
const DISEASE_LABELS: Record<string, string> = {
  healthy: '健康', leaf_spot: '叶斑病', rust: '锈病',
  powdery_mildew: '白粉病', early_blight: '早疫病', late_blight: '晚疫病',
  bacterial_spot: '细菌性斑点病', leaf_mold: '叶霉病', septoria: '斑枯病'
}

function getDisplayLabel(key: string): string {
  return DISEASE_LABELS[key] || key
}

async function loadHistory() {
  try {
    const res = await api.get('/history?limit=20')
    const records = res.data.records || []
    historyRecords.value = records.map((r: any) => {
      const diseaseDetections = (r.detections || []).filter((d: any) =>
        d.label !== 'Healthy' && d.label !== '健康' && d.label_en !== 'healthy'
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
        _imageUrl: r.result_image || r.image_url
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

async function compareRecords() {
  if (selectedRecords.value.length !== 2) return

  const r1 = historyRecords.value.find(r => r.id === selectedRecords.value[0])
  const r2 = historyRecords.value.find(r => r.id === selectedRecords.value[1])
  if (!r1 || !r2) return

  comparing.value = true

  try {
    // Try backend comparison API
    const res = await api.post('/history/compare', {
      period1: { start: r1.created_at?.split(' ')[0], end: r1.created_at?.split(' ')[0] },
      period2: { start: r2.created_at?.split(' ')[0], end: r2.created_at?.split(' ')[0] },
      comparison_type: 'disease'
    })

    comparisonResult.value = {
      record1: {
        date: r1.created_at?.split(' ')[0],
        disease: r1._diseaseLabel,
        diseaseCount: r1._diseaseCount,
        healthyCount: r1._healthyCount,
        severity: r1._severity,
        image: r1._imageUrl
      },
      record2: {
        date: r2.created_at?.split(' ')[0],
        disease: r2._diseaseLabel,
        diseaseCount: r2._diseaseCount,
        healthyCount: r2._healthyCount,
        severity: r2._severity,
        image: r2._imageUrl
      },
      deepAnalysis: res.data?.deep_analysis,
      categories: res.data?.categories || [],
      period1Values: res.data?.period1_values || [],
      period2Values: res.data?.period2_values || [],
    }

    await nextTick()
    renderComparisonChart()
  } catch {
    // Fallback to local comparison
    comparisonResult.value = {
      record1: {
        date: r1.created_at?.split(' ')[0],
        disease: r1._diseaseLabel,
        diseaseCount: r1._diseaseCount,
        healthyCount: r1._healthyCount,
        severity: r1._severity,
        image: r1._imageUrl
      },
      record2: {
        date: r2.created_at?.split(' ')[0],
        disease: r2._diseaseLabel,
        diseaseCount: r2._diseaseCount,
        healthyCount: r2._healthyCount,
        severity: r2._severity,
        image: r2._imageUrl
      },
      changes: {
        diseaseChange: r2._diseaseCount - r1._diseaseCount,
        changePercent: r1._diseaseCount > 0
          ? ((r2._diseaseCount - r1._diseaseCount) / r1._diseaseCount * 100).toFixed(1)
          : '0',
        effectiveness: r2._diseaseCount < r1._diseaseCount ? '有效' : r2._diseaseCount === r1._diseaseCount ? '持平' : '待观察'
      }
    }
  } finally {
    comparing.value = false
  }
}

function clearSelection() {
  selectedRecords.value = []
  comparisonResult.value = null
  if (comparisonChart) {
    comparisonChart.dispose()
    comparisonChart = null
  }
}

function renderComparisonChart() {
  const el = document.getElementById('comparisonChart')
  if (!el || !comparisonResult.value?.categories?.length) return
  if (comparisonChart) comparisonChart.dispose()

  comparisonChart = echarts.init(el)
  comparisonChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#171717', fontSize: 12 }
    },
    legend: {
      data: ['记录 1', '记录 2'],
      bottom: 0,
      textStyle: { fontSize: 11, color: '#737373' }
    },
    grid: { left: 48, right: 24, bottom: 40, top: 16 },
    xAxis: {
      type: 'category',
      data: comparisonResult.value.categories.map((c: string) => getDisplayLabel(c)),
      axisLabel: { color: '#737373', fontSize: 10 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.04)' } },
      axisLabel: { color: '#737373', fontSize: 11 }
    },
    series: [
      {
        name: '记录 1',
        type: 'bar',
        data: comparisonResult.value.period1Values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b82f6' }, { offset: 1, color: '#93c5fd' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        barWidth: '35%',
        barGap: '20%'
      },
      {
        name: '记录 2',
        type: 'bar',
        data: comparisonResult.value.period2Values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#16a34a' }, { offset: 1, color: '#86efac' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        barWidth: '35%'
      }
    ]
  })
}

function getSeverityColor(severity: string): string {
  const map: Record<string, string> = {
    '严重': 'var(--color-danger)',
    '中等': 'var(--color-warning)',
    '轻度': 'var(--color-info)',
    '健康': 'var(--color-success)'
  }
  return map[severity] || 'var(--text-muted)'
}

function getSeverityBg(severity: string): string {
  const map: Record<string, string> = {
    '严重': 'var(--color-danger-bg)',
    '中等': 'var(--color-warning-bg)',
    '轻度': 'var(--color-info-bg)',
    '健康': 'var(--color-success-bg)'
  }
  return map[severity] || 'rgba(0,0,0,0.04)'
}

onMounted(() => {
  loadHistory()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="page-header animate-fade-down">
      <h2>🔄 历史对比</h2>
      <p>对比不同时期的检测结果，分析病害变化趋势和防治效果</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- History Records List -->
      <div class="glass-card animate-fade-up stagger-1">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
          <h3 style="font-weight:700;color:var(--text-primary);font-size:1.05rem;">📋 历史检测记录</h3>
          <span style="font-size:0.8rem;color:var(--text-muted);">
            已选 {{ selectedRecords.length }}/2 条
          </span>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 4" :key="i" class="skeleton" style="height:88px;"></div>
        </div>

        <!-- Records -->
        <div v-else-if="historyRecords.length > 0" class="space-y-3" style="max-height:520px;overflow-y:auto;">
          <div
            v-for="record in historyRecords"
            :key="record.id"
            @click="toggleSelect(record.id)"
            :class="['section-card', { 'card-accent': selectedRecords.includes(record.id) }]"
            style="cursor:pointer;padding:16px;transition:all 0.2s;"
            :style="selectedRecords.includes(record.id) ? 'border-color:var(--color-primary);background:var(--color-primary-bg);' : ''"
          >
            <div style="display:flex;align-items:center;gap:14px;">
              <!-- Image Preview -->
              <div style="width:72px;height:72px;border-radius:10px;overflow:hidden;flex-shrink:0;background:rgba(0,0,0,0.04);display:flex;align-items:center;justify-content:center;">
                <img
                  v-if="record._imageUrl"
                  :src="record._imageUrl"
                  alt="检测图片"
                  style="width:100%;height:100%;object-fit:cover;"
                  @error="($event.target as HTMLImageElement).style.display='none'"
                />
                <svg v-if="!record._imageUrl" class="w-8 h-8" style="color:var(--text-muted);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>

              <!-- Info -->
              <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                  <span style="font-weight:600;color:var(--text-primary);">{{ record._diseaseLabel }}</span>
                  <span
                    style="padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:600;"
                    :style="{ background: getSeverityBg(record._severity), color: getSeverityColor(record._severity) }"
                  >
                    {{ record._severity }}
                  </span>
                </div>
                <p style="font-size:0.8rem;color:var(--text-muted);">{{ record.created_at }}</p>
                <div style="display:flex;gap:16px;margin-top:4px;">
                  <span style="font-size:0.78rem;color:var(--text-secondary);">
                    病害: <strong style="color:var(--color-danger);">{{ record._diseaseCount }}</strong>
                  </span>
                  <span style="font-size:0.78rem;color:var(--text-secondary);">
                    健康: <strong style="color:var(--color-success);">{{ record._healthyCount }}</strong>
                  </span>
                </div>
              </div>

              <!-- Check indicator -->
              <div
                style="width:24px;height:24px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:all 0.2s;"
                :style="selectedRecords.includes(record.id)
                  ? 'background:var(--color-primary);color:#fff;'
                  : 'border:2px solid var(--surface-border);color:transparent;'"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty -->
        <div v-else style="text-align:center;padding:48px 20px;">
          <div style="font-size:3rem;margin-bottom:12px;">📭</div>
          <p style="color:var(--text-secondary);">暂无检测记录</p>
          <p style="color:var(--text-muted);font-size:0.85rem;">请先进行图片检测</p>
        </div>

        <!-- Actions -->
        <div style="display:flex;gap:12px;margin-top:16px;">
          <button
            @click="compareRecords"
            :disabled="selectedRecords.length !== 2 || comparing"
            class="btn btn-primary"
            style="flex:1;"
          >
            {{ comparing ? '⏳ 分析中...' : '📊 对比分析' }}
          </button>
          <button @click="clearSelection" class="btn btn-outline">
            清除选择
          </button>
        </div>
      </div>

      <!-- Comparison Result -->
      <div class="animate-fade-up stagger-2">
        <!-- Result Display -->
        <div v-if="comparisonResult" class="glass-card space-y-4">
          <h3 style="font-weight:700;color:var(--text-primary);font-size:1.05rem;">📊 对比结果</h3>

          <!-- Two Records Side by Side -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div style="padding:16px;background:var(--color-info-bg);border-radius:12px;text-align:center;">
              <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">记录 1</p>
              <p style="font-weight:700;color:var(--text-primary);font-size:1.05rem;">{{ comparisonResult.record1.disease }}</p>
              <p style="font-size:0.75rem;color:var(--text-muted);">{{ comparisonResult.record1.date }}</p>
              <div style="display:flex;justify-content:center;gap:16px;margin-top:8px;">
                <div>
                  <p style="font-size:1.3rem;font-weight:800;color:var(--color-danger);">{{ comparisonResult.record1.diseaseCount }}</p>
                  <p style="font-size:0.7rem;color:var(--text-muted);">病害</p>
                </div>
                <div>
                  <p style="font-size:1.3rem;font-weight:800;color:var(--color-success);">{{ comparisonResult.record1.healthyCount }}</p>
                  <p style="font-size:0.7rem;color:var(--text-muted);">健康</p>
                </div>
              </div>
            </div>
            <div style="padding:16px;background:var(--color-success-bg);border-radius:12px;text-align:center;">
              <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">记录 2</p>
              <p style="font-weight:700;color:var(--text-primary);font-size:1.05rem;">{{ comparisonResult.record2.disease }}</p>
              <p style="font-size:0.75rem;color:var(--text-muted);">{{ comparisonResult.record2.date }}</p>
              <div style="display:flex;justify-content:center;gap:16px;margin-top:8px;">
                <div>
                  <p style="font-size:1.3rem;font-weight:800;color:var(--color-danger);">{{ comparisonResult.record2.diseaseCount }}</p>
                  <p style="font-size:0.7rem;color:var(--text-muted);">病害</p>
                </div>
                <div>
                  <p style="font-size:1.3rem;font-weight:800;color:var(--color-success);">{{ comparisonResult.record2.healthyCount }}</p>
                  <p style="font-size:0.7rem;color:var(--text-muted);">健康</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Changes Analysis -->
          <div v-if="comparisonResult.changes" style="padding:16px;background:rgba(0,0,0,0.015);border-radius:12px;">
            <h4 style="font-weight:600;color:var(--text-primary);margin-bottom:10px;">📈 变化分析</h4>
            <div class="space-y-3">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:var(--text-secondary);font-size:0.85rem;">数量变化</span>
                <span style="font-weight:700;" :style="{ color: comparisonResult.changes.diseaseChange > 0 ? 'var(--color-danger)' : comparisonResult.changes.diseaseChange < 0 ? 'var(--color-success)' : 'var(--text-secondary)' }">
                  {{ comparisonResult.changes.diseaseChange > 0 ? '+' : '' }}{{ comparisonResult.changes.diseaseChange }}
                </span>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:var(--text-secondary);font-size:0.85rem;">变化率</span>
                <span style="font-weight:700;" :style="{ color: parseFloat(comparisonResult.changes.changePercent) > 0 ? 'var(--color-danger)' : parseFloat(comparisonResult.changes.changePercent) < 0 ? 'var(--color-success)' : 'var(--text-secondary)' }">
                  {{ parseFloat(comparisonResult.changes.changePercent) > 0 ? '+' : '' }}{{ comparisonResult.changes.changePercent }}%
                </span>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:var(--text-secondary);font-size:0.85rem;">效果评估</span>
                <span style="padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;"
                  :style="{
                    background: comparisonResult.changes.effectiveness === '有效' ? 'var(--color-success-bg)' : comparisonResult.changes.effectiveness === '持平' ? 'var(--color-info-bg)' : 'var(--color-warning-bg)',
                    color: comparisonResult.changes.effectiveness === '有效' ? 'var(--color-success)' : comparisonResult.changes.effectiveness === '持平' ? 'var(--color-info)' : 'var(--color-warning)'
                  }"
                >
                  {{ comparisonResult.changes.effectiveness }}
                </span>
              </div>
            </div>
          </div>

          <!-- Chart for deep comparison -->
          <div v-if="comparisonResult.categories?.length">
            <h4 style="font-weight:600;color:var(--text-primary);margin-bottom:8px;">📊 病害对比图</h4>
            <div id="comparisonChart" style="height:280px;"></div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="glass-card" style="text-align:center;padding:64px 32px;">
          <div style="font-size:4rem;margin-bottom:16px;">🔍</div>
          <p style="font-weight:600;color:var(--text-primary);font-size:1.05rem;">选择记录进行对比</p>
          <p style="color:var(--text-muted);font-size:0.85rem;margin-top:6px;">
            从左侧选择两条历史检测记录<br>点击"对比分析"查看详细对比结果
          </p>
        </div>

        <!-- Tips -->
        <div class="info-banner" style="margin-top:16px;">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div style="font-size:0.82rem;">
            <strong>使用提示：</strong>选择两个不同时期的检测记录进行对比，系统将自动分析病害变化趋势和防治效果。
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
