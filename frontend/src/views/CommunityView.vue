<template>
  <div class="page">
    <div class="toolbar">
      <h2>社区中心</h2>
      <div>
        <el-button @click="loadAll">刷新</el-button>
        <el-button type="primary" @click="postVisible = true">发布交流帖</el-button>
        <el-button type="primary" plain @click="resourceVisible = true">分享资料</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="学习交流" name="posts">
        <el-card class="block">
          <template #header>
            <div class="toolbar">
              <span>交流帖子</span>
              <el-select v-model="selectedPostCategory" clearable placeholder="全部分类" style="width: 180px" @change="loadPosts">
                <el-option v-for="category in postCategories" :key="category" :label="category" :value="category" />
              </el-select>
            </div>
          </template>
          <el-card v-for="post in posts" :key="post.id" class="block" shadow="never">
            <template #header>
              <div class="toolbar">
                <div>
                  <b>{{ post.title }}</b>
                  <span class="muted" style="margin-left: 8px">{{ post.author_name }} · {{ post.created_at }}</span>
                </div>
                <el-tag size="small">{{ post.category }}</el-tag>
              </div>
            </template>
            <p>{{ post.content }}</p>
            <div class="toolbar">
              <div>
                <el-button size="small" :type="post.liked_by_me ? 'primary' : 'default'" @click="togglePostLike(post)">
                  点赞 {{ post.likes_count || 0 }}
                </el-button>
                <el-button size="small" :type="post.favorited_by_me ? 'warning' : 'default'" @click="togglePostFavorite(post)">
                  收藏 {{ post.favorites_count || 0 }}
                </el-button>
                <el-button size="small" @click="openReplies(post)">查看/回复 {{ post.replies_count || 0 }}</el-button>
              </div>
              <el-button v-if="canDeletePost(post)" size="small" type="danger" plain @click="deletePost(post)">删除</el-button>
            </div>
          </el-card>
          <el-empty v-if="posts.length === 0" description="暂无社区帖子" />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="资料分享" name="resources">
        <el-card class="block">
          <template #header>
            <div class="toolbar">
              <span>资料列表</span>
              <div>
                <el-input v-model="resourceKeyword" clearable placeholder="搜索资料" style="width: 220px; margin-right: 8px" @clear="loadResources" @keyup.enter="loadResources" />
                <el-button size="small" @click="loadResources">搜索</el-button>
              </div>
            </div>
          </template>
          <el-card v-for="resource in resources" :key="resource.id" class="block" shadow="never">
            <template #header>
              <div class="toolbar">
                <div>
                  <b>{{ resource.title }}</b>
                  <span class="muted" style="margin-left: 8px">{{ resource.publisher_name }} · {{ resource.created_at }}</span>
                </div>
                <el-tag size="small">{{ resource.category }}</el-tag>
              </div>
            </template>
            <p>{{ resource.summary || '暂无简介' }}</p>
            <div class="toolbar">
              <div>
                <el-link v-if="resource.url" :href="resource.url" target="_blank" type="primary">打开网页</el-link>
                <el-link v-if="resource.attachment" :href="resource.attachment" target="_blank" type="success" download>下载附件</el-link>
                <el-button size="small" :type="resource.favorited_by_me ? 'warning' : 'default'" @click="toggleResourceFavorite(resource)">
                  收藏 {{ resource.favorites_count || 0 }}
                </el-button>
              </div>
              <el-button v-if="canDeleteResource(resource)" size="small" type="danger" plain @click="deleteResource(resource)">删除</el-button>
            </div>
          </el-card>
          <el-empty v-if="resources.length === 0" description="暂无资料分享" />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="我的收藏" name="favorites">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-card class="block">
              <template #header>收藏的交流帖</template>
              <div v-for="post in favoritePosts" :key="post.id" class="mine-item">
                <div>
                  <b>{{ post.title }}</b>
                  <p class="muted">{{ post.author_name }}</p>
                </div>
                <el-button size="small" @click="openReplies(post)">查看</el-button>
              </div>
              <el-empty v-if="favoritePosts.length === 0" description="暂无收藏交流帖" />
            </el-card>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-card class="block">
              <template #header>收藏的资料</template>
              <div v-for="resource in favoriteResources" :key="resource.id" class="mine-item">
                <div>
                  <b>{{ resource.title }}</b>
                  <p class="muted">{{ resource.publisher_name }}</p>
                </div>
                <el-link v-if="resource.url" :href="resource.url" target="_blank" type="primary">打开</el-link>
              </div>
              <el-empty v-if="favoriteResources.length === 0" description="暂无收藏资料" />
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="我的发布" name="mine">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-card class="block">
              <template #header>我的交流帖</template>
              <div v-for="post in myPosts" :key="post.id" class="mine-item">
                <span>{{ post.title }}</span>
                <el-button size="small" type="danger" plain @click="deletePost(post)">删除</el-button>
              </div>
              <el-empty v-if="myPosts.length === 0" description="你还没有发布交流帖" />
            </el-card>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-card class="block">
              <template #header>我的资料分享</template>
              <div v-for="resource in myResources" :key="resource.id" class="mine-item">
                <span>{{ resource.title }}</span>
                <el-button size="small" type="danger" plain @click="deleteResource(resource)">删除</el-button>
              </div>
              <el-empty v-if="myResources.length === 0" description="你还没有分享学习资料" />
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="postVisible" title="发布交流帖" width="520px">
      <el-form :model="postForm" label-position="top">
        <el-form-item label="标题"><el-input v-model="postForm.title" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="postForm.category">
            <el-option v-for="category in postCategories" :key="category" :label="category" :value="category" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="postForm.content" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="配图"><input type="file" accept="image/*" @change="postImage = $event.target.files[0]" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="postVisible = false">取消</el-button>
        <el-button type="primary" @click="createPost">发布</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resourceVisible" title="分享资料" width="520px">
      <el-form :model="resourceForm" label-position="top">
        <el-form-item label="标题"><el-input v-model="resourceForm.title" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="resourceForm.category" /></el-form-item>
        <el-form-item label="网页地址"><el-input v-model="resourceForm.url" placeholder="可选" /></el-form-item>
        <el-form-item label="附件"><input type="file" accept=".pdf,.doc,.docx,.ppt,.pptx,.zip" @change="resourceAttachment = $event.target.files[0]" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="resourceForm.summary" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="封面"><input type="file" accept="image/*" @change="resourceCover = $event.target.files[0]" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resourceVisible = false">取消</el-button>
        <el-button type="primary" @click="createResource">发布</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="replyVisible" title="帖子回复" width="640px">
      <div v-for="reply in replies" :key="reply.id" class="reply">
        <div class="toolbar">
          <b>{{ reply.author_name }}</b>
          <el-button v-if="canDeleteReply(reply)" size="small" type="danger" text @click="deleteReply(reply)">删除</el-button>
        </div>
        <p>{{ reply.content }}</p>
      </div>
      <el-input v-model="replyContent" type="textarea" :rows="3" placeholder="输入回复内容" />
      <template #footer>
        <el-button @click="replyVisible = false">关闭</el-button>
        <el-button type="primary" @click="createReply">回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const activeTab = ref('posts')
const posts = ref([])
const resources = ref([])
const myPosts = ref([])
const myResources = ref([])
const favoritePosts = ref([])
const favoriteResources = ref([])
const replies = ref([])
const currentPost = ref(null)
const postVisible = ref(false)
const resourceVisible = ref(false)
const replyVisible = ref(false)
const replyContent = ref('')
const postImage = ref(null)
const resourceCover = ref(null)
const resourceAttachment = ref(null)
const resourceKeyword = ref('')
const selectedPostCategory = ref('')
const postCategories = ref(['学习方法', '课程讨论', '考试交流', '资料推荐', '证书答疑', '项目实践', '问题求助', '经验分享', '其他'])
const postForm = reactive({ title: '', category: '学习方法', content: '' })
const resourceForm = reactive({ title: '', category: '学习资料', url: '', summary: '' })

function normalizeList(data) {
  return data?.results || data || []
}

function canDeletePost(post) {
  return auth.role === 'admin' || post.author === auth.user?.id
}

function canDeleteResource(resource) {
  return auth.role === 'admin' || resource.publisher === auth.user?.id
}

function canDeleteReply(reply) {
  return auth.role === 'admin' || reply.author === auth.user?.id
}

async function loadPostCategories() {
  try {
    const { data } = await http.get('/community/posts/categories/')
    postCategories.value = data
    if (!postCategories.value.includes(postForm.category)) {
      postForm.category = postCategories.value[0] || '学习方法'
    }
  } catch {
    postCategories.value = [...postCategories.value]
  }
}

async function loadPosts() {
  const params = {}
  if (selectedPostCategory.value) params.category = selectedPostCategory.value
  const { data } = await http.get('/community/posts/', { params })
  posts.value = normalizeList(data)
}

async function loadResources() {
  const params = {}
  if (resourceKeyword.value.trim()) params.search = resourceKeyword.value.trim()
  const { data } = await http.get('/community/resources/', { params })
  resources.value = normalizeList(data)
}

async function loadMine() {
  const [postRes, resourceRes] = await Promise.all([
    http.get('/community/posts/', { params: { mine: true } }),
    http.get('/community/resources/', { params: { mine: true } })
  ])
  myPosts.value = normalizeList(postRes.data)
  myResources.value = normalizeList(resourceRes.data)
}

async function loadFavorites() {
  const [postRes, resourceRes] = await Promise.all([
    http.get('/community/posts/favorites/'),
    http.get('/community/resources/favorites/')
  ])
  favoritePosts.value = normalizeList(postRes.data)
  favoriteResources.value = normalizeList(resourceRes.data)
}

async function loadAll() {
  await Promise.all([loadPostCategories(), loadPosts(), loadResources(), loadMine(), loadFavorites()])
}

async function createPost() {
  if (!postForm.title.trim() || !postForm.content.trim()) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  const formData = new FormData()
  formData.append('title', postForm.title.trim())
  formData.append('category', postForm.category)
  formData.append('content', postForm.content.trim())
  if (postImage.value) formData.append('image', postImage.value)
  await http.post('/community/posts/', formData)
  postForm.title = ''
  postForm.content = ''
  postImage.value = null
  postVisible.value = false
  ElMessage.success('帖子已发布')
  await loadAll()
}

async function createResource() {
  const rawUrl = resourceForm.url.trim()
  if (!resourceForm.title.trim()) {
    ElMessage.warning('请填写资料标题')
    return
  }
  if (!rawUrl && !resourceAttachment.value) {
    ElMessage.warning('网页地址和附件至少填写一个')
    return
  }
  const formData = new FormData()
  formData.append('title', resourceForm.title.trim())
  formData.append('category', resourceForm.category.trim() || '学习资料')
  formData.append('summary', resourceForm.summary.trim())
  if (rawUrl) formData.append('url', /^https?:\/\//i.test(rawUrl) ? rawUrl : `https://${rawUrl}`)
  if (resourceAttachment.value) formData.append('attachment', resourceAttachment.value)
  if (resourceCover.value) formData.append('cover', resourceCover.value)
  await http.post('/community/resources/', formData)
  Object.assign(resourceForm, { title: '', category: '学习资料', url: '', summary: '' })
  resourceAttachment.value = null
  resourceCover.value = null
  resourceVisible.value = false
  ElMessage.success('资料已分享')
  await loadAll()
}

async function togglePostLike(post) {
  const { data } = await http.post(`/community/posts/${post.id}/toggle_like/`)
  post.liked_by_me = data.liked
  post.likes_count = data.likes_count
}

async function togglePostFavorite(post) {
  const { data } = await http.post(`/community/posts/${post.id}/toggle_favorite/`)
  post.favorited_by_me = data.favorited
  post.favorites_count = data.favorites_count
  await loadFavorites()
}

async function toggleResourceFavorite(resource) {
  const { data } = await http.post(`/community/resources/${resource.id}/toggle_favorite/`)
  resource.favorited_by_me = data.favorited
  resource.favorites_count = data.favorites_count
  await loadFavorites()
}

async function deletePost(post) {
  await ElMessageBox.confirm(`确定删除“${post.title}”吗？`, '删除确认', { type: 'warning' })
  await http.delete(`/community/posts/${post.id}/`)
  ElMessage.success('帖子已删除')
  await loadAll()
}

async function deleteResource(resource) {
  await ElMessageBox.confirm(`确定删除“${resource.title}”吗？`, '删除确认', { type: 'warning' })
  await http.delete(`/community/resources/${resource.id}/`)
  ElMessage.success('资料已删除')
  await loadAll()
}

async function openReplies(post) {
  currentPost.value = post
  const { data } = await http.get(`/community/posts/${post.id}/replies/`)
  replies.value = normalizeList(data)
  replyVisible.value = true
}

async function createReply() {
  const content = replyContent.value.trim()
  if (!content) {
    ElMessage.warning('请输入回复内容')
    return
  }
  await http.post('/community/replies/', { post: currentPost.value.id, content })
  replyContent.value = ''
  ElMessage.success('回复已发布')
  await openReplies(currentPost.value)
  await loadAll()
}

async function deleteReply(reply) {
  await http.delete(`/community/replies/${reply.id}/`)
  ElMessage.success('回复已删除')
  await openReplies(currentPost.value)
  await loadAll()
}

watch(activeTab, async (tab) => {
  if (tab === 'favorites') await loadFavorites()
  if (tab === 'mine') await loadMine()
})

onMounted(loadAll)
</script>

<style scoped>
.block {
  margin-bottom: 12px;
}

.mine-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #e5e7eb;
}

.mine-item:last-child {
  border-bottom: none;
}

.reply {
  padding: 10px 0;
  border-bottom: 1px solid #e5e7eb;
}
</style>
