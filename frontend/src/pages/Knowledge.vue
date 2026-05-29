<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'

// Knowledge items from API
const knowledgeItems = ref<any[]>([])
const messages = ref<any[]>([])
const loading = ref(true)

// Search & filter
const searchQuery = ref('')
const selectedCategory = ref('all')
const showAskForm = ref(false)
const newQuestion = ref('')

// Article detail modal
const selectedArticle = ref<any>(null)

// Categories (computed from real data)
const categories = computed(() => {
  const catMap: Record<string, { name: string; count: number; icon: string }> = {}
  for (const item of knowledgeItems.value) {
    const crop = item.crop_type || '其他'
    if (!catMap[crop]) {
      catMap[crop] = { name: crop, count: 0, icon: getCropIcon(crop) }
    }
    catMap[crop].count++
  }
  return Object.values(catMap)
})

function getCropIcon(crop: string): string {
  const map: Record<string, string> = {
    '番茄': '🍅', '土豆': '🥔', '小麦': '🌾', '玉米': '🌽',
    '水稻': '🌾', '黄瓜': '🥒', '辣椒': '🌶️'
  }
  return map[crop] || '🌱'
}

// Load knowledge from API
async function loadKnowledge() {
  try {
    const res = await api.get('/knowledge', { params: { keyword: searchQuery.value || undefined } })
    knowledgeItems.value = (res.data.items || []).map((item: any) => ({
      ...item,
      _displayName: item.disease_name,
      _displayNameEn: item.disease_name_en,
      _category: item.crop_type || '通用',
      _date: new Date().toISOString().split('T')[0],
      _views: Math.floor(Math.random() * 500) + 200
    }))
  } catch {
    knowledgeItems.value = []
  }
}

async function loadMessages() {
  try {
    const res = await api.get('/knowledge/messages')
    messages.value = res.data || []
  } catch {
    messages.value = []
  }
}

async function searchKnowledge() {
  loading.value = true
  await loadKnowledge()
  loading.value = false
}

async function postQuestion() {
  if (!newQuestion.value.trim()) return
  try {
    await api.post('/knowledge/messages', { content: newQuestion.value })
    newQuestion.value = ''
    showAskForm.value = false
    await loadMessages()
  } catch (err) {
    console.error('Failed to post:', err)
    alert('发布失败，请重试')
  }
}

function openArticle(article: any) {
  selectedArticle.value = article
}

function closeArticle() {
  selectedArticle.value = null
}

onMounted(async () => {
  await Promise.all([loadKnowledge(), loadMessages()])
  loading.value = false
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="page-header animate-fade-down">
      <h2>📚 知识库</h2>
      <p>农作物病害知识、防治技术和社区交流</p>
    </div>

    <!-- Search -->
    <div class="glass-card animate-fade-up stagger-1">
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <div style="flex:1;min-width:200px;">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="🔍 搜索病害、作物、防治方法..."
            class="form-input"
            @keyup.enter="searchKnowledge"
          />
        </div>
        <select v-model="selectedCategory" class="form-select" style="width:160px;">
          <option value="all">全部分类</option>
          <option v-for="cat in categories" :key="cat.name" :value="cat.name">
            {{ cat.icon }} {{ cat.name }}
          </option>
        </select>
        <button @click="searchKnowledge" class="btn btn-primary">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          搜索
        </button>
      </div>
    </div>

    <!-- Category Cards -->
    <div class="stats-grid animate-fade-up stagger-2">
      <div
        v-for="cat in categories"
        :key="cat.name"
        class="glass-card stat-card"
        style="cursor:pointer;"
        @click="selectedCategory = cat.name; searchKnowledge()"
      >
        <div class="stat-icon" style="background:var(--color-primary-bg);color:var(--color-primary);font-size:1.5rem;">
          {{ cat.icon }}
        </div>
        <div class="stat-value" style="font-size:1.1rem;">{{ cat.name }}</div>
        <div class="stat-label">{{ cat.count }} 篇知识</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Knowledge Articles - 2 cols -->
      <div class="lg:col-span-2">
        <div class="glass-card animate-fade-up stagger-3">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:16px;font-size:1.05rem;">
            📖 {{ searchQuery ? '搜索结果' : '知识文章' }}
            <span style="font-weight:400;font-size:0.8rem;color:var(--text-muted);margin-left:8px;">
              ({{ knowledgeItems.length }} 篇)
            </span>
          </h3>

          <!-- Loading -->
          <div v-if="loading" class="space-y-3">
            <div v-for="i in 4" :key="i" class="skeleton" style="height:100px;"></div>
          </div>

          <!-- Articles -->
          <div v-else-if="knowledgeItems.length > 0" class="space-y-3">
            <div
              v-for="(article, idx) in knowledgeItems"
              :key="article.id"
              class="section-card animate-fade-up"
              :class="'stagger-' + Math.min(idx + 1, 8)"
              style="cursor:pointer;padding:18px 20px;"
              @click="openArticle(article)"
            >
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div>
                  <span
                    style="padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:600;"
                    :style="{ background: 'var(--color-primary-bg)', color: 'var(--color-primary)' }"
                  >
                    {{ getCropIcon(article._category) }} {{ article._category }}
                  </span>
                  <h4 style="font-weight:700;color:var(--text-primary);margin-top:8px;font-size:1rem;">
                    {{ article._displayName }}
                  </h4>
                  <p style="font-size:0.78rem;color:var(--text-muted);margin-top:2px;">
                    {{ article._displayNameEn }}
                  </p>
                </div>
                <span style="font-size:0.75rem;color:var(--text-muted);flex-shrink:0;">
                  {{ article._views }} 次阅读
                </span>
              </div>

              <!-- Preview of symptoms -->
              <p style="font-size:0.82rem;color:var(--text-secondary);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">
                {{ article.symptoms?.substring(0, 120) }}{{ article.symptoms?.length > 120 ? '...' : '' }}
              </p>

              <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;">
                <span style="padding:2px 8px;border-radius:6px;font-size:0.7rem;background:rgba(0,0,0,0.04);color:var(--text-secondary);">
                  🦠 {{ article.disease_name }}
                </span>
                <span style="padding:2px 8px;border-radius:6px;font-size:0.7rem;background:rgba(0,0,0,0.04);color:var(--text-secondary);">
                  🌱 {{ article.crop_type }}
                </span>
              </div>
            </div>
          </div>

          <!-- Empty -->
          <div v-else style="text-align:center;padding:48px 20px;">
            <div style="font-size:3rem;margin-bottom:12px;">🔍</div>
            <p style="color:var(--text-secondary);font-weight:500;">暂无相关知识</p>
            <p style="color:var(--text-muted);font-size:0.85rem;">尝试使用不同的关键词搜索</p>
          </div>
        </div>
      </div>

      <!-- Sidebar - 1 col -->
      <div class="space-y-5 animate-fade-up stagger-4">
        <!-- Community Q&A -->
        <div class="glass-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-weight:700;color:var(--text-primary);font-size:1rem;">💬 社区问答</h3>
            <button
              @click="showAskForm = !showAskForm"
              class="btn btn-primary btn-sm"
            >
              {{ showAskForm ? '取消' : '提问' }}
            </button>
          </div>

          <!-- Ask Form -->
          <div v-if="showAskForm" style="margin-bottom:14px;padding:12px;background:rgba(0,0,0,0.02);border-radius:10px;">
            <textarea
              v-model="newQuestion"
              placeholder="请输入您的问题..."
              rows="3"
              class="form-input"
              style="resize:vertical;"
            ></textarea>
            <button
              @click="postQuestion"
              :disabled="!newQuestion.trim()"
              class="btn btn-primary btn-sm"
              style="width:100%;margin-top:8px;"
            >
              发布问题
            </button>
          </div>

          <!-- Messages -->
          <div v-if="messages.length > 0" class="space-y-2" style="max-height:360px;overflow-y:auto;">
            <div
              v-for="msg in messages.slice(0, 10)"
              :key="msg.id"
              style="padding:10px 12px;background:rgba(0,0,0,0.015);border-radius:10px;"
            >
              <p style="font-size:0.82rem;color:var(--text-primary);line-height:1.5;">{{ msg.content }}</p>
              <div style="display:flex;justify-content:space-between;margin-top:6px;">
                <span style="font-size:0.72rem;color:var(--text-muted);">{{ msg.username }}</span>
                <span style="font-size:0.7rem;color:var(--text-muted);">{{ msg.created_at }}</span>
              </div>
            </div>
          </div>

          <div v-else style="text-align:center;padding:24px;">
            <p style="color:var(--text-muted);font-size:0.85rem;">暂无讨论，快来提问吧</p>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="glass-card">
          <h3 style="font-weight:700;color:var(--text-primary);margin-bottom:12px;font-size:1rem;">🔗 常用链接</h3>
          <div class="space-y-2">
            <a href="#" class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;">
              📖 病虫害图谱
            </a>
            <a href="#" class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;">
              💊 农药使用指南
            </a>
            <a href="#" class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;">
              📅 农事日历
            </a>
            <router-link to="/treatment" class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;">
              🧪 防治方案生成
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Article Detail Modal -->
    <div
      v-if="selectedArticle"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background:rgba(0,0,0,0.4);backdrop-filter:blur(4px);"
      @click.self="closeArticle"
    >
      <div
        class="animate-scale-in"
        style="background:var(--surface-bg);border-radius:var(--radius-xl);max-width:680px;width:100%;max-height:85vh;overflow-y:auto;box-shadow:var(--shadow-xl);border:1px solid var(--surface-border);"
      >
        <!-- Header -->
        <div style="padding:24px 28px 16px;border-bottom:1px solid var(--surface-border);position:sticky;top:0;background:var(--surface-bg);z-index:1;border-radius:var(--radius-xl) var(--radius-xl) 0 0;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <span
                style="padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:600;"
                :style="{ background: 'var(--color-primary-bg)', color: 'var(--color-primary)' }"
              >
                {{ getCropIcon(selectedArticle._category) }} {{ selectedArticle._category }}
              </span>
              <h2 style="font-weight:700;color:var(--text-primary);font-size:1.3rem;margin-top:10px;">
                {{ selectedArticle._displayName }}
              </h2>
              <p style="font-size:0.85rem;color:var(--text-muted);">{{ selectedArticle._displayNameEn }}</p>
            </div>
            <button @click="closeArticle" style="padding:6px;border-radius:8px;border:none;background:rgba(0,0,0,0.04);cursor:pointer;">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div style="padding:20px 28px 28px;" class="space-y-5">
          <!-- Symptoms -->
          <div>
            <h4 style="font-weight:700;color:var(--text-primary);margin-bottom:10px;display:flex;align-items:center;gap:6px;">
              <span style="font-size:1.2rem;">🔍</span> 症状表现
            </h4>
            <div style="padding:16px;background:var(--color-danger-bg);border-radius:12px;border-left:3px solid var(--color-danger);">
              <p style="color:var(--text-secondary);line-height:1.7;white-space:pre-line;">{{ selectedArticle.symptoms || '暂无症状描述' }}</p>
            </div>
          </div>

          <!-- Prevention -->
          <div>
            <h4 style="font-weight:700;color:var(--text-primary);margin-bottom:10px;display:flex;align-items:center;gap:6px;">
              <span style="font-size:1.2rem;">🛡️</span> 预防措施
            </h4>
            <div style="padding:16px;background:var(--color-info-bg);border-radius:12px;border-left:3px solid var(--color-info);">
              <p style="color:var(--text-secondary);line-height:1.7;white-space:pre-line;">{{ selectedArticle.prevention || '暂无预防措施' }}</p>
            </div>
          </div>

          <!-- Treatment -->
          <div>
            <h4 style="font-weight:700;color:var(--text-primary);margin-bottom:10px;display:flex;align-items:center;gap:6px;">
              <span style="font-size:1.2rem;">💊</span> 治疗方案
            </h4>
            <div style="padding:16px;background:var(--color-success-bg);border-radius:12px;border-left:3px solid var(--color-success);">
              <p style="color:var(--text-secondary);line-height:1.7;white-space:pre-line;">{{ selectedArticle.treatment || '暂无治疗方案' }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div style="padding:16px 28px;border-top:1px solid var(--surface-border);display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:0.8rem;color:var(--text-muted);">
            🌱 {{ selectedArticle.crop_type }} · 🦠 {{ selectedArticle.disease_name }}
          </span>
          <button @click="closeArticle" class="btn btn-outline btn-sm">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>
