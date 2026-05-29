<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NotificationDropdown from '@/components/NotificationDropdown.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const sidebarOpen = ref(false)
const refreshKey = ref(0)

const menuSections = [
  {
    title: '主菜单',
    items: [
      { path: '/dashboard', label: '📊 数据看板', icon: '📊' },
      { path: '/image', label: '📷 图片检测', icon: '📷' },
      { path: '/video', label: '🎥 视频检测', icon: '🎥' },
      { path: '/camera', label: '📡 实时摄像头', icon: '📡' },
    ]
  },
  {
    title: '智能分析',
    items: [
      { path: '/analysis', label: '🧠 智能分析', icon: '🧠' },
      { path: '/trend', label: '📈 趋势预测', icon: '📈' },
      { path: '/treatment', label: '💊 防治方案', icon: '💊' },
      { path: '/evaluation', label: '⭐ 效果评估', icon: '⭐' },
    ]
  },
  {
    title: '资源',
    items: [
      { path: '/knowledge', label: '📚 知识库', icon: '📚' },
    ]
  }
]

const currentPath = computed(() => route.path)
const pageTitle = computed(() => {
  const metaTitle = route.meta?.title as string | undefined
  return metaTitle || '页面'
})

function navigateTo(path: string) {
  router.push(path)
  sidebarOpen.value = false
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function goProfile() {
  router.push('/profile')
  sidebarOpen.value = false
}

function refreshPage() {
  refreshKey.value++
}

onMounted(() => {
  if (!authStore.token) {
    const token = localStorage.getItem('token')
    if (token) {
      authStore.token = token
    }
  }
})
</script>

<template>
  <div class="app-layout">
    <!-- Mobile menu toggle -->
    <button
      class="menu-toggle"
      @click="sidebarOpen = !sidebarOpen"
      v-show="!sidebarOpen"
    >
      <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>

    <!-- Sidebar -->
    <aside :class="['sidebar', { open: sidebarOpen }]">
      <!-- Logo -->
      <div class="sidebar-logo">
        <span class="logo-icon">🌾</span>
        <h1>智慧农害</h1>
        <div class="subtitle">SMART AGRICULTURE DISEASE DETECTION</div>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <div v-for="section in menuSections" :key="section.title" class="nav-section">
          <div class="nav-section-title">{{ section.title }}</div>
          <button
            v-for="item in section.items"
            :key="item.path"
            :class="['nav-item', { active: currentPath === item.path }]"
            @click="navigateTo(item.path)"
          >
            <span class="nav-item-icon">{{ item.icon }}</span>
            <span>{{ item.label.replace(/^[^\s]+\s/, '') }}</span>
          </button>
        </div>
      </nav>

      <!-- Footer -->
      <div class="sidebar-footer">
        <div class="user-info" @click="goProfile" style="cursor:pointer;">
          <div class="user-avatar">
            {{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}
          </div>
          <div>
            <div class="user-name">{{ authStore.user?.username || '管理员' }}</div>
            <div class="user-role">{{ authStore.user?.role === 'admin' ? '系统管理员' : '普通用户' }}</div>
          </div>
        </div>
        <button class="btn btn-outline btn-sm" style="width:100%;" @click="handleLogout">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          退出登录
        </button>
        <div style="text-align:center;color:rgba(255,255,255,0.15);font-size:0.6rem;margin-top:10px;">
          v4.0 · CNN + PyTorch + YOLO
        </div>
      </div>
    </aside>

    <!-- Overlay for mobile -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Top Bar -->
      <header class="topbar glass">
        <div class="topbar-left">
          <div class="topbar-breadcrumb">
            <span class="breadcrumb-home" @click="router.push('/dashboard')">🏠</span>
            <span class="breadcrumb-sep">/</span>
            <span class="breadcrumb-current">{{ pageTitle }}</span>
          </div>
        </div>
        <div class="topbar-right">
          <button class="topbar-btn" title="刷新页面" @click="refreshPage">
            🔄
          </button>
          <NotificationDropdown />
          <ThemeToggle />
        </div>
      </header>

      <!-- Page Content -->
      <div class="page-content">
        <RouterView v-slot="{ Component, route: r }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="refreshKey + '-' + r.fullPath" />
          </transition>
        </RouterView>
      </div>
    </div>
  </div>
</template>

<style scoped>
.menu-toggle {
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 150;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(10, 40, 20, 0.9);
  color: #fff;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  z-index: 99;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

/* ── Top Bar ── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 56px;
  margin-bottom: 20px;
  border-radius: var(--radius-lg);
  position: sticky;
  top: 12px;
  z-index: 50;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}

.breadcrumb-home {
  cursor: pointer;
  font-size: 1rem;
  transition: transform 0.2s;
}
.breadcrumb-home:hover {
  transform: scale(1.2);
}

.breadcrumb-sep {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.breadcrumb-current {
  color: var(--text-secondary);
  font-weight: 600;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  color: var(--text-primary);
  backdrop-filter: blur(10px);
  padding: 0;
}
.topbar-btn:hover {
  border-color: var(--color-accent);
  background: var(--glass-bg-hover);
  transform: scale(1.08);
}

/* ── Page Content ── */
.page-content {
  min-height: calc(100vh - 96px);
}

/* ── Sidebar user info hover ── */
.user-info {
  border-radius: 12px;
  padding: 8px;
  margin: -8px;
  transition: background 0.2s;
}
.user-info:hover {
  background: rgba(255, 255, 255, 0.06);
}

@media (max-width: 768px) {
  .menu-toggle { display: flex; }
  .topbar {
    padding: 0 14px;
    height: 50px;
    margin-bottom: 14px;
  }
  .breadcrumb-current {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
