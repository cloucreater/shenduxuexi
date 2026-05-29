<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { isDark, toggle } = useTheme()
</script>

<template>
  <button
    class="theme-toggle-btn"
    :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
    @click="toggle"
  >
    <span class="theme-toggle-icon">{{ isDark ? '☀️' : '🌙' }}</span>
  </button>
</template>

<style scoped>
.theme-toggle-btn {
  width: 38px; height: 38px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  backdrop-filter: blur(10px);
  padding: 0;
}
.theme-toggle-btn:hover {
  border-color: var(--color-accent);
  background: var(--glass-bg-hover);
  transform: rotate(15deg) scale(1.08);
}
.theme-toggle-icon {
  font-size: 1rem;
  line-height: 1;
}
</style>
