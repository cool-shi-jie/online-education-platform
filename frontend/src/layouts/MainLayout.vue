<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand" @click="$router.push('/courses')">
        <BrandLogo size="sm" />
      </div>
      <nav class="menu" aria-label="主导航">
        <div class="nav-tree">
          <template v-for="(item, index) in visibleTreeNavItems" :key="item.path">
            <button class="nav-node" :class="{ active: isNavActive(item) }" type="button" @click="router.push(item.path)">
              <span class="node-dot">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </button>
            <span v-if="index < visibleTreeNavItems.length - 1" class="nav-connector" :class="{ active: isConnectorActive(index) }"></span>
          </template>
        </div>
      </nav>
      <div class="userbar">
        <template v-if="auth.isLoggedIn">
          <el-dropdown trigger="click">
            <el-button class="user-identity-card" text>
              <el-avatar class="identity-avatar" :size="38" :src="auth.user?.avatar">{{ auth.user?.username?.slice(0, 1) }}</el-avatar>
              <span class="identity-copy">
                <strong>{{ auth.user?.username }}</strong>
                <span class="identity-meta">
                  <span class="role-badge" :class="roleClass">{{ roleLabel }}</span>
                  <span class="status-leaf">{{ statusLabel }}</span>
                </span>
              </span>
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
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BrandLogo from '../components/BrandLogo.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const roleLabel = computed(() => ({ student: '学生', teacher: '教师', admin: '管理员' }[auth.role] || '访客'))
const roleClass = computed(() => `role-${auth.role || 'guest'}`)
const statusLabel = computed(() => {
  const labels = {
    happy: '😊 开心',
    cool: '😐 冷漠',
    learning: '📖 学习中',
    focused: '🎯 专注中',
    reading: '📚 阅读中',
    practicing: '💻 实践中',
    thinking: '🤔 思考中',
    examing: '📝 备考中',
    asking: '🙋 求助中',
    busy: '💼 忙碌',
    resting: '🌿 休息中',
    charging: '⚡ 充电中'
  }
  return labels[auth.user?.status] || '📖 学习中'
})

const roleCenterNav = computed(() => {
  if (auth.role === 'teacher') return { label: '教师中心', path: '/teacher', icon: '师' }
  if (auth.role === 'admin') return { label: '管理后台', path: '/admin', icon: '管' }
  if (auth.role === 'student') return { label: '学生中心', path: '/student', icon: '学' }
  return null
})

const visibleTreeNavItems = computed(() => {
  const items = [{ label: '课程广场', path: '/courses', icon: '课' }]
  if (roleCenterNav.value) items.push(roleCenterNav.value)
  if (auth.isLoggedIn) items.push({ label: '社区中心', path: '/community', icon: '社' })
  return items
})

function isNavActive(item) {
  if (item.path === '/courses') return router.currentRoute.value.path.startsWith('/courses')
  return router.currentRoute.value.path === item.path || router.currentRoute.value.path.startsWith(`${item.path}/`)
}

function isConnectorActive(index) {
  return visibleTreeNavItems.value.slice(0, index + 2).some((item) => isNavActive(item))
}

function logout() {
  auth.logout()
  router.push('/login')
}

function syncAuthState() {
  auth.syncFromStorage()
}

onMounted(() => {
  window.addEventListener('auth-storage-cleared', syncAuthState)
})

onBeforeUnmount(() => {
  window.removeEventListener('auth-storage-cleared', syncAuthState)
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  gap: 18px;
  height: 72px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.brand {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.menu {
  display: flex;
  flex: 1;
  justify-content: center;
  min-width: 0;
}

.nav-tree {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: min(560px, 100%);
}

.nav-node {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 112px;
  padding: 9px 14px;
  color: #31566a;
  font: inherit;
  font-size: 14px;
  font-weight: 800;
  background: #f8fafc;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  box-shadow: 0 8px 18px rgba(15, 63, 87, 0.06);
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.nav-node:hover {
  color: #0f766e;
  border-color: #7dd3fc;
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.12);
}

.nav-node.active {
  color: #fff;
  background:
    radial-gradient(circle at 16% 20%, rgba(255, 255, 255, 0.34), transparent 28%),
    linear-gradient(135deg, #0ea5e9, #0f766e);
  border-color: transparent;
  box-shadow: 0 14px 30px rgba(14, 165, 233, 0.28);
}

.node-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  color: #0f766e;
  background: #ecfeff;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 900;
}

.nav-node.active .node-dot {
  color: #0f766e;
  background: rgba(255, 255, 255, 0.9);
}

.nav-connector {
  width: clamp(34px, 5vw, 72px);
  height: 3px;
  margin: 0 8px;
  background: linear-gradient(90deg, #bae6fd, #bbf7d0);
  border-radius: 999px;
  transition:
    height 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.nav-connector.active {
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0f766e);
  box-shadow: 0 8px 16px rgba(14, 165, 233, 0.16);
}

.userbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-identity-card {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 52px;
  padding: 6px 12px 6px 7px;
  border: 1px solid transparent;
  border-radius: 999px;
  color: #0f3f57;
  background:
    linear-gradient(#fff, #fff) padding-box,
    linear-gradient(135deg, rgba(34, 197, 94, 0.72), rgba(14, 165, 233, 0.72), rgba(30, 58, 138, 0.64)) border-box;
  box-shadow: 0 12px 26px rgba(15, 63, 87, 0.1);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.user-identity-card:hover,
.user-identity-card:focus {
  color: #0f3f57;
  transform: translateY(-1px);
  box-shadow: 0 16px 34px rgba(15, 118, 110, 0.16);
}

.identity-avatar {
  flex: 0 0 auto;
  border: 2px solid rgba(255, 255, 255, 0.88);
  box-shadow: 0 8px 18px rgba(14, 165, 233, 0.14);
}

.identity-copy {
  display: grid;
  gap: 4px;
  min-width: 0;
  line-height: 1;
  text-align: left;
}

.identity-copy strong {
  max-width: 112px;
  overflow: hidden;
  color: #0f3f57;
  font-size: 14px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.identity-meta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  color: #0f766e;
  background: #ecfeff;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 900;
}

.role-teacher {
  color: #0369a1;
  background: #e0f2fe;
}

.role-admin {
  color: #1e3a8a;
  background: #dbeafe;
}

.status-leaf {
  position: relative;
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px 0 18px;
  color: #31566a;
  background: #f8fafc;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 900;
}

.status-leaf::before {
  content: '';
  position: absolute;
  left: 6px;
  width: 9px;
  height: 7px;
  background: linear-gradient(135deg, #22c55e, #0f766e);
  border-radius: 8px 1px 8px 1px;
  transform: rotate(-24deg);
}

@media (max-width: 860px) {
  .header {
    height: auto;
    flex-wrap: wrap;
    padding: 12px 16px;
  }

  .menu {
    flex-basis: 100%;
    order: 3;
  }

  .nav-tree {
    width: 100%;
  }

  .nav-node {
    min-width: auto;
    padding: 8px 10px;
    font-size: 13px;
  }

  .nav-connector {
    flex: 1;
    min-width: 18px;
    margin: 0 5px;
  }

  .user-identity-card {
    min-height: 44px;
    padding-right: 8px;
  }

  .identity-avatar {
    width: 32px;
    height: 32px;
  }

  .identity-meta {
    display: none;
  }
}
</style>
