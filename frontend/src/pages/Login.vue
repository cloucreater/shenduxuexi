<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeMode = ref<'login' | 'register'>('login')
const isLogin = computed(() => activeMode.value === 'login')

// ── Login fields ──
const username = ref('')
const password = ref('')
const captcha = ref('')
const captchaSvg = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

// ── Register fields ──
const regUsername = ref('')
const regEmail = ref('')
const regPhone = ref('')
const regPassword = ref('')
const regConfirmPassword = ref('')
const regShowPwd = ref(false)
const regShowConfirm = ref(false)

async function refreshCaptcha() {
  try {
    const api = (await import('@/api')).default
    const res = await api.get('/captcha', { responseType: 'text' })
    captchaSvg.value = res.data
  } catch { /* ignore */ }
}

function fillDemoAccount() {
  username.value = 'admin'
  password.value = 'admin'
  captcha.value = 'test'
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value, captcha.value || 'test')
    if (rememberMe.value) localStorage.setItem('remembered_user', username.value)
    if (authStore.user?.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/')
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  if (!regUsername.value || !regPassword.value || !regConfirmPassword.value || !regEmail.value || !regPhone.value) {
    error.value = '请填写所有必填字段'
    return
  }
  if (regPassword.value !== regConfirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (regPassword.value.length < 6) {
    error.value = '密码长度至少为6位'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(regEmail.value)) {
    error.value = '请输入有效的邮箱地址'
    return
  }
  if (!/^1[3-9]\d{9}$/.test(regPhone.value)) {
    error.value = '请输入有效的手机号'
    return
  }
  loading.value = true
  try {
    await authStore.register(regUsername.value, regPassword.value, regEmail.value, regPhone.value)
    router.push('/')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshCaptcha()
  const remembered = localStorage.getItem('remembered_user')
  if (remembered) {
    username.value = remembered
    rememberMe.value = true
  }
  if (localStorage.getItem('token')) {
    router.push('/')
  }
})

// ── Feature list for left panel ──
const features = [
  { icon: 'M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5zM14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z', title: '智能分析', desc: 'CNN + YOLOv8 深度学习模型，精准识别病害' },
  { icon: 'M23 6l-9.5 9.5-5-5L1 18m0-5V6h7', title: '趋势预测', desc: '基于历史数据与气象信息，预测病害发生趋势' },
  { icon: 'M12 2L9 7l-5 1 4 4-1 5 5-2.5L17 17l-1-5 4-4-5-1-3-5z', title: '防治方案', desc: '智能生成针对性防治方案，精准施药减损增收' },
  { icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', title: '效果评估', desc: '防治前后对比分析，量化评估防治效果' },
  { icon: 'M4 19.5A2.5 2.5 0 016.5 17H20M4 4v16a2.5 2.5 0 002.5 2.5H20V2H6.5A2.5 2.5 0 004 4.5V4z', title: '知识库', desc: '丰富的作物病害图鉴与防治知识，随时查阅' },
]
</script>

<template>
  <div class="login-root">
    <!-- ===== LEFT PANEL ===== -->
    <div class="login-left">
      <div class="left-bg"></div>
      <div class="left-overlay"></div>

      <div class="left-content">
        <!-- Logo -->
        <div class="left-logo">
          <div class="logo-icon">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2L2 22h20L12 2z" />
              <path d="M12 2v20" />
              <path d="M8 14c1.5-2 2.5-4 4-4s2.5 2 4 4" />
            </svg>
          </div>
          <div>
            <h1 class="left-title">SmartAgri</h1>
            <p class="left-subtitle">智慧农业病害检测系统</p>
          </div>
        </div>

        <!-- Tagline -->
        <p class="left-tagline">
          基于深度学习的<br />农作物病虫害智能检测与防治平台
        </p>

        <!-- Features -->
        <div class="features-list">
          <div v-for="(f, i) in features" :key="f.title" class="feature-item" :style="{ animationDelay: `${0.15 * i}s` }">
            <div class="feature-icon">
              <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                <path :d="f.icon"/>
              </svg>
            </div>
            <div>
              <h4>{{ f.title }}</h4>
              <p>{{ f.desc }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="left-footer">
          <span>Powered by YOLOv8 + PyTorch</span>
        </div>
      </div>
    </div>

    <!-- ===== RIGHT PANEL ===== -->
    <div class="login-right">
      <div class="right-card">

        <!-- Header -->
        <div class="right-header">
          <p class="welcome-back">欢迎回来</p>
          <h2 v-if="isLogin">登录账户</h2>
          <h2 v-else>创建账户</h2>
          <p class="header-sub">智慧农业病害检测系统</p>
        </div>

        <!-- Mode Switch -->
        <div class="mode-switch">
          <button :class="['mode-btn', { active: isLogin }]" @click="activeMode = 'login'">登录</button>
          <button :class="['mode-btn', { active: !isLogin }]" @click="activeMode = 'register'">注册</button>
        </div>

        <!-- Error -->
        <div v-if="error" class="error-bar">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span>{{ error }}</span>
        </div>

        <!-- ═══ LOGIN FORM ═══ -->
        <form v-if="isLogin" @submit.prevent="handleLogin" class="auth-form">
          <div class="field">
            <label class="field-label">用户名</label>
            <div class="field-wrap">
              <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
              <input v-model="username" type="text" placeholder="请输入用户名" required autocomplete="username" />
            </div>
          </div>

          <div class="field">
            <label class="field-label">密码</label>
            <div class="field-wrap">
              <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input v-model="password" type="password" placeholder="请输入密码" required autocomplete="current-password" />
            </div>
          </div>

          <div class="field">
            <label class="field-label">验证码</label>
            <div class="captcha-row">
              <div class="field-wrap" style="flex:1;">
                <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                <input v-model="captcha" type="text" placeholder="验证码" maxlength="6" required />
              </div>
              <div class="captcha-img" @click="refreshCaptcha" v-html="captchaSvg" title="点击刷新验证码"></div>
            </div>
          </div>

          <!-- Remember & Forgot -->
          <div class="form-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="rememberMe" />
              <span class="checkmark"></span>
              记住我
            </label>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <!-- Login Button -->
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            <template v-else>
              <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/></svg>
              登 录
            </template>
          </button>

          <!-- Demo fill -->
          <button type="button" class="demo-btn" @click="fillDemoAccount">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            快速填充演示账号 (admin / admin)
          </button>

          <!-- Register link -->
          <p class="switch-text">
            还没有账号？
            <a href="#" @click.prevent="activeMode = 'register'">立即注册</a>
          </p>
        </form>

        <!-- ═══ REGISTER FORM ═══ -->
        <form v-else @submit.prevent="handleRegister" class="auth-form">
          <div class="field">
            <label class="field-label">用户名 <span class="req">*</span></label>
            <div class="field-wrap">
              <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
              <input v-model="regUsername" type="text" placeholder="请输入用户名" required autocomplete="username" />
            </div>
          </div>

          <div class="field">
            <label class="field-label">邮箱 <span class="req">*</span></label>
            <div class="field-wrap">
              <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 4L12 13 2 4"/></svg>
              <input v-model="regEmail" type="email" placeholder="请输入邮箱地址" required autocomplete="email" />
            </div>
          </div>

          <div class="field">
            <label class="field-label">手机号 <span class="req">*</span></label>
            <div class="field-wrap">
              <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
              <input v-model="regPhone" type="tel" placeholder="请输入手机号" required autocomplete="tel" />
            </div>
          </div>

          <div class="field">
            <label class="field-label">密码 <span class="req">*</span></label>
            <div class="field-wrap">
              <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input v-model="regPassword" :type="regShowPwd ? 'text' : 'password'" placeholder="至少6位密码" required autocomplete="new-password" />
              <button type="button" class="toggle-pwd" @click="regShowPwd = !regShowPwd">
                <svg v-if="regShowPwd" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242"/></svg>
              </button>
            </div>
          </div>

          <div class="field">
            <label class="field-label">确认密码 <span class="req">*</span></label>
            <div class="field-wrap">
              <svg class="field-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input v-model="regConfirmPassword" :type="regShowConfirm ? 'text' : 'password'" placeholder="请再次输入密码" required autocomplete="new-password" />
              <button type="button" class="toggle-pwd" @click="regShowConfirm = !regShowConfirm">
                <svg v-if="regShowConfirm" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242"/></svg>
              </button>
            </div>
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            <template v-else>
              <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
              注 册
            </template>
          </button>

          <p class="switch-text">
            已有账号？
            <a href="#" @click.prevent="activeMode = 'login'">立即登录</a>
          </p>
        </form>

      </div>

      <!-- Right footer -->
      <p class="right-footer">&copy; 2026 SmartAgri. All rights reserved.</p>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════
   ROOT LAYOUT — full viewport split
   ═══════════════════════════════════════════════ */
.login-root {
  display: flex;
  min-height: 100vh;
  font-family: 'Inter', 'Noto Sans SC', system-ui, -apple-system, sans-serif;
  background: #f5f7f5;
}

/* ═══════════ LEFT PANEL (40%) ═══════════ */
.login-left {
  width: 40%;
  min-width: 380px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #0a3514;
}

.left-bg {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(160deg, #0b3412 0%, #0f4a1e 25%, #125922 50%, #0d3d18 75%, #0a2f0f 100%);
}

.left-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 80% 20%, rgba(102, 187, 106, 0.18) 0%, transparent 50%),
    radial-gradient(ellipse at 20% 80%, rgba(45, 138, 78, 0.25) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 5%, rgba(255, 255, 255, 0.06) 0%, transparent 60%);
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Ccircle cx='30' cy='30' r='1.5'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.left-content {
  position: relative;
  z-index: 2;
  padding: 60px 48px;
  max-width: 480px;
  width: 100%;
}

/* Logo */
.left-logo {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 32px;
}
.logo-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  background: rgba(255,255,255,0.12);
  display: flex; align-items: center; justify-content: center;
  color: #66bb6a;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.1);
  flex-shrink: 0;
}
.left-title {
  font-family: 'Noto Serif SC', 'Noto Sans SC', serif;
  font-size: 1.65rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.04em;
  line-height: 1.2;
}
.left-subtitle {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.55);
  letter-spacing: 0.02em;
  margin-top: 2px;
}

/* Tagline */
.left-tagline {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.1rem;
  color: rgba(255,255,255,0.65);
  line-height: 1.7;
  margin-bottom: 40px;
  letter-spacing: 0.03em;
}

/* Features */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 48px;
}
.feature-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  animation: fadeSlideIn 0.6s ease both;
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}
.feature-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  background: rgba(255,255,255,0.08);
  display: flex; align-items: center; justify-content: center;
  color: #66bb6a;
  flex-shrink: 0;
  border: 1px solid rgba(255,255,255,0.06);
}
.feature-item h4 {
  font-size: 0.92rem;
  font-weight: 600;
  color: #e8f5e9;
  margin-bottom: 2px;
}
.feature-item p {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.45);
  line-height: 1.4;
}

.left-footer {
  font-size: 0.7rem;
  color: rgba(255,255,255,0.25);
  letter-spacing: 0.02em;
}

/* ═══════════ RIGHT PANEL (60%) ═══════════ */
.login-right {
  width: 60%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #f5f7f5;
}

.right-card {
  width: 100%;
  max-width: 440px;
  background: #fff;
  border-radius: 24px;
  padding: 48px 44px 40px;
  box-shadow:
    0 2px 24px rgba(0,0,0,0.04),
    0 12px 48px rgba(0,0,0,0.06),
    0 0 0 1px rgba(0,0,0,0.03);
}

/* Header */
.right-header {
  text-align: center;
  margin-bottom: 28px;
}
.welcome-back {
  font-size: 0.8rem;
  color: #66bb6a;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.right-header h2 {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.7rem;
  font-weight: 700;
  color: #1b2e1b;
  margin-bottom: 4px;
}
.header-sub {
  font-size: 0.85rem;
  color: #7a9a7a;
}

/* Mode switch */
.mode-switch {
  display: flex;
  background: #f0f4f0;
  border-radius: 12px;
  padding: 3px;
  margin-bottom: 24px;
}
.mode-btn {
  flex: 1;
  padding: 9px 0;
  border: none;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.25s;
  background: transparent;
  color: #8a9a8a;
}
.mode-btn.active {
  background: #fff;
  color: #1b5e2a;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}

/* Error */
.error-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fef0ef;
  border: 1px solid #f5c6cb;
  color: #c62828;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.85rem;
  margin-bottom: 20px;
}

/* Form */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #2e3a2e;
  margin-bottom: 6px;
}
.req { color: #e53935; }

.field-wrap {
  display: flex;
  align-items: center;
  border: 1.5px solid #e0e5e0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  background: #fafcfa;
}
.field-wrap:focus-within {
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76,175,80,0.08);
  background: #fff;
}
.field-icon {
  color: #b0c0b0;
  margin-left: 14px;
  flex-shrink: 0;
}
.field-wrap input {
  flex: 1;
  padding: 13px 14px 13px 10px;
  border: none;
  font-size: 0.93rem;
  font-family: inherit;
  background: transparent;
  color: #1a2e1a;
  outline: none;
  min-width: 0;
}
.field-wrap input::placeholder { color: #b0c0b0; }

/* Captcha */
.captcha-row {
  display: flex;
  gap: 10px;
  align-items: stretch;
}
.captcha-img {
  width: 130px;
  min-width: 130px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 1.5px solid #e0e5e0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafcfa;
  transition: all 0.2s;
}
.captcha-img:hover {
  border-color: #4caf50;
  transform: scale(1.03);
}

/* Remember + Forgot row */
.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #6a7a6a;
  cursor: pointer;
}
.checkbox-label input[type="checkbox"] {
  width: 17px; height: 17px;
  accent-color: #4caf50;
  cursor: pointer;
}
.forgot-link {
  font-size: 0.85rem;
  color: #4caf50;
  text-decoration: none;
  font-weight: 500;
}
.forgot-link:hover { text-decoration: underline; }

/* Submit button */
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  letter-spacing: 0.05em;
  color: #fff;
  background: linear-gradient(135deg, #1b5e2a, #2d8a4e, #43a047);
  box-shadow: 0 4px 20px rgba(45,138,78,0.3);
  transition: all 0.3s;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(45,138,78,0.4);
}
.submit-btn:active:not(:disabled) { transform: translateY(0); }
.submit-btn:disabled { opacity: 0.65; cursor: wait; }

.btn-spinner {
  width: 20px; height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Demo */
.demo-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  border: 1.5px dashed #c8dcc8;
  border-radius: 12px;
  background: #f6fdf7;
  color: #4caf50;
  font-size: 0.83rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}
.demo-btn:hover {
  background: #edf7ee;
  border-color: #4caf50;
}

/* Switch text */
.switch-text {
  text-align: center;
  font-size: 0.85rem;
  color: #7a9a7a;
}
.switch-text a {
  color: #2d8a4e;
  font-weight: 600;
  text-decoration: none;
}
.switch-text a:hover { text-decoration: underline; }

/* Toggle password */
.toggle-pwd {
  background: none; border: none;
  color: #b0c0b0;
  cursor: pointer;
  padding: 0 12px;
  display: flex; align-items: center;
  transition: color 0.2s;
}
.toggle-pwd:hover { color: #5a7a5a; }

/* Right footer */
.right-footer {
  margin-top: 24px;
  font-size: 0.72rem;
  color: #b0c0b0;
}

/* ═══════════ RESPONSIVE ═══════════ */
@media (max-width: 860px) {
  .login-root {
    flex-direction: column;
  }
  .login-left {
    width: 100%;
    min-width: unset;
    padding: 36px 24px;
  }
  .left-content {
    padding: 24px 16px;
    max-width: 100%;
  }
  .left-tagline { margin-bottom: 24px; }
  .features-list { display: none; }
  .left-footer { display: none; }

  .login-right {
    width: 100%;
    padding: 24px 16px;
  }
  .right-card {
    padding: 32px 24px 28px;
    max-width: 100%;
    border-radius: 20px 20px 0 0;
    margin-top: -16px;
    position: relative;
    z-index: 3;
  }
}
</style>
