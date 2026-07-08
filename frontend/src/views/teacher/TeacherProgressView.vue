<template>
  <div class="page">
    <h2>学生进度与成绩</h2>
    <el-card style="margin-bottom: 16px">
      <template #header>学习进度</template>
      <el-table :data="enrollments">
        <el-table-column prop="student_name" label="学生" />
        <el-table-column prop="course_title" label="课程" />
        <el-table-column prop="progress_percent" label="进度">
          <template #default="{ row }"><el-progress :percentage="row.progress_percent" /></template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-card>
      <template #header>考试成绩</template>
      <el-table :data="submissions">
        <el-table-column prop="student_name" label="学生" />
        <el-table-column prop="exam_title" label="考试" />
        <el-table-column prop="score" label="分数" />
        <el-table-column prop="passed" label="是否合格" />
        <el-table-column prop="submitted_at" label="提交时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../../api/http'

const enrollments = ref([])
const submissions = ref([])

async function load() {
  const [enrollmentRes, submissionRes] = await Promise.all([http.get('/enrollments/'), http.get('/submissions/')])
  enrollments.value = enrollmentRes.data.results || enrollmentRes.data
  submissions.value = submissionRes.data.results || submissionRes.data
}

onMounted(load)
</script>
