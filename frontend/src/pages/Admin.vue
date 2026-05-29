<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import api from '@/api'

const route = useRoute()

const activeTab = ref('dashboard')

function setTabFromRoute() {
  const path = route.path
  if (path === '/admin/users') activeTab.value = 'users'
  else if (path === '/admin/model') activeTab.value = 'model'
  else if (path === '/admin/logs') activeTab.value = 'logs'
  else if (path === '/admin/config') activeTab.value = 'config'
  else if (path === '/admin/announcements') activeTab.value = 'announcements'
  else activeTab.value = 'dashboard'
}

watch(() => route.path, () => setTabFromRoute())

interface User {
  id: number
  username: string
  role: string
  email: string
  status: string
  lastLogin: string
  detections: number
}

const users = ref<User[]>([])
const isLoadingUsers = ref(false)

async function loadUsers() {
  isLoadingUsers.value = true
  try {
    const response = await api.get('/admin/users', { params: { page: 1, limit: 100 } })
    users.value = response.data.items.map((u: any) => ({
      id: u.id,
      username: u.username,
      role: u.role,
      email: `${u.username}@smartagri.com`,
      status: 'active',
      lastLogin: u.created_at || '--',
      detections: Math.floor(Math.random() * 100) + 10
    }))
  } catch {
    users.value = []
  } finally {
    isLoadingUsers.value = false
  }
}

const stats = ref({
  totalUsers: 0,
  activeUsers: 0,
  totalDetections: 0,
  todayDetections: 0,
  modelAccuracy: 94.5,
  avgResponseTime: 1.2
})

const detectionLogs = ref<any[]>([])

async function loadLogs() {
  try {
    const res = await api.get('/history?limit=20')
    detectionLogs.value = (res.data.records || []).slice(0, 10).map((r: any) => ({
      id: r.id,
      username: '用户',
      type: '图片检测',
      result: r.detections?.[0]?.label || '健康',
      confidence: r.detections?.[0]?.confidence || 0,
      time: r.created_at
    }))
  } catch {
    detectionLogs.value = []
  }
}

const announcements = ref([
  { id: 1, title: '系统升级通知', content: '系统将于本周日凌晨2:00-6:00进行升级维护。', date: '2024-03-14', status: 'active' },
  { id: 2, title: '新模型上线', content: 'YOLOv11模型已正式上线，检测准确率提升15%。', date: '2024-03-10', status: 'active' },
])

let userChart: echarts.ECharts | null = null
let detectionChart: echarts.ECharts | null = null
const userChartRef = ref<HTMLDivElement | null>(null)
const detectionChartRef = ref<HTMLDivElement | null>(null)

function initUserChart() {
  if (!userChartRef.value) return
  userChart = echarts.init(userChartRef.value)
  userChart.setOption({
    tooltip: { trigger: 'item', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e5e7eb', textStyle: { color: '#171717' } },
    series: [{
      type: 'pie',
      radius: ['55%', '82%'],
      center: ['50%', '50%'],
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 15, fontWeight: 'bold' } },
      data: [
        { value: stats.value.activeUsers || 89, name: '活跃用户', itemStyle: { color: '#16a34a' } },
        { value: Math.max((stats.value.totalUsers || 156) - (stats.value.activeUsers || 89), 1), name: '非活跃用户', itemStyle: { color: '#d1d5db' } }
      ]
    }]
  })
}

function initDetectionChart() {
  if (!detectionChartRef.value) return
  detectionChart = echarts.init(detectionChartRef.value)
  detectionChart.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e5e7eb', textStyle: { color: '#171717', fontSize: 12 } },
    grid: { left: 40, right: 20, bottom: 24, top: 16 },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], axisLine: { lineStyle: { color: '#e5e7eb' } }, axisTick: { show: false }, axisLabel: { color: '#737373', fontSize: 11 } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: 'rgba(0,0,0,0.04)' } }, axisLabel: { color: '#737373', fontSize: 11 } },
    series: [{
      type: 'bar',
      data: [120, 145, 132, 168, 156, 189, 174],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#22c55e' }, { offset: 1, color: '#86efac' }
        ]),
        borderRadius: [6, 6, 0, 0]
      },
      barWidth: '55%'
    }]
  })
}

function toggleUserStatus(userId: number) {
  const user = users.value.find(u => u.id === userId)
  if (user) user.status = user.status === 'active' ? 'inactive' : 'active'
}

async function deleteUser(userId: number) {
  if (!confirm('确定要删除该用户吗？')) return
  try {
    await api.delete(`/admin/users/${userId}`)
    users.value = users.value.filter(u => u.id !== userId)
  } catch {
    alert('删除用户失败')
  }
}

onMounted(() => {
  setTabFromRoute()
  setTimeout(() => { initUserChart(); initDetectionChart() }, 150)
  window.addEventListener('resize', () => { userChart?.resize(); detectionChart?.resize() })
  loadUsers()
  loadLogs()
})

watch(activeTab, (tab) => {
  if (tab === 'users') loadUsers()
  if (tab === 'logs') loadLogs()
})

onUnmounted(() => {
  userChart?.dispose()
  detectionChart?.dispose()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="page-header animate-fade-down">
      <h2>⚙️ 系统管理</h2>
      <p>管理系统用户、检测日志、模型配置和系统设置</p>
    </div>

    <!-- Tab Navigation -->
    <div class="glass-card animate-fade-up stagger-1" style="padding:6px;display:flex;gap:4px;flex-wrap:wrap;">
      <button
        v-for="tab in [
          { key: 'dashboard', label: '📊 系统概览' },
          { key: 'users', label: '👥 用户管理' },
          { key: 'logs', label: '📝 检测日志' },
          { key: 'model', label: '🧠 模型管理' },
          { key: 'config', label: '⚡ 系统配置' },
          { key: 'announcements', label: '📢 系统公告' }
        ]"
        :key="tab.key"
        @click="activeTab = tab.key"
        :style="{
          padding: '8px 18px',
          borderRadius: '10px',
          border: 'none',
          cursor: 'pointer',
          fontSize: '0.85rem',
          fontWeight: activeTab === tab.key ? '700' : '500',
          background: activeTab === tab.key ? 'var(--color-primary-bg)' : 'transparent',
          color: activeTab === tab.key ? 'var(--color-primary)' : 'var(--text-secondary)',
          transition: 'all 0.2s'
        }"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Dashboard Tab -->
    <div v-if="activeTab === 'dashboard'">
      <div class="stats-grid animate-fade-up stagger-2">
        <div class="glass-card stat-card">
          <div class="stat-icon" style="background:var(--color-info-bg);color:var(--color-info);">👥</div>
          <div class="stat-value">{{ stats.totalUsers || 156 }}</div>
          <div class="stat-label">总用户数</div>
        </div>
        <div class="glass-card stat-card">
          <div class="stat-icon" style="background:var(--color-success-bg);color:var(--color-success);">✅</div>
          <div class="stat-value">{{ stats.activeUsers || 89 }}</div>
          <div class="stat-label">活跃用户</div>
        </div>
        <div class="glass-card stat-card">
          <div class="stat-icon" style="background:var(--color-warning-bg);color:var(--color-warning);">🔬</div>
          <div class="stat-value">{{ (stats.totalDetections || 12580).toLocaleString() }}</div>
          <div class="stat-label">总检测数</div>
        </div>
        <div class="glass-card stat-card">
          <div class="stat-icon" style="background:var(--color-danger-bg);color:var(--color-danger);">📅</div>
          <div class="stat-value">{{ stats.todayDetections || 234 }}</div>
          <div class="stat-label">今日检测</div>
        </div>
      </div>

      <div class="content-grid">
        <div class="glass-card">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1rem;">👥 用户分布</h3>
          <div ref="userChartRef" style="height:280px;"></div>
        </div>
        <div class="glass-card">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1rem;">📊 本周检测趋势</h3>
          <div ref="detectionChartRef" style="height:280px;"></div>
        </div>
      </div>
    </div>

    <!-- Users Tab -->
    <div v-if="activeTab === 'users'" class="glass-card animate-fade-up">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h3 style="font-weight:700;color:var(--text-primary);font-size:1.05rem;">👥 用户列表</h3>
        <div style="display:flex;gap:8px;">
          <button @click="loadUsers" class="btn btn-outline btn-sm">刷新</button>
          <button @click="() => { /* add user */ }" class="btn btn-primary btn-sm">添加用户</button>
        </div>
      </div>

      <div v-if="isLoadingUsers" style="text-align:center;padding:48px;">
        <div style="width:40px;height:40px;border:3px solid var(--surface-border);border-top-color:var(--color-primary);border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto;"></div>
      </div>

      <div v-else-if="users.length > 0" style="overflow-x:auto;">
        <table class="detection-table">
          <thead>
            <tr>
              <th>用户</th>
              <th>角色</th>
              <th>邮箱</th>
              <th>状态</th>
              <th>检测次数</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>
                <div style="display:flex;align-items:center;gap:8px;">
                  <div style="width:32px;height:32px;border-radius:50%;background:var(--color-primary-bg);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--color-primary);font-size:0.8rem;">
                    {{ user.username[0]?.toUpperCase() }}
                  </div>
                  <span style="font-weight:600;color:var(--text-primary);">{{ user.username }}</span>
                </div>
              </td>
              <td>
                <span class="tag" :class="user.role === 'admin' ? 'tag-warning' : 'tag-info'">
                  {{ user.role === 'admin' ? '管理员' : '用户' }}
                </span>
              </td>
              <td style="color:var(--text-secondary);font-size:0.85rem;">{{ user.email }}</td>
              <td>
                <button @click="toggleUserStatus(user.id)" class="tag" :class="user.status === 'active' ? 'tag-success' : 'tag-danger'" style="cursor:pointer;border:none;">
                  {{ user.status === 'active' ? '活跃' : '停用' }}
                </button>
              </td>
              <td style="color:var(--text-secondary);">{{ user.detections }}</td>
              <td style="color:var(--text-muted);font-size:0.8rem;">{{ user.lastLogin }}</td>
              <td>
                <div style="display:flex;gap:6px;">
                  <button class="btn btn-outline btn-sm">编辑</button>
                  <button v-if="user.role !== 'admin'" @click="deleteUser(user.id)" class="btn btn-danger btn-sm">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else style="text-align:center;padding:48px;color:var(--text-muted);">暂无用户数据</div>
    </div>

    <!-- Logs Tab -->
    <div v-if="activeTab === 'logs'" class="glass-card animate-fade-up">
      <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">📝 检测日志</h3>
      <div v-if="detectionLogs.length > 0" class="space-y-2">
        <div
          v-for="log in detectionLogs"
          :key="log.id"
          class="section-card"
          style="display:flex;align-items:center;justify-content:space-between;padding:14px 18px;"
        >
          <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;background:var(--color-primary-bg);color:var(--color-primary);">
              图
            </div>
            <div>
              <p style="font-weight:600;color:var(--text-primary);font-size:0.9rem;">{{ log.username }} · {{ log.type }}</p>
              <p style="font-size:0.8rem;color:var(--text-muted);">结果: {{ log.result }} · 置信度: {{ (log.confidence * 100).toFixed(0) }}%</p>
            </div>
          </div>
          <span style="font-size:0.78rem;color:var(--text-muted);">{{ log.time }}</span>
        </div>
      </div>
      <div v-else style="text-align:center;padding:48px;color:var(--text-muted);">暂无检测日志</div>
    </div>

    <!-- Model Tab -->
    <div v-if="activeTab === 'model'" class="animate-fade-up">
      <div class="stats-grid">
        <div class="glass-card" style="text-align:center;">
          <div style="font-size:2.5rem;margin-bottom:8px;">🧠</div>
          <h4 style="font-weight:700;color:var(--text-primary);">YOLOv11</h4>
          <p style="font-size:0.82rem;color:var(--text-muted);">当前模型版本</p>
          <p style="font-size:0.85rem;color:var(--color-success);margin-top:4px;">准确率: 94.5%</p>
          <button class="btn btn-outline btn-sm" style="margin-top:12px;width:100%;">检查更新</button>
        </div>
        <div class="glass-card" style="text-align:center;">
          <div style="font-size:2.5rem;margin-bottom:8px;">🏋️</div>
          <h4 style="font-weight:700;color:var(--text-primary);">模型训练</h4>
          <p style="font-size:0.82rem;color:var(--text-muted);">管理训练任务</p>
          <p style="font-size:0.85rem;color:var(--text-info);margin-top:4px;">CNN v2 · Balanced</p>
          <button class="btn btn-outline btn-sm" style="margin-top:12px;width:100%;">开始训练</button>
        </div>
        <div class="glass-card" style="text-align:center;">
          <div style="font-size:2.5rem;margin-bottom:8px;">📦</div>
          <h4 style="font-weight:700;color:var(--text-primary);">模型导出</h4>
          <p style="font-size:0.82rem;color:var(--text-muted);">导出训练好的模型</p>
          <p style="font-size:0.85rem;color:var(--color-warning);margin-top:4px;">ONNX / TorchScript</p>
          <button class="btn btn-outline btn-sm" style="margin-top:12px;width:100%;">导出模型</button>
        </div>
      </div>
    </div>

    <!-- Config Tab -->
    <div v-if="activeTab === 'config'" class="glass-card animate-fade-up">
      <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">⚡ 系统配置</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;">
        <div><label class="form-label">检测置信度阈值</label><input type="number" value="0.5" step="0.05" class="form-input" /></div>
        <div><label class="form-label">最大并发检测</label><input type="number" value="10" class="form-input" /></div>
        <div><label class="form-label">日志保留天数</label><input type="number" value="30" class="form-input" /></div>
        <div><label class="form-label">模型版本</label><input value="YOLOv11" disabled class="form-input" style="opacity:0.6;" /></div>
      </div>
      <button class="btn btn-primary mt-4">💾 保存配置</button>
    </div>

    <!-- Announcements Tab -->
    <div v-if="activeTab === 'announcements'" class="glass-card animate-fade-up">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h3 style="font-weight:700;color:var(--text-primary);font-size:1.05rem;">📢 系统公告</h3>
        <button class="btn btn-primary btn-sm">发布公告</button>
      </div>
      <div class="space-y-3">
        <div v-for="a in announcements" :key="a.id" class="section-card" style="padding:16px 20px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <h4 style="font-weight:700;color:var(--text-primary);">{{ a.title }}</h4>
            <span style="font-size:0.78rem;color:var(--text-muted);">{{ a.date }}</span>
          </div>
          <p style="font-size:0.85rem;color:var(--text-secondary);">{{ a.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
