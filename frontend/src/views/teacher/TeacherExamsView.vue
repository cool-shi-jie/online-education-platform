<template>
  <div class="page">
    <div class="toolbar">
      <h2>考试管理</h2>
      <el-button type="primary" @click="examVisible = true">创建考试</el-button>
    </div>
    <el-table :data="exams">
      <el-table-column prop="title" label="考试" />
      <el-table-column prop="course_title" label="课程" />
      <el-table-column prop="is_published" label="已发布" />
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openQuestion(row)">添加题目</el-button>
          <el-button size="small" type="primary" @click="publish(row)">发布</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="examVisible" title="创建考试" width="520px">
      <el-form :model="examForm" label-position="top">
        <el-form-item label="课程">
          <el-select v-model="examForm.course" class="full-width">
            <el-option v-for="course in courses" :key="course.id" :label="course.title" :value="course.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="examForm.title" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="examForm.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="examVisible = false">取消</el-button>
        <el-button type="primary" @click="createExam">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="questionVisible" title="添加题目" width="640px">
      <el-form :model="questionForm" label-position="top">
        <el-form-item label="题干"><el-input v-model="questionForm.title" type="textarea" /></el-form-item>
        <el-form-item label="题型">
          <el-select v-model="questionForm.question_type">
            <el-option label="单选" value="single" />
            <el-option label="多选" value="multiple" />
          </el-select>
        </el-form-item>
        <el-form-item label="分值"><el-input-number v-model="questionForm.score" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="questionVisible = false">取消</el-button>
        <el-button type="primary" @click="createQuestion">保存并添加选项</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="choiceVisible" title="添加选项" width="520px">
      <el-form :model="choiceForm" label-position="top">
        <el-form-item label="选项内容"><el-input v-model="choiceForm.content" /></el-form-item>
        <el-form-item label="是否正确"><el-switch v-model="choiceForm.is_correct" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="choiceVisible = false">完成</el-button>
        <el-button type="primary" @click="createChoice">继续添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const courses = ref([])
const exams = ref([])
const currentExam = ref(null)
const currentQuestion = ref(null)
const examVisible = ref(false)
const questionVisible = ref(false)
const choiceVisible = ref(false)
const examForm = reactive({ course: '', title: '', description: '', is_published: false, total_score: 100 })
const questionForm = reactive({ title: '', question_type: 'single', score: 10, order: 1 })
const choiceForm = reactive({ content: '', is_correct: false, order: 1 })

async function load() {
  const [courseRes, examRes] = await Promise.all([http.get('/courses/'), http.get('/exams/')])
  courses.value = courseRes.data.results || courseRes.data
  exams.value = examRes.data.results || examRes.data
}

async function createExam() {
  await http.post('/exams/', examForm)
  ElMessage.success('考试已创建')
  examVisible.value = false
  await load()
}

function openQuestion(exam) {
  currentExam.value = exam
  questionVisible.value = true
}

async function createQuestion() {
  const { data } = await http.post('/questions/', { ...questionForm, exam: currentExam.value.id })
  currentQuestion.value = data
  questionVisible.value = false
  choiceVisible.value = true
}

async function createChoice() {
  await http.post('/choices/', { ...choiceForm, question: currentQuestion.value.id })
  choiceForm.content = ''
  choiceForm.is_correct = false
  choiceForm.order += 1
  ElMessage.success('选项已添加')
}

async function publish(exam) {
  await http.patch(`/exams/${exam.id}/`, { is_published: true })
  ElMessage.success('考试已发布')
  await load()
}

onMounted(load)
</script>
