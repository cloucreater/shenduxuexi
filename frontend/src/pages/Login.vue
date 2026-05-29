<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const captcha = ref('')
const captchaSvg = ref('')
const captchaText = ref('')
const loading = ref(false)
const error = ref('')

async function refreshCaptcha() {
  try {
    const api = (await import('@/api')).default
    const res = await api.get('/captcha', { responseType: 'text' })
    captchaSvg.value = res.data
    captchaText.value = res.headers['x-captcha-text'] || ''
  } catch { /* ignore */ }
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value, captcha.value || 'test')
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

onMounted(() => {
  refreshCaptcha()
  if (localStorage.getItem('token')) {
    router.push('/')
  }
})
</script>

<template>
  <div class="login-page">
    <!-- Agricultural Background -->
    <div class="login-bg"></div>

    <!-- Decorative floating elements -->
    <div class="floating-leaves">
      <span class="leaf leaf-1">🌿</span>
      <span class="leaf leaf-2">🍃</span>
      <span class="leaf leaf-3">🌱</span>
      <span class="leaf leaf-4">🍀</span>
      <span class="leaf leaf-5">🌾</span>
    </div>

    <!-- Login Card -->
    <div class="login-card animate-scale">
      <!-- Logo Section -->
      <div class="login-logo">
        <div class="login-icon-wrapper">
          <span class="login-icon">🌾</span>
        </div>
        <h1>智慧农害</h1>
        <p>基于深度学习的农作物病虫害检测与防治系统</p>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="login-error">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Username -->
        <div class="input-group">
          <label>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            用户名
          </label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            required
            autocomplete="username"
          />
        </div>

        <!-- Password -->
        <div class="input-group">
          <label>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            密码
          </label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
            autocomplete="current-password"
          />
        </div>

        <!-- Captcha -->
        <div class="input-group">
          <label>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            验证码
          </label>
          <div class="captcha-row">
            <input
              v-model="captcha"
              type="text"
              placeholder="请输入验证码"
              maxlength="6"
              required
            />
            <div
              class="captcha-img"
              @click="refreshCaptcha"
              v-html="captchaSvg"
              title="点击刷新验证码"
            ></div>
          </div>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <template v-else>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            登 录
          </template>
        </button>

        <!-- Register Link -->
        <div class="login-footer">
          <span>还没有账号？</span>
          <router-link to="/register">立即注册 →</router-link>
        </div>
      </form>

      <!-- Demo Account Hint -->
      <div class="login-hint">
        <div class="hint-icon">💡</div>
        <p>演示账号：<strong>admin</strong> / 密码：<strong>admin</strong></p>
      </div>
    </div>

    <!-- Footer -->
    <div class="login-credit">
      <span>Powered by YOLOv8 + PyTorch Deep Learning</span>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* ── Agricultural Background ── */
.login-bg {
  position: fixed;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(11, 52, 18, 0.82) 0%, rgba(27, 94, 42, 0.7) 35%, rgba(56, 142, 60, 0.55) 65%, rgba(27, 94, 42, 0.72) 100%),
    url('https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=1920&q=80') center/cover no-repeat;
  z-index: 0;
}

.login-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 25% 45%, rgba(255, 255, 255, 0.08) 0%, transparent 55%),
    radial-gradient(circle at 72% 28%, rgba(102, 187, 106, 0.25) 0%, transparent 50%),
    radial-gradient(circle at 40% 75%, rgba(45, 138, 78, 0.15) 0%, transparent 45%);
}

/* ── Floating Leaves ── */
.floating-leaves {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.leaf {
  position: absolute;
  font-size: 2rem;
  opacity: 0.18;
  animation: floatLeaf 8s ease-in-out infinite;
}
.leaf-1 { top: 10%; left: 8%; animation-delay: 0s; font-size: 2.5rem; }
.leaf-2 { top: 18%; right: 12%; animation-delay: 1.5s; font-size: 2rem; }
.leaf-3 { bottom: 22%; left: 15%; animation-delay: 3s; font-size: 2.2rem; }
.leaf-4 { bottom: 15%; right: 10%; animation-delay: 4.5s; font-size: 2.8rem; }
.leaf-5 { top: 50%; left: 5%; animation-delay: 6s; font-size: 1.8rem; }

@keyframes floatLeaf {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.15; }
  25% { transform: translateY(-18px) rotate(5deg); opacity: 0.25; }
  50% { transform: translateY(-8px) rotate(-3deg); opacity: 0.18; }
  75% { transform: translateY(-22px) rotate(4deg); opacity: 0.22; }
}

/* ── Login Card ── */
.login-card {
  position: relative;
  z-index: 1;
  width: 440px;
  max-width: 92vw;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: saturate(180%) blur(28px);
  -webkit-backdrop-filter: saturate(180%) blur(28px);
  border-radius: 28px;
  padding: 44px 40px;
  box-shadow:
    0 8px 48px rgba(0, 0, 0, 0.13),
    0 0 100px rgba(102, 187, 106, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.5);
  margin: 20px;
}

/* ── Logo ── */
.login-logo { text-align: center; margin-bottom: 32px; }

.login-icon-wrapper {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(45, 138, 78, 0.08), rgba(102, 187, 106, 0.15));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 4px 20px rgba(102, 187, 106, 0.15);
}
.login-icon {
  font-size: 2.4rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.login-logo h1 {
  font-size: 1.9rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1b5e2a, #2d8a4e, #43a047);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.02em;
}
.login-logo p {
  color: #5a7a5a;
  font-size: 0.84rem;
  margin-top: 6px;
  letter-spacing: 0.01em;
}

/* ── Error ── */
.login-error {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(229, 57, 53, 0.06);
  border: 1px solid rgba(229, 57, 53, 0.18);
  color: #c62828;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.85rem;
  margin-bottom: 22px;
}

/* ── Form ── */
.login-form { display: flex; flex-direction: column; gap: 20px; }

.input-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #2e3a2e;
  margin-bottom: 6px;
}

.input-group input {
  width: 100%;
  padding: 13px 16px;
  border: 2px solid rgba(0, 0, 0, 0.07);
  border-radius: 14px;
  font-size: 0.93rem;
  background: rgba(255, 255, 255, 0.65);
  transition: all 0.2s ease;
  outline: none;
  font-family: inherit;
  color: #1a2e1a;
}
.input-group input:focus {
  border-color: #2d8a4e;
  box-shadow: 0 0 0 4px rgba(45, 138, 78, 0.1);
  background: #fff;
}
.input-group input::placeholder { color: #a0b0a0; }

.captcha-row { display: flex; gap: 12px; }
.captcha-row input { flex: 1; }

.captcha-img {
  height: 48px;
  min-width: 130px;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid rgba(0, 0, 0, 0.07);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.7);
}
.captcha-img:hover {
  border-color: #2d8a4e;
  box-shadow: 0 0 0 4px rgba(45, 138, 78, 0.08);
  transform: scale(1.02);
}

/* ── Submit Button ── */
.login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: 16px;
  font-size: 1.02rem;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(135deg, #1b5e2a, #2d8a4e, #43a047);
  color: #fff;
  box-shadow: 0 4px 24px rgba(45, 138, 78, 0.32);
  transition: all 0.3s ease;
  font-family: inherit;
  letter-spacing: 0.04em;
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 32px rgba(45, 138, 78, 0.45);
}
.login-btn:active:not(:disabled) { transform: translateY(0); }
.login-btn:disabled { opacity: 0.7; cursor: wait; }

.spinner {
  display: inline-block;
  width: 22px; height: 22px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer Link ── */
.login-footer {
  text-align: center;
  font-size: 0.85rem;
  color: #5a7a5a;
}
.login-footer a {
  color: #2d8a4e;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}
.login-footer a:hover { color: #1b5e2a; text-decoration: underline; }

/* ── Demo Account Hint ── */
.login-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}
.login-hint .hint-icon { font-size: 1rem; }
.login-hint p {
  font-size: 0.78rem;
  color: #8a9a8a;
}
.login-hint strong {
  color: #2d8a4e;
  font-weight: 600;
}

/* ── Credit Footer ── */
.login-credit {
  position: fixed;
  bottom: 20px;
  z-index: 1;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.45);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}
</style>
