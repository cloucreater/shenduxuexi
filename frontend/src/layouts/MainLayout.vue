<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isDark = ref(false)
const sidebarOpen = ref(false)

const menuSections = [
  {
    title: '主菜单',
    items: [
      { path: '/', label: '📊 数据看板', icon: 'dashboard', roles: ['user', 'admin'] },
      { path: '/detect/image', label: '🔍 图片检测', icon: 'image', roles: ['user', 'admin'] },
      { path: '/detect/video', label: '🎬 视频检测', icon: 'video', roles: ['user', 'admin'] },
      { path: '/detect/camera', label: '📷 实时摄像头', icon: 'camera', roles: ['user', 'admin'] },
    ]
  },
  {
    title: '智能分析',
    items: [
      { path: '/predict', label: '📈 趋势预测', icon: 'trend', roles: ['user', 'admin'] },
      { path: '/treatment', label: '💊 防治方案', icon: 'treatment', roles: ['user', 'admin'] },
      { path: '/evaluation', label: '📋 效果评估', icon: 'evaluation', roles: ['user', 'admin'] },
      { path: '/compare', label: '🔄 历史对比', icon: 'compare', roles: ['user', 'admin'] },
    ]
  },
  {
    title: '资源',
    items: [
      { path: '/knowledge', label: '📚 知识库', icon: 'knowledge', roles: ['user', 'admin'] },
      { path: '/profile', label: '👤 个人中心', icon: 'profile', roles: ['user'] },
    ]
  },
  {
    title: '系统管理',
    items: [
      { path: '/admin', label: '⚙️ 系统概览', icon: 'admin', roles: ['admin'] },
    ]
  }
]

const currentPath = computed(() => route.path)
const userRole = computed(() => authStore.user?.role || 'user')

const visibleSections = computed(() =>
  menuSections.map(s => ({
    ...s,
    items: s.items.filter(i => i.roles.includes(userRole.value))
  })).filter(s => s.items.length > 0)
)

const breadcrumbs = computed(() => {
  const map: Record<string, { label: string; path: string }[]> = {}
  for (const section of menuSections) {
    for (const item of section.items) {
      map[item.path] = [{ label: item.label.replace(/^[^\s]+\s/, ''), path: item.path }]
    }
  }
  // Handle sub-routes
  if (route.path.startsWith('/detect/image/history')) {
    return [
      { label: '图片检测', path: '/detect/image' },
      { label: '历史记录', path: route.path }
    ]
  }
  if (route.path.startsWith('/detect/video/history')) {
    return [
      { label: '视频检测', path: '/detect/video' },
      { label: '历史记录', path: route.path }
    ]
  }
  if (route.path.startsWith('/detect/camera/history')) {
    return [
      { label: '实时摄像头', path: '/detect/camera' },
      { label: '历史记录', path: route.path }
    ]
  }
  return map[route.path] || [{ label: '数据看板', path: '/' }]
})

function navigateTo(path: string) {
  router.push(path)
  sidebarOpen.value = false
}

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved === 'dark') {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<template>
  <div class="flex min-h-screen">
    <!-- Background overlay -->
    <div class="bg-overlay"></div>

    <!-- Mobile menu button -->
    <button
      class="menu-btn fixed top-3 left-3 z-50 p-2.5 rounded-xl"
      style="display: none; background: var(--surface-bg); border: 1px solid var(--surface-border);"
      @click="sidebarOpen = !sidebarOpen"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>

    <!-- Sidebar -->
    <aside :class="['sidebar', { open: sidebarOpen }]">
      <!-- Logo Area -->
      <div class="sidebar-logo">
        <div class="flex items-center justify-center gap-2 mb-1">
          <span class="text-2xl">🌾</span>
          <h1>智慧农害</h1>
        </div>
        <div class="subtitle">Smart Agriculture · Disease Detection</div>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <div v-for="section in visibleSections" :key="section.title" class="nav-section">
          <div class="nav-section-title">{{ section.title }}</div>
          <button
            v-for="item in section.items"
            :key="item.path"
            :class="['nav-item', { active: currentPath === item.path || (item.path !== '/' && currentPath.startsWith(item.path)) }]"
            @click="navigateTo(item.path)"
          >
            <span class="nav-item-icon">{{ item.label.split(' ')[0] }}</span>
            <span class="nav-item-label">{{ item.label.replace(/^[^\s]+\s/, '') }}</span>
            <span v-if="currentPath === item.path || (item.path !== '/' && currentPath.startsWith(item.path))" class="nav-item-dot"></span>
          </button>
        </div>
      </nav>

      <!-- Sidebar Footer -->
      <div class="sidebar-footer">
        <div class="flex items-center gap-3 px-3 py-2">
          <div class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
          <span style="color: rgba(255,255,255,0.5); font-size: 0.72rem;">系统运行中</span>
        </div>
        <div class="text-center" style="color: rgba(255,255,255,0.22); font-size: 0.65rem; padding: 8px;">
          v3.0 · CNN + PyTorch + YOLO
        </div>
      </div>
    </aside>

    <!-- Main Area -->
    <div class="main-content">
      <!-- Topbar -->
      <header class="topbar">
        <!-- Breadcrumb -->
        <nav class="breadcrumb">
          <template v-for="(crumb, idx) in breadcrumbs" :key="crumb.path">
            <a v-if="idx < breadcrumbs.length - 1" href="#" @click.prevent="navigateTo(crumb.path)">
              {{ crumb.label }}
            </a>
            <span v-else class="current">{{ crumb.label }}</span>
            <span v-if="idx < breadcrumbs.length - 1" class="sep">›</span>
          </template>
        </nav>

        <!-- Right Actions -->
        <div class="topbar-actions">
          <!-- Theme Toggle -->
          <button
            class="theme-toggle"
            @click="toggleTheme"
            :title="isDark ? '切换浅色模式' : '切换深色模式'"
          >
            {{ isDark ? '☀️' : '🌙' }}
          </button>

          <!-- Notifications -->
          <button class="theme-toggle relative" title="通知中心">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span class="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white dark:border-gray-800"></span>
          </button>

          <!-- User Menu -->
          <div class="user-badge" @click="navigateTo('/profile')">
            <div class="user-avatar">
              {{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}
            </div>
            <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
            <svg class="w-3.5 h-3.5" style="color:var(--text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <!-- Logout -->
          <button class="btn btn-outline btn-sm" @click="handleLogout">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            退出
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <div class="page-content">
        <router-view v-slot="{ Component, route: r }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="r.fullPath" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Sidebar footer */
.sidebar-footer {
  padding: 10px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* Nav item label & dot */
.nav-item-label {
  flex: 1;
}
.nav-item-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--green-400);
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
}

/* Page transition */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Page content wrapper */
.page-content {
  min-height: calc(100vh - var(--topbar-height) - 64px);
}
</style>
