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
      <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
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
          <svg width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" style="margin-bottom:10px;opacity:0.4;"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
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
              <svg v-if="notif.type === 'success'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
              <svg v-else-if="notif.type === 'warning'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
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
  background: rgba(10,38,20,0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
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
