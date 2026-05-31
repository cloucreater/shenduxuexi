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
    meta: { title: '数据看板', requiresAuth: true }
  },
  {
    path: '/image',
    name: 'ImageDetection',
    component: () => import('@/views/ImageDetection.vue'),
    meta: { title: '图片检测', requiresAuth: true }
  },
  {
    path: '/video',
    name: 'VideoDetection',
    component: () => import('@/views/VideoDetection.vue'),
    meta: { title: '视频检测', requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { title: '历史对比', requiresAuth: true }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: '智能分析', requiresAuth: true }
  },
  {
    path: '/trend',
    name: 'Trend',
    component: () => import('@/views/Trend.vue'),
    meta: { title: '趋势预测', requiresAuth: true }
  },
  {
    path: '/treatment',
    name: 'Treatment',
    component: () => import('@/views/Treatment.vue'),
    meta: { title: '防治方案', requiresAuth: true }
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: () => import('@/views/Evaluation.vue'),
    meta: { title: '效果评估', requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/views/Knowledge.vue'),
    meta: { title: '知识库', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { title: '系统管理', requiresAuth: true, roles: ['admin'] }
  },
  // Backward compatibility redirects
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
    redirect: '/dashboard'
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

  const token = localStorage.getItem('token')
  if (!authStore.token && token) {
    authStore.token = token
  }

  if (requiresAuth && !token && !authStore.token) {
    next('/login')
    return
  }

  if ((to.path === '/login' || to.path === '/register') && (token || authStore.token)) {
    if (authStore.user?.role === 'admin') {
      next('/admin')
    } else {
      next('/dashboard')
    }
    return
  }

  // Role guard: admin-only routes
  const requiredRoles = to.meta.roles as string[] | undefined
  if (requiredRoles && requiredRoles.length > 0) {
    const userRole = authStore.user?.role
    if (!userRole || !requiredRoles.includes(userRole)) {
      next('/dashboard')
      return
    }
  }

  next()
})

export default router
