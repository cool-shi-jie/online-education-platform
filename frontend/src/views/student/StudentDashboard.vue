<template>
  <div class="page">
    <div class="toolbar">
      <h2>学生中心</h2>
      <div>
        <el-button @click="$router.push('/student/questions')">疑难解答</el-button>
        <el-button @click="$router.push('/certificates')">我的证书</el-button>
      </div>
    </div>
    <el-card>
      <template #header>我的课程</template>
      <el-table :data="enrollments">
        <el-table-column prop="course_title" label="课程" />
        <el-table-column prop="progress_percent" label="进度">
          <template #default="{ row }">
            <el-progress :percentage="row.progress_percent" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="$router.push(`/student/courses/${row.course}/learn`)">继续学习</el-button>
            <el-button size="small" @click="$router.push(`/community/${row.course}`)">社区</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../../api/http'

const enrollments = ref([])

async function load() {
  const { data } = await http.get('/enrollments/')
  enrollments.value = data.results || data
}

onMounted(load)
</script>
