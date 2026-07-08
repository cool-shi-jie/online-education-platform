<template>
  <div class="page">
    <div class="toolbar">
      <h2>课程论坛</h2>
      <el-button type="primary" @click="postVisible = true">发布帖子</el-button>
    </div>
    <el-card v-for="post in posts" :key="post.id" style="margin-bottom: 12px">
      <template #header>
        <div class="toolbar">
          <span>{{ post.title }}</span>
          <span class="muted">{{ post.author_name }} · {{ post.created_at }}</span>
        </div>
      </template>
      <p>{{ post.content }}</p>
      <el-button size="small" @click="openReplies(post)">查看/回复</el-button>
    </el-card>
    <el-empty v-if="posts.length === 0" description="暂无帖子" />

    <el-dialog v-model="postVisible" title="发布帖子" width="520px">
      <el-form :model="postForm" label-position="top">
        <el-form-item label="标题"><el-input v-model="postForm.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="postForm.content" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="postVisible = false">取消</el-button>
        <el-button type="primary" @click="createPost">发布</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="replyVisible" title="帖子回复" width="640px">
      <div v-for="reply in replies" :key="reply.id" class="reply">
        <b>{{ reply.author_name }}</b>
        <p>{{ reply.content }}</p>
      </div>
      <el-input v-model="replyContent" type="textarea" placeholder="输入回复内容" />
      <template #footer>
        <el-button @click="replyVisible = false">关闭</el-button>
        <el-button type="primary" @click="createReply">回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const route = useRoute()
const posts = ref([])
const replies = ref([])
const currentPost = ref(null)
const postVisible = ref(false)
const replyVisible = ref(false)
const replyContent = ref('')
const postForm = reactive({ title: '', content: '' })

async function load() {
  const { data } = await http.get('/forum/posts/', { params: { course: route.params.courseId } })
  posts.value = data.results || data
}

async function createPost() {
  await http.post('/forum/posts/', { ...postForm, course: route.params.courseId })
  ElMessage.success('帖子已发布')
  postVisible.value = false
  postForm.title = ''
  postForm.content = ''
  await load()
}

async function openReplies(post) {
  currentPost.value = post
  const { data } = await http.get(`/forum/posts/${post.id}/replies/`)
  replies.value = data.results || data
  replyVisible.value = true
}

async function createReply() {
  await http.post('/forum/replies/', { post: currentPost.value.id, content: replyContent.value })
  ElMessage.success('回复已发布')
  replyContent.value = ''
  await openReplies(currentPost.value)
}

onMounted(load)
</script>

<style scoped>
.reply {
  padding: 10px 0;
  border-bottom: 1px solid #e5e7eb;
}
</style>
