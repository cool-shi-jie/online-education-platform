<template>
  <div class="page student-dashboard">
    <section class="student-hero">
      <div>
        <h2>学生中心</h2>
        <p class="muted">沿着学习路径继续推进课程、证书和疑难解答。</p>
      </div>
      <div class="hero-stat">
        <b>{{ averageProgress }}%</b>
        <span>平均进度</span>
      </div>
    </section>

    <section class="student-layout">
      <aside class="student-tree-panel">
        <div class="panel-title">
          <span>成长路径</span>
          <b>{{ activeSection?.label }}</b>
        </div>
        <div class="student-tree">
          <template v-for="(section, index) in studentSections" :key="section.name">
            <button class="student-node" :class="{ active: activeSectionName === section.name }" type="button" @click="activeSectionName = section.name">
              <span class="node-dot">{{ index + 1 }}</span>
              <span>{{ section.label }}</span>
            </button>
            <span v-if="index < studentSections.length - 1" class="tree-connector" :class="{ active: isConnectorActive(index) }"></span>
          </template>
        </div>
      </aside>

      <main class="student-content">
        <section v-if="activeSectionName === 'learning'" class="content-section">
          <div class="content-tools">
            <div>
              <h3>我的学习</h3>
              <p class="muted">用课程卡片追踪进度，快速回到学习现场。</p>
            </div>
          </div>
          <section class="stat-grid">
            <div class="stat-card">
              <span>课程总数</span>
              <b>{{ courseCount }}</b>
            </div>
            <div class="stat-card">
              <span>进行中</span>
              <b>{{ activeCourseCount }}</b>
            </div>
            <div class="stat-card">
              <span>已完成</span>
              <b>{{ completedCourseCount }}</b>
            </div>
            <div class="stat-card">
              <span>平均进度</span>
              <b>{{ averageProgress }}%</b>
            </div>
          </section>
          <div class="course-grid">
            <article v-for="item in enrollments" :key="item.id || item.course" class="course-card">
              <div class="course-card-head">
                <el-tag size="small" effect="plain">{{ progressLabel(item) }}</el-tag>
                <h3>{{ item.course_title }}</h3>
              </div>
              <el-progress :percentage="item.progress_percent || 0" />
              <div class="course-actions">
                <el-button class="card-action-button card-action-button--primary" type="primary" @click="$router.push(`/student/courses/${item.course}/learn`)">继续学习</el-button>
                <el-button class="card-action-button card-action-button--secondary" @click="$router.push(`/community/${item.course}`)">课程社区</el-button>
              </div>
            </article>
          </div>
          <p v-if="enrollments.length === 0" class="compact-empty">你还没有报名课程。</p>
        </section>

        <section v-else-if="activeSectionName === 'certificates'" class="content-section">
          <div class="content-tools">
            <div>
              <h3>证书成果</h3>
              <p class="muted">直接预览已经获得的网页虚拟证书。</p>
            </div>
          </div>
          <div v-if="certificates.length" class="certificate-preview-grid">
            <article v-for="certificate in certificates" :key="certificate.id" class="certificate-preview-card">
              <div class="cert-preview-mark">
                <BrandLogo size="sm" mark-only />
              </div>
              <div>
                <el-tag size="small" type="success" effect="plain">网页证书</el-tag>
                <h3>{{ certificate.course_title }}</h3>
                <p class="muted">获证人：{{ certificate.student_name }}</p>
              </div>
              <div class="cert-preview-meta">
                <span>证书编号</span>
                <b>{{ certificate.code }}</b>
              </div>
              <div class="cert-preview-meta">
                <span>颁发时间</span>
                <b>{{ formatDate(certificate.issued_at) }}</b>
              </div>
              <div class="course-actions">
                <el-button class="card-action-button card-action-button--primary" type="primary" @click="openCertificate(certificate)">查看证书</el-button>
                <el-link v-if="certificate.file" :href="certificate.file" target="_blank" type="primary">下载证书</el-link>
              </div>
            </article>
          </div>
          <p v-else class="compact-empty">暂无证书，达到课程优秀线后会自动获得证书。</p>
        </section>

        <section v-else-if="activeSectionName === 'questions'" class="content-section">
          <div class="content-tools">
            <div>
              <h3>疑难解答</h3>
              <p class="muted">直接查看课程提问、老师回复和解决状态。</p>
            </div>
          </div>
          <div class="question-group-grid">
            <section v-for="group in questionGroups" :key="group.key" class="question-group-card">
              <div class="question-group-head">
                <h4>{{ group.label }}</h4>
                <el-tag>{{ group.items.length }}</el-tag>
              </div>
              <p v-if="group.items.length === 0" class="compact-empty">暂无记录</p>
              <article v-for="question in group.items" :key="question.id" class="question-record-card">
                <div>
                  <el-tag size="small" effect="plain">{{ question.course_title }}</el-tag>
                  <h3>{{ question.title }}</h3>
                  <p class="muted">{{ question.chapter_title || '课程通用问题' }}</p>
                  <p class="answer-text">{{ question.answer || '待老师回复' }}</p>
                </div>
                <el-button v-if="question.status === 'answered'" size="small" type="success" @click="resolveQuestion(question)">标记已解决</el-button>
              </article>
            </section>
          </div>
        </section>

        <section v-else-if="activeSectionName === 'records'" class="content-section">
          <div class="content-tools">
            <div>
              <h3>学习记录</h3>
              <p class="muted">根据课程进度生成的简洁学习概览。</p>
            </div>
          </div>
          <div class="record-grid">
            <div class="record-card">
              <span>正在学习</span>
              <b>{{ activeCourseCount }} 门</b>
              <p class="muted">进度大于 0 且未完成的课程。</p>
            </div>
            <div class="record-card">
              <span>即将完成</span>
              <b>{{ nearlyDoneCount }} 门</b>
              <p class="muted">进度达到 80% 以上的课程。</p>
            </div>
            <div class="record-card">
              <span>已完成</span>
              <b>{{ completedCourseCount }} 门</b>
              <p class="muted">进度已经达到 100% 的课程。</p>
            </div>
          </div>
          <div v-if="nextCourse" class="feature-card continue-card">
            <div>
              <h3>最近可继续</h3>
              <p class="muted">{{ nextCourse.course_title }} · 当前进度 {{ nextCourse.progress_percent || 0 }}%</p>
            </div>
            <el-button class="card-action-button card-action-button--primary" type="primary" @click="$router.push(`/student/courses/${nextCourse.course}/learn`)">继续学习</el-button>
          </div>
        </section>
      </main>
    </section>

    <el-dialog v-model="certificateVisible" title="网页虚拟证书" width="760px">
      <div v-if="currentCertificate" class="virtual-certificate">
        <div class="certificate-inner">
          <div class="certificate-topline">
            <BrandLogo size="sm" />
            <span>水木学堂在线教育平台</span>
          </div>
          <h1>课程结业优秀证书</h1>
          <p class="certificate-text">
            兹证明
            <strong>{{ currentCertificate.student_name }}</strong>
            同学已完成
            <strong>{{ currentCertificate.course_title }}</strong>
            课程学习，并在课程考试中达到优秀标准，特发此证。
          </p>
          <div class="certificate-info">
            <div>
              <span>证书编号</span>
              <b>{{ currentCertificate.code }}</b>
            </div>
            <div>
              <span>颁发日期</span>
              <b>{{ formatDate(currentCertificate.issued_at) }}</b>
            </div>
          </div>
          <div class="certificate-footer">
            <span>认证平台：水木学堂在线教育平台</span>
            <span>优秀结业认证</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-link v-if="currentCertificate?.file" :href="currentCertificate.file" target="_blank" type="primary">下载证书文件</el-link>
        <el-button @click="certificateVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import BrandLogo from '../../components/BrandLogo.vue'
import http from '../../api/http'

const enrollments = ref([])
const certificates = ref([])
const questions = ref([])
const certificateVisible = ref(false)
const currentCertificate = ref(null)
const activeSectionName = ref('learning')
const studentSections = [
  { name: 'learning', label: '我的学习' },
  { name: 'certificates', label: '证书成果' },
  { name: 'questions', label: '疑难解答' },
  { name: 'records', label: '学习记录' }
]

const activeSection = computed(() => studentSections.find((section) => section.name === activeSectionName.value))
const courseCount = computed(() => enrollments.value.length)
const completedCourseCount = computed(() => enrollments.value.filter((item) => (item.progress_percent || 0) >= 100).length)
const activeCourseCount = computed(() => enrollments.value.filter((item) => (item.progress_percent || 0) > 0 && (item.progress_percent || 0) < 100).length)
const nearlyDoneCount = computed(() => enrollments.value.filter((item) => (item.progress_percent || 0) >= 80 && (item.progress_percent || 0) < 100).length)
const averageProgress = computed(() => {
  if (enrollments.value.length === 0) return 0
  const total = enrollments.value.reduce((sum, item) => sum + (item.progress_percent || 0), 0)
  return Math.round(total / enrollments.value.length)
})
const nextCourse = computed(() => enrollments.value.find((item) => (item.progress_percent || 0) < 100) || enrollments.value[0])
const questionGroups = computed(() => {
  const statuses = [
    { key: 'pending', label: '待回复' },
    { key: 'answered', label: '已回复' },
    { key: 'resolved', label: '已解决' },
  ]
  return statuses.map((status) => ({
    ...status,
    items: questions.value.filter((item) => item.status === status.key),
  }))
})

function isConnectorActive(index) {
  const activeIndex = studentSections.findIndex((section) => section.name === activeSectionName.value)
  return activeIndex > index
}

function progressLabel(item) {
  const progress = item.progress_percent || 0
  if (progress >= 100) return '已完成'
  if (progress >= 80) return '即将完成'
  if (progress > 0) return '学习中'
  return '未开始'
}

function openCertificate(certificate) {
  currentCertificate.value = certificate
  certificateVisible.value = true
}

function formatDate(value) {
  if (!value) return '暂无'
  return new Date(value).toLocaleDateString('zh-CN')
}

async function load() {
  const [enrollmentRes, certificateRes, questionRes] = await Promise.all([
    http.get('/enrollments/'),
    http.get('/certificates/'),
    http.get('/course-questions/')
  ])
  enrollments.value = enrollmentRes.data.results || enrollmentRes.data
  certificates.value = certificateRes.data.results || certificateRes.data
  questions.value = questionRes.data.results || questionRes.data
}

async function resolveQuestion(row) {
  await http.post(`/course-questions/${row.id}/resolve/`)
  ElMessage.success('已标记为已解决')
  await load()
}

onMounted(load)
</script>

<style scoped>
.student-dashboard {
  display: grid;
  gap: 18px;
}

.student-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
  border: 1px solid rgba(125, 211, 252, 0.42);
  border-radius: 28px;
  background:
    radial-gradient(circle at 12% 20%, rgba(14, 165, 233, 0.18), transparent 30%),
    radial-gradient(circle at 90% 70%, rgba(34, 197, 94, 0.14), transparent 28%),
    #fff;
  box-shadow: 0 18px 48px rgba(15, 63, 87, 0.08);
}

.student-hero h2 {
  margin: 0 0 8px;
  color: #0f3f57;
  font-size: 30px;
}

.hero-stat {
  display: grid;
  place-items: center;
  min-width: 108px;
  min-height: 88px;
  color: #0f766e;
  border-radius: 24px;
  background: linear-gradient(135deg, #ecfeff, #f0fdf4);
}

.hero-stat b {
  font-size: 30px;
  line-height: 1;
}

.hero-stat span {
  color: #3b7188;
  font-size: 13px;
  font-weight: 700;
}

.student-layout {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.student-tree-panel {
  position: sticky;
  top: 88px;
  padding: 18px;
  border: 1px solid #e0f2fe;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 16px 40px rgba(15, 63, 87, 0.07);
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-title span {
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

.panel-title b {
  color: #0f3f57;
  font-size: 14px;
}

.student-tree {
  display: grid;
  justify-items: start;
}

.student-node {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
  padding: 10px;
  color: #31566a;
  font: inherit;
  font-size: 14px;
  font-weight: 800;
  text-align: left;
  background: #f8fafc;
  border: 1px solid #e0f2fe;
  border-radius: 16px;
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.student-node:hover {
  color: #0f766e;
  border-color: #7dd3fc;
  transform: translateX(2px);
}

.student-node.active {
  color: #fff;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  border-color: transparent;
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.2);
}

.node-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex: 0 0 auto;
  color: #0f766e;
  background: #ecfeff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 900;
}

.student-node.active .node-dot {
  background: rgba(255, 255, 255, 0.9);
}

.tree-connector {
  width: 3px;
  height: 18px;
  margin-left: 22px;
  background: linear-gradient(#bae6fd, #bbf7d0);
  border-radius: 999px;
}

.tree-connector.active {
  width: 4px;
  background: linear-gradient(#0ea5e9, #0f766e);
}

.student-content,
.content-section {
  display: grid;
  gap: 16px;
}

.stat-grid,
.course-grid,
.record-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card,
.record-card,
.feature-card,
.course-card {
  border: 1px solid #e0f2fe;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 14px 34px rgba(15, 63, 87, 0.06);
}

.stat-card {
  display: grid;
  gap: 8px;
  padding: 16px;
}

.stat-card span,
.record-card span {
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

.stat-card b,
.record-card b {
  color: #0f3f57;
  font-size: 26px;
  line-height: 1;
}

.content-tools {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e0f2fe;
  border-radius: 22px;
  background: #fff;
}

.content-tools h3,
.feature-card h3 {
  margin: 0 0 6px;
  color: #0f3f57;
}

.course-card {
  display: grid;
  gap: 16px;
  overflow: hidden;
  padding: 18px;
}

.course-card-head {
  min-height: 104px;
  padding: 18px;
  margin: -18px -18px 0;
  background:
    radial-gradient(circle at 15% 18%, rgba(255, 255, 255, 0.62), transparent 26%),
    linear-gradient(135deg, #e0f7fa, #f0fdf4);
}

.course-card-head h3 {
  margin: 14px 0 0;
  color: #0f3f57;
  line-height: 1.35;
}

.course-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.card-action-button {
  min-width: 112px;
  height: 36px;
  margin-left: 0;
  border-radius: 999px;
  font-weight: 800;
}

.card-action-button + .card-action-button {
  margin-left: 0;
}

.card-action-button--primary {
  border: none;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  box-shadow: 0 10px 20px rgba(14, 165, 233, 0.2);
}

.card-action-button--primary:hover {
  border: none;
  background: linear-gradient(135deg, #0284c7, #0d9488);
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.26);
}

.card-action-button--secondary {
  color: #0f766e;
  border-color: #99f6e4;
  background: #ecfeff;
}

.card-action-button--secondary:hover {
  color: #0f3f57;
  border-color: #7dd3fc;
  background: #f0fdfa;
}

.course-actions :deep(.el-link) {
  height: 36px;
  align-items: center;
  padding: 0 12px;
  border-radius: 999px;
  background: #f8fafc;
  font-weight: 800;
}

.feature-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px;
}

.certificate-card {
  background:
    radial-gradient(circle at 8% 18%, rgba(14, 165, 233, 0.12), transparent 28%),
    #fff;
}

.question-card {
  background:
    radial-gradient(circle at 8% 18%, rgba(34, 197, 94, 0.12), transparent 28%),
    #fff;
}

.continue-card {
  background:
    radial-gradient(circle at 8% 18%, rgba(45, 212, 191, 0.12), transparent 28%),
    #fff;
}

.record-card {
  display: grid;
  gap: 8px;
  padding: 16px;
}

.record-card p,
.feature-card p,
.stat-card p {
  margin: 0;
}

.certificate-preview-grid,
.question-group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.certificate-preview-card,
.question-group-card,
.question-record-card {
  border: 1px solid #e0f2fe;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 14px 34px rgba(15, 63, 87, 0.06);
}

.certificate-preview-card {
  display: grid;
  gap: 14px;
  padding: 18px;
}

.cert-preview-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 58px;
  height: 58px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(34, 197, 94, 0.18));
}

.certificate-preview-card h3,
.question-record-card h3 {
  margin: 10px 0 6px;
  color: #0f3f57;
}

.cert-preview-meta {
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}

.cert-preview-meta span,
.certificate-info span {
  color: #64748b;
  font-size: 12px;
}

.cert-preview-meta b,
.certificate-info b {
  color: #0f3f57;
}

.question-group-card {
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 16px;
}

.question-group-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.question-group-head h4 {
  margin: 0;
  color: #0f3f57;
}

.question-record-card {
  display: grid;
  gap: 12px;
  padding: 14px;
  box-shadow: none;
}

.answer-text {
  margin: 10px 0 0;
  padding: 10px;
  color: #334155;
  background: #f8fafc;
  border-radius: 12px;
  line-height: 1.6;
}

.virtual-certificate {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #e0f7fa, #f0fdf4);
}

.certificate-inner {
  padding: 44px;
  border: 8px double #1e5b7a;
  border-radius: 18px;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 34%),
    radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.14), transparent 34%),
    #fff;
  text-align: center;
}

.certificate-topline {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: #1e5b7a;
  font-weight: 800;
  letter-spacing: 4px;
}

.certificate-inner h1 {
  margin: 22px 0;
  color: #0f3f57;
  font-size: 34px;
  letter-spacing: 8px;
}

.certificate-text {
  max-width: 560px;
  margin: 0 auto;
  color: #334155;
  font-size: 18px;
  line-height: 2.1;
}

.certificate-text strong {
  color: #14532d;
  font-size: 22px;
}

.certificate-info {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  max-width: 520px;
  margin: 34px auto;
}

.certificate-info div {
  display: grid;
  gap: 6px;
  padding: 14px;
  border-radius: 14px;
  background: #ecfeff;
}

.certificate-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  color: #475569;
  font-weight: 700;
}

.compact-empty {
  margin: 0;
  padding: 12px 14px;
  color: #64748b;
  background: #f8fafc;
  border: 1px dashed #bae6fd;
  border-radius: 14px;
  font-size: 13px;
}

@media (max-width: 900px) {
  .student-hero,
  .content-tools,
  .feature-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .student-layout {
    grid-template-columns: 1fr;
  }

  .student-tree-panel {
    position: static;
  }

  .student-tree {
    display: flex;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .student-node {
    width: auto;
    flex: 0 0 auto;
    white-space: nowrap;
  }

  .tree-connector {
    width: 24px;
    height: 3px;
    flex: 0 0 auto;
    margin: 19px 4px 0;
  }
}

@media (max-width: 560px) {
  .hero-stat,
  .course-actions,
  .course-actions .el-button,
  .feature-card .el-button {
    width: 100%;
  }

  .stat-grid,
  .course-grid,
  .record-grid,
  .certificate-preview-grid,
  .question-group-grid,
  .certificate-info {
    grid-template-columns: 1fr;
  }

  .certificate-inner {
    padding: 24px;
  }

  .certificate-inner h1 {
    font-size: 26px;
    letter-spacing: 4px;
  }

  .certificate-footer {
    align-items: center;
    flex-direction: column;
  }
}
</style>
