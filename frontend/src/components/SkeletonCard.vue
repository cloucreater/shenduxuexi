<script setup lang="ts">
withDefaults(defineProps<{
  width?: string
  height?: string
  borderRadius?: string
  lines?: number
  variant?: 'card' | 'text' | 'circle' | 'chart'
}>(), {
  width: '100%',
  height: '20px',
  borderRadius: '10px',
  lines: 3,
  variant: 'text',
})
</script>

<template>
  <div v-if="variant === 'card'" class="skeleton-card" :style="{ borderRadius }">
    <div class="skeleton-block" style="height:180px;margin-bottom:16px;"></div>
    <div class="skeleton-block" style="width:60%;height:22px;margin-bottom:12px;"></div>
    <div class="skeleton-block" style="width:90%;height:14px;margin-bottom:8px;"></div>
    <div class="skeleton-block" style="width:75%;height:14px;"></div>
  </div>

  <div v-else-if="variant === 'chart'" class="skeleton-card" :style="{ borderRadius }">
    <div class="skeleton-block" style="height:24px;width:40%;margin-bottom:16px;"></div>
    <div class="skeleton-block" :style="{ height, width, borderRadius: '12px' }"></div>
  </div>

  <div v-else-if="variant === 'circle'" class="skeleton-circle" :style="{ width: height, height }">
    <div class="skeleton-block" style="width:100%;height:100%;border-radius:50%;"></div>
  </div>

  <div v-else class="skeleton-lines" :style="{ width }">
    <div
      v-for="i in lines"
      :key="i"
      class="skeleton-block"
      :style="{
        height,
        width: i === lines ? '60%' : '100%',
        marginBottom: i < lines ? '10px' : '0',
        borderRadius,
      }"
    ></div>
  </div>
</template>

<style scoped>
.skeleton-card,
.skeleton-lines {
  width: 100%;
}

.skeleton-block {
  background: linear-gradient(90deg,
    rgba(255,255,255,0.04) 25%,
    rgba(255,255,255,0.08) 50%,
    rgba(255,255,255,0.04) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 10px;
}

.skeleton-circle {
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>