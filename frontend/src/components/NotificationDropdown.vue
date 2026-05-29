<script setup lang="ts">
import { ref } from 'vue'
import { useNotification } from '@/composables/useNotification'

const { notifications, unreadCount, markAsRead, markAllRead, clearAll } = useNotification()
const isOpen = ref(false)

function toggle() {
  isOpen.value = !isOpen.value
}

function handleItemClick(id: number) {
  markAsRead(id)
}

function handleMarkAll() {
  markAllRead()
}
</script>

<template>
  <div class="notif-wrapper">
    <button class="notif-trigger" @click.stop="toggle" title="通知中心">
      🔔
      <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
    </button>

    <!-- Dropdown -->
    <Transition name="drop">
      <div v-if="isOpen" class="notif-dropdown glass" @click.stop>
        <div class="notif-header">
          <h3>通知中心</h3>
          <div class="notif-header-actions">
            <button v-if="unreadCount > 0" class="notif-action" @click="handleMarkAll">标记已读</button>
            <button v-if="notifications.length > 0" class="notif-action" @click="clearAll">清空</button>
          </div>
        </div>

        <div v-if="notifications.length === 0" class="notif-empty">
          <div style="font-size:2.5rem;margin-bottom:10px;">🔔</div>
          <p>暂无通知</p>
        </div>

        <div v-else class="notif-list">
          <div
            v-for="notif in notifications"
            :key="notif.id"
            :class="['notif-item', { unread: !notif.read }]"
            @click="handleItemClick(notif.id)"
          >
            <div class="notif-icon-wrap" :class="'notif-' + notif.type">
              {{ notif.icon }}
            </div>
            <div class="notif-body">
              <div class="notif-title">
                {{ notif.title }}
                <span v-if="!notif.read" class="notif-dot"></span>
              </div>
              <p class="notif-message">{{ notif.message }}</p>
              <span class="notif-time">{{ notif.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.notif-wrapper { position: relative; }

.notif-trigger {
  position: relative;
  width: 38px; height: 38px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  cursor: pointer;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: var(--text-primary);
  backdrop-filter: blur(10px);
}
.notif-trigger:hover {
  border-color: var(--color-accent);
  background: var(--glass-bg-hover);
  transform: scale(1.08);
}

.notif-badge {
  position: absolute;
  top: -4px; right: -6px;
  min-width: 18px; height: 18px;
  border-radius: 9px;
  background: #f44336;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid var(--topbar-bg);
}

.notif-dropdown {
  position: absolute;
  top: 48px; right: -10px;
  width: 380px;
  max-height: 480px;
  overflow-y: auto;
  padding: 0;
  z-index: 300;
  animation: fadeInDown 0.2s ease both;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid var(--glass-border);
}
.notif-header h3 {
  font-weight: 700;
  font-size: 1rem;
  margin: 0;
  color: var(--text-primary);
}
.notif-header-actions { display: flex; gap: 10px; }
.notif-action {
  font-size: 0.78rem;
  color: var(--color-accent);
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
}
.notif-action:hover { background: rgba(76,175,80,0.1); }

.notif-empty {
  text-align: center;
  padding: 48px 20px;
  color: var(--text-muted);
}

.notif-list { padding: 8px; }

.notif-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.notif-item:hover { background: var(--section-bg); }
.notif-item.unread {
  background: var(--color-accent-glow);
  border-color: rgba(76,175,80,0.12);
}

.notif-icon-wrap {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.notif-success { background: var(--color-success-bg); }
.notif-warning { background: var(--color-warning-bg); }
.notif-info { background: var(--color-info-bg); }

.notif-body { flex: 1; min-width: 0; }
.notif-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}
.notif-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #f44336;
  flex-shrink: 0;
}
.notif-message {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin: 4px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.notif-time {
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* Drop transition */
.drop-enter-active { transition: all 0.25s cubic-bezier(0.16,1,0.3,1); }
.drop-leave-active { transition: all 0.15s ease; }
.drop-enter-from { opacity: 0; transform: translateY(-10px) scale(0.96); }
.drop-leave-to { opacity: 0; transform: translateY(-6px) scale(0.96); }

@media (max-width: 480px) {
  .notif-dropdown {
    width: 300px;
    right: -60px;
  }
}
</style>
