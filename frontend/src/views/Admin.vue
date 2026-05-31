<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const activeTab = ref('dashboard')

// ── User types ──
interface User {
  id: number
  username: string
  role: string
  email: string | null
  phone: string | null
  is_active: boolean
  created_at: string
}

// ═══════════ Dashboard Stats ═══════════
const stats = ref({
  totalUsers: 0,
  todayDetections: 0,
  modelAccuracy: 0,
  systemUptimeDays: 0,
})
const isLoadingStats = ref(false)
const weeklyChartData = ref<any[]>([])
const roleChartData = ref<any[]>([])

async function loadStats() {
  isLoadingStats.value = true
  try {
    const res = await api.get('/admin/stats')
    const d = res.data
    stats.value = {
      totalUsers: d.totalUsers || 0,
      todayDetections: d.todayDetections || 0,
      modelAccuracy: d.modelAccuracy || 0,
      systemUptimeDays: d.systemUptimeDays || 0,
    }
    weeklyChartData.value = d.weeklyData || []
    roleChartData.value = d.roleDistribution || []
    // 数据加载完成后初始化图表
    await nextTick()
    setTimeout(() => {
      initUserChart()
      initDetectionChart()
    }, 100)
  } catch {
    // keep defaults
  } finally {
    isLoadingStats.value = false
  }
}

// ═══════════ User Management ═══════════
const users = ref<User[]>([])
const isLoadingUsers = ref(false)
const userPage = ref(1)
const userLimit = ref(10)
const userTotal = ref(0)
const userSearch = ref('')
const totalPages = computed(() => Math.ceil(userTotal.value / userLimit.value) || 1)

async function loadUsers() {
  isLoadingUsers.value = true
  try {
    const params: any = { page: userPage.value, limit: userLimit.value }
    if (userSearch.value) params.search = userSearch.value
    const res = await api.get('/admin/users', { params })
    users.value = res.data.items
    userTotal.value = res.data.total
  } catch {
    users.value = []
  } finally {
    isLoadingUsers.value = false
  }
}

function onSearch() { userPage.value = 1; loadUsers() }
function goToPage(p: number) { userPage.value = p; loadUsers() }

async function toggleUserStatus(userId: number) {
  try {
    const res = await api.put(`/admin/users/${userId}/toggle`)
    const user = users.value.find(u => u.id === userId)
    if (user) user.is_active = res.data.is_active
  } catch { alert('操作失败') }
}

async function deleteUser(userId: number) {
  if (!confirm('确定要删除该用户吗？此操作不可撤销。')) return
  try {
    await api.delete(`/admin/users/${userId}`)
    users.value = users.value.filter(u => u.id !== userId)
    userTotal.value--
  } catch { alert('删除用户失败') }
}

// ── User Modal State ──
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingUser = ref<User | null>(null)
const modalLoading = ref(false)
const modalError = ref('')
const addForm = ref({ username: '', password: '', role: 'user', email: '', phone: '' })
const editForm = ref({ username: '', password: '', role: 'user', email: '', phone: '' })

function openAddModal() {
  addForm.value = { username: '', password: '', role: 'user', email: '', phone: '' }
  modalError.value = ''
  showAddModal.value = true
}

async function handleAddUser() {
  modalError.value = ''
  if (!addForm.value.username || !addForm.value.password) { modalError.value = '用户名和密码为必填项'; return }
  modalLoading.value = true
  try {
    await api.post('/admin/users', addForm.value)
    showAddModal.value = false
    loadUsers()
  } catch (e: any) {
    modalError.value = e?.response?.data?.detail || '创建失败'
  } finally { modalLoading.value = false }
}

function openEditModal(user: User) {
  editingUser.value = user
  editForm.value = { username: user.username, password: '', role: user.role, email: user.email || '', phone: user.phone || '' }
  modalError.value = ''
  showEditModal.value = true
}

async function handleEditUser() {
  if (!editingUser.value) return
  modalError.value = ''
  const payload: any = { username: editForm.value.username, role: editForm.value.role, email: editForm.value.email || null, phone: editForm.value.phone || null }
  if (editForm.value.password) payload.password = editForm.value.password
  modalLoading.value = true
  try {
    await api.put(`/admin/users/${editingUser.value.id}`, payload)
    showEditModal.value = false
    loadUsers()
  } catch (e: any) {
    modalError.value = e?.response?.data?.detail || '更新失败'
  } finally { modalLoading.value = false }
}

// ═══════════ Detection Logs ═══════════
const detectionLogs = ref<any[]>([])
const isLoadingLogs = ref(false)
const logPage = ref(1)
const logTotal = ref(0)
const logLimit = ref(20)
const logStartDate = ref('')
const logEndDate = ref('')
const logTotalPages = computed(() => Math.ceil(logTotal.value / logLimit.value) || 1)

async function loadLogs() {
  isLoadingLogs.value = true
  try {
    const params: any = { page: logPage.value, limit: logLimit.value }
    if (logStartDate.value) params.start_date = logStartDate.value
    if (logEndDate.value) params.end_date = logEndDate.value
    const res = await api.get('/admin/logs', { params })
    detectionLogs.value = res.data.items || []
    logTotal.value = res.data.total || 0
  } catch { detectionLogs.value = [] } finally { isLoadingLogs.value = false }
}

function onLogSearch() { logPage.value = 1; loadLogs() }
function goToLogPage(p: number) { logPage.value = p; loadLogs() }

// ── Image Viewer ──
const showImageModal = ref(false)
const viewingImage = ref('')
const viewingImageId = ref(0)

async function viewDetectionImage(detectionId: number) {
  viewingImageId.value = detectionId
  viewingImage.value = ''
  showImageModal.value = true
  try {
    const res = await api.get(`/admin/detections/${detectionId}/image`)
    viewingImage.value = res.data.image
  } catch {
    viewingImage.value = ''
  }
}

// ═══════════ Model Management ═══════════
const modelInfo = ref<any>(null)
const isLoadingModel = ref(false)
const trainingStatus = ref({ running: false, progress: 0, epoch: 0, total_epochs: 8, message: '' })
let trainingTimer: ReturnType<typeof setInterval> | null = null

async function loadModelInfo() {
  isLoadingModel.value = true
  try {
    const res = await api.get('/admin/model')
    modelInfo.value = res.data
  } catch { modelInfo.value = null } finally { isLoadingModel.value = false }
}

async function fetchTrainingStatus() {
  try {
    const res = await api.get('/admin/model/train/status')
    trainingStatus.value = res.data
  } catch { /* ignore */ }
}

async function startTraining() {
  try {
    const res = await api.post('/admin/model/train')
    if (res.data.success) {
      // Start polling for training status
      if (trainingTimer) clearInterval(trainingTimer)
      trainingTimer = setInterval(async () => {
        await fetchTrainingStatus()
        if (!trainingStatus.value.running) {
          if (trainingTimer) { clearInterval(trainingTimer); trainingTimer = null }
        }
      }, 1500)
    } else {
      alert(res.data.message || '训练启动失败')
    }
  } catch { alert('启动训练失败') }
}

const exportFormat = ref('onnx')
const isExporting = ref(false)
const exportResult = ref('')

async function exportModel() {
  isExporting.value = true
  exportResult.value = ''
  try {
    const res = await api.post('/admin/model/export', null, { params: { format: exportFormat.value } })
    exportResult.value = res.data.message
    setTimeout(() => { exportResult.value = '' }, 5000)
  } catch (e: any) {
    exportResult.value = e?.response?.data?.detail || '导出失败'
  } finally { isExporting.value = false }
}

// ═══════════ System Config ═══════════
const isLoadingConfig = ref(false)
const configSaved = ref(false)
const configForm = ref({
  confidence_threshold: 0.5,
  max_concurrent_detections: 10,
  log_retention_days: 30,
  model_version: 'YOLOv11',
  enable_notifications: true,
  auto_save_results: true,
  detection_timeout: 60,
  max_file_size_mb: 50,
})

async function loadConfig() {
  isLoadingConfig.value = true
  try {
    const res = await api.get('/admin/config')
    configForm.value = { ...configForm.value, ...res.data }
  } catch { /* use defaults */ } finally { isLoadingConfig.value = false }
}

async function saveConfig() {
  isLoadingConfig.value = true
  try {
    await api.put('/admin/config', configForm.value)
    configSaved.value = true
    setTimeout(() => configSaved.value = false, 2000)
  } catch { alert('保存配置失败') } finally { isLoadingConfig.value = false }
}

// ═══════════ Announcements ═══════════
const announcements = ref<any[]>([])
const isLoadingAnnouncements = ref(false)
const showAnnounceModal = ref(false)
const announceForm = ref({ title: '', content: '', status: 'active' })
const announceLoading = ref(false)
const announceError = ref('')
const editingAnnouncement = ref<any>(null)

async function loadAnnouncements() {
  isLoadingAnnouncements.value = true
  try {
    const res = await api.get('/admin/announcements')
    announcements.value = res.data.items || []
  } catch { announcements.value = [] } finally { isLoadingAnnouncements.value = false }
}

function openAnnounceModal(announcement: any = null) {
  editingAnnouncement.value = announcement
  if (announcement) {
    announceForm.value = { title: announcement.title, content: announcement.content, status: announcement.status }
  } else {
    announceForm.value = { title: '', content: '', status: 'active' }
  }
  announceError.value = ''
  showAnnounceModal.value = true
}

async function handleSaveAnnouncement() {
  announceError.value = ''
  if (!announceForm.value.title || !announceForm.value.content) { announceError.value = '标题和内容为必填项'; return }
  announceLoading.value = true
  try {
    if (editingAnnouncement.value) {
      await api.put(`/admin/announcements/${editingAnnouncement.value.id}`, announceForm.value)
    } else {
      await api.post('/admin/announcements', announceForm.value)
    }
    showAnnounceModal.value = false
    loadAnnouncements()
  } catch (e: any) {
    announceError.value = e?.response?.data?.detail || '操作失败'
  } finally { announceLoading.value = false }
}

async function deleteAnnouncement(id: number) {
  if (!confirm('确定要删除该公告吗？')) return
  try {
    await api.delete(`/admin/announcements/${id}`)
    announcements.value = announcements.value.filter(a => a.id !== id)
  } catch { alert('删除公告失败') }
}

// ═══════════ Charts ═══════════
let userChart: echarts.ECharts | null = null
let detectionChart: echarts.ECharts | null = null
const userChartRef = ref<HTMLDivElement | null>(null)
const detectionChartRef = ref<HTMLDivElement | null>(null)

function initUserChart() {
  try {
    if (!userChartRef.value) {
      console.error('用户分布图表容器不存在')
      return
    }
    if (userChart) userChart.dispose()
    userChart = echarts.init(userChartRef.value)

    const data = roleChartData.value.length > 0
      ? roleChartData.value.map((r: any) => ({
          value: r.value || 0, name: r.name,
          itemStyle: { color: r.name === '管理员' ? '#ff9800' : '#4caf50' }
        }))
      : [
          { value: 1, name: '管理员', itemStyle: { color: '#ff9800' } },
          { value: stats.value.totalUsers > 0 ? stats.value.totalUsers - 1 : 0, name: '普通用户', itemStyle: { color: '#4caf50' } }
        ]

    // 过滤掉值为0的项
    const filteredData = data.filter((d: any) => d.value > 0)
    if (filteredData.length === 0) {
      filteredData.push({ value: 1, name: '暂无数据', itemStyle: { color: '#666' } })
    }

    userChart.setOption({
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(15,45,30,0.95)',
        borderColor: 'rgba(76,175,80,0.3)',
        textStyle: { color: '#fff' },
        formatter: '{b}: {c} 人 ({d}%)',
      },
      legend: {
        bottom: 8,
        textStyle: { color: 'rgba(255,255,255,0.6)', fontSize: 12 },
      },
      series: [{
        type: 'pie',
        radius: ['50%', '78%'],
        center: ['50%', '48%'],
        itemStyle: { borderRadius: 8, borderColor: 'rgba(10,40,20,0.5)', borderWidth: 3 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 15, fontWeight: 'bold' } },
        data: filteredData,
      }],
    })
  } catch (error) {
    console.error('初始化用户分布图表失败:', error)
  }
}

function initDetectionChart() {
  try {
    if (!detectionChartRef.value) {
      console.error('检测趋势图表容器不存在')
      return
    }
    if (detectionChart) detectionChart.dispose()
    detectionChart = echarts.init(detectionChartRef.value)

    const hasReal = weeklyChartData.value.length > 0
    const dates = hasReal ? weeklyChartData.value.map((d: any) => d.label || d.date) : ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    const values = hasReal ? weeklyChartData.value.map((d: any) => d.count || 0) : [0, 0, 0, 0, 0, 0, 0]

    detectionChart.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15,45,30,0.95)',
        borderColor: 'rgba(76,175,80,0.3)',
        textStyle: { color: '#fff', fontSize: 12 },
        formatter: (params: any) => `${params[0].name}<br/>检测次数：<b>${params[0].value}</b>`,
      },
      grid: { left: 40, right: 20, bottom: 24, top: 16 },
      xAxis: {
        type: 'category', data: dates,
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
        axisTick: { show: false },
        axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false }, axisTick: { show: false },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
        minInterval: 1,
      },
      series: [{
        type: 'bar',
        data: values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#4caf50' },
            { offset: 1, color: '#a5d6a7' },
          ]),
          borderRadius: [6, 6, 0, 0],
        },
        barWidth: '55%',
      }],
    })
  } catch (error) {
    console.error('初始化检测趋势图表失败:', error)
  }
}

// ═══════════ Lifecycle ═══════════
onMounted(() => {
  loadStats()
  loadUsers()
  loadLogs()
  loadModelInfo()
  loadConfig()
  loadAnnouncements()
  fetchTrainingStatus()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  userChart?.dispose()
  detectionChart?.dispose()
  window.removeEventListener('resize', handleResize)
  if (trainingTimer) clearInterval(trainingTimer)
})

function handleResize() {
  try {
    userChart?.resize()
    detectionChart?.resize()
  } catch (error) {
    console.error('图表resize失败:', error)
  }
}

watch(activeTab, (tab) => {
  if (tab === 'users') loadUsers()
  if (tab === 'logs') loadLogs()
  if (tab === 'dashboard') { 
    loadStats()
    // 切换到dashboard时重新初始化图表
    nextTick(() => {
      setTimeout(() => {
        initUserChart()
        initDetectionChart()
      }, 100)
    })
  }
  if (tab === 'model') { loadModelInfo(); fetchTrainingStatus() }
  if (tab === 'config') loadConfig()
  if (tab === 'announcements') loadAnnouncements()
})

// ── Tab defs ──
const tabs = [
  { key: 'dashboard', label: '系统概览', icon: 'M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zm0 6a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1h-4a1 1 0 01-1-1v-5zM4 13a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1v-5z' },
  { key: 'users', label: '用户管理', icon: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2m8-10a4 4 0 110-8 4 4 0 010 8zm11 10v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75' },
  { key: 'logs', label: '检测日志', icon: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 1.5V8h4.5M8 13h8m-8 4h5' },
  { key: 'model', label: '模型管理', icon: 'M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5zM14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z' },
  { key: 'config', label: '系统配置', icon: 'M12 15a3 3 0 100-6 3 3 0 000 6zm8-3c0 .34-.02.68-.06 1.02l2.13 1.67-2 3.46-2.5-1.03a7.03 7.03 0 01-1.74 1.01L15.47 21h-4l-.36-2.87a7.03 7.03 0 01-1.74-1.01l-2.5 1.03-2-3.46 2.13-1.67A7.13 7.13 0 017 12c0-.34.02-.68.06-1.02L4.93 9.31l2-3.46 2.5 1.03a7.03 7.03 0 011.74-1.01L11.53 3h4l.36 2.87c.62.25 1.2.58 1.74 1.01l2.5-1.03 2 3.46-2.13 1.67c.04.34.06.68.06 1.02z' },
  { key: 'announcements', label: '系统公告', icon: 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z' },
]
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>系统管理</h2>
      <p>管理系统用户、检测日志、模型配置和系统设置</p>
    </div>

    <!-- Tab Navigation -->
    <div class="glass animate-fade-up stagger-1" style="padding:6px;display:flex;gap:4px;flex-wrap:wrap;">
      <button
        v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        :style="{
          padding: '8px 18px', borderRadius: '10px', border: 'none', cursor: 'pointer',
          fontSize: '0.85rem', fontWeight: activeTab === tab.key ? '700' : '500',
          background: activeTab === tab.key ? 'var(--color-primary-bg, rgba(76,175,80,0.15))' : 'transparent',
          color: activeTab === tab.key ? 'var(--color-accent, #4caf50)' : 'var(--text-secondary)',
          transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '6px',
        }"
      >
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path :d="tab.icon"/></svg>
        {{ tab.label }}
      </button>
    </div>

    <!-- ═══════════ Dashboard ═══════════ -->
    <div v-if="activeTab === 'dashboard'">
      <!-- Loading -->
      <div v-if="isLoadingStats" class="glass" style="text-align:center;padding:64px;">
        <div class="spinner-lg"></div>
        <p style="margin-top:16px;color:var(--text-muted);">正在加载统计数据...</p>
      </div>

      <template v-else>
        <!-- Stat Cards -->
        <div class="stats-grid animate-fade-up stagger-2">
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(33,150,243,0.15);">
              <svg width="16" height="16" fill="none" stroke="#2196f3" stroke-width="2" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2m8-10a4 4 0 110-8 4 4 0 010 8z"/></svg>
            </div>
            <div class="stat-value">{{ stats.totalUsers.toLocaleString() }}</div>
            <div class="stat-label">总用户数</div>
          </div>
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(244,67,54,0.15);">
              <svg width="16" height="16" fill="none" stroke="#f44336" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="stat-value">{{ stats.todayDetections.toLocaleString() }}</div>
            <div class="stat-label">今日检测数</div>
          </div>
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(76,175,80,0.15);">
              <svg width="16" height="16" fill="none" stroke="#4caf50" stroke-width="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
            </div>
            <div class="stat-value">{{ stats.modelAccuracy.toFixed(1) }}%</div>
            <div class="stat-label">模型准确率</div>
          </div>
          <div class="glass stat-card">
            <div class="stat-icon" style="background:rgba(255,152,0,0.15);">
              <svg width="16" height="16" fill="none" stroke="#ff9800" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="stat-value">{{ stats.systemUptimeDays.toLocaleString() }}</div>
            <div class="stat-label">系统运行天数</div>
          </div>
        </div>

        <!-- Charts -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:4px;font-size:1rem;">用户分布</h3>
            <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px;">管理员 / 普通用户占比</p>
            <div ref="userChartRef" style="height:300px;position:relative;">
              <div v-if="!userChart" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:var(--text-muted);font-size:0.85rem;">
                加载中...
              </div>
            </div>
          </div>
          <div class="glass">
            <h3 style="font-weight:700;margin-bottom:4px;font-size:1rem;">本周检测趋势</h3>
            <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px;">近7天每日检测次数</p>
            <div ref="detectionChartRef" style="height:300px;position:relative;">
              <div v-if="!detectionChart" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:var(--text-muted);font-size:0.85rem;">
                加载中...
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ═══════════ Users Tab ═══════════ -->
    <div v-if="activeTab === 'users'" class="glass animate-fade-up">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
        <h3 style="font-weight:700;font-size:1.05rem;">用户列表</h3>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
          <div class="search-wrap">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            <input v-model="userSearch" placeholder="搜索用户名或邮箱..." @keyup.enter="onSearch" class="search-input" />
          </div>
          <button @click="onSearch" class="btn btn-outline btn-sm">搜索</button>
          <button @click="openAddModal" class="btn btn-primary btn-sm">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            添加用户
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoadingUsers" style="text-align:center;padding:48px;">
        <div class="spinner"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="users.length === 0" style="text-align:center;padding:48px;color:var(--text-muted);">
        <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="margin:0 auto 12px;opacity:0.3;"><circle cx="12" cy="8" r="4"/><path d="M6 21v-2a4 4 0 014-4h4a4 4 0 014 4v2"/></svg>
        <p>{{ userSearch ? '未找到匹配的用户' : '暂无用户数据' }}</p>
      </div>

      <!-- User Table -->
      <template v-else>
        <div class="user-table-wrap">
          <table class="user-table">
            <thead>
              <tr>
                <th class="col-user">用户</th>
                <th class="col-role">角色</th>
                <th class="col-email">邮箱</th>
                <th class="col-phone">手机号</th>
                <th class="col-status">状态</th>
                <th class="col-date">注册时间</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <div class="user-cell">
                    <div class="user-avatar-sm">{{ user.username[0]?.toUpperCase() }}</div>
                    <span class="user-name-text">{{ user.username }}</span>
                  </div>
                </td>
                <td><span class="tag" :class="user.role === 'admin' ? 'tag-warning' : 'tag-info'">{{ user.role === 'admin' ? '管理员' : '用户' }}</span></td>
                <td class="cell-secondary">{{ user.email || '—' }}</td>
                <td class="cell-secondary">{{ user.phone || '—' }}</td>
                <td>
                  <button @click="toggleUserStatus(user.id)" :disabled="user.role === 'admin'" class="status-toggle" :title="user.is_active ? '点击停用' : '点击启用'">
                    <span class="status-dot" :class="user.is_active ? 'dot-active' : 'dot-inactive'"></span>
                    <span>{{ user.is_active ? '活跃' : '停用' }}</span>
                  </button>
                </td>
                <td class="cell-muted">{{ user.created_at }}</td>
                <td>
                  <div class="action-btns">
                    <button @click="openEditModal(user)" class="btn btn-outline btn-sm">编辑</button>
                    <button v-if="user.role !== 'admin'" @click="deleteUser(user.id)" class="btn btn-outline btn-sm btn-danger">删除</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="user-mobile-cards">
          <div v-for="user in users" :key="user.id" class="user-mobile-card section-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div class="user-cell">
                <div class="user-avatar-sm">{{ user.username[0]?.toUpperCase() }}</div>
                <div>
                  <div class="user-name-text">{{ user.username }}</div>
                  <div style="font-size:0.72rem;color:var(--text-muted);">{{ user.created_at }}</div>
                </div>
              </div>
              <span class="tag" :class="user.role === 'admin' ? 'tag-warning' : 'tag-info'">{{ user.role === 'admin' ? '管理员' : '用户' }}</span>
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;font-size:0.82rem;color:var(--text-secondary);margin-bottom:10px;">
              <div><span style="color:var(--text-muted);">邮箱：</span>{{ user.email || '—' }}</div>
              <div><span style="color:var(--text-muted);">手机：</span>{{ user.phone || '—' }}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <button @click="toggleUserStatus(user.id)" :disabled="user.role === 'admin'" class="status-toggle">
                <span class="status-dot" :class="user.is_active ? 'dot-active' : 'dot-inactive'"></span>
                <span>{{ user.is_active ? '活跃' : '停用' }}</span>
              </button>
              <div class="action-btns">
                <button @click="openEditModal(user)" class="btn btn-outline btn-sm">编辑</button>
                <button v-if="user.role !== 'admin'" @click="deleteUser(user.id)" class="btn btn-outline btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination-bar">
          <button @click="goToPage(userPage - 1)" :disabled="userPage <= 1" class="btn btn-outline btn-sm">上一页</button>
          <template v-for="p in totalPages" :key="p">
            <button
              v-if="p === 1 || p === totalPages || Math.abs(p - userPage) <= 2"
              @click="goToPage(p)"
              class="btn btn-sm"
              :class="p === userPage ? 'btn-primary' : 'btn-outline'"
              style="min-width:36px;"
            >{{ p }}</button>
            <span v-else-if="Math.abs(p - userPage) === 3" style="color:var(--text-muted);">...</span>
          </template>
          <button @click="goToPage(userPage + 1)" :disabled="userPage >= totalPages" class="btn btn-outline btn-sm">下一页</button>
          <span class="pagination-total">共 {{ userTotal }} 条</span>
        </div>
      </template>
    </div>

    <!-- ═══════════ Logs Tab ═══════════ -->
    <div v-if="activeTab === 'logs'" class="glass animate-fade-up">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
        <h3 style="font-weight:700;font-size:1.05rem;">检测日志</h3>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <input v-model="logStartDate" type="date" class="date-input" title="开始日期" />
          <span style="color:var(--text-muted);font-size:0.8rem;">至</span>
          <input v-model="logEndDate" type="date" class="date-input" title="结束日期" />
          <button @click="onLogSearch" class="btn btn-outline btn-sm">筛选</button>
          <button @click="logStartDate='';logEndDate='';onLogSearch()" class="btn btn-outline btn-sm" style="font-size:0.75rem;">清除</button>
          <span style="font-size:0.8rem;color:var(--text-muted);">共 {{ logTotal }} 条</span>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoadingLogs" style="text-align:center;padding:48px;">
        <div class="spinner"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="detectionLogs.length === 0" style="text-align:center;padding:48px;color:var(--text-muted);">
        <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="margin:0 auto 12px;opacity:0.3;"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        <p>暂无检测日志</p>
      </div>

      <!-- Log List -->
      <template v-else>
        <div class="space-y-2">
          <div v-for="log in detectionLogs" :key="log.id" class="section-card log-card">
            <div class="log-left">
              <div :style="{width:'40px',height:'40px',borderRadius:'10px',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'0.75rem',fontWeight:'700',background:log.type==='视频检测'?'rgba(33,150,243,0.15)':'rgba(76,175,80,0.15)',color:log.type==='视频检测'?'#2196f3':'#4caf50',flexShrink:'0'}">{{ log.type === '视频检测' ? '视' : '图' }}</div>
              <div style="flex:1;min-width:0;">
                <p style="font-weight:600;font-size:0.9rem;">{{ log.username }} · {{ log.type }}</p>
                <p style="font-size:0.8rem;color:var(--text-muted);">
                  结果: <span style="color:var(--text-primary);font-weight:500;">{{ log.result }}</span>
                  <span v-if="log.confidence > 0" style="margin-left:8px;">· 置信度: <span style="color:#4caf50;font-weight:600;">{{ (log.confidence * 100).toFixed(0) }}%</span></span>
                  <span style="margin-left:8px;">· 检测数: <span style="color:var(--text-primary);font-weight:600;">{{ log.detection_count }}</span></span>
                </p>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;flex-shrink:0;">
              <button v-if="log.has_image" @click="viewDetectionImage(log.id)" class="btn btn-outline btn-sm" style="white-space:nowrap;">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                查看
              </button>
              <span style="font-size:0.78rem;color:var(--text-muted);white-space:nowrap;">{{ log.time }}</span>
            </div>
          </div>
        </div>

        <!-- Log Pagination -->
        <div v-if="logTotalPages > 1" class="pagination-bar">
          <button @click="goToLogPage(logPage - 1)" :disabled="logPage <= 1" class="btn btn-outline btn-sm">上一页</button>
          <template v-for="p in logTotalPages" :key="'lp'+p">
            <button
              v-if="p === 1 || p === logTotalPages || Math.abs(p - logPage) <= 2"
              @click="goToLogPage(p)"
              class="btn btn-sm"
              :class="p === logPage ? 'btn-primary' : 'btn-outline'"
              style="min-width:36px;"
            >{{ p }}</button>
            <span v-else-if="Math.abs(p - logPage) === 3" style="color:var(--text-muted);">...</span>
          </template>
          <button @click="goToLogPage(logPage + 1)" :disabled="logPage >= logTotalPages" class="btn btn-outline btn-sm">下一页</button>
          <span class="pagination-total">共 {{ logTotal }} 条</span>
        </div>
      </template>
    </div>

    <!-- ═══════════ Model Tab ═══════════ -->
    <div v-if="activeTab === 'model'" class="animate-fade-up">
      <!-- Loading -->
      <div v-if="isLoadingModel" style="text-align:center;padding:48px;">
        <div class="spinner-lg"></div>
        <p style="margin-top:12px;color:var(--text-muted);">加载模型信息...</p>
      </div>

      <template v-else>
        <!-- Model Cards -->
        <div class="stats-grid">
          <div class="glass" style="text-align:center;">
            <svg width="48" height="48" fill="none" stroke="#4caf50" stroke-width="1.5" viewBox="0 0 24 24" style="margin-bottom:12px;"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5zM14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z"/></svg>
            <h4 style="font-weight:700;">{{ modelInfo?.yolo?.name || 'YOLOv11' }}</h4>
            <p style="font-size:0.82rem;color:var(--text-muted);">目标检测模型</p>
            <p style="font-size:0.85rem;color:#4caf50;margin-top:4px;">mAP: {{ modelInfo?.yolo?.mAP || '—' }}% · {{ modelInfo?.yolo?.classes || '—' }} 类</p>
            <p style="font-size:0.72rem;color:var(--text-muted);margin-top:2px;">状态: <span style="color:#4caf50;font-weight:600;">{{ modelInfo?.yolo?.status === 'active' ? '运行中' : modelInfo?.yolo?.status || '—' }}</span></p>
            <p v-if="modelInfo?.yolo?.file" style="font-size:0.72rem;color:var(--text-muted);margin-top:2px;">文件: {{ modelInfo.yolo.file }}</p>
          </div>
          <div class="glass" style="text-align:center;">
            <svg width="48" height="48" fill="none" stroke="#2196f3" stroke-width="1.5" viewBox="0 0 24 24" style="margin-bottom:12px;"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <h4 style="font-weight:700;">{{ modelInfo?.cnn?.name || 'CNN v2' }}</h4>
            <p style="font-size:0.82rem;color:var(--text-muted);">分类模型</p>
            <p style="font-size:0.85rem;color:#2196f3;margin-top:4px;">准确率: {{ modelInfo?.cnn?.accuracy || '—' }}% · {{ modelInfo?.cnn?.classes || '—' }} 类</p>
            <p style="font-size:0.72rem;color:var(--text-muted);margin-top:2px;">训练方式: {{ modelInfo?.cnn?.training_method || '—' }}</p>
            <p v-if="modelInfo?.cnn?.file" style="font-size:0.72rem;color:var(--text-muted);margin-top:2px;">文件: {{ modelInfo.cnn.file }}</p>
          </div>
          <div class="glass" style="text-align:center;">
            <svg width="48" height="48" fill="none" stroke="#ff9800" stroke-width="1.5" viewBox="0 0 24 24" style="margin-bottom:12px;"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <h4 style="font-weight:700;">模型导出</h4>
            <p style="font-size:0.82rem;color:var(--text-muted);">导出训练好的模型</p>
            <div style="margin-top:8px;">
              <select v-model="exportFormat" class="form-input" style="width:auto;display:inline-block;font-size:0.8rem;">
                <option v-for="fmt in (modelInfo?.export_formats || ['ONNX', 'TorchScript'])" :key="fmt" :value="fmt.toLowerCase()">{{ fmt }}</option>
              </select>
            </div>
            <button @click="exportModel" :disabled="isExporting" class="btn btn-primary btn-sm" style="margin-top:10px;width:100%;">
              <span v-if="isExporting" class="btn-spinner" style="width:14px;height:14px;border-width:2px;"></span>
              <template v-else>导出模型</template>
            </button>
            <p v-if="exportResult" style="font-size:0.78rem;color:#4caf50;margin-top:6px;font-weight:500;">{{ exportResult }}</p>
          </div>
        </div>

        <!-- Training Progress -->
        <div class="glass" style="margin-top:20px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
            <div>
              <h3 style="font-weight:700;font-size:1.05rem;">模型训练</h3>
              <p style="font-size:0.78rem;color:var(--text-muted);">启动模型训练以提升检测精度</p>
            </div>
            <button @click="startTraining" :disabled="trainingStatus.running" class="btn btn-primary btn-sm">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              {{ trainingStatus.running ? '训练中...' : '开始训练' }}
            </button>
          </div>

          <div v-if="trainingStatus.running || trainingStatus.progress > 0" style="margin-top:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:0.8rem;">
              <span style="color:var(--text-secondary);">进度</span>
              <span style="color:#4caf50;font-weight:600;">{{ trainingStatus.progress }}%</span>
            </div>
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{
                  width: trainingStatus.progress + '%',
                  background: trainingStatus.progress >= 100
                    ? 'linear-gradient(90deg, #4caf50, #81c784)'
                    : 'linear-gradient(90deg, #2196f3, #4caf50)',
                }"
              ></div>
            </div>
            <p style="font-size:0.8rem;color:var(--text-muted);margin-top:8px;">
              <span v-if="trainingStatus.epoch > 0">Epoch {{ trainingStatus.epoch }}/{{ trainingStatus.total_epochs }} · </span>
              {{ trainingStatus.message }}
            </p>
          </div>

          <div v-else style="text-align:center;padding:24px;color:var(--text-muted);">
            <svg width="36" height="36" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="margin:0 auto 8px;opacity:0.3;"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            <p style="font-size:0.85rem;">点击「开始训练」启动模拟训练流程</p>
          </div>
        </div>

        <!-- Export Formats Info -->
        <div class="glass" style="margin-top:16px;">
          <h3 style="font-weight:700;font-size:1rem;margin-bottom:8px;">支持导出格式</h3>
          <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <span v-for="fmt in (modelInfo?.export_formats || ['ONNX', 'TorchScript', 'TensorFlow SavedModel'])" :key="fmt" class="tag tag-info" style="font-size:0.78rem;padding:6px 14px;">{{ fmt }}</span>
          </div>
        </div>
      </template>
    </div>

    <!-- ═══════════ Config Tab ═══════════ -->
    <div v-if="activeTab === 'config'" class="glass animate-fade-up">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px;">
        <h3 style="font-weight:700;font-size:1.05rem;">系统配置</h3>
        <div style="display:flex;align-items:center;gap:10px;">
          <span v-if="configSaved" style="font-size:0.8rem;color:#4caf50;font-weight:600;">✓ 已保存</span>
          <button @click="saveConfig" class="btn btn-primary btn-sm" :disabled="isLoadingConfig">
            <span v-if="isLoadingConfig" class="btn-spinner" style="width:14px;height:14px;border-width:2px;"></span>
            <template v-else>保存配置</template>
          </button>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;">
        <div class="section-card" style="padding:16px;">
          <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:8px;color:var(--text-primary);">检测置信度阈值</label>
          <input v-model.number="configForm.confidence_threshold" type="number" step="0.05" min="0.1" max="1.0" class="form-input" style="width:100%;" />
          <p style="font-size:0.72rem;color:var(--text-muted);margin-top:4px;">当前: {{ (configForm.confidence_threshold * 100).toFixed(0) }}%</p>
        </div>
        <div class="section-card" style="padding:16px;">
          <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:8px;color:var(--text-primary);">最大并发检测数</label>
          <input v-model.number="configForm.max_concurrent_detections" type="number" min="1" max="100" class="form-input" style="width:100%;" />
        </div>
        <div class="section-card" style="padding:16px;">
          <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:8px;color:var(--text-primary);">日志保留天数</label>
          <input v-model.number="configForm.log_retention_days" type="number" min="1" max="365" class="form-input" style="width:100%;" />
        </div>
        <div class="section-card" style="padding:16px;">
          <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:8px;color:var(--text-primary);">模型版本</label>
          <input v-model="configForm.model_version" class="form-input" style="width:100%;" />
        </div>
        <div class="section-card" style="padding:16px;">
          <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:8px;color:var(--text-primary);">检测超时 (秒)</label>
          <input v-model.number="configForm.detection_timeout" type="number" min="10" max="600" class="form-input" style="width:100%;" />
        </div>
        <div class="section-card" style="padding:16px;">
          <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:8px;color:var(--text-primary);">最大文件大小 (MB)</label>
          <input v-model.number="configForm.max_file_size_mb" type="number" min="1" max="500" class="form-input" style="width:100%;" />
        </div>
        <div class="section-card" style="padding:16px;display:flex;align-items:center;gap:12px;">
          <label style="display:flex;align-items:center;gap:10px;cursor:pointer;font-size:0.85rem;font-weight:600;color:var(--text-primary);">
            <input v-model="configForm.enable_notifications" type="checkbox" style="width:18px;height:18px;accent-color:#4caf50;" /> 启用通知
          </label>
        </div>
        <div class="section-card" style="padding:16px;display:flex;align-items:center;gap:12px;">
          <label style="display:flex;align-items:center;gap:10px;cursor:pointer;font-size:0.85rem;font-weight:600;color:var(--text-primary);">
            <input v-model="configForm.auto_save_results" type="checkbox" style="width:18px;height:18px;accent-color:#4caf50;" /> 自动保存结果
          </label>
        </div>
      </div>
    </div>

    <!-- ═══════════ Announcements Tab ═══════════ -->
    <div v-if="activeTab === 'announcements'" class="glass animate-fade-up">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
        <h3 style="font-weight:700;font-size:1.05rem;">系统公告</h3>
        <button @click="openAnnounceModal()" class="btn btn-primary btn-sm">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          发布公告
        </button>
      </div>

      <!-- Loading -->
      <div v-if="isLoadingAnnouncements" style="text-align:center;padding:48px;">
        <div class="spinner"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="announcements.length === 0" style="text-align:center;padding:48px;color:var(--text-muted);">
        <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24" style="margin:0 auto 12px;opacity:0.3;"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
        <p>暂无公告</p>
      </div>

      <!-- Announcement List -->
      <template v-else>
        <div class="space-y-3">
          <div v-for="a in announcements" :key="a.id" class="section-card" style="padding:18px 20px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
              <div style="display:flex;align-items:center;gap:10px;">
                <span class="tag" :class="a.status === 'active' ? 'tag-success' : 'tag-danger'" style="font-size:0.7rem;">{{ a.status === 'active' ? '已发布' : '已下线' }}</span>
                <h4 style="font-weight:700;">{{ a.title }}</h4>
              </div>
              <span style="font-size:0.78rem;color:var(--text-muted);white-space:nowrap;">{{ a.date }}</span>
            </div>
            <p style="font-size:0.85rem;color:var(--text-secondary);line-height:1.6;margin-bottom:10px;">{{ a.content }}</p>
            <div style="display:flex;gap:6px;">
              <button @click="openAnnounceModal(a)" class="btn btn-outline btn-sm">编辑</button>
              <button @click="deleteAnnouncement(a.id)" class="btn btn-outline btn-sm btn-danger">删除</button>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ═══════════ Add User Modal ═══════════ -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-card glass animate-scale">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <h3 style="font-weight:700;font-size:1.1rem;">添加用户</h3>
          <button @click="showAddModal = false" class="modal-close-btn">&times;</button>
        </div>
        <div v-if="modalError" class="error-bar" style="margin-bottom:16px;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>{{ modalError }}</div>
        <form @submit.prevent="handleAddUser" class="modal-form">
          <div class="form-field"><label>用户名 <span style="color:#e53935;">*</span></label><input v-model="addForm.username" type="text" placeholder="请输入用户名" required /></div>
          <div class="form-field"><label>密码 <span style="color:#e53935;">*</span></label><input v-model="addForm.password" type="password" placeholder="请输入密码" required /></div>
          <div class="form-field"><label>角色</label><select v-model="addForm.role" class="form-input" style="width:100%;"><option value="user">普通用户</option><option value="admin">管理员</option></select></div>
          <div class="form-field"><label>邮箱</label><input v-model="addForm.email" type="email" placeholder="请输入邮箱" /></div>
          <div class="form-field"><label>手机号</label><input v-model="addForm.phone" type="tel" placeholder="请输入手机号" /></div>
          <div style="display:flex;gap:10px;margin-top:8px;">
            <button type="button" @click="showAddModal = false" class="btn btn-outline" style="flex:1;">取消</button>
            <button type="submit" class="btn btn-primary" style="flex:1;" :disabled="modalLoading"><span v-if="modalLoading" class="btn-spinner" style="width:16px;height:16px;border-width:2px;"></span><template v-else>确认添加</template></button>
          </div>
        </form>
      </div>
    </div>

    <!-- ═══════════ Edit User Modal ═══════════ -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-card glass animate-scale">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <h3 style="font-weight:700;font-size:1.1rem;">编辑用户</h3>
          <button @click="showEditModal = false" class="modal-close-btn">&times;</button>
        </div>
        <div v-if="modalError" class="error-bar" style="margin-bottom:16px;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>{{ modalError }}</div>
        <form @submit.prevent="handleEditUser" class="modal-form">
          <div class="form-field"><label>用户名</label><input v-model="editForm.username" type="text" placeholder="请输入用户名" required /></div>
          <div class="form-field"><label>新密码 <span style="font-size:0.72rem;color:var(--text-muted);">（留空则不修改）</span></label><input v-model="editForm.password" type="password" placeholder="请输入新密码" /></div>
          <div class="form-field"><label>角色</label><select v-model="editForm.role" class="form-input" style="width:100%;"><option value="user">普通用户</option><option value="admin">管理员</option></select></div>
          <div class="form-field"><label>邮箱</label><input v-model="editForm.email" type="email" placeholder="请输入邮箱" /></div>
          <div class="form-field"><label>手机号</label><input v-model="editForm.phone" type="tel" placeholder="请输入手机号" /></div>
          <div style="display:flex;gap:10px;margin-top:8px;">
            <button type="button" @click="showEditModal = false" class="btn btn-outline" style="flex:1;">取消</button>
            <button type="submit" class="btn btn-primary" style="flex:1;" :disabled="modalLoading"><span v-if="modalLoading" class="btn-spinner" style="width:16px;height:16px;border-width:2px;"></span><template v-else>保存修改</template></button>
          </div>
        </form>
      </div>
    </div>

    <!-- ═══════════ Announcement Modal ═══════════ -->
    <div v-if="showAnnounceModal" class="modal-overlay" @click.self="showAnnounceModal = false">
      <div class="modal-card glass animate-scale">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <h3 style="font-weight:700;font-size:1.1rem;">{{ editingAnnouncement ? '编辑公告' : '发布公告' }}</h3>
          <button @click="showAnnounceModal = false" class="modal-close-btn">&times;</button>
        </div>
        <div v-if="announceError" class="error-bar" style="margin-bottom:16px;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>{{ announceError }}</div>
        <form @submit.prevent="handleSaveAnnouncement" class="modal-form">
          <div class="form-field"><label>标题 <span style="color:#e53935;">*</span></label><input v-model="announceForm.title" type="text" placeholder="请输入公告标题" required /></div>
          <div class="form-field"><label>状态</label><select v-model="announceForm.status" class="form-input" style="width:100%;"><option value="active">已发布</option><option value="inactive">已下线</option></select></div>
          <div class="form-field"><label>内容 <span style="color:#e53935;">*</span></label><textarea v-model="announceForm.content" placeholder="请输入公告内容" rows="4" class="form-textarea" required></textarea></div>
          <div style="display:flex;gap:10px;margin-top:8px;">
            <button type="button" @click="showAnnounceModal = false" class="btn btn-outline" style="flex:1;">取消</button>
            <button type="submit" class="btn btn-primary" style="flex:1;" :disabled="announceLoading"><span v-if="announceLoading" class="btn-spinner" style="width:16px;height:16px;border-width:2px;"></span><template v-else>{{ editingAnnouncement ? '保存修改' : '发布公告' }}</template></button>
          </div>
        </form>
      </div>
    </div>

    <!-- ═══════════ Image Viewer Modal ═══════════ -->
    <div v-if="showImageModal" class="modal-overlay" @click.self="showImageModal = false">
      <div class="modal-card glass animate-scale" style="width:680px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h3 style="font-weight:700;font-size:1.05rem;">检测图片 #{{ viewingImageId }}</h3>
          <button @click="showImageModal = false" class="modal-close-btn">&times;</button>
        </div>
        <div v-if="!viewingImage" style="text-align:center;padding:48px;">
          <div class="spinner"></div>
        </div>
        <div v-else style="text-align:center;">
          <img :src="'data:image/jpeg;base64,' + viewingImage" style="max-width:100%;max-height:70vh;border-radius:12px;" alt="检测结果图" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Stats Grid Override ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  padding: 12px 16px !important;
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-card .stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-bottom: 0;
}

.stat-card .stat-value {
  font-size: 1.2rem;
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

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* ── Search ── */
.search-wrap {
  display: flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; padding: 6px 14px; transition: border-color 0.2s;
}
.search-wrap:focus-within { border-color: rgba(76,175,80,0.4); }
.search-wrap svg { color: var(--text-muted); flex-shrink: 0; }
.search-input {
  background: transparent; border: none; outline: none;
  color: var(--text-primary); font-size: 0.85rem; font-family: inherit; width: 160px;
}
.search-input::placeholder { color: var(--text-muted); }

/* ── Date Input ── */
.date-input {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px; padding: 5px 10px; color: var(--text-primary);
  font-size: 0.8rem; font-family: inherit; outline: none;
}
.date-input:focus { border-color: rgba(76,175,80,0.4); }
.date-input::-webkit-calendar-picker-indicator { filter: invert(0.7); cursor: pointer; }

/* ── Form Textarea ── */
.form-textarea {
  width: 100%; padding: 10px 14px;
  border: 1px solid rgba(255,255,255,0.12); border-radius: 10px;
  background: rgba(255,255,255,0.04); color: var(--text-primary);
  font-size: 0.9rem; font-family: inherit; outline: none; resize: vertical;
  transition: border-color 0.2s;
}
.form-textarea:focus { border-color: rgba(76,175,80,0.4); }

/* ── User Table ── */
.user-table-wrap { overflow-x: auto; }
.user-table {
  width: 100%; border-collapse: collapse; font-size: 0.85rem;
  table-layout: fixed;
}
.user-table thead th {
  position: sticky; top: 0; z-index: 2;
  background: rgba(15,40,25,0.95); backdrop-filter: blur(10px);
  padding: 12px 10px; text-align: left;
  color: var(--text-muted); font-weight: 600; font-size: 0.78rem;
  border-bottom: 2px solid rgba(255,255,255,0.08);
  white-space: nowrap;
}
.user-table tbody td {
  padding: 11px 10px; vertical-align: middle;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.user-table tbody tr { transition: background 0.15s; }
.user-table tbody tr:hover { background: rgba(76,175,80,0.06); }

/* Column widths */
.col-user { width: 15%; }
.col-role { width: 8%; }
.col-email { width: 20%; }
.col-phone { width: 12%; }
.col-status { width: 8%; }
.col-date { width: 15%; }
.col-actions { width: 12%; }

.user-cell { display: flex; align-items: center; gap: 8px; }
.user-avatar-sm {
  width: 30px; height: 30px; border-radius: 50%;
  background: rgba(76,175,80,0.15); display: flex;
  align-items: center; justify-content: center;
  font-weight: 700; color: #4caf50; font-size: 0.75rem; flex-shrink: 0;
}
.user-name-text { font-weight: 600; }
.cell-secondary { color: var(--text-secondary); font-size: 0.84rem; }
.cell-muted { color: var(--text-muted); font-size: 0.8rem; white-space: nowrap; }
.action-btns { display: flex; gap: 6px; }

/* Status toggle */
.status-toggle {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.03); cursor: pointer;
  font-size: 0.8rem; color: var(--text-primary);
  transition: all 0.2s; font-family: inherit; white-space: nowrap;
}
.status-toggle:hover:not(:disabled) { border-color: rgba(76,175,80,0.3); background: rgba(76,175,80,0.08); }
.status-toggle:disabled { opacity: 0.5; cursor: not-allowed; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-active { background: #4caf50; box-shadow: 0 0 6px rgba(76,175,80,0.5); }
.dot-inactive { background: #f44336; box-shadow: 0 0 6px rgba(244,67,54,0.4); }

/* Tags */
.tag { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
.tag-info { background: rgba(33,150,243,0.12); color: #2196f3; }
.tag-warning { background: rgba(255,152,0,0.12); color: #ff9800; }
.tag-success { background: rgba(76,175,80,0.12); color: #4caf50; }
.tag-danger { background: rgba(244,67,54,0.12); color: #f44336; }

.btn-danger { 
  background: rgba(244,67,54,0.85); 
  color: #fff; 
  border: 1px solid rgba(244,67,54,0.4);
  box-shadow: 0 2px 8px rgba(244,67,54,0.2);
}
.btn-danger:hover { 
  background: #d32f2f; 
  border-color: #ef5350;
  box-shadow: 0 4px 16px rgba(244,67,54,0.4);
  transform: translateY(-1px);
}

/* ── Log Card ── */
.log-card { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; gap: 12px; }
.log-left { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }

@media (max-width: 640px) {
  .log-card { flex-direction: column; align-items: flex-start; }
  .log-card > :last-child { width: 100%; justify-content: space-between; }
}

/* ── Progress Bar ── */
.progress-track {
  width: 100%; height: 10px; border-radius: 10px;
  background: rgba(255,255,255,0.06); overflow: hidden;
}
.progress-fill {
  height: 100%; border-radius: 10px;
  transition: width 0.5s ease;
}

/* Pagination */
.pagination-bar {
  display: flex; justify-content: center; align-items: center; gap: 6px;
  margin-top: 16px; padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.05);
}
.pagination-total { font-size: 0.8rem; color: var(--text-muted); margin-left: 8px; }

/* Mobile cards (hidden on desktop) */
.user-mobile-cards { display: none; }
.user-mobile-card { padding: 16px; }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,0.55); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal-card { width: 440px; max-width: 92vw; max-height: 90vh; overflow-y: auto; padding: 28px 30px; border-radius: 20px; }
.modal-close-btn { background: none; border: none; cursor: pointer; color: var(--text-muted); font-size: 1.3rem; line-height: 1; }
.modal-close-btn:hover { color: var(--text-primary); }
.modal-form { display: flex; flex-direction: column; gap: 14px; }
.form-field label { display: block; font-size: 0.82rem; font-weight: 600; margin-bottom: 5px; color: var(--text-primary); }
.form-field input, .form-field select {
  width: 100%; padding: 10px 14px;
  border: 1px solid rgba(255,255,255,0.12); border-radius: 10px;
  background: rgba(255,255,255,0.04); color: var(--text-primary);
  font-size: 0.9rem; font-family: inherit; outline: none; transition: border-color 0.2s;
}
.form-field input:focus, .form-field select:focus { border-color: rgba(76,175,80,0.4); }

/* ── Error ── */
.error-bar {
  display: flex; align-items: center; gap: 10px;
  background: rgba(229,57,53,0.08); border: 1px solid rgba(229,57,53,0.2);
  color: #ef5350; padding: 10px 14px; border-radius: 10px; font-size: 0.84rem;
}

/* ── Spinner ── */
.spinner {
  width: 36px; height: 36px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #4caf50; border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
.spinner-lg {
  width: 48px; height: 48px;
  border: 4px solid rgba(255,255,255,0.1);
  border-top-color: #4caf50; border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
.btn-spinner {
  display: inline-block; border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ── */
@media (max-width: 860px) {
  .search-wrap { width: 100%; }
  .search-input { width: 100%; }
}
@media (max-width: 768px) {
  .user-table-wrap table { display: none; }
  .user-mobile-cards { display: flex; flex-direction: column; gap: 12px; }
}
</style>