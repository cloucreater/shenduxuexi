import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/theme.css'
import './styles/global.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初始化认证
const initApp = async () => {
  const authStore = useAuthStore()
  await authStore.initAuth()
  app.mount('#app')
}

initApp()
