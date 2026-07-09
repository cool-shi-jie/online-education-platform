<template>
  <div class="page learning-page" v-if="course">
    <section class="learning-hero">
      <div>
        <span class="eyebrow">章节学习</span>
        <h2>{{ course.title }}</h2>
        <p class="muted">沿着章节树一步步完成学习，遇到问题可以直接关联当前章节提问。</p>
      </div>
      <div class="hero-actions">
        <div class="hero-progress" :style="progressRingStyle">
          <b>{{ progressPercent }}%</b>
          <span>总进度</span>
        </div>
        <el-button class="community-button" @click="$router.push(`/community/${course.id}`)">课程社区</el-button>
      </div>
    </section>

    <section class="learning-layout">
      <aside class="chapter-tree-panel">
        <div class="tree-progress-card">
          <div>
            <span class="eyebrow">学习树</span>
            <h3>{{ completedCount }} / {{ chapterList.length }} 章完成</h3>
          </div>
          <el-progress :percentage="progressPercent" />
        </div>

        <div class="chapter-tree">
          <template v-for="(chapter, index) in chapterList" :key="chapter.id">
            <button class="chapter-leaf-node" :class="chapterNodeClass(chapter)" type="button" @click="selectChapter(chapter)">
              <span class="leaf-shape">
                <span class="leaf-vein"></span>
                <b>{{ index + 1 }}</b>
              </span>
              <span class="chapter-node-text">
                <strong>{{ chapter.title }}</strong>
                <small>{{ chapterStatusText(chapter) }}</small>
              </span>
            </button>
            <span v-if="index < chapterList.length - 1" class="tree-trunk" :class="{ completed: isChapterCompleted(chapter) }"></span>
          </template>
        </div>
      </aside>

      <main class="learning-stage" v-if="currentChapter">
        <section class="chapter-stage-card">
          <div class="stage-head">
            <div>
              <el-tag effect="plain">{{ currentChapter.order ? `第 ${currentChapter.order} 章` : '当前章节' }}</el-tag>
              <h3>{{ currentChapter.title }}</h3>
              <p>{{ currentChapter.description || '暂无章节说明，完成本节学习后可以继续推进课程进度。' }}</p>
            </div>
            <el-tag :type="isChapterCompleted(currentChapter) ? 'success' : 'info'">{{ chapterStatusText(currentChapter) }}</el-tag>
          </div>

          <div v-if="currentChapter.video" class="video-shell">
            <video class="video" :src="currentChapter.video" controls @ended="markVideoFinished(currentChapter)" />
            <p class="video-hint">{{ isVideoFinished(currentChapter) || isChapterCompleted(currentChapter) ? '视频已播放完成，可以标记本章完成。' : '请播放至结束后再标记本章完成。' }}</p>
          </div>
          <div v-else class="no-video-card">
            <b>本章暂无视频</b>
            <p>阅读章节说明后，可以直接标记完成。</p>
          </div>

          <div class="stage-actions">
            <el-button class="complete-button" :disabled="!canCompleteChapter(currentChapter)" @click="completeChapter(currentChapter)">
              {{ completeButtonText(currentChapter) }}
            </el-button>
            <span class="muted">{{ currentChapter.video ? '视频章节需要播放结束' : '无视频章节可直接完成' }}</span>
          </div>
        </section>

        <section class="learning-support-grid">
          <section class="support-card exam-card">
            <div class="support-head">
              <div>
                <span class="eyebrow">课程考试</span>
                <h3>完成后检验成果</h3>
              </div>
              <el-tag>{{ exams.length }}</el-tag>
            </div>
            <el-empty v-if="exams.length === 0" description="暂无考试" />
            <el-button v-for="exam in exams" :key="exam.id" class="exam-button" @click="$router.push(`/student/exams/${exam.id}`)">
              参加考试：{{ exam.title }}
            </el-button>
          </section>

          <section class="support-card question-card">
            <div class="support-head">
              <div>
                <span class="eyebrow">本课提问</span>
                <h3>向老师提出疑问</h3>
              </div>
              <el-tag>{{ questions.length }}</el-tag>
            </div>

            <el-form :model="questionForm" label-position="top" class="question-form">
              <el-form-item label="关联章节">
                <el-select v-model="questionForm.chapter" clearable placeholder="默认关联当前章节">
                  <el-option v-for="chapter in chapterList" :key="chapter.id" :label="chapter.title" :value="chapter.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="问题标题">
                <el-input v-model="questionForm.title" maxlength="160" show-word-limit />
              </el-form-item>
              <el-form-item label="问题描述">
                <el-input v-model="questionForm.content" type="textarea" :rows="3" maxlength="1000" show-word-limit />
              </el-form-item>
              <el-button class="submit-question-button" @click="createQuestion">提交问题</el-button>
            </el-form>

            <div class="question-list">
              <el-empty v-if="questions.length === 0" description="你还没有提问" />
              <article v-for="question in orderedQuestions" :key="question.id" class="question-item">
                <div class="question-item-head">
                  <div>
                    <b>{{ question.title }}</b>
                    <p class="muted">{{ question.chapter_title || '课程通用问题' }}</p>
                  </div>
                  <el-tag :type="statusTagType(question.status)">{{ statusLabel(question.status) }}</el-tag>
                </div>
                <p>{{ question.content }}</p>
                <div v-if="question.answer" class="answer-box">
                  <b>教师回复：</b>
                  <p>{{ question.answer }}</p>
                </div>
                <div class="question-footer">
                  <span class="muted">提问时间：{{ question.created_at }}</span>
                  <el-button v-if="question.status === 'answered'" size="small" type="success" @click="resolveQuestion(question)">标记已解决</el-button>
                </div>
              </article>
            </div>
          </section>
        </section>
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const route = useRoute()
const course = ref(null)
const progress = ref(null)
const exams = ref([])
const questions = ref([])
const activeChapterId = ref(null)
const videoFinishedIds = ref(new Set())
const questionForm = reactive({ chapter: '', title: '', content: '' })

const chapterList = computed(() => course.value?.chapters || [])
const progressPercent = computed(() => progress.value?.progress_percent || 0)
const progressRingStyle = computed(() => ({ '--progress': `${progressPercent.value}%` }))
const completedChapterIds = computed(() => {
  const records = progress.value?.chapter_progress || []
  return new Set(records.filter((record) => record.is_completed).map((record) => record.chapter))
})
const completedCount = computed(() => chapterList.value.filter((chapter) => isChapterCompleted(chapter)).length)
const currentChapter = computed(() => chapterList.value.find((chapter) => chapter.id === activeChapterId.value) || chapterList.value[0])
const orderedQuestions = computed(() => {
  const currentId = activeChapterId.value
  return [...questions.value].sort((a, b) => {
    const aCurrent = a.chapter === currentId ? 0 : 1
    const bCurrent = b.chapter === currentId ? 0 : 1
    return aCurrent - bCurrent
  })
})

watch(activeChapterId, (chapterId) => {
  questionForm.chapter = chapterId || ''
})

async function load() {
  const courseId = route.params.id
  const [courseRes, progressRes, examsRes, questionsRes] = await Promise.all([
    http.get(`/courses/${courseId}/`),
    http.get(`/courses/${courseId}/progress/`),
    http.get('/exams/', { params: { course: courseId, is_published: true } }),
    http.get('/course-questions/', { params: { course: courseId } }),
  ])
  course.value = courseRes.data
  progress.value = progressRes.data
  exams.value = examsRes.data.results || examsRes.data
  questions.value = questionsRes.data.results || questionsRes.data
  ensureActiveChapter()
}

function ensureActiveChapter() {
  if (activeChapterId.value && chapterList.value.some((chapter) => chapter.id === activeChapterId.value)) {
    questionForm.chapter = activeChapterId.value
    return
  }
  const nextChapter = chapterList.value.find((chapter) => !isChapterCompleted(chapter)) || chapterList.value[0]
  activeChapterId.value = nextChapter?.id || null
}

function selectChapter(chapter) {
  activeChapterId.value = chapter.id
}

function isChapterCompleted(chapter) {
  return completedChapterIds.value.has(chapter.id)
}

function isVideoFinished(chapter) {
  return videoFinishedIds.value.has(chapter.id)
}

function markVideoFinished(chapter) {
  videoFinishedIds.value = new Set([...videoFinishedIds.value, chapter.id])
}

function canCompleteChapter(chapter) {
  if (!chapter || isChapterCompleted(chapter)) return false
  return !chapter.video || isVideoFinished(chapter)
}

function completeButtonText(chapter) {
  if (isChapterCompleted(chapter)) return '本章已完成'
  if (chapter.video && !isVideoFinished(chapter)) return '看完视频后可完成'
  return '标记本章完成'
}

function chapterStatusText(chapter) {
  if (isChapterCompleted(chapter)) return '已完成'
  if (chapter.id === activeChapterId.value) return '正在学习'
  return chapter.video ? '待观看' : '待完成'
}

function chapterNodeClass(chapter) {
  return {
    active: chapter.id === activeChapterId.value,
    completed: isChapterCompleted(chapter),
    pending: !isChapterCompleted(chapter),
  }
}

async function completeChapter(chapter) {
  if (!canCompleteChapter(chapter)) return
  await http.post(`/courses/${course.value.id}/complete_chapter/`, {
    chapter: chapter.id,
    watched_seconds: chapter.video ? chapter.duration_seconds || 1 : 0,
  })
  ElMessage.success('学习进度已更新')
  await load()
  selectNextIncompleteChapter(chapter)
}

async function createQuestion() {
  if (!questionForm.title.trim() || !questionForm.content.trim()) {
    ElMessage.warning('请填写问题标题和描述')
    return
  }
  await http.post('/course-questions/', {
    course: course.value.id,
    chapter: questionForm.chapter || null,
    title: questionForm.title.trim(),
    content: questionForm.content.trim(),
  })
  ElMessage.success('问题已提交')
  questionForm.title = ''
  questionForm.content = ''
  questionForm.chapter = activeChapterId.value || ''
  await load()
}

async function resolveQuestion(question) {
  await http.post(`/course-questions/${question.id}/resolve/`)
  ElMessage.success('已标记为已解决')
  await load()
}

function statusLabel(status) {
  return { pending: '待回复', answered: '已回复', resolved: '已解决' }[status] || status
}

function statusTagType(status) {
  return { pending: 'warning', answered: 'primary', resolved: 'success' }[status] || 'info'
}

function selectNextIncompleteChapter(completedChapter) {
  const currentIndex = chapterList.value.findIndex((chapter) => chapter.id === completedChapter.id)
  const nextChapter =
    chapterList.value.slice(currentIndex + 1).find((chapter) => !isChapterCompleted(chapter))
    || chapterList.value.find((chapter) => !isChapterCompleted(chapter))
    || completedChapter
  activeChapterId.value = nextChapter.id
}

onMounted(load)
</script>

<style scoped>
.learning-page {
  display: grid;
  gap: 18px;
}

.learning-hero,
.chapter-tree-panel,
.chapter-stage-card,
.support-card {
  border: 1px solid rgba(125, 211, 252, 0.42);
  border-radius: 28px;
  background: #fff;
  box-shadow: 0 18px 48px rgba(15, 63, 87, 0.08);
}

.learning-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
  background:
    radial-gradient(circle at 12% 20%, rgba(34, 197, 94, 0.14), transparent 28%),
    radial-gradient(circle at 90% 72%, rgba(14, 165, 233, 0.16), transparent 30%),
    #fff;
}

.learning-hero h2,
.tree-progress-card h3,
.stage-head h3,
.support-head h3 {
  margin: 6px 0;
  color: #0f3f57;
}

.eyebrow {
  color: #0f766e;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 1px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hero-progress {
  display: grid;
  place-items: center;
  width: 94px;
  height: 94px;
  color: #fff;
  background: conic-gradient(#0f766e var(--progress, 68%), #e0f2fe 0);
  border-radius: 999px;
  box-shadow: 0 16px 32px rgba(15, 118, 110, 0.18);
}

.hero-progress b {
  font-size: 24px;
}

.hero-progress span {
  margin-top: -18px;
  font-size: 12px;
  font-weight: 800;
}

.community-button,
.complete-button,
.submit-question-button,
.exam-button {
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: linear-gradient(135deg, #10b981, #075985);
  font-weight: 900;
}

.learning-layout {
  display: grid;
  grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.chapter-tree-panel {
  position: sticky;
  top: 88px;
  padding: 18px;
}

.tree-progress-card {
  padding: 16px;
  border-radius: 22px;
  background:
    radial-gradient(circle at 12% 18%, rgba(255, 255, 255, 0.7), transparent 28%),
    linear-gradient(135deg, #ecfeff, #dcfce7);
}

.chapter-tree {
  display: grid;
  justify-items: start;
  margin-top: 18px;
  padding-left: 8px;
}

.chapter-leaf-node {
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 0;
  border: 0;
  color: #3b7188;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.leaf-shape {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 42px;
  color: #0f766e;
  background: linear-gradient(135deg, #ccfbf1, #e0f2fe);
  border: 2px solid rgba(15, 118, 110, 0.14);
  border-radius: 70% 8px 70% 10px;
  transform: rotate(-12deg);
  box-shadow: 0 10px 20px rgba(15, 118, 110, 0.1);
}

.leaf-shape b {
  position: relative;
  z-index: 1;
  transform: rotate(12deg);
}

.leaf-vein {
  position: absolute;
  width: 34px;
  height: 2px;
  background: rgba(15, 118, 110, 0.34);
  transform: rotate(-28deg);
}

.chapter-leaf-node.completed .leaf-shape {
  color: #fff;
  background: linear-gradient(135deg, #22c55e, #047857);
}

.chapter-leaf-node.active .leaf-shape {
  color: #fff;
  background: linear-gradient(135deg, #14b8a6, #0f3f57);
  box-shadow: 0 14px 30px rgba(15, 63, 87, 0.18);
}

.chapter-node-text {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.chapter-node-text strong {
  color: #0f3f57;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-node-text small {
  color: #64748b;
  font-weight: 800;
}

.tree-trunk {
  width: 9px;
  height: 28px;
  margin: 2px 0 2px 21px;
  border-radius: 999px;
  background: linear-gradient(#b45309, #0f766e);
  opacity: 0.32;
}

.tree-trunk.completed {
  opacity: 0.85;
  background: linear-gradient(#16a34a, #0f766e);
}

.learning-stage {
  display: grid;
  gap: 18px;
}

.chapter-stage-card,
.support-card {
  padding: 22px;
}

.stage-head,
.support-head,
.question-item-head,
.question-footer,
.stage-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.stage-head {
  align-items: flex-start;
  margin-bottom: 16px;
}

.stage-head p {
  max-width: 760px;
  color: #475569;
  line-height: 1.8;
}

.video-shell {
  overflow: hidden;
  border-radius: 22px;
  background: #020617;
}

.video {
  display: block;
  width: 100%;
  max-height: 520px;
  background: #000;
}

.video-hint {
  margin: 0;
  padding: 12px 16px;
  color: #dbeafe;
  font-weight: 800;
}

.no-video-card {
  padding: 28px;
  border: 1px dashed #7dd3fc;
  border-radius: 22px;
  color: #0f3f57;
  background:
    radial-gradient(circle at 18% 20%, rgba(255, 255, 255, 0.7), transparent 28%),
    linear-gradient(135deg, #ecfeff, #f0fdf4);
}

.stage-actions {
  justify-content: flex-start;
  margin-top: 18px;
}

.complete-button.is-disabled {
  color: #64748b;
  background: #e2e8f0;
}

.learning-support-grid {
  display: grid;
  grid-template-columns: minmax(240px, 0.8fr) minmax(320px, 1.2fr);
  gap: 18px;
}

.exam-card {
  align-content: start;
  display: grid;
  gap: 12px;
}

.exam-button {
  justify-content: flex-start;
  min-height: 40px;
}

.question-form {
  margin: 12px 0 16px;
}

.question-list {
  display: grid;
  gap: 12px;
}

.question-item {
  padding: 14px;
  border: 1px solid #e0f2fe;
  border-radius: 18px;
  background: #f8fafc;
}

.question-item p {
  color: #475569;
  line-height: 1.7;
}

.answer-box {
  padding: 10px 12px;
  border-left: 4px solid #0ea5e9;
  background: #f0f9ff;
  margin: 8px 0;
}

@media (max-width: 980px) {
  .learning-hero,
  .hero-actions,
  .stage-head,
  .support-head,
  .question-item-head,
  .question-footer {
    align-items: flex-start;
    flex-direction: column;
  }

  .learning-layout,
  .learning-support-grid {
    grid-template-columns: 1fr;
  }

  .chapter-tree-panel {
    position: static;
  }

  .chapter-tree {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .chapter-leaf-node {
    width: 210px;
    flex: 0 0 210px;
  }

  .tree-trunk {
    width: 28px;
    height: 8px;
    flex: 0 0 28px;
    margin: 18px 0 0;
  }
}
</style>
