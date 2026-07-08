<template>
  <div class="page" v-if="exam">
    <el-card>
      <template #header>
        <div class="toolbar">
          <h2>{{ exam.title }}</h2>
          <span class="muted">总分 {{ exam.total_score }}</span>
        </div>
      </template>
      <p>{{ exam.description }}</p>
      <el-form>
        <el-card v-for="question in exam.questions" :key="question.id" style="margin-bottom: 12px">
          <p><b>{{ question.order }}. {{ question.title }}</b>（{{ question.score }} 分）</p>
          <el-checkbox-group v-if="question.question_type === 'multiple'" v-model="answers[question.id]">
            <el-checkbox v-for="choice in question.choices" :key="choice.id" :label="choice.id">{{ choice.content }}</el-checkbox>
          </el-checkbox-group>
          <el-radio-group v-else v-model="answers[question.id]">
            <el-radio v-for="choice in question.choices" :key="choice.id" :label="choice.id">{{ choice.content }}</el-radio>
          </el-radio-group>
        </el-card>
        <el-button type="primary" :loading="submitting" @click="submit">提交试卷</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const route = useRoute()
const router = useRouter()
const exam = ref(null)
const answers = reactive({})
const submitting = ref(false)

async function load() {
  const { data } = await http.get(`/exams/${route.params.id}/`)
  exam.value = data
  data.questions.forEach((question) => {
    answers[question.id] = question.question_type === 'multiple' ? [] : ''
  })
}

async function submit() {
  submitting.value = true
  try {
    const { data } = await http.post('/submissions/', { exam: exam.value.id, answers })
    ElMessage.success(`提交成功，得分 ${data.score}`)
    router.push('/student')
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>
