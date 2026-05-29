<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const user = ref({
  username: authStore.user?.username || '管理员',
  email: 'admin@smart-agri.com',
  phone: '138****6789',
  role: authStore.user?.role === 'admin' ? '系统管理员' : '普通用户',
  avatar: '',
  createdAt: '2025-03-15',
})

// Avatar upload
const avatarPreview = ref('')
function handleAvatarUpload(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    avatarPreview.value = URL.createObjectURL(target.files[0])
  }
}

// Password form
const passwordForm = ref({ oldPass: '', newPass: '', confirmPass: '' })
const pwdChanging = ref(false)
const pwdMsg = ref('')

async function changePassword() {
  if (!passwordForm.value.oldPass || !passwordForm.value.newPass || !passwordForm.value.confirmPass) {
    pwdMsg.value = '请填写完整的密码信息'
    return
  }
  if (passwordForm.value.newPass !== passwordForm.value.confirmPass) {
    pwdMsg.value = '两次新密码输入不一致'
    return
  }
  if (passwordForm.value.newPass.length < 6) {
    pwdMsg.value = '新密码长度不能少于6位'
    return
  }
  pwdChanging.value = true
  pwdMsg.value = ''
  await new Promise(resolve => setTimeout(resolve, 1200))
  pwdMsg.value = '✅ 密码修改成功'
  passwordForm.value = { oldPass: '', newPass: '', confirmPass: '' }
  pwdChanging.value = false
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

// Stats
const stats = ref({
  totalDetections: 1248,
  totalTreatments: 86,
  accountCreated: '2025-03-15',
})

const diseaseOptions = ['叶斑病', '白粉病', '锈病', '早疫病', '晚疫病']
const cropOptions = ['番茄', '黄瓜', '辣椒', '土豆', '小麦', '水稻']
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>👤 个人中心</h2>
      <p>管理个人信息、密码和偏好设置</p>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start;">

      <!-- Left Column -->
      <div class="space-y-4 animate-slide-left">

        <!-- Personal Info Card -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:20px;">📋 个人资料</h3>

          <!-- Avatar -->
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
            <div
              class="profile-avatar"
              :style="avatarPreview ? { backgroundImage: 'url(' + avatarPreview + ')', backgroundSize: 'cover' } : {}"
            >
              <span v-if="!avatarPreview">{{ user.username[0]?.toUpperCase() }}</span>
            </div>
            <div>
              <label class="btn btn-outline btn-sm" style="cursor:pointer;">
                📷 更换头像
                <input type="file" accept="image/*" style="display:none" @change="handleAvatarUpload" />
              </label>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">{{ user.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">电子邮箱</span>
              <span class="info-value">{{ user.email }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">手机号码</span>
              <span class="info-value">{{ user.phone }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">角色</span>
              <span class="info-value">
                <span class="tag tag-success">{{ user.role }}</span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">注册时间</span>
              <span class="info-value">{{ user.createdAt }}</span>
            </div>
          </div>
        </div>

        <!-- Statistics -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:16px;">📊 数据统计</h3>
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
          <h3 style="font-weight:700;margin-bottom:20px;">🔒 修改密码</h3>

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
             :style="{color: pwdMsg.includes('✅') ? '#4caf50' : '#ff9800'}">
            {{ pwdMsg }}
          </p>

          <button @click="changePassword" :disabled="pwdChanging" class="btn btn-primary" style="width:100%;">
            {{ pwdChanging ? '⏳ 修改中...' : '🔑 修改密码' }}
          </button>
        </div>

        <!-- Preferences -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:20px;">⚙️ 偏好设置</h3>

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
              <span class="form-label" style="margin-bottom:0;">📧 邮件通知</span>
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
            💾 保存设置
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

/* Toggle Switch */
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
