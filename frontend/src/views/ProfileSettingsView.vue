<template>
  <div class="page">
    <h2>个人信息设置</h2>

    <el-row :gutter="16">
      <el-col :xs="24" :md="14">
        <el-card class="block">
          <template #header><b>基础信息</b></template>
          <el-form :model="profileForm" label-position="top">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="profileForm.bio" type="textarea" :rows="4" maxlength="300" show-word-limit />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile">保存信息</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="10">
        <el-card class="block">
          <template #header><b>头像设置</b></template>
          <div class="avatar-box">
            <el-avatar :size="88" :src="auth.user?.avatar">{{ auth.user?.username?.slice(0, 1) }}</el-avatar>
            <input type="file" accept="image/*" @change="onAvatarChange" />
            <el-button type="primary" plain :disabled="!avatarFile" @click="saveAvatar">上传头像</el-button>
          </div>
        </el-card>

        <el-card class="block">
          <template #header><b>修改密码</b></template>
          <el-form :model="passwordForm" label-position="top">
            <el-form-item label="旧密码">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="submitPassword">更新密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const avatarFile = ref(null)
const profileForm = reactive({
  username: '',
  email: '',
  bio: ''
})
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

function fillFromUser() {
  profileForm.username = auth.user?.username || ''
  profileForm.email = auth.user?.email || ''
  profileForm.bio = auth.user?.bio || ''
}

async function init() {
  await auth.fetchMe()
  fillFromUser()
}

async function saveProfile() {
  await auth.updateProfile({
    username: profileForm.username.trim(),
    email: profileForm.email.trim(),
    bio: profileForm.bio.trim()
  })
  ElMessage.success('个人信息已更新')
  fillFromUser()
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
.block {
  margin-bottom: 14px;
}

.avatar-box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}
</style>
