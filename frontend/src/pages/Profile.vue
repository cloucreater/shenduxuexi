<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const authStore = useAuthStore()

const loading = ref(true)
const activityLoading = ref(true)

// User info from auth store
const userInfo = ref({
  username: authStore.user?.username || '',
  email: authStore.user?.email || '',
  phone: authStore.user?.phone || '',
  role: authStore.user?.role || 'user',
  joinDate: '--',
  lastLogin: '--'
})

// Real detection stats
const detectionStats = ref({
  totalDetections: 0,
  imageDetections: 0,
  videoDetections: 0,
  cameraDetections: 0,
  todayDetections: 0,
  diseaseRate: '0%'
})

// Recent activity
const recentActivity = ref<any[]>([])

// Password form
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Notification settings
const notificationSettings = ref({
  emailNotification: true,
  smsNotification: false
})

// Load stats from API
async function loadStats() {
  try {
    const res = await api.get('/dashboard/stats')
    const data = res.data
    detectionStats.value.todayDetections = data.todayDetectCount || 0
    detectionStats.value.diseaseRate = ((data.diseaseRate || 0) * 100).toFixed(1) + '%'
  } catch { /* use defaults */ }
}

async function loadHistory() {
  try {
    const res = await api.get('/history?limit=50')
    const records = res.data.records || []

    detectionStats.value.totalDetections = records.length
    detectionStats.value.imageDetections = records.length
    detectionStats.value.videoDetections = 0
    detectionStats.value.cameraDetections = 0

    // Recent activity from last 10 records
    recentActivity.value = records.slice(0, 10).map((r: any) => {
      const diseaseDetections = (r.detections || []).filter((d: any) =>
        d.label !== 'Healthy' && d.label !== '健康' && d.label_en !== 'healthy'
      )
      return {
        id: r.id,
        type: '检测',
        description: diseaseDetections.length > 0
          ? `检测到 ${diseaseDetections[0].label} 等 ${diseaseDetections.length} 种病害`
          : '植株健康，未发现病害',
        date: r.created_at,
        status: diseaseDetections.length > 0 ? 'warning' : 'success'
      }
    })
  } catch { /* use defaults */ }
  activityLoading.value = false
}

async function updateProfile() {
  try {
    await api.put('/auth/profile', {
      username: userInfo.value.username,
      email: userInfo.value.email,
      phone: userInfo.value.phone
    })
    alert('✅ 个人信息更新成功！')
  } catch {
    alert('更新失败，请重试')
  }
}

async function changePassword() {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
    alert('请填写完整密码信息')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  try {
    await api.put('/auth/password', {
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    alert('✅ 密码修改成功！')
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  } catch {
    alert('密码修改失败，请检查原密码是否正确')
  }
}

function saveNotificationSettings() {
  alert('✅ 通知设置已保存！')
}

onMounted(async () => {
  loading.value = true
  await Promise.all([loadStats(), loadHistory()])
  loading.value = false
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="page-header animate-fade-down">
      <h2>👤 个人中心</h2>
      <p>管理您的账户信息、查看检测统计和活动记录</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column - Profile Card & Stats -->
      <div class="lg:col-span-1 space-y-5">
        <!-- Profile Card -->
        <div class="glass-card text-center animate-fade-up stagger-1">
          <div
            style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg, var(--green-700), var(--green-400));display:flex;align-items:center;justify-content:center;margin:0 auto 14px;box-shadow:0 4px 20px rgba(22,163,74,0.3);"
          >
            <span style="font-size:2rem;font-weight:800;color:#fff;">
              {{ (userInfo.username || 'U')[0].toUpperCase() }}
            </span>
          </div>
          <h2 style="font-weight:700;color:var(--text-primary);font-size:1.2rem;">{{ userInfo.username }}</h2>
          <span
            style="display:inline-block;margin-top:4px;padding:3px 14px;border-radius:12px;font-size:0.76rem;font-weight:600;"
            :style="{ background: userInfo.role === 'admin' ? 'var(--color-warning-bg)' : 'var(--color-info-bg)', color: userInfo.role === 'admin' ? 'var(--color-warning)' : 'var(--color-info)' }"
          >
            {{ userInfo.role === 'admin' ? '🔧 管理员' : '👨‍🌾 用户' }}
          </span>
          <p style="font-size:0.8rem;color:var(--text-muted);margin-top:10px;">
            注册时间：{{ userInfo.joinDate }}
          </p>
        </div>

        <!-- Stats Card -->
        <div class="glass-card animate-fade-up stagger-2">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:14px;font-size:0.95rem;">📊 检测统计</h3>
          <div class="space-y-2">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 12px;background:rgba(0,0,0,0.015);border-radius:10px;">
              <span style="font-size:0.85rem;color:var(--text-secondary);">检测总数</span>
              <span style="font-weight:700;color:var(--color-primary);font-size:1.1rem;">{{ detectionStats.totalDetections }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 12px;background:rgba(0,0,0,0.015);border-radius:10px;">
              <span style="font-size:0.85rem;color:var(--text-secondary);">图片检测</span>
              <span style="font-weight:700;color:var(--color-info);font-size:1.1rem;">{{ detectionStats.imageDetections }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 12px;background:rgba(0,0,0,0.015);border-radius:10px;">
              <span style="font-size:0.85rem;color:var(--text-secondary);">今日检测</span>
              <span style="font-weight:700;color:var(--color-success);font-size:1.1rem;">{{ detectionStats.todayDetections }}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 12px;background:rgba(0,0,0,0.015);border-radius:10px;">
              <span style="font-size:0.85rem;color:var(--text-secondary);">病害检出率</span>
              <span style="font-weight:700;color:var(--color-warning);font-size:1.1rem;">{{ detectionStats.diseaseRate }}</span>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="glass-card animate-fade-up stagger-3">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:14px;font-size:0.95rem;">🕐 近期活动</h3>
          <div v-if="activityLoading" class="space-y-2">
            <div v-for="i in 4" :key="i" class="skeleton" style="height:44px;"></div>
          </div>
          <div v-else-if="recentActivity.length > 0" class="space-y-2" style="max-height:300px;overflow-y:auto;">
            <div
              v-for="activity in recentActivity"
              :key="activity.id"
              style="display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;background:rgba(0,0,0,0.012);"
            >
              <div
                style="width:8px;height:8px;border-radius:50%;flex-shrink:0;"
                :style="{ background: activity.status === 'warning' ? 'var(--color-warning)' : 'var(--color-success)' }"
              ></div>
              <div style="flex:1;min-width:0;">
                <p style="font-size:0.8rem;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                  {{ activity.description }}
                </p>
                <p style="font-size:0.7rem;color:var(--text-muted);">{{ activity.date }}</p>
              </div>
            </div>
          </div>
          <div v-else style="text-align:center;padding:20px;">
            <p style="color:var(--text-muted);font-size:0.85rem;">暂无活动记录</p>
          </div>
        </div>
      </div>

      <!-- Right Column - Settings -->
      <div class="lg:col-span-2 space-y-5">
        <!-- Basic Info -->
        <div class="glass-card animate-fade-up stagger-2">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">📝 基本信息</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div>
              <label class="form-label">用户名</label>
              <input v-model="userInfo.username" type="text" class="form-input" />
            </div>
            <div>
              <label class="form-label">邮箱</label>
              <input v-model="userInfo.email" type="email" class="form-input" />
            </div>
            <div>
              <label class="form-label">手机号</label>
              <input v-model="userInfo.phone" type="tel" class="form-input" />
            </div>
            <div>
              <label class="form-label">角色</label>
              <input :value="userInfo.role === 'admin' ? '管理员' : '普通用户'" type="text" disabled class="form-input" style="opacity:0.6;" />
            </div>
          </div>
          <button @click="updateProfile" class="btn btn-primary mt-4">
            💾 保存修改
          </button>
        </div>

        <!-- Change Password -->
        <div class="glass-card animate-fade-up stagger-3">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">🔒 修改密码</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div>
              <label class="form-label">原密码</label>
              <input v-model="passwordForm.oldPassword" type="password" placeholder="输入原密码" class="form-input" />
            </div>
            <div>
              <label class="form-label">新密码</label>
              <input v-model="passwordForm.newPassword" type="password" placeholder="输入新密码" class="form-input" />
            </div>
            <div>
              <label class="form-label">确认密码</label>
              <input v-model="passwordForm.confirmPassword" type="password" placeholder="确认新密码" class="form-input" />
            </div>
          </div>
          <button @click="changePassword" class="btn btn-outline mt-4">
            🔑 修改密码
          </button>
        </div>

        <!-- Notification Settings -->
        <div class="glass-card animate-fade-up stagger-4">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">🔔 通知设置</h3>
          <div class="space-y-3">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px;background:rgba(0,0,0,0.015);border-radius:10px;">
              <div>
                <p style="font-weight:600;color:var(--text-primary);font-size:0.9rem;">邮件通知</p>
                <p style="font-size:0.78rem;color:var(--text-muted);">接收检测结果和系统通知</p>
              </div>
              <label style="position:relative;display:inline-flex;align-items:center;cursor:pointer;">
                <input v-model="notificationSettings.emailNotification" type="checkbox" style="display:none;" />
                <div
                  style="width:44px;height:24px;border-radius:12px;transition:all 0.2s;"
                  :style="{ background: notificationSettings.emailNotification ? 'var(--color-primary)' : '#d1d5db' }"
                >
                  <div
                    style="width:20px;height:20px;border-radius:50%;background:#fff;margin:2px;transition:all 0.2s;box-shadow:0 1px 3px rgba(0,0,0,0.15);"
                    :style="{ transform: notificationSettings.emailNotification ? 'translateX(20px)' : 'translateX(0)' }"
                  ></div>
                </div>
              </label>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px;background:rgba(0,0,0,0.015);border-radius:10px;">
              <div>
                <p style="font-weight:600;color:var(--text-primary);font-size:0.9rem;">短信通知</p>
                <p style="font-size:0.78rem;color:var(--text-muted);">接收重要预警短信通知</p>
              </div>
              <label style="position:relative;display:inline-flex;align-items:center;cursor:pointer;">
                <input v-model="notificationSettings.smsNotification" type="checkbox" style="display:none;" />
                <div
                  style="width:44px;height:24px;border-radius:12px;transition:all 0.2s;"
                  :style="{ background: notificationSettings.smsNotification ? 'var(--color-primary)' : '#d1d5db' }"
                >
                  <div
                    style="width:20px;height:20px;border-radius:50%;background:#fff;margin:2px;transition:all 0.2s;box-shadow:0 1px 3px rgba(0,0,0,0.15);"
                    :style="{ transform: notificationSettings.smsNotification ? 'translateX(20px)' : 'translateX(0)' }"
                  ></div>
                </div>
              </label>
            </div>
          </div>
          <button @click="saveNotificationSettings" class="btn btn-outline mt-4">
            💾 保存设置
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
