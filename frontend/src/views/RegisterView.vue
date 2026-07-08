<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <h2>注册</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
          <el-button style="margin-top: 8px" :disabled="cooldown > 0" :loading="sendingCode" @click="sendCode">
            {{ cooldown > 0 ? `${cooldown}s 后重发` : '发送验证码' }}
          </el-button>
        </el-form-item>
        <el-form-item label="验证码">
          <el-input v-model="form.verification_code" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio-button label="student">学生</el-radio-button>
            <el-radio-button label="teacher">教师</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-button class="full-width" type="primary" :loading="loading" @click="submit">注册</el-button>
      </el-form>
      <p class="muted">已有账号？<el-link type="primary" @click="$router.push('/login')">去登录</el-link></p>
    </el-card>
  </div>
</template>

<script setup>
import { onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import http from '../api/http'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const sendingCode = ref(false)
const cooldown = ref(0)
let timerId = null
const form = reactive({ username: '', email: '', password: '', verification_code: '', role: 'student' })

function startCooldown(seconds = 60) {
  cooldown.value = seconds
  if (timerId) clearInterval(timerId)
  timerId = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) {
      clearInterval(timerId)
      timerId = null
    }
  }, 1000)
}

async function sendCode() {
  const email = form.email.trim()
  if (!email) {
    ElMessage.warning('请先输入邮箱')
    return
  }
  sendingCode.value = true
  try {
    await http.post('/auth/email-code/send/', { email, purpose: 'register' })
    ElMessage.success('验证码已发送，请查收邮箱')
    startCooldown(60)
  } finally {
    sendingCode.value = false
  }
}

async function submit() {
  loading.value = true
  try {
    await auth.register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  if (timerId) clearInterval(timerId)
})
</script>

<style scoped>
.auth-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
}

.auth-card {
  width: 380px;
}
</style>
