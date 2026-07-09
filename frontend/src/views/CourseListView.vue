<template>
  <div class="page course-square-page">
    <section class="course-hero">
      <div>
        <h2>课程广场</h2>
        <p class="muted">按分类快速发现感兴趣的课程，也可以输入关键词搜索。</p>
      </div>
      <div class="hero-stat">
        <b>{{ courses.length }}</b>
        <span>门课程</span>
      </div>
    </section>

    <section class="course-square-layout">
      <aside class="category-panel">
        <div class="panel-title">
          <span>分类树</span>
          <b>{{ activeCategoryLabel }}</b>
        </div>
        <div class="category-tree">
          <template v-for="(category, index) in categoryNodes" :key="category.value || 'all'">
            <button class="category-node" :class="{ active: selectedCategory === category.value }" type="button" @click="selectCategory(category.value)">
              <span class="category-dot">{{ index + 1 }}</span>
              <span>{{ category.label }}</span>
            </button>
            <span v-if="index < categoryNodes.length - 1" class="category-connector" :class="{ active: isCategoryConnectorActive(index) }"></span>
          </template>
        </div>
      </aside>

      <main class="course-content">
        <div class="content-tools">
          <div>
            <h3>{{ activeCategoryLabel }}</h3>
            <p class="muted">{{ courseCountText }}</p>
          </div>
          <el-input v-model="keyword" placeholder="搜索课程" clearable class="course-search" @clear="load" @keyup.enter="load" />
        </div>

        <div class="course-grid">
          <el-card v-for="course in courses" :key="course.id" shadow="hover" class="course-card">
            <div class="course-title-block" :style="categoryTone(course.category)">
              <el-tag size="small" effect="plain">{{ course.category }}</el-tag>
              <h3>{{ course.title }}</h3>
            </div>
            <div class="course-meta">
              <span>教师：{{ course.teacher_name }}</span>
              <span>{{ course.enrolled_count || 0 }} 人学习</span>
              <span>{{ course.chapters?.length || 0 }} 章</span>
            </div>
            <p class="course-description">{{ course.description || '暂无课程简介' }}</p>
            <div class="course-footer">
              <span class="muted">{{ course.language }}</span>
              <el-button class="course-detail-button" :style="categoryTone(course.category)" @click="$router.push(`/courses/${course.id}`)">查看详情</el-button>
            </div>
          </el-card>
        </div>
        <el-empty v-if="!loading && courses.length === 0" description="暂无课程，试试切换分类或搜索关键词" />
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import http from '../api/http'

const fallbackCategories = [
  '计算机与互联网',
  '人工智能与数据',
  '经济管理',
  '语言学习',
  '学科基础',
  '考研与升学',
  '职业发展',
  '设计与创意',
  '人文社科',
  '自然科学与工程',
  '医学与健康',
  '法律与公共事务',
  '兴趣拓展',
  '其他'
]

const defaultTone = {
  start: '#10b981',
  end: '#075985',
  soft: 'rgba(14, 165, 233, 0.18)'
}

const categoryTones = {
  学科基础: { start: '#34d399', end: '#0f766e', soft: 'rgba(52, 211, 153, 0.2)' },
  医学与健康: { start: '#22c55e', end: '#047857', soft: 'rgba(34, 197, 94, 0.2)' },
  兴趣拓展: { start: '#2dd4bf', end: '#0f766e', soft: 'rgba(45, 212, 191, 0.2)' },
  语言学习: { start: '#14b8a6', end: '#0891b2', soft: 'rgba(20, 184, 166, 0.2)' },
  人文社科: { start: '#06b6d4', end: '#0e7490', soft: 'rgba(6, 182, 212, 0.2)' },
  经济管理: { start: '#38bdf8', end: '#0284c7', soft: 'rgba(56, 189, 248, 0.2)' },
  职业发展: { start: '#0ea5e9', end: '#0369a1', soft: 'rgba(14, 165, 233, 0.2)' },
  设计与创意: { start: '#22d3ee', end: '#1d4ed8', soft: 'rgba(34, 211, 238, 0.2)' },
  计算机与互联网: { start: '#0ea5e9', end: '#1d4ed8', soft: 'rgba(14, 165, 233, 0.2)' },
  人工智能与数据: { start: '#2563eb', end: '#1e3a8a', soft: 'rgba(37, 99, 235, 0.2)' },
  自然科学与工程: { start: '#0891b2', end: '#1e40af', soft: 'rgba(8, 145, 178, 0.2)' },
  法律与公共事务: { start: '#0284c7', end: '#172554', soft: 'rgba(2, 132, 199, 0.2)' },
  考研与升学: { start: '#0d9488', end: '#1e3a8a', soft: 'rgba(13, 148, 136, 0.2)' },
  其他: { start: '#10b981', end: '#075985', soft: 'rgba(16, 185, 129, 0.2)' }
}

const categories = ref([...fallbackCategories])
const courses = ref([])
const keyword = ref('')
const selectedCategory = ref('')
const loading = ref(false)

const categoryNodes = computed(() => [{ label: '全部课程', value: '' }, ...categories.value.map((category) => ({ label: category, value: category }))])
const activeCategoryLabel = computed(() => selectedCategory.value || '全部课程')
const courseCountText = computed(() => `当前显示 ${courses.value.length} 门课程`)

function normalizeList(data) {
  return data?.results || data || []
}

async function fetchAllPages(url, params = {}) {
  const items = []
  let nextUrl = url
  let nextParams = { ...params }

  while (nextUrl) {
    const { data } = await http.get(nextUrl, { params: nextParams })
    items.push(...normalizeList(data))
    nextUrl = data?.next || ''
    nextParams = {}
  }

  return items
}

async function load() {
  loading.value = true
  try {
    const params = { status: 'published', search: keyword.value }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    courses.value = await fetchAllPages('/courses/', params)
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const { data } = await http.get('/courses/categories/')
    categories.value = data
  } catch {
    categories.value = [...fallbackCategories]
  }
}

function selectCategory(category) {
  selectedCategory.value = category
  load()
}

function isCategoryConnectorActive(index) {
  const activeIndex = categoryNodes.value.findIndex((category) => category.value === selectedCategory.value)
  return activeIndex > index
}

function categoryTone(category) {
  const tone = categoryTones[category] || defaultTone
  return {
    '--tone-start': tone.start,
    '--tone-end': tone.end,
    '--tone-soft': tone.soft
  }
}

onMounted(() => {
  loadCategories()
  load()
})
</script>

<style scoped>
.course-square-page {
  display: grid;
  gap: 18px;
}

.course-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
  border: 1px solid rgba(125, 211, 252, 0.42);
  border-radius: 28px;
  background:
    radial-gradient(circle at 12% 20%, rgba(14, 165, 233, 0.18), transparent 30%),
    radial-gradient(circle at 90% 70%, rgba(34, 197, 94, 0.14), transparent 28%),
    #fff;
  box-shadow: 0 18px 48px rgba(15, 63, 87, 0.08);
}

.course-hero h2 {
  margin: 0 0 8px;
  color: #0f3f57;
  font-size: 30px;
}

.hero-stat {
  display: grid;
  place-items: center;
  min-width: 108px;
  min-height: 88px;
  color: #0f766e;
  border-radius: 24px;
  background: linear-gradient(135deg, #ecfeff, #f0fdf4);
}

.hero-stat b {
  font-size: 30px;
  line-height: 1;
}

.hero-stat span {
  color: #3b7188;
  font-size: 13px;
  font-weight: 700;
}

.course-square-layout {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.category-panel {
  position: sticky;
  top: 88px;
  padding: 18px;
  border: 1px solid #e0f2fe;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 16px 40px rgba(15, 63, 87, 0.07);
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-title span {
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

.panel-title b {
  color: #0f3f57;
  font-size: 14px;
}

.category-tree {
  display: grid;
  justify-items: start;
}

.category-node {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
  padding: 9px 10px;
  color: #31566a;
  font: inherit;
  font-size: 14px;
  font-weight: 800;
  text-align: left;
  background: #f8fafc;
  border: 1px solid #e0f2fe;
  border-radius: 16px;
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.category-node:hover {
  color: #0f766e;
  border-color: #7dd3fc;
  transform: translateX(2px);
}

.category-node.active {
  color: #fff;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  border-color: transparent;
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.2);
}

.category-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex: 0 0 auto;
  color: #0f766e;
  background: #ecfeff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 900;
}

.category-node.active .category-dot {
  background: rgba(255, 255, 255, 0.9);
}

.category-connector {
  width: 3px;
  height: 18px;
  margin-left: 22px;
  background: linear-gradient(#bae6fd, #bbf7d0);
  border-radius: 999px;
}

.category-connector.active {
  width: 4px;
  background: linear-gradient(#0ea5e9, #0f766e);
}

.course-content {
  display: grid;
  gap: 16px;
}

.content-tools {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e0f2fe;
  border-radius: 22px;
  background: #fff;
}

.content-tools h3 {
  margin: 0 0 6px;
  color: #0f3f57;
}

.course-search {
  width: min(320px, 100%);
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.course-card {
  overflow: hidden;
  border: 1px solid rgba(14, 165, 233, 0.16);
  border-radius: 22px;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease;
}

.course-card:hover {
  transform: translateY(-3px);
  border-color: rgba(14, 165, 233, 0.34);
  box-shadow: 0 18px 42px rgba(15, 63, 87, 0.12);
}

.course-title-block {
  min-height: 116px;
  padding: 18px;
  margin: -20px -20px 16px;
  overflow: hidden;
  position: relative;
  background:
    radial-gradient(circle at 14% 20%, rgba(255, 255, 255, 0.36), transparent 28%),
    radial-gradient(circle at 88% 18%, var(--tone-soft, rgba(14, 165, 233, 0.18)), transparent 32%),
    linear-gradient(135deg, var(--tone-start, #10b981), var(--tone-end, #075985));
  box-shadow: inset 0 -22px 42px rgba(15, 23, 42, 0.12);
}

.course-title-block::after {
  content: '';
  position: absolute;
  right: -36px;
  bottom: -54px;
  width: 150px;
  height: 150px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
}

.course-title-block :deep(.el-tag) {
  position: relative;
  z-index: 1;
  color: #fff;
  border-color: rgba(255, 255, 255, 0.45);
  background: rgba(255, 255, 255, 0.18);
  font-weight: 800;
}

.course-title-block h3 {
  position: relative;
  z-index: 1;
  margin: 16px 0 0;
  color: #fff;
  font-size: 20px;
  line-height: 1.35;
  text-shadow: 0 2px 12px rgba(15, 23, 42, 0.22);
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.course-meta span {
  padding: 6px 9px;
  color: #3b7188;
  background: #f8fafc;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.course-description {
  min-height: 72px;
  color: #475569;
  line-height: 1.7;
}

.course-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
}

.course-detail-button {
  min-width: 104px;
  height: 38px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: linear-gradient(135deg, var(--tone-start, #10b981), var(--tone-end, #075985));
  box-shadow: 0 10px 22px rgba(15, 118, 110, 0.2);
  font-weight: 900;
  letter-spacing: 0.5px;
}

.course-detail-button:hover,
.course-detail-button:focus {
  color: #fff;
  background: linear-gradient(135deg, var(--tone-end, #075985), var(--tone-start, #10b981));
  box-shadow: 0 14px 28px rgba(15, 63, 87, 0.24);
  transform: translateY(-1px);
}

@media (max-width: 900px) {
  .course-hero,
  .content-tools {
    align-items: flex-start;
    flex-direction: column;
  }

  .course-square-layout {
    grid-template-columns: 1fr;
  }

  .category-panel {
    position: static;
  }

  .category-tree {
    display: flex;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .category-node {
    width: auto;
    flex: 0 0 auto;
    white-space: nowrap;
  }

  .category-connector {
    width: 24px;
    height: 3px;
    flex: 0 0 auto;
    margin: 18px 4px 0;
  }
}
</style>
