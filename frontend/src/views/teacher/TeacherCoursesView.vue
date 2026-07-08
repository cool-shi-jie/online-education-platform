<template>
  <div class="page">
    <div class="toolbar">
      <h2>课程管理</h2>
      <el-button type="primary" @click="dialogVisible = true">创建课程</el-button>
    </div>
    <el-table :data="courses">
      <el-table-column prop="title" label="课程" />
      <el-table-column prop="category" label="分类" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openChapter(row)">添加章节</el-button>
          <el-button size="small" @click="$router.push(`/community/${row.id}`)">社区</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="创建课程" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="课程名称"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="语言"><el-input v-model="form.language" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="草稿" value="draft" />
            <el-option label="发布" value="published" />
            <el-option label="下架" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createCourse">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="chapterVisible" title="添加章节" width="520px">
      <el-form :model="chapterForm" label-position="top">
        <el-form-item label="标题"><el-input v-model="chapterForm.title" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="chapterForm.description" type="textarea" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="chapterForm.order" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="chapterVisible = false">取消</el-button>
        <el-button type="primary" @click="createChapter">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const courses = ref([])
const dialogVisible = ref(false)
const chapterVisible = ref(false)
const currentCourse = ref(null)
const form = reactive({ title: '', description: '', category: '', language: 'zh-CN', status: 'draft' })
const chapterForm = reactive({ title: '', description: '', order: 1 })

async function load() {
  const { data } = await http.get('/courses/')
  courses.value = data.results || data
}

async function createCourse() {
  await http.post('/courses/', form)
  ElMessage.success('课程已创建')
  dialogVisible.value = false
  await load()
}

function openChapter(course) {
  currentCourse.value = course
  chapterVisible.value = true
}

async function createChapter() {
  await http.post('/chapters/', { ...chapterForm, course: currentCourse.value.id })
  ElMessage.success('章节已创建')
  chapterVisible.value = false
  await load()
}

onMounted(load)
</script>
