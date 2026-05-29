import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '📊 数据看板', requiresAuth: true }
  },
  {
    path: '/image',
    name: 'ImageDetection',
    component: () => import('@/views/ImageDetection.vue'),
    meta: { title: '📷 图片检测', requiresAuth: true }
  },
  {
    path: '/video',
    name: 'VideoDetection',
    component: () => import('@/views/VideoDetection.vue'),
    meta: { title: '🎥 视频检测', requiresAuth: true }
  },
  {
    path: '/camera',
    name: 'Camera',
    component: () => import('@/views/Camera.vue'),
    meta: { title: '📡 实时摄像头', requiresAuth: true }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: '🧠 智能分析', requiresAuth: true }
  },
  {
    path: '/trend',
    name: 'Trend',
    component: () => import('@/views/Trend.vue'),
    meta: { title: '📈 趋势预测', requiresAuth: true }
  },
  {
    path: '/treatment',
    name: 'Treatment',
    component: () => import('@/views/Treatment.vue'),
    meta: { title: '💊 防治方案', requiresAuth: true }
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: () => import('@/views/Evaluation.vue'),
    meta: { title: '⭐ 效果评估', requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/views/Knowledge.vue'),
    meta: { title: '📚 知识库', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '👤 个人中心', requiresAuth: true }
  },
  // Keep old routes for backward compatibility
  {
    path: '/detect/image',
    redirect: '/image'
  },
  {
    path: '/detect/video',
    redirect: '/video'
  },
  {
    path: '/detect/camera',
    redirect: '/camera'
  },
  {
    path: '/predict',
    redirect: '/trend'
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  // Check localStorage for token
  const token = localStorage.getItem('token')
  if (!authStore.token && token) {
    authStore.token = token
  }

  if (requiresAuth && !token && !authStore.token) {
    next('/login')
    return
  }

  if ((to.path === '/login' || to.path === '/register') && (token || authStore.token)) {
    next('/dashboard')
    return
  }

  next()
})

export default router
