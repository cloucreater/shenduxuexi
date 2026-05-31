<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''

  if (!username.value || !password.value || !confirmPassword.value || !email.value || !phone.value) {
    errorMessage.value = '请填写所有必填字段'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  if (password.value.length < 6) {
    errorMessage.value = '密码长度至少为6位'
    return
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }

  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    errorMessage.value = '请输入有效的手机号'
    return
  }

  isLoading.value = true
  try {
    await authStore.register(username.value, password.value, email.value || undefined, phone.value || undefined)
    router.push('/')
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <!-- Background -->
    <div class="register-bg"></div>

    <!-- Floating elements -->
    <div class="floating-leaves">
      <span class="leaf leaf-1"></span>
      <span class="leaf leaf-2"></span>
      <span class="leaf leaf-3"></span>
      <span class="leaf leaf-4"></span>
    </div>

    <!-- Register Card -->
    <div class="register-card animate-scale">
      <!-- Logo -->
      <div class="register-logo">
        <div class="register-icon-wrapper">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 22h20L12 2z" />
            <path d="M12 2v20" />
            <path d="M8 14c1.5-2 2.5-4 4-4s2.5 2 4 4" />
          </svg>
        </div>
        <h1>创建账号</h1>
        <p>加入智慧农业病害检测系统</p>
      </div>

      <!-- Error -->
      <div v-if="errorMessage" class="register-error">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="input-group">
          <label>用户名 <span class="required">*</span></label>
          <input v-model="username" type="text" placeholder="请输入用户名" autocomplete="username" />
        </div>

        <div class="input-group">
          <label>邮箱 <span class="required">*</span></label>
          <input v-model="email" type="email" placeholder="请输入邮箱地址" autocomplete="email" />
        </div>

        <div class="input-group">
          <label>手机号 <span class="required">*</span></label>
          <input v-model="phone" type="tel" placeholder="请输入手机号" autocomplete="tel" />
        </div>

        <div class="input-group">
          <label>密码 <span class="required">*</span></label>
          <div class="relative">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="pr-12"
              placeholder="请输入密码（至少6位）"
              autocomplete="new-password"
            />
            <button
              @click="showPassword = !showPassword"
              type="button"
              class="toggle-password"
            >
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242" />
              </svg>
            </button>
          </div>
        </div>

        <div class="input-group">
          <label>确认密码 <span class="required">*</span></label>
          <div class="relative">
            <input
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="pr-12"
              placeholder="请再次输入密码"
              autocomplete="new-password"
            />
            <button
              @click="showConfirmPassword = !showConfirmPassword"
              type="button"
              class="toggle-password"
            >
              <svg v-if="showConfirmPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242" />
              </svg>
            </button>
          </div>
        </div>

        <button type="submit" :disabled="isLoading" class="register-btn">
          <span v-if="isLoading" class="spinner"></span>
          <template v-else>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            注 册
          </template>
        </button>

        <div class="register-footer">
          <span>已有账号？</span>
          <router-link to="/login">立即登录 →</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* ── Background ── */
.register-bg {
  position: fixed;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(11, 52, 18, 0.8) 0%, rgba(27, 94, 42, 0.68) 35%, rgba(56, 142, 60, 0.52) 65%, rgba(27, 94, 42, 0.7) 100%),
    url('https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=1920&q=80') center/cover no-repeat;
  z-index: 0;
}
.register-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 30% 40%, rgba(255, 255, 255, 0.07) 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, rgba(102, 187, 106, 0.2) 0%, transparent 45%);
}

/* ── Floating Leaves ── */
.floating-leaves { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
.floating-leaves .leaf {
  position: absolute;
  width: 40px; height: 40px;
  border-radius: 0 80% 0 80%;
  background: rgba(102, 187, 106, 0.1);
  animation: floatLeaf 8s ease-in-out infinite;
}
.floating-leaves .leaf-1 { top: 8%; left: 10%; animation-delay: 0s; }
.floating-leaves .leaf-2 { top: 20%; right: 14%; animation-delay: 2s; width: 32px; height: 32px; border-radius: 80% 0 80% 0; }
.floating-leaves .leaf-3 { bottom: 18%; left: 12%; animation-delay: 4s; width: 36px; height: 36px; }
.floating-leaves .leaf-4 { bottom: 12%; right: 8%; animation-delay: 6s; width: 44px; height: 44px; border-radius: 80% 0 80% 0; }

@keyframes floatLeaf {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.14; }
  25% { transform: translateY(-20px) rotate(6deg); opacity: 0.24; }
  50% { transform: translateY(-8px) rotate(-4deg); opacity: 0.16; }
  75% { transform: translateY(-24px) rotate(3deg); opacity: 0.22; }
}

/* ── Card ── */
.register-card {
  position: relative;
  z-index: 1;
  width: 460px;
  max-width: 92vw;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: saturate(180%) blur(28px);
  -webkit-backdrop-filter: saturate(180%) blur(28px);
  border-radius: 28px;
  padding: 40px 40px 36px;
  box-shadow:
    0 8px 48px rgba(0, 0, 0, 0.13),
    0 0 100px rgba(102, 187, 106, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.5);
  margin: 20px;
}

/* ── Logo ── */
.register-logo { text-align: center; margin-bottom: 24px; }
.register-icon-wrapper {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(45, 138, 78, 0.12), rgba(102, 187, 106, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 4px 20px rgba(102, 187, 106, 0.2);
  animation: float 3s ease-in-out infinite;
  color: #2d8a4e;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.register-logo h1 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1b5e2a;
}
.register-logo p {
  color: #5a7a5a;
  font-size: 0.82rem;
  margin-top: 4px;
}

/* ── Error ── */
.register-error {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(229, 57, 53, 0.06);
  border: 1px solid rgba(229, 57, 53, 0.18);
  color: #c62828;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.85rem;
  margin-bottom: 20px;
}

/* ── Form ── */
.register-form { display: flex; flex-direction: column; gap: 16px; }

.input-group label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #2e3a2e;
  margin-bottom: 6px;
}
.input-group .required { color: #e53935; }

.input-group input {
  width: 100%;
  padding: 12px 16px;
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

.relative { position: relative; }

.toggle-password {
  position: absolute;
  right: 4px; top: 50%;
  transform: translateY(-50%);
  background: none; border: none;
  color: #8a9a8a;
  cursor: pointer;
  padding: 8px;
  transition: color 0.2s;
}
.toggle-password:hover { color: #2d8a4e; }

/* ── Button ── */
.register-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(135deg, #1b5e2a, #2d8a4e, #43a047);
  color: #fff;
  box-shadow: 0 4px 24px rgba(45, 138, 78, 0.32);
  transition: all 0.3s ease;
  font-family: inherit;
  margin-top: 4px;
}
.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 32px rgba(45, 138, 78, 0.45);
}
.register-btn:disabled { opacity: 0.7; cursor: wait; }

.spinner {
  display: inline-block;
  width: 22px; height: 22px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer ── */
.register-footer {
  text-align: center;
  font-size: 0.85rem;
  color: #5a7a5a;
}
.register-footer a {
  color: #2d8a4e;
  font-weight: 600;
  text-decoration: none;
}
.register-footer a:hover { color: #1b5e2a; text-decoration: underline; }
</style>
