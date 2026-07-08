<template>
  <div class="page">
    <div class="toolbar">
      <div>
        <h2>处理疑问</h2>
        <p class="muted">集中回复学生在课程学习中提交的问题。</p>
      </div>
      <el-radio-group v-model="activeStatus">
        <el-radio-button v-for="tab in statusTabs" :key="tab.name" :label="tab.name">
          {{ tab.label }} {{ questionCount(tab.name) }}
        </el-radio-button>
      </el-radio-group>
    </div>

    <div class="question-grid" v-if="filteredQuestions.length">
      <el-card v-for="question in filteredQuestions" :key="question.id" shadow="hover" class="question-card">
        <template #header>
          <div class="question-head">
            <div>
              <b>{{ question.title }}</b>
              <p class="muted">{{ question.course_title }} · {{ question.chapter_title || '课程问题' }}</p>
            </div>
            <el-tag :type="statusTag(question.status)">{{ question.status_text }}</el-tag>
          </div>
        </template>
        <p class="muted">学生：{{ question.student_name }} · {{ question.created_at }}</p>
        <p class="question-content">{{ question.content }}</p>
        <el-input
          v-model="answerDrafts[question.id]"
          type="textarea"
          :rows="3"
          placeholder="输入回复内容"
        />
        <div class="question-actions">
          <el-button type="primary" @click="answerQuestion(question)">
            {{ question.answer ? '更新回复' : '提交回复' }}
          </el-button>
          <span v-if="question.answer" class="muted">当前回复：{{ question.answer }}</span>
        </div>
      </el-card>
    </div>
    <el-empty v-else description="暂无对应状态的学生疑问" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const questions = ref([])
const activeStatus = ref('pending')
const answerDrafts = ref({})
const statusTabs = [
  { name: 'all', label: '全部' },
  { name: 'pending', label: '待回复' },
  { name: 'answered', label: '已回复' },
  { name: 'resolved', label: '已解决' }
]

const filteredQuestions = computed(() => {
  if (activeStatus.value === 'all') return questions.value
  return questions.value.filter((question) => question.status === activeStatus.value)
})

async function load() {
  const { data } = await http.get('/course-questions/')
  questions.value = data.results || data
  answerDrafts.value = questions.value.reduce((drafts, question) => {
    drafts[question.id] = question.answer || ''
    return drafts
  }, {})
}

async function answerQuestion(question) {
  const answer = (answerDrafts.value[question.id] || '').trim()
  if (!answer) {
    ElMessage.warning('请输入回复内容')
    return
  }
  const { data } = await http.post(`/course-questions/${question.id}/answer/`, { answer })
  Object.assign(question, data)
  answerDrafts.value[question.id] = data.answer
  ElMessage.success('回复已保存')
}

function statusTag(status) {
  return { pending: 'warning', answered: 'primary', resolved: 'success' }[status] || 'info'
}

function questionCount(status) {
  if (status === 'all') return questions.value.length
  return questions.value.filter((question) => question.status === status).length
}

onMounted(load)
</script>

<style scoped>
.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.question-card {
  border-radius: 18px;
}

.question-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f8fafc, #eef2ff);
}

.question-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.question-content {
  min-height: 58px;
  color: #334155;
  line-height: 1.7;
}

.question-actions {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}
</style>
