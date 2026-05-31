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
const isAdmin = computed(() => authStore.user?.role === 'admin')

const menuSections = computed(() => {
  const base = [
    {
      title: '主菜单',
      items: [
        { path: '/dashboard', label: '数据看板', icon: 'dashboard' },
        { path: '/image', label: '图片检测', icon: 'image' },
        { path: '/video', label: '视频检测', icon: 'video' },
        { path: '/history', label: '历史对比', icon: 'history' },
      ]
    },
    {
      title: '智能分析',
      items: [
        { path: '/analysis', label: '智能分析', icon: 'brain' },
        { path: '/trend', label: '趋势预测', icon: 'trend' },
        { path: '/treatment', label: '防治方案', icon: 'treatment' },
        { path: '/evaluation', label: '效果评估', icon: 'evaluation' },
      ]
    },
    {
      title: '资源',
      items: [
        { path: '/knowledge', label: '知识库', icon: 'knowledge' },
      ]
    }
  ]

  if (isAdmin.value) {
    base.push({
      title: '系统管理',
      items: [
        { path: '/admin', label: '系统管理', icon: 'admin' },
      ]
    })
  }

  return base
})

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

onMounted(async () => {
  if (!authStore.token) {
    const token = localStorage.getItem('token')
    if (token) {
      authStore.token = token
    }
  }
  
  // 初始化认证状态，获取用户信息（包括头像）
  await authStore.initAuth()
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
        <span class="logo-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 22h20L12 2z" />
            <path d="M12 2v20" />
            <path d="M8 14c1.5-2 2.5-4 4-4s2.5 2 4 4" />
          </svg>
        </span>
        <h1>智慧农业病害检测</h1>
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
            <span class="nav-item-icon">
              <svg v-if="item.icon === 'dashboard'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
              <svg v-else-if="item.icon === 'image'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
              <svg v-else-if="item.icon === 'video'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="16" height="16" rx="2"/><polygon points="22,7 18,10 18,14 22,17"/></svg>
              <svg v-else-if="item.icon === 'history'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.5 17.5A9 9 0 102 12"/></svg>
              <svg v-else-if="item.icon === 'brain'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.95.5H8a2.5 2.5 0 01-2.5-2.5V6.5A2.5 2.5 0 019.5 4h.5z"/><path d="M14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.95.5H16a2.5 2.5 0 002.5-2.5V6.5A2.5 2.5 0 0014.5 4h-.5z"/></svg>
              <svg v-else-if="item.icon === 'trend'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
              <svg v-else-if="item.icon === 'treatment'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L9 7l-5 1 4 4-1 5 5-2.5L17 17l-1-5 4-4-5-1-3-5z"/></svg>
              <svg v-else-if="item.icon === 'evaluation'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26"/></svg>
              <svg v-else-if="item.icon === 'knowledge'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4v16a2.5 2.5 0 002.5 2.5H20V2H6.5A2.5 2.5 0 004 4.5V4z"/></svg>
              <svg v-else-if="item.icon === 'admin'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>
            </span>
            <span>{{ item.label }}</span>
          </button>
        </div>
      </nav>

      <!-- Footer -->
      <div class="sidebar-footer">
        <div class="user-info" @click="goProfile" style="cursor:pointer;">
          <div 
            class="user-avatar"
            :style="authStore.user?.avatar ? { backgroundImage: 'url(' + authStore.user.avatar + ')', backgroundSize: 'cover' } : {}"
          >
            <span v-if="!authStore.user?.avatar">{{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}</span>
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
            <span class="breadcrumb-home" @click="router.push('/dashboard')" title="首页">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            </span>
            <span class="breadcrumb-sep">/</span>
            <span class="breadcrumb-current">{{ pageTitle }}</span>
          </div>
        </div>
        <div class="topbar-right">
          <button class="topbar-btn" title="刷新页面" @click="refreshPage">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <polyline points="23 4 23 10 17 10"/>
              <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/>
            </svg>
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