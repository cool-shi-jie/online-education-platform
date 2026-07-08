import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', component: () => import('../views/LoginView.vue') },
  { path: '/register', component: () => import('../views/RegisterView.vue') },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: '/courses' },
      { path: 'courses', component: () => import('../views/CourseListView.vue') },
      { path: 'courses/:id', component: () => import('../views/CourseDetailView.vue') },
      { path: 'student', component: () => import('../views/student/StudentDashboard.vue'), meta: { roles: ['student'] } },
      { path: 'student/courses/:id/learn', component: () => import('../views/student/LearningView.vue'), meta: { roles: ['student'] } },
      { path: 'student/questions', component: () => import('../views/student/StudentTroubleshootingView.vue'), meta: { roles: ['student'] } },
      { path: 'student/exams/:id', component: () => import('../views/student/ExamTakeView.vue'), meta: { roles: ['student'] } },
      { path: 'student/certificates', component: () => import('../views/student/CertificatesView.vue'), meta: { roles: ['student'] } },
      { path: 'certificates', component: () => import('../views/student/CertificatesView.vue'), meta: { roles: ['student', 'teacher', 'admin'] } },
      { path: 'community', component: () => import('../views/CommunityView.vue'), meta: { roles: ['student', 'teacher', 'admin'] } },
      { path: 'profile', component: () => import('../views/ProfileSettingsView.vue'), meta: { roles: ['student', 'teacher', 'admin'] } },
      { path: 'teacher', component: () => import('../views/teacher/TeacherDashboard.vue'), meta: { roles: ['teacher'] } },
      { path: 'teacher/courses', component: () => import('../views/teacher/TeacherCoursesView.vue'), meta: { roles: ['teacher'] } },
      { path: 'teacher/exams', component: () => import('../views/teacher/TeacherExamsView.vue'), meta: { roles: ['teacher'] } },
      { path: 'teacher/progress', component: () => import('../views/teacher/TeacherProgressView.vue'), meta: { roles: ['teacher'] } },
      { path: 'teacher/questions', component: () => import('../views/teacher/TeacherQuestionsView.vue'), meta: { roles: ['teacher'] } },
      { path: 'admin', component: () => import('../views/admin/AdminDashboard.vue'), meta: { roles: ['admin'] } },
      { path: 'admin/users', component: () => import('../views/admin/AdminUsersView.vue'), meta: { roles: ['admin'] } },
      { path: 'admin/content', component: () => import('../views/admin/AdminContentView.vue'), meta: { roles: ['admin'] } },
      { path: 'community/:courseId', redirect: '/community' },
      { path: 'forum/:courseId', redirect: (to) => `/community/${to.params.courseId}` }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const roles = to.meta.roles
  if (roles && !auth.isLoggedIn) {
    return '/login'
  }
  if (roles && !roles.includes(auth.role)) {
    return '/courses'
  }
})

export function homeByRole(role) {
  if (role === 'teacher') return '/teacher'
  if (role === 'admin') return '/admin'
  return '/student'
}

export default router
