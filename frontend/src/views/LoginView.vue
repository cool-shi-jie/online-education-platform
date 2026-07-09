<template>
  <div class="auth-page">
    <div class="river-flow" aria-hidden="true">
      <span class="river-layer river-layer-main"></span>
      <span class="river-layer river-layer-light"></span>
      <span class="river-layer river-layer-deep"></span>
    </div>
    <section class="auth-shell">
      <aside class="brand-panel">
        <BrandLogo size="lg" show-subtitle />
        <div class="brand-copy">
          <span class="eyebrow">WELCOME BACK</span>
          <h1>水润知识，木向成长</h1>
          <p>继续你的学习旅程。</p>
        </div>
        <div class="value-list">
          <div class="value-item">
            <b>课程成长</b>
          </div>
          <div class="value-item">
            <b>在线测评</b>
          </div>
          <div class="value-item">
            <b>学习社区</b>
          </div>
        </div>
      </aside>

      <el-card class="auth-card" shadow="never">
        <div class="form-head">
          <span>账号登录</span>
          <h2>欢迎回到水木学堂</h2>
          <p>登录后进入学习空间。</p>
        </div>
        <el-form :model="form" label-position="top" @submit.prevent="submit">
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" size="large" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              autocomplete="current-password"
              show-password
              size="large"
              placeholder="请输入密码"
            />
          </el-form-item>
          <el-button class="auth-submit" type="primary" :loading="loading" @click="submit">登录</el-button>
        </el-form>
        <p class="switch-tip">没有账号？<el-link type="primary" @click="$router.push('/register')">去注册</el-link></p>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import BrandLogo from '../components/BrandLogo.vue'
import { useAuthStore } from '../stores/auth'
import { homeByRole } from '../router'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function submit() {
  loading.value = true
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    router.push(homeByRole(auth.role))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  display: grid;
  min-height: 100vh;
  place-items: center;
  overflow: hidden;
  padding: 32px;
  background:
    radial-gradient(circle at 18% 18%, rgba(56, 189, 248, 0.32), transparent 28%),
    radial-gradient(circle at 84% 78%, rgba(34, 197, 94, 0.22), transparent 28%),
    linear-gradient(120deg, #e0f7fa, #f0fdf4, #dbeafe, #ecfeff);
  background-size: 180% 180%;
  animation: waterFlow 9s ease-in-out infinite;
}

.auth-page::before {
  position: absolute;
  inset: 0;
  content: "";
  background:
    radial-gradient(circle at 22% 20%, rgba(255, 255, 255, 0.62), transparent 20%),
    radial-gradient(circle at 78% 72%, rgba(255, 255, 255, 0.48), transparent 24%);
  opacity: 0.72;
}

.river-flow {
  position: absolute;
  inset: -18% -24%;
  overflow: hidden;
  transform: rotate(-16deg);
  transform-origin: center;
  pointer-events: none;
}

.river-layer {
  position: absolute;
  left: -18%;
  width: 136%;
  border-radius: 45% 55% 48% 52% / 48% 44% 56% 52%;
  transform: translate3d(-4%, 3%, 0);
  animation: riverDrift 6.8s ease-in-out infinite alternate;
}

.river-layer::before,
.river-layer::after {
  position: absolute;
  right: 0;
  left: 0;
  height: 78px;
  content: "";
  background-image: radial-gradient(132px 58px at 50% 100%, var(--river-color) 0 62%, transparent 64%);
  background-size: 264px 78px;
  background-repeat: repeat-x;
}

.river-layer::before {
  top: -54px;
  background-position: 0 0;
}

.river-layer::after {
  bottom: -54px;
  background-image: radial-gradient(132px 58px at 50% 0%, var(--river-color) 0 62%, transparent 64%);
  background-position: 132px 0;
}

.river-layer-main {
  top: 31%;
  height: 172px;
  --river-color: #72d7f4;
  background: var(--river-color);
}

.river-layer-light {
  top: 45%;
  height: 96px;
  --river-color: #d9fbff;
  background: var(--river-color);
  animation-duration: 5.4s;
}

.river-layer-deep {
  top: 55%;
  height: 118px;
  --river-color: #7ddcc8;
  background: var(--river-color);
  animation-duration: 7.6s;
}

.auth-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) 420px;
  gap: 28px;
  width: min(1080px, 100%);
  align-items: stretch;
}

.brand-panel,
.auth-card {
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 28px 80px rgba(15, 63, 87, 0.16);
  backdrop-filter: blur(18px);
}

.brand-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 520px;
  overflow: hidden;
  padding: 42px;
}

.brand-copy {
  max-width: 460px;
  margin-top: 54px;
}

.eyebrow {
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.2em;
}

.brand-copy h1 {
  margin: 14px 0 18px;
  color: #0f3f57;
  font-size: 44px;
  line-height: 1.15;
}

.brand-copy p {
  margin: 0;
  color: #3b7188;
  font-size: 16px;
  line-height: 1.8;
}

.value-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.value-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border: 1px solid rgba(14, 165, 233, 0.14);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.56);
}

.value-item b {
  color: #0f3f57;
}

.auth-card {
  padding: 14px;
}

.form-head {
  margin-bottom: 24px;
  text-align: left;
}

.form-head span {
  color: #0f766e;
  font-size: 13px;
  font-weight: 800;
}

.form-head h2 {
  margin: 10px 0 10px;
  color: #0f3f57;
  font-size: 28px;
}

.form-head p,
.switch-tip {
  margin: 0;
  color: #64748b;
}

.auth-submit {
  width: 100%;
  height: 44px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(100deg, #0ea5e9, #0f766e);
  font-weight: 800;
  letter-spacing: 0.1em;
}

.auth-submit:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.24);
}

.switch-tip {
  margin-top: 18px;
  text-align: center;
}

:deep(.el-card__body) {
  padding: 34px;
}

:deep(.el-input__wrapper) {
  border-radius: 14px;
  box-shadow: 0 0 0 1px #dbeafe inset;
}

@keyframes waterFlow {
  0%,
  100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

@keyframes riverDrift {
  0% {
    transform: translate3d(-6%, 5%, 0) rotate(0deg) scaleX(1);
  }
  38% {
    transform: translate3d(-1%, -2%, 0) rotate(0.8deg) scaleX(1.02);
  }
  72% {
    transform: translate3d(4%, 2%, 0) rotate(-0.4deg) scaleX(1.03);
  }
  100% {
    transform: translate3d(7%, -5%, 0) rotate(0deg) scaleX(1.04);
  }
}

@media (max-width: 860px) {
  .auth-page {
    padding: 18px;
  }

  .auth-shell {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    min-height: auto;
    padding: 28px;
  }

  .brand-copy {
    margin-top: 28px;
  }

  .brand-copy h1 {
    font-size: 32px;
  }

  .value-list {
    grid-template-columns: 1fr;
    margin-top: 26px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .auth-page,
  .river-layer {
    animation: none;
  }
}
</style>
