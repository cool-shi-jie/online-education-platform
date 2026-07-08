<template>
  <div class="page">
    <div class="toolbar">
      <div>
        <h2>课程广场</h2>
        <p class="muted">按分类快速发现感兴趣的课程，也可以输入关键词搜索。</p>
      </div>
      <el-input v-model="keyword" placeholder="搜索课程" clearable style="width: 260px" @clear="load" @keyup.enter="load" />
    </div>

    <div class="category-filter">
      <el-button :type="selectedCategory === '' ? 'primary' : 'default'" round @click="selectCategory('')">全部</el-button>
      <el-button
        v-for="category in categories"
        :key="category"
        :type="selectedCategory === category ? 'primary' : 'default'"
        round
        @click="selectCategory(category)"
      >
        {{ category }}
      </el-button>
    </div>

    <div class="card-grid">
      <el-card v-for="course in courses" :key="course.id" shadow="hover">
        <template #header>
          <div class="course-card-header">
            <b>{{ course.title }}</b>
            <el-tag size="small">{{ course.category }}</el-tag>
          </div>
        </template>
        <p class="muted">教师：{{ course.teacher_name }} · {{ course.language }} · {{ course.enrolled_count || 0 }} 人学习</p>
        <p class="course-description">{{ course.description }}</p>
        <div class="course-footer">
          <span class="muted">共 {{ course.chapters?.length || 0 }} 章</span>
          <el-button type="primary" @click="$router.push(`/courses/${course.id}`)">查看详情</el-button>
        </div>
      </el-card>
    </div>
    <el-empty v-if="!loading && courses.length === 0" description="暂无课程" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
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

const categories = ref([...fallbackCategories])
const courses = ref([])
const keyword = ref('')
const selectedCategory = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const params = { status: 'published', search: keyword.value }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    const { data } = await http.get('/courses/', { params })
    courses.value = data.results || data
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

onMounted(() => {
  loadCategories()
  load()
})
</script>

<style scoped>
.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.course-card-header,
.course-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.course-description {
  min-height: 72px;
}
</style>
