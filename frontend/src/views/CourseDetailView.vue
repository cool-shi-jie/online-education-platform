<template>
  <div class="page" v-if="course">
    <el-card>
      <div class="toolbar">
        <div>
          <h2>{{ course.title }}</h2>
          <p class="muted">{{ course.category }} · {{ course.language }} · 教师：{{ course.teacher_name }}</p>
        </div>
        <el-button v-if="auth.role === 'student'" type="primary" :loading="loading" @click="enroll">报名学习</el-button>
      </div>
      <p>{{ course.description }}</p>
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header>章节</template>
      <el-timeline>
        <el-timeline-item v-for="chapter in course.chapters" :key="chapter.id" :timestamp="`第 ${chapter.order} 章`">
          {{ chapter.title }}
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const course = ref(null)
const loading = ref(false)

async function load() {
  const { data } = await http.get(`/courses/${route.params.id}/`)
  course.value = data
}

async function enroll() {
  loading.value = true
  try {
    await http.post(`/courses/${course.value.id}/enroll/`)
    ElMessage.success('报名成功')
    router.push(`/student/courses/${course.value.id}/learn`)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
