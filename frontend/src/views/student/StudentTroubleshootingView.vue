<template>
  <div class="page">
    <div class="toolbar">
      <h2>疑难解答</h2>
      <el-button @click="$router.push('/student')">返回学生中心</el-button>
    </div>

    <el-card v-for="group in groups" :key="group.key" style="margin-bottom: 16px">
      <template #header>
        <div class="toolbar">
          <span>{{ group.label }}</span>
          <el-tag>{{ group.items.length }}</el-tag>
        </div>
      </template>
      <el-empty v-if="group.items.length === 0" description="暂无记录" />
      <el-table v-else :data="group.items">
        <el-table-column prop="course_title" label="课程" />
        <el-table-column prop="chapter_title" label="章节">
          <template #default="{ row }">{{ row.chapter_title || '课程通用问题' }}</template>
        </el-table-column>
        <el-table-column prop="title" label="问题标题" />
        <el-table-column label="教师回复">
          <template #default="{ row }">{{ row.answer || '待老师回复' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button v-if="row.status === 'answered'" size="small" type="success" @click="resolveQuestion(row)">标记已解决</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const questions = ref([])

const groups = computed(() => {
  const statuses = [
    { key: 'pending', label: '待回复' },
    { key: 'answered', label: '已回复' },
    { key: 'resolved', label: '已解决' },
  ]
  return statuses.map((status) => ({
    ...status,
    items: questions.value.filter((item) => item.status === status.key),
  }))
})

async function load() {
  const { data } = await http.get('/course-questions/')
  questions.value = data.results || data
}

async function resolveQuestion(row) {
  await http.post(`/course-questions/${row.id}/resolve/`)
  ElMessage.success('已标记为已解决')
  await load()
}

onMounted(load)
</script>
