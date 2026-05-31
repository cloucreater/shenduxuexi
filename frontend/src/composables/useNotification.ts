import { ref, computed } from 'vue'

const notifications = ref([
  {
    id: 1,
    type: 'success',
    title: '模型训练完成',
    message: 'CNN v3 病害分类模型训练完成，准确率提升至 68.5%',
    time: '10 分钟前',
    read: false,
  },
  {
    id: 2,
    type: 'warning',
    title: '检测到新病害',
    message: '摄像头检测到疑似晚疫病新发病例，建议立即查看',
    time: '28 分钟前',
    read: false,
  },
  {
    id: 3,
    type: 'info',
    title: '防治方案更新',
    message: '叶斑病防治方案已更新，新增 2 种推荐药剂',
    time: '1 小时前',
    read: false,
  },
  {
    id: 4,
    type: 'info',
    title: '系统公告',
    message: '系统将于本周六凌晨 2:00-4:00 进行维护升级，届时服务暂停',
    time: '2 小时前',
    read: true,
  },
  {
    id: 5,
    type: 'success',
    title: '数据报告生成',
    message: '本月病害检测月报已自动生成，可在数据看板查看',
    time: '5 小时前',
    read: true,
  },
  {
    id: 6,
    type: 'warning',
    title: '气象预警',
    message: '未来48小时有连续降雨，请注意田间排水和晚疫病预防',
    time: '8 小时前',
    read: true,
  },
])

export function useNotification() {
  const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

  function markAsRead(id: number) {
    const n = notifications.value.find(x => x.id === id)
    if (n) n.read = true
  }

  function markAllRead() {
    notifications.value.forEach(n => { n.read = true })
  }

  function clearAll() {
    notifications.value = []
  }

  function addNotification(notif: { type: string; title: string; message: string }) {
    notifications.value.unshift({
      id: Date.now(),
      type: notif.type,
      title: notif.title,
      message: notif.message,
      time: '刚刚',
      read: false,
    })
  }

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllRead,
    clearAll,
    addNotification,
  }
}
