<template>
  <div class="page profile-settings-page">
    <section class="profile-hero">
      <div class="hero-user">
        <el-avatar :size="88" :src="auth.user?.avatar">{{ auth.user?.username?.slice(0, 1) }}</el-avatar>
        <div>
          <span class="eyebrow">个人设置</span>
          <h2>{{ auth.user?.username || '水木用户' }}</h2>
          <div class="hero-tags">
            <span class="role-pill">{{ roleLabel }}</span>
            <span class="status-pill">{{ currentStatusLabel }}</span>
          </div>
        </div>
      </div>
      <p class="muted">维护你的个人资料、在线状态和登录安全，右上角身份卡会同步展示最新状态。</p>
    </section>

    <section class="settings-stack">
      <el-card class="settings-card avatar-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <span class="eyebrow">Avatar</span>
              <h3>头像设置</h3>
            </div>
            <span class="leaf-dot"></span>
          </div>
        </template>
        <div class="avatar-box">
          <el-avatar :size="96" :src="auth.user?.avatar">{{ auth.user?.username?.slice(0, 1) }}</el-avatar>
          <div class="avatar-actions">
            <b>{{ auth.user?.username || '未命名用户' }}</b>
            <p class="muted">选择一张清晰头像，让学习社区更容易识别你。</p>
            <input ref="avatarInput" class="hidden-file" type="file" accept="image/*" @change="onAvatarChange" />
            <div class="button-row">
              <el-button class="theme-button secondary" @click="triggerAvatarInput">更换头像</el-button>
              <el-button class="theme-button" :disabled="!avatarFile" @click="saveAvatar">上传头像</el-button>
            </div>
            <span v-if="avatarFile" class="file-name">{{ avatarFile.name }}</span>
          </div>
        </div>
      </el-card>

      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <span class="eyebrow">Profile</span>
              <h3>基础信息与状态</h3>
            </div>
            <span class="leaf-dot"></span>
          </div>
        </template>
        <el-form :model="profileForm" label-position="top" class="profile-form">
          <div class="form-grid">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" size="large" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" size="large" />
            </el-form-item>
          </div>
          <el-form-item label="个人简介">
            <el-input v-model="profileForm.bio" type="textarea" :rows="4" maxlength="300" show-word-limit />
          </el-form-item>
          <div class="status-section">
            <div class="status-title">
              <b>当前状态</b>
              <span class="muted">选择后会同步到右上角身份卡</span>
            </div>
            <div class="status-grid">
              <button v-for="status in statusOptions" :key="status.value" class="status-card" :class="{ active: profileForm.status === status.value }" type="button" @click="profileForm.status = status.value">
                <span class="status-emoji">{{ status.emoji }}</span>
                <strong>{{ status.label }}</strong>
                <small>{{ status.description }}</small>
              </button>
            </div>
          </div>
          <el-button class="theme-button save-button" @click="saveProfile">保存信息</el-button>
        </el-form>
      </el-card>

      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <span class="eyebrow">Security</span>
              <h3>修改密码</h3>
            </div>
            <span class="leaf-dot"></span>
          </div>
        </template>
        <el-form :model="passwordForm" label-position="top" class="password-form">
          <div class="form-grid">
            <el-form-item label="旧密码">
              <el-input v-model="passwordForm.old_password" type="password" show-password size="large" />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.new_password" type="password" show-password size="large" />
            </el-form-item>
          </div>
          <el-form-item label="确认新密码">
            <el-input v-model="passwordForm.confirm_password" type="password" show-password size="large" />
          </el-form-item>
          <el-button class="theme-button warning-button" @click="submitPassword">更新密码</el-button>
        </el-form>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const avatarFile = ref(null)
const avatarInput = ref(null)
const statusOptions = [
  { value: 'happy', label: '开心', emoji: '😊', description: '今天状态很好' },
  { value: 'cool', label: '冷漠', emoji: '😐', description: '保持安静专注' },
  { value: 'learning', label: '学习中', emoji: '📖', description: '正在投入学习' },
  { value: 'focused', label: '专注中', emoji: '🎯', description: '屏蔽干扰冲刺中' },
  { value: 'reading', label: '阅读中', emoji: '📚', description: '正在消化资料' },
  { value: 'practicing', label: '实践中', emoji: '💻', description: '动手完成练习' },
  { value: 'thinking', label: '思考中', emoji: '🤔', description: '整理问题和思路' },
  { value: 'examing', label: '备考中', emoji: '📝', description: '准备测验考试' },
  { value: 'asking', label: '求助中', emoji: '🙋', description: '等待老师答疑' },
  { value: 'busy', label: '忙碌', emoji: '💼', description: '任务较多处理中' },
  { value: 'resting', label: '休息中', emoji: '🌿', description: '短暂恢复能量' },
  { value: 'charging', label: '充电中', emoji: '⚡', description: '积蓄新的动力' }
]
const profileForm = reactive({
  username: '',
  email: '',
  bio: '',
  status: 'learning'
})
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const roleLabel = computed(() => ({ student: '学生', teacher: '教师', admin: '管理员' }[auth.role] || '访客'))
const currentStatus = computed(() => statusOptions.find((status) => status.value === profileForm.status) || statusOptions[2])
const currentStatusLabel = computed(() => `${currentStatus.value.emoji} ${currentStatus.value.label}`)

function fillFromUser() {
  profileForm.username = auth.user?.username || ''
  profileForm.email = auth.user?.email || ''
  profileForm.bio = auth.user?.bio || ''
  profileForm.status = auth.user?.status || 'learning'
}

async function init() {
  await auth.fetchMe()
  fillFromUser()
}

async function saveProfile() {
  await auth.updateProfile({
    username: profileForm.username.trim(),
    email: profileForm.email.trim(),
    bio: profileForm.bio.trim(),
    status: profileForm.status
  })
  ElMessage.success('个人信息已更新')
  fillFromUser()
}

function triggerAvatarInput() {
  avatarInput.value?.click()
}

function onAvatarChange(event) {
  avatarFile.value = event.target.files[0] || null
}

async function saveAvatar() {
  if (!avatarFile.value) return
  const formData = new FormData()
  formData.append('avatar', avatarFile.value)
  await auth.updateProfile(formData)
  avatarFile.value = null
  if (avatarInput.value) avatarInput.value.value = ''
  ElMessage.success('头像已更新')
}

async function submitPassword() {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
    ElMessage.warning('请完整填写密码信息')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次新密码输入不一致')
    return
  }
  await auth.changePassword({
    old_password: passwordForm.old_password,
    new_password: passwordForm.new_password
  })
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  ElMessage.success('密码更新成功，请重新登录')
}

onMounted(init)
</script>

<style scoped>
.profile-settings-page {
  display: grid;
  gap: 18px;
  max-width: 980px;
  margin: 0 auto;
}

.profile-hero,
.settings-card {
  border: 1px solid rgba(125, 211, 252, 0.42);
  border-radius: 28px;
  background: #fff;
  box-shadow: 0 18px 48px rgba(15, 63, 87, 0.08);
}

.profile-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 26px;
  background:
    radial-gradient(circle at 12% 20%, rgba(34, 197, 94, 0.14), transparent 30%),
    radial-gradient(circle at 90% 72%, rgba(14, 165, 233, 0.16), transparent 32%),
    #fff;
}

.hero-user,
.avatar-box,
.card-head,
.button-row,
.status-title {
  display: flex;
  align-items: center;
  gap: 14px;
}

.hero-user h2,
.card-head h3 {
  margin: 6px 0;
  color: #0f3f57;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.role-pill,
.status-pill {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.role-pill {
  color: #0369a1;
  background: #e0f2fe;
}

.status-pill {
  color: #0f766e;
  background: #dcfce7;
}

.eyebrow {
  color: #0f766e;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 1px;
}

.settings-stack {
  display: grid;
  gap: 16px;
}

.settings-card {
  overflow: hidden;
}

.settings-card :deep(.el-card__header) {
  border-bottom: 1px solid #e0f2fe;
  background:
    radial-gradient(circle at 8% 12%, rgba(255, 255, 255, 0.72), transparent 28%),
    linear-gradient(135deg, #ecfeff, #f0fdf4);
}

.card-head {
  justify-content: space-between;
}

.leaf-dot,
.status-leaf {
  display: inline-flex;
  background: linear-gradient(135deg, #22c55e, #0f766e);
  border-radius: 70% 8px 70% 10px;
  transform: rotate(-24deg);
}

.leaf-dot {
  width: 28px;
  height: 22px;
}

.status-leaf {
  width: 22px;
  height: 17px;
  flex: 0 0 auto;
}

.avatar-card :deep(.el-card__body) {
  padding: 24px;
}

.avatar-box {
  align-items: flex-start;
}

.avatar-actions {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.avatar-actions b {
  color: #0f3f57;
  font-size: 18px;
}

.hidden-file {
  display: none;
}

.file-name {
  color: #3b7188;
  font-size: 12px;
  font-weight: 800;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.status-section {
  display: grid;
  gap: 12px;
  margin: 6px 0 18px;
}

.status-title {
  justify-content: space-between;
}

.status-title b {
  color: #0f3f57;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.status-card {
  display: grid;
  justify-items: start;
  gap: 8px;
  padding: 14px;
  color: #31566a;
  background: #f8fafc;
  border: 1px solid #e0f2fe;
  border-radius: 18px;
  text-align: left;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease;
}

.status-card strong {
  color: #0f3f57;
}

.status-card small {
  color: #64748b;
  font-weight: 700;
}

.status-card.active {
  border-color: rgba(15, 118, 110, 0.42);
  background:
    radial-gradient(circle at 12% 18%, rgba(255, 255, 255, 0.72), transparent 30%),
    linear-gradient(135deg, #ecfeff, #dcfce7);
  box-shadow: 0 14px 30px rgba(15, 118, 110, 0.12);
  transform: translateY(-2px);
}

.status-emoji {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: rgba(255, 255, 255, 0.86);
  border-radius: 14px;
  font-size: 20px;
  box-shadow: 0 8px 18px rgba(15, 118, 110, 0.1);
}

.theme-button {
  min-width: 112px;
  height: 38px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: linear-gradient(135deg, #10b981, #075985);
  font-weight: 900;
}

.theme-button.secondary {
  color: #0f766e;
  background: #ecfeff;
  border: 1px solid #99f6e4;
}

.theme-button.warning-button {
  background: linear-gradient(135deg, #0ea5e9, #1e3a8a);
}

.save-button,
.warning-button {
  margin-top: 4px;
}

@media (max-width: 760px) {
  .profile-hero,
  .hero-user,
  .avatar-box,
  .status-title {
    align-items: flex-start;
    flex-direction: column;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
