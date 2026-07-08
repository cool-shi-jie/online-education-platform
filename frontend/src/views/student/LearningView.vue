<template>
  <div class="page" v-if="course">
    <div class="toolbar">
      <h2>{{ course.title }}</h2>
      <el-button @click="$router.push(`/community/${course.id}`)">社区中心</el-button>
    </div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card>
          <template #header>章节学习</template>
          <el-collapse>
            <el-collapse-item v-for="chapter in course.chapters" :key="chapter.id" :title="chapter.title">
              <p>{{ chapter.description || '暂无章节说明' }}</p>
              <video v-if="chapter.video" class="video" :src="chapter.video" controls />
              <el-button type="success" @click="completeChapter(chapter)">标记完成</el-button>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>学习进度</template>
          <el-progress :percentage="progress?.progress_percent || 0" />
          <el-divider />
          <el-button v-for="exam in exams" :key="exam.id" class="full-width" style="margin-bottom: 8px" @click="$router.push(`/student/exams/${exam.id}`)">
            参加考试：{{ exam.title }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top: 16px">
      <template #header>课程疑难解答</template>
      <el-form :model="questionForm" label-position="top" class="question-form">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="关联章节">
              <el-select v-model="questionForm.chapter" clearable placeholder="可选，默认整门课程">
                <el-option v-for="chapter in course.chapters" :key="chapter.id" :label="chapter.title" :value="chapter.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="问题标题">
              <el-input v-model="questionForm.title" maxlength="160" show-word-limit />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="问题描述">
          <el-input v-model="questionForm.content" type="textarea" :rows="3" maxlength="1000" show-word-limit />
        </el-form-item>
        <el-button type="primary" @click="createQuestion">提交问题</el-button>
      </el-form>
      <el-divider />
      <el-empty v-if="questions.length === 0" description="你还没有提问" />
      <el-card v-for="question in questions" :key="question.id" class="question-item" shadow="never">
        <template #header>
          <div class="toolbar">
            <div>
              <b>{{ question.title }}</b>
              <span class="muted" style="margin-left: 8px"> {{ question.chapter_title || '课程通用问题' }} </span>
            </div>
            <el-tag :type="statusTagType(question.status)">{{ statusLabel(question.status) }}</el-tag>
          </div>
        </template>
        <p>{{ question.content }}</p>
        <div v-if="question.answer" class="answer-box">
          <b>教师回复：</b>
          <p>{{ question.answer }}</p>
        </div>
        <div class="toolbar">
          <span class="muted">提问时间：{{ question.created_at }}</span>
          <el-button v-if="question.status === 'answered'" size="small" type="success" @click="resolveQuestion(question)">标记已解决</el-button>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const route = useRoute()
const course = ref(null)
const progress = ref(null)
const exams = ref([])
const questions = ref([])
const questionForm = reactive({ chapter: '', title: '', content: '' })

async function load() {
  const courseId = route.params.id
  const [courseRes, progressRes, examsRes, questionsRes] = await Promise.all([
    http.get(`/courses/${courseId}/`),
    http.get(`/courses/${courseId}/progress/`),
    http.get('/exams/', { params: { course: courseId, is_published: true } }),
    http.get('/course-questions/', { params: { course: courseId } }),
  ])
  course.value = courseRes.data
  progress.value = progressRes.data
  exams.value = examsRes.data.results || examsRes.data
  questions.value = questionsRes.data.results || questionsRes.data
  if (!questionForm.chapter && course.value.chapters.length > 0) {
    questionForm.chapter = course.value.chapters[0].id
  }
}

async function completeChapter(chapter) {
  await http.post(`/courses/${course.value.id}/complete_chapter/`, {
    chapter: chapter.id,
    watched_seconds: chapter.duration_seconds
  })
  ElMessage.success('学习进度已更新')
  await load()
}

async function createQuestion() {
  if (!questionForm.title.trim() || !questionForm.content.trim()) {
    ElMessage.warning('请填写问题标题和描述')
    return
  }
  await http.post('/course-questions/', {
    course: course.value.id,
    chapter: questionForm.chapter || null,
    title: questionForm.title.trim(),
    content: questionForm.content.trim(),
  })
  ElMessage.success('问题已提交')
  questionForm.title = ''
  questionForm.content = ''
  await load()
}

async function resolveQuestion(question) {
  await http.post(`/course-questions/${question.id}/resolve/`)
  ElMessage.success('已标记为已解决')
  await load()
}

function statusLabel(status) {
  return { pending: '待回复', answered: '已回复', resolved: '已解决' }[status] || status
}

function statusTagType(status) {
  return { pending: 'warning', answered: 'primary', resolved: 'success' }[status] || 'info'
}

onMounted(load)
</script>

<style scoped>
.video {
  display: block;
  width: 100%;
  max-height: 420px;
  margin-bottom: 12px;
  background: #000;
}

.question-form {
  margin-bottom: 8px;
}

.question-item {
  margin-bottom: 12px;
}

.answer-box {
  padding: 10px 12px;
  border-left: 4px solid #60a5fa;
  background: #f8fbff;
  margin: 8px 0;
}
</style>
