<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

let chart: echarts.ECharts | null = null

const metrics = ref([
  { label: '模型准确率', value: '66.7%', icon: '🎯', color: '#4caf50' },
  { label: '精确率 Precision', value: '71.2%', icon: '📐', color: '#2196f3' },
  { label: '召回率 Recall', value: '63.8%', icon: '🔄', color: '#ff9800' },
  { label: 'F1 Score', value: '0.673', icon: '⭐', color: '#9c27b0' },
])

const classMetrics = ref([
  { name: '叶斑病', precision: 0.72, recall: 0.68, f1: 0.70, support: 581, color: '#f44336' },
  { name: '白粉病', precision: 0.69, recall: 0.62, f1: 0.65, support: 512, color: '#ff9800' },
  { name: '锈病', precision: 0.75, recall: 0.70, f1: 0.72, support: 423, color: '#ff5722' },
  { name: '早疫病', precision: 0.68, recall: 0.60, f1: 0.64, support: 398, color: '#2196f3' },
  { name: '晚疫病', precision: 0.71, recall: 0.65, f1: 0.68, support: 356, color: '#9c27b0' },
  { name: '健康', precision: 0.82, recall: 0.89, f1: 0.85, support: 870, color: '#4caf50' },
])

function renderChart() {
  const el = document.getElementById('analysisChart')
  if (!el) return
  if (chart) chart.dispose()
  chart = echarts.init(el)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,45,30,0.95)',
      borderColor: 'rgba(76,175,80,0.3)',
      textStyle: { color: '#fff' },
    },
    legend: {
      data: ['Precision', 'Recall', 'F1 Score'],
      bottom: 0,
      textStyle: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
    },
    grid: { left: 48, right: 20, bottom: 40, top: 20 },
    xAxis: {
      type: 'category',
      data: classMetrics.value.map(m => m.name),
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11, rotate: 20 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value', min: 0, max: 1,
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
    },
    series: [
      {
        name: 'Precision', type: 'bar',
        data: classMetrics.value.map(m => +(m.precision).toFixed(2)),
        itemStyle: { color: '#4caf50', borderRadius: [6, 6, 0, 0] },
        barWidth: '22%',
      },
      {
        name: 'Recall', type: 'bar',
        data: classMetrics.value.map(m => +(m.recall).toFixed(2)),
        itemStyle: { color: '#2196f3', borderRadius: [6, 6, 0, 0] },
        barWidth: '22%',
      },
      {
        name: 'F1 Score', type: 'bar',
        data: classMetrics.value.map(m => +(m.f1).toFixed(2)),
        itemStyle: { color: '#ff9800', borderRadius: [6, 6, 0, 0] },
        barWidth: '22%',
      },
    ]
  })
}

onMounted(() => {
  setTimeout(renderChart, 200)
  window.addEventListener('resize', () => chart?.resize())
})
onUnmounted(() => { chart?.dispose() })
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>🧠 智能分析</h2>
      <p>模型性能评估与病害检测数据分析</p>
    </div>

    <!-- Overall Metrics -->
    <div class="flex-card-row cols-4 animate-fade-up">
      <div v-for="m in metrics" :key="m.label" class="glass stat-card">
        <div class="stat-icon" :style="{background:m.color+'20',color:m.color}">{{ m.icon }}</div>
        <div class="stat-value">{{ m.value }}</div>
        <div class="stat-label">{{ m.label }}</div>
      </div>
    </div>

    <!-- Per-Class Chart -->
    <div class="glass animate-fade-up stagger-1">
      <h3 style="font-weight:700;margin-bottom:16px;">📊 各类别性能指标</h3>
      <div id="analysisChart" style="width:100%;height:340px;"></div>
    </div>

    <!-- Class Details -->
    <div class="glass animate-fade-up stagger-2">
      <h3 style="font-weight:700;margin-bottom:16px;">📋 各类别详细数据</h3>
      <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
          <thead>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
              <th style="text-align:left;padding:10px 14px;color:var(--text-tertiary);font-weight:600;font-size:0.78rem;">类别</th>
              <th style="text-align:center;padding:10px 14px;color:var(--text-tertiary);font-weight:600;font-size:0.78rem;">Precision</th>
              <th style="text-align:center;padding:10px 14px;color:var(--text-tertiary);font-weight:600;font-size:0.78rem;">Recall</th>
              <th style="text-align:center;padding:10px 14px;color:var(--text-tertiary);font-weight:600;font-size:0.78rem;">F1 Score</th>
              <th style="text-align:center;padding:10px 14px;color:var(--text-tertiary);font-weight:600;font-size:0.78rem;">Support</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cm in classMetrics" :key="cm.name" style="border-bottom:1px solid rgba(255,255,255,0.03);">
              <td style="padding:10px 14px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <div style="width:10px;height:10px;border-radius:50%;" :style="{background:cm.color}"></div>
                  <span style="font-weight:600;">{{ cm.name }}</span>
                </div>
              </td>
              <td style="text-align:center;padding:10px 14px;">{{ (cm.precision*100).toFixed(1) }}%</td>
              <td style="text-align:center;padding:10px 14px;">{{ (cm.recall*100).toFixed(1) }}%</td>
              <td style="text-align:center;padding:10px 14px;font-weight:700;" :style="{color:cm.color}">{{ cm.f1.toFixed(2) }}</td>
              <td style="text-align:center;padding:10px 14px;color:var(--text-secondary);">{{ cm.support }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Model Info -->
    <div class="glass animate-fade-up stagger-3">
      <h3 style="font-weight:700;margin-bottom:16px;">🤖 模型信息</h3>
      <div class="flex-card-row cols-3" style="margin-bottom:0;">
        <div class="section-card" style="padding:16px;">
          <p style="font-weight:700;margin-bottom:6px;">🏗 模型架构</p>
          <p style="font-size:0.85rem;color:var(--text-secondary);">CNN (Convolutional Neural Network) v2</p>
          <p style="font-size:0.82rem;color:var(--text-tertiary);">优化器：Adam · 损失函数：CrossEntropyLoss</p>
        </div>
        <div class="section-card" style="padding:16px;">
          <p style="font-weight:700;margin-bottom:6px;">📦 数据集</p>
          <p style="font-size:0.85rem;color:var(--text-secondary);">PlantVillage 增强数据集</p>
          <p style="font-size:0.82rem;color:var(--text-tertiary);">总数 5,802 · 训练70% · 验证15% · 测试15%</p>
        </div>
        <div class="section-card" style="padding:16px;">
          <p style="font-weight:700;margin-bottom:6px;">⚡ 推理性能</p>
          <p style="font-size:0.85rem;color:var(--text-secondary);">平均推理时间：1.2s/张</p>
          <p style="font-size:0.82rem;color:var(--text-tertiary);">GPU: RTX 3060 · Batch Size: 32</p>
        </div>
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
.flex-card-row.cols-4 > * {
  flex: 0 0 calc(25% - 13.5px);
}
.flex-card-row.cols-3 > * {
  flex: 0 0 calc(33.333% - 12px);
}
.flex-card-row > .stat-card,
.flex-card-row > .section-card {
  min-width: 0;
}

@media (max-width: 768px) {
  .flex-card-row {
    gap: 12px;
  }
  .flex-card-row.cols-4 > * {
    flex: 0 0 calc(50% - 6px);
  }
  .flex-card-row.cols-3 > * {
    flex: 0 0 calc(50% - 6px);
  }
}

@media (max-width: 480px) {
  .flex-card-row.cols-4 > *,
  .flex-card-row.cols-3 > * {
    flex: 0 0 100%;
  }
}
</style>
