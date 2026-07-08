<template>
  <div class="page">
    <h2>内容管理</h2>
    <el-card style="margin-bottom: 16px">
      <template #header>课程</template>
      <el-table :data="courses">
        <el-table-column prop="title" label="课程" />
        <el-table-column prop="teacher_name" label="教师" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="category" label="分类" />
      </el-table>
    </el-card>
    <el-card style="margin-bottom: 16px">
      <template #header>论坛帖子</template>
      <el-table :data="posts">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="course_title" label="课程" />
        <el-table-column prop="author_name" label="作者" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="removePost(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-card>
      <template #header>证书记录</template>
      <el-table :data="certificates">
        <el-table-column prop="code" label="编号" />
        <el-table-column prop="student_name" label="学生" />
        <el-table-column prop="course_title" label="课程" />
        <el-table-column prop="issued_at" label="颁发时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const courses = ref([])
const posts = ref([])
const certificates = ref([])

async function load() {
  const [courseRes, postRes, certRes] = await Promise.all([
    http.get('/courses/'),
    http.get('/forum/posts/'),
    http.get('/certificates/')
  ])
  courses.value = courseRes.data.results || courseRes.data
  posts.value = postRes.data.results || postRes.data
  certificates.value = certRes.data.results || certRes.data
}

async function removePost(row) {
  await http.delete(`/forum/posts/${row.id}/`)
  ElMessage.success('帖子已删除')
  await load()
}

onMounted(load)
</script>
