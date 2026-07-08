<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand" @click="$router.push('/courses')">在线教育平台</div>
      <el-menu mode="horizontal" router :default-active="$route.path" class="menu">
        <el-menu-item index="/courses">课程广场</el-menu-item>
        <el-menu-item v-if="auth.role === 'student'" index="/student">学生中心</el-menu-item>
        <el-menu-item v-if="auth.role === 'teacher'" index="/teacher">教师中心</el-menu-item>
        <el-menu-item v-if="auth.role === 'admin'" index="/admin">管理后台</el-menu-item>
        <el-menu-item v-if="auth.isLoggedIn" index="/community">社区中心</el-menu-item>
      </el-menu>
      <div class="userbar">
        <template v-if="auth.isLoggedIn">
          <span class="user-name">{{ auth.user?.username }}（{{ roleLabel }}）</span>
          <el-dropdown trigger="click">
            <el-button class="avatar-btn" text>
              <el-avatar :size="30" :src="auth.user?.avatar">{{ auth.user?.username?.slice(0, 1) }}</el-avatar>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人设置</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button size="small" @click="$router.push('/login')">登录</el-button>
          <el-button size="small" type="primary" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const roleLabel = computed(() => ({ student: '学生', teacher: '教师', admin: '管理员' }[auth.role] || '访客'))

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  gap: 18px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.brand {
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
}

.menu {
  flex: 1;
  border-bottom: 0;
}

.userbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  white-space: nowrap;
}

.avatar-btn {
  padding: 0;
  border: none;
}
</style>
