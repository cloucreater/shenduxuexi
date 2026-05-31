<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const authStore = useAuthStore()

const user = computed(() => ({
  username: authStore.user?.username || '用户',
  email: authStore.user?.email || '—',
  phone: authStore.user?.phone || '—',
  role: authStore.user?.role === 'admin' ? '系统管理员' : '普通用户',
  avatar: authStore.user?.avatar || '',
  createdAt: '—',
}))

const editProfile = ref({
  email: authStore.user?.email || '',
  phone: authStore.user?.phone || '',
})

// Avatar upload
const avatarPreview = ref('')
const avatarUploading = ref(false)
const avatarMsg = ref('')

// 初始化头像预览
function initAvatarPreview() {
  if (authStore.user?.avatar) {
    avatarPreview.value = authStore.user.avatar
  } else {
    avatarPreview.value = ''
  }
}

async function handleAvatarUpload(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 先显示本地预览
  const localPreview = URL.createObjectURL(file)
  avatarPreview.value = localPreview
  avatarUploading.value = true
  avatarMsg.value = ''

  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post('/auth/avatar', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    console.log('头像上传响应:', res.data)
    avatarMsg.value = '头像上传成功'
    
    // 释放本地预览URL
    URL.revokeObjectURL(localPreview)
    
    if (res.data.avatar_url) {
      avatarPreview.value = res.data.avatar_url
      // 更新authStore中的用户信息
      await authStore.fetchCurrentUser()
      console.log('头像上传成功，用户信息已更新:', authStore.user)
    } else {
      console.error('响应中没有avatar_url:', res.data)
      avatarMsg.value = '上传失败：服务器未返回头像URL'
    }
  } catch (e: any) {
    avatarMsg.value = e?.response?.data?.detail || '上传失败'
    console.error('头像上传失败:', e)
    // 上传失败时，恢复原来的头像
    initAvatarPreview()
  } finally {
    avatarUploading.value = false
  }
}

// Password form
const passwordForm = ref({ oldPass: '', newPass: '', confirmPass: '' })
const pwdChanging = ref(false)
const pwdMsg = ref('')
const pwdError = ref(false)

async function changePassword() {
  if (!passwordForm.value.oldPass || !passwordForm.value.newPass || !passwordForm.value.confirmPass) {
    pwdMsg.value = '请填写完整的密码信息'
    pwdError.value = true
    return
  }
  if (passwordForm.value.newPass !== passwordForm.value.confirmPass) {
    pwdMsg.value = '两次新密码输入不一致'
    pwdError.value = true
    return
  }
  if (passwordForm.value.newPass.length < 6) {
    pwdMsg.value = '新密码长度不能少于6位'
    pwdError.value = true
    return
  }
  pwdChanging.value = true
  pwdMsg.value = ''
  pwdError.value = false

  try {
    await authStore.updatePassword(passwordForm.value.oldPass, passwordForm.value.newPass)
    pwdMsg.value = '密码修改成功'
    pwdError.value = false
    passwordForm.value = { oldPass: '', newPass: '', confirmPass: '' }
  } catch (e: any) {
    pwdMsg.value = e?.response?.data?.detail || '密码修改失败'
    pwdError.value = true
  } finally {
    pwdChanging.value = false
  }
}

// Profile update
const profileSaving = ref(false)
const profileMsg = ref('')

async function saveProfile() {
  profileSaving.value = true
  profileMsg.value = ''
  try {
    await authStore.updateProfile({
      email: editProfile.value.email || undefined,
      phone: editProfile.value.phone || undefined,
    })
    profileMsg.value = '个人资料已更新'
  } catch (e: any) {
    profileMsg.value = e?.response?.data?.detail || '保存失败'
  } finally {
    profileSaving.value = false
  }
}

// Preferences
const preferences = ref({
  defaultDisease: '叶斑病',
  defaultCrop: '番茄',
  emailNotify: true,
})

function savePreferences() {
  localStorage.setItem('user-preferences', JSON.stringify(preferences.value))
  alert('偏好设置已保存')
}

onMounted(async () => {
  const saved = localStorage.getItem('user-preferences')
  if (saved) {
    try { Object.assign(preferences.value, JSON.parse(saved)) } catch {}
  }
  
  // 确保用户信息已加载
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  
  if (authStore.user) {
    editProfile.value.email = authStore.user.email || ''
    editProfile.value.phone = authStore.user.phone || ''
    // 初始化头像预览
    initAvatarPreview()
  }
})

// Stats (hardcoded defaults since there's no user stats endpoint)
const stats = ref({
  totalDetections: 0,
  totalTreatments: 0,
  accountCreated: '—',
})

const diseaseOptions = ['叶斑病', '白粉病', '锈病', '早疫病', '晚疫病']
const cropOptions = ['番茄', '黄瓜', '辣椒', '土豆', '小麦', '水稻']
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>个人中心</h2>
      <p>管理个人信息、密码和偏好设置</p>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start;">

      <!-- Left Column -->
      <div class="space-y-4 animate-slide-left">

        <!-- Personal Info Card -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:20px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>个人资料</h3>

          <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
            <div
              class="profile-avatar"
              :style="(avatarPreview || user.avatar) ? { backgroundImage: 'url(' + (avatarPreview || user.avatar) + ')', backgroundSize: 'cover' } : {}"
            >
              <span v-if="!avatarPreview && !user.avatar">{{ user.username[0]?.toUpperCase() }}</span>
            </div>
            <div>
              <label class="btn btn-outline btn-sm" style="cursor:pointer;">
                {{ avatarUploading ? '上传中...' : '更换头像' }}
                <input type="file" accept="image/*" style="display:none" @change="handleAvatarUpload" :disabled="avatarUploading" />
              </label>
              <p v-if="avatarMsg" style="font-size:0.75rem;margin-top:4px;" :style="{color: avatarMsg.includes('成功') ? '#4caf50' : '#ff9800'}">
                {{ avatarMsg }}
              </p>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">{{ user.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">角色</span>
              <span class="info-value">
                <span class="tag tag-success">{{ user.role }}</span>
              </span>
            </div>
          </div>

          <div style="margin-top:16px;">
            <h4 style="font-weight:600;margin-bottom:12px;font-size:0.9rem;">编辑资料</h4>
            <div class="form-group">
              <label class="form-label">电子邮箱</label>
              <input v-model="editProfile.email" type="email" class="form-input" placeholder="请输入邮箱" />
            </div>
            <div class="form-group">
              <label class="form-label">手机号码</label>
              <input v-model="editProfile.phone" type="text" class="form-input" placeholder="请输入手机号" />
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <button @click="saveProfile" :disabled="profileSaving" class="btn btn-primary btn-sm">
                {{ profileSaving ? '保存中...' : '保存资料' }}
              </button>
              <span v-if="profileMsg" style="font-size:0.8rem;" :style="{color: profileMsg.includes('已更新') ? '#4caf50' : '#ff9800'}">
                {{ profileMsg }}
              </span>
            </div>
          </div>
        </div>

        <!-- Statistics -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="18" y="3" width="4" height="18"/><rect x="10" y="8" width="4" height="13"/><rect x="2" y="13" width="4" height="8"/></svg>数据统计</h3>
          <div style="display:flex;gap:14px;">
            <div style="flex:1;text-align:center;padding:18px 12px;background:rgba(76,175,80,0.1);border-radius:14px;">
              <p style="font-size:1.8rem;font-weight:800;color:#4caf50;">{{ stats.totalDetections.toLocaleString() }}</p>
              <p style="font-size:0.78rem;color:var(--text-secondary);">总检测次数</p>
            </div>
            <div style="flex:1;text-align:center;padding:18px 12px;background:rgba(33,150,243,0.1);border-radius:14px;">
              <p style="font-size:1.8rem;font-weight:800;color:#2196f3;">{{ stats.totalTreatments }}</p>
              <p style="font-size:0.78rem;color:var(--text-secondary);">防治方案数</p>
            </div>
            <div style="flex:1;text-align:center;padding:18px 12px;background:rgba(255,152,0,0.1);border-radius:14px;">
              <p style="font-size:0.95rem;font-weight:700;color:#ff9800;">{{ stats.accountCreated }}</p>
              <p style="font-size:0.78rem;color:var(--text-secondary);">创建时间</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="space-y-4 animate-slide-right">

        <!-- Change Password -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:20px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>修改密码</h3>

          <div class="form-group">
            <label class="form-label">原密码</label>
            <input v-model="passwordForm.oldPass" type="password" class="form-input" placeholder="请输入原密码" />
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input v-model="passwordForm.newPass" type="password" class="form-input" placeholder="请输入新密码（至少6位）" />
          </div>
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input v-model="passwordForm.confirmPass" type="password" class="form-input" placeholder="请再次输入新密码" />
          </div>

          <p v-if="pwdMsg" style="font-size:0.85rem;margin-bottom:8px;"
             :style="{color: pwdError ? '#ff9800' : '#4caf50'}">
            {{ pwdMsg }}
          </p>

          <button @click="changePassword" :disabled="pwdChanging" class="btn btn-primary" style="width:100%;">
            {{ pwdChanging ? '修改中...' : '修改密码' }}
          </button>
        </div>

        <!-- Preferences -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:20px;display:flex;align-items:center;gap:8px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>偏好设置</h3>

          <div class="form-group">
            <label class="form-label">默认病害类型</label>
            <select v-model="preferences.defaultDisease" class="form-select">
              <option v-for="d in diseaseOptions" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">默认作物种类</label>
            <select v-model="preferences.defaultCrop" class="form-select">
              <option v-for="c in cropOptions" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <div class="form-group">
            <label style="display:flex;align-items:center;justify-content:space-between;cursor:pointer;">
              <span class="form-label" style="margin-bottom:0;">邮件通知</span>
              <div
                class="toggle-switch"
                :class="{ active: preferences.emailNotify }"
                @click="preferences.emailNotify = !preferences.emailNotify"
              >
                <div class="toggle-knob"></div>
              </div>
            </label>
            <p style="font-size:0.75rem;color:var(--text-muted);margin-top:4px;">
              开启后将收到病害预警、方案更新等邮件通知
            </p>
          </div>

          <button @click="savePreferences" class="btn btn-outline" style="width:100%;margin-top:8px;">
            保存设置
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--green-700), var(--green-500));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(46,125,50,0.3);
}

.info-grid { display: grid; gap: 2px; }
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 11px 14px;
  background: var(--section-bg);
  border-radius: 10px;
}
.info-label { font-size: 0.85rem; color: var(--text-secondary); }
.info-value { font-size: 0.88rem; font-weight: 600; color: var(--text-primary); }

.toggle-switch {
  width: 48px; height: 26px;
  border-radius: 13px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.1);
  cursor: pointer;
  position: relative;
  transition: all 0.25s;
}
.toggle-switch.active {
  background: var(--color-success);
  border-color: var(--color-success);
}
.toggle-knob {
  width: 20px; height: 20px;
  border-radius: 50%;
  background: #fff;
  position: absolute;
  top: 2px; left: 2px;
  transition: all 0.25s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-switch.active .toggle-knob {
  left: 24px;
}
</style>