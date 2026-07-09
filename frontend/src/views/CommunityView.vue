<template>
  <div class="page community-page">
    <section class="community-hero">
      <div>
        <h2>社区中心</h2>
        <p class="muted">交流学习经验，收藏优质资料，沉淀你的学习资源。</p>
      </div>
      <div class="hero-actions">
        <el-button @click="loadAll">刷新</el-button>
      </div>
    </section>

    <nav class="community-section-nav" aria-label="社区分区">
      <div class="section-panel">
        <div class="panel-title">
          <span>社区树</span>
          <b>{{ activeSection?.label }}</b>
        </div>
        <div class="section-tree">
          <template v-for="(section, index) in communitySections" :key="section.name">
            <button class="section-node" :class="{ active: activeTab === section.name }" type="button" @click="activeTab = section.name">
              <span class="section-dot">{{ index + 1 }}</span>
              <span>{{ section.label }}</span>
            </button>
            <span v-if="index < communitySections.length - 1" class="section-connector" :class="{ active: isSectionConnectorActive(index) }"></span>
          </template>
        </div>
      </div>
    </nav>

    <section class="community-layout">
      <main class="community-content">
        <div v-if="activeTab === 'posts'" class="content-section">
          <div class="inner-layout">
            <aside class="inner-category-panel">
              <div class="panel-title">
                <span>交流分类</span>
                <b>{{ activePostCategoryLabel }}</b>
              </div>
              <div class="inner-category-tree">
                <template v-for="(category, index) in postCategoryNodes" :key="category.value || 'all-posts'">
                  <button class="inner-category-node" :class="{ active: selectedPostCategory === category.value }" type="button" @click="selectPostCategory(category.value)">
                    <span class="inner-category-dot">{{ index + 1 }}</span>
                    <span>{{ category.label }}</span>
                  </button>
                  <span v-if="index < postCategoryNodes.length - 1" class="inner-category-connector" :class="{ active: isPostCategoryConnectorActive(index) }"></span>
                </template>
              </div>
            </aside>

            <div class="inner-card-column">
              <div class="content-tools">
                <div>
                  <h3>学习交流</h3>
                  <p class="muted">当前显示 {{ posts.length }} 条交流帖</p>
                </div>
                <div class="tool-actions">
                  <el-button class="publish-button" type="primary" @click="postVisible = true">发布交流帖</el-button>
                </div>
              </div>
              <div class="post-grid">
                <el-card v-for="post in posts" :key="post.id" class="post-card" shadow="hover">
                  <div class="card-title-block">
                    <el-tag size="small" effect="plain">{{ post.category }}</el-tag>
                    <h3>{{ post.title }}</h3>
                    <p>{{ post.author_name }} · {{ post.created_at }}</p>
                  </div>
                  <p class="card-summary">{{ post.content }}</p>
                  <div class="card-actions">
                    <div class="action-group">
                      <el-button class="emoji-action" :class="{ active: post.liked_by_me }" size="small" @click="togglePostLike(post)">👍 {{ post.likes_count || 0 }}</el-button>
                      <el-button class="emoji-action star-action" :class="{ active: post.favorited_by_me }" size="small" @click="togglePostFavorite(post)">{{ postFavoriteIcon(post) }} {{ post.favorites_count || 0 }}</el-button>
                      <el-button class="emoji-action" size="small" @click="openReplies(post)">💬 {{ post.replies_count || 0 }}</el-button>
                    </div>
                    <el-button v-if="canDeletePost(post)" size="small" type="danger" plain @click="deletePost(post)">删除</el-button>
                  </div>
                </el-card>
              </div>
              <el-empty v-if="posts.length === 0" description="暂无社区帖子" />
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'resources'" class="content-section">
          <div class="inner-layout">
            <aside class="inner-category-panel">
              <div class="panel-title">
                <span>资料分类</span>
                <b>{{ activeResourceCategoryLabel }}</b>
              </div>
              <div class="inner-category-tree">
                <template v-for="(category, index) in resourceCategoryNodes" :key="category.value || 'all-resources'">
                  <button class="inner-category-node" :class="{ active: selectedResourceCategory === category.value }" type="button" @click="selectResourceCategory(category.value)">
                    <span class="inner-category-dot">{{ index + 1 }}</span>
                    <span>{{ category.label }}</span>
                  </button>
                  <span v-if="index < resourceCategoryNodes.length - 1" class="inner-category-connector" :class="{ active: isResourceCategoryConnectorActive(index) }"></span>
                </template>
              </div>
            </aside>

            <div class="inner-card-column">
              <div class="content-tools">
                <div>
                  <h3>资料分享</h3>
                  <p class="muted">当前显示 {{ visibleResources.length }} 条资料</p>
                </div>
                <div class="resource-search">
                  <el-input v-model="resourceKeyword" clearable placeholder="搜索资料" @clear="loadResources" @keyup.enter="loadResources" />
                  <el-button @click="loadResources">搜索</el-button>
                  <el-button class="publish-button" type="primary" @click="resourceVisible = true">分享资料</el-button>
                </div>
              </div>
              <div class="resource-grid">
                <el-card v-for="resource in visibleResources" :key="resource.id" class="resource-card" shadow="hover">
                  <div class="resource-preview">
                    <img v-if="resourcePreviewImage(resource)" :class="{ 'site-logo-preview': isSiteIconPreview(resource) }" :src="resourcePreviewImage(resource)" :alt="resource.title" @error="markPreviewFailed(resource)" />
                    <div v-else class="resource-preview-placeholder" :class="{ 'file-resource': isAttachmentOnlyResource(resource) }">
                      <span>{{ resourceFileType(resource) }}</span>
                      <b>{{ isAttachmentOnlyResource(resource) ? '文件资料' : '学习资料' }}</b>
                    </div>
                    <span class="resource-preview-label">{{ resourcePreviewLabel(resource) }}</span>
                  </div>
                  <div class="card-title-block resource-title-block resource-title-block--with-preview">
                    <el-tag size="small" effect="plain">{{ resource.category }}</el-tag>
                    <h3>{{ resource.title }}</h3>
                    <p>{{ resource.publisher_name }} · {{ resource.created_at }}</p>
                  </div>
                  <p class="card-summary">{{ resource.summary || '暂无简介' }}</p>
                  <div class="card-actions">
                    <div class="action-group">
                      <el-link v-if="resource.url" class="go-action" :href="resource.url" target="_blank">GO</el-link>
                      <el-link v-if="resource.attachment" class="download-action" :href="resource.attachment" target="_blank" download>下载</el-link>
                      <el-button class="emoji-action star-action" :class="{ active: resource.favorited_by_me }" size="small" @click="toggleResourceFavorite(resource)">{{ resourceFavoriteIcon(resource) }} {{ resource.favorites_count || 0 }}</el-button>
                    </div>
                    <el-button v-if="canDeleteResource(resource)" size="small" type="danger" plain @click="deleteResource(resource)">删除</el-button>
                  </div>
                </el-card>
              </div>
              <el-empty v-if="visibleResources.length === 0" description="暂无资料分享" />
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'favorites'" class="content-section">
          <div class="content-tools">
            <div>
              <h3>我的收藏</h3>
              <p class="muted">集中查看收藏的帖子和资料</p>
            </div>
          </div>
          <div class="cabinet-grid">
            <section class="cabinet-card">
              <div class="cabinet-head">
                <div>
                  <h4>收藏的交流帖</h4>
                  <p class="muted">{{ favoritePosts.length }} 条内容</p>
                </div>
                <span class="cabinet-count">{{ favoritePosts.length }}</span>
              </div>
              <p v-if="favoritePosts.length === 0" class="compact-empty">暂无收藏交流帖</p>
              <div v-for="group in favoritePostGroups" :key="group.key" class="timeline-group">
                <div class="timeline-label">{{ group.label }}</div>
                <article v-for="post in group.items" :key="post.id" class="timeline-card">
                  <div>
                    <b>{{ post.title }}</b>
                    <p class="muted">{{ post.author_name }} · {{ post.created_at }}</p>
                  </div>
                  <el-button class="emoji-action" size="small" @click="openReplies(post)">💬 查看</el-button>
                </article>
              </div>
            </section>

            <section class="cabinet-card">
              <div class="cabinet-head">
                <div>
                  <h4>收藏的资料</h4>
                  <p class="muted">{{ favoriteResources.length }} 条内容</p>
                </div>
                <span class="cabinet-count">{{ favoriteResources.length }}</span>
              </div>
              <p v-if="favoriteResources.length === 0" class="compact-empty">暂无收藏资料</p>
              <div v-for="group in favoriteResourceGroups" :key="group.key" class="timeline-group">
                <div class="timeline-label">{{ group.label }}</div>
                <article v-for="resource in group.items" :key="resource.id" class="timeline-card resource-timeline-card">
                  <div class="timeline-resource-preview">
                    <img v-if="resourcePreviewImage(resource)" :class="{ 'site-logo-preview': isSiteIconPreview(resource) }" :src="resourcePreviewImage(resource)" :alt="resource.title" @error="markPreviewFailed(resource)" />
                    <span v-else>{{ resourceFileType(resource) }}</span>
                  </div>
                  <div class="timeline-resource-body">
                    <b>{{ resource.title }}</b>
                    <p class="muted">{{ resource.publisher_name }} · {{ resource.created_at }}</p>
                    <span class="resource-mini-label">{{ resourcePreviewLabel(resource) }}</span>
                  </div>
                  <div class="timeline-resource-actions">
                    <el-link v-if="resource.url" class="go-action" :href="resource.url" target="_blank">GO</el-link>
                    <el-link v-if="resource.attachment" class="download-action" :href="resource.attachment" target="_blank" download>下载</el-link>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </div>

        <div v-else-if="activeTab === 'mine'" class="content-section">
          <div class="content-tools">
            <div>
              <h3>我的发布</h3>
              <p class="muted">管理我发布的交流帖和资料</p>
            </div>
          </div>
          <div class="cabinet-grid">
            <section class="cabinet-card">
              <div class="cabinet-head">
                <div>
                  <h4>我的交流帖</h4>
                  <p class="muted">{{ myPosts.length }} 条内容</p>
                </div>
                <span class="cabinet-count">{{ myPosts.length }}</span>
              </div>
              <p v-if="myPosts.length === 0" class="compact-empty">你还没有发布交流帖</p>
              <div v-for="group in myPostGroups" :key="group.key" class="timeline-group">
                <div class="timeline-label">{{ group.label }}</div>
                <article v-for="post in group.items" :key="post.id" class="timeline-card">
                  <div>
                    <b>{{ post.title }}</b>
                    <p class="muted">{{ post.created_at }}</p>
                  </div>
                  <el-button class="danger-action" size="small" type="danger" plain @click="deletePost(post)">删除</el-button>
                </article>
              </div>
            </section>

            <section class="cabinet-card">
              <div class="cabinet-head">
                <div>
                  <h4>我的资料分享</h4>
                  <p class="muted">{{ myResources.length }} 条内容</p>
                </div>
                <span class="cabinet-count">{{ myResources.length }}</span>
              </div>
              <p v-if="myResources.length === 0" class="compact-empty">你还没有分享学习资料</p>
              <div v-for="group in myResourceGroups" :key="group.key" class="timeline-group">
                <div class="timeline-label">{{ group.label }}</div>
                <article v-for="resource in group.items" :key="resource.id" class="timeline-card resource-timeline-card">
                  <div class="timeline-resource-preview">
                    <img v-if="resourcePreviewImage(resource)" :class="{ 'site-logo-preview': isSiteIconPreview(resource) }" :src="resourcePreviewImage(resource)" :alt="resource.title" @error="markPreviewFailed(resource)" />
                    <span v-else>{{ resourceFileType(resource) }}</span>
                  </div>
                  <div class="timeline-resource-body">
                    <b>{{ resource.title }}</b>
                    <p class="muted">{{ resource.created_at }}</p>
                    <span class="resource-mini-label">{{ resourcePreviewLabel(resource) }}</span>
                  </div>
                  <div class="timeline-resource-actions">
                    <el-link v-if="resource.url" class="go-action" :href="resource.url" target="_blank">GO</el-link>
                    <el-link v-if="resource.attachment" class="download-action" :href="resource.attachment" target="_blank" download>下载</el-link>
                    <el-button class="danger-action" size="small" type="danger" plain @click="deleteResource(resource)">删除</el-button>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </div>
      </main>
    </section>

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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const activeTab = ref('posts')
const communitySections = [
  { name: 'posts', label: '学习交流' },
  { name: 'resources', label: '资料分享' },
  { name: 'favorites', label: '我的收藏' },
  { name: 'mine', label: '我的发布' }
]
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
const selectedResourceCategory = ref('')
const failedPreviewIds = ref(new Set())
const postCategories = ref(['学习方法', '课程讨论', '考试交流', '资料推荐', '证书答疑', '项目实践', '问题求助', '经验分享', '其他'])
const postForm = reactive({ title: '', category: '学习方法', content: '' })
const resourceForm = reactive({ title: '', category: '学习资料', url: '', summary: '' })

const activeSection = computed(() => communitySections.find((section) => section.name === activeTab.value))
const postCategoryNodes = computed(() => [{ label: '全部帖子', value: '' }, ...postCategories.value.map((category) => ({ label: category, value: category }))])
const activePostCategoryLabel = computed(() => selectedPostCategory.value || '全部帖子')
const resourceCategoryNodes = computed(() => {
  const categorySet = new Set(resources.value.map((resource) => resource.category).filter(Boolean))
  return [{ label: '全部资料', value: '' }, ...Array.from(categorySet).map((category) => ({ label: category, value: category }))]
})
const activeResourceCategoryLabel = computed(() => selectedResourceCategory.value || '全部资料')
const visibleResources = computed(() => {
  if (!selectedResourceCategory.value) return resources.value
  return resources.value.filter((resource) => resource.category === selectedResourceCategory.value)
})
const favoritePostGroups = computed(() => groupByTimeBucket(favoritePosts.value))
const favoriteResourceGroups = computed(() => groupByTimeBucket(favoriteResources.value))
const myPostGroups = computed(() => groupByTimeBucket(myPosts.value))
const myResourceGroups = computed(() => groupByTimeBucket(myResources.value))

function isSectionConnectorActive(index) {
  const activeIndex = communitySections.findIndex((section) => section.name === activeTab.value)
  return activeIndex > index
}

function isPostCategoryConnectorActive(index) {
  const activeIndex = postCategoryNodes.value.findIndex((category) => category.value === selectedPostCategory.value)
  return activeIndex > index
}

function isResourceCategoryConnectorActive(index) {
  const activeIndex = resourceCategoryNodes.value.findIndex((category) => category.value === selectedResourceCategory.value)
  return activeIndex > index
}

function selectPostCategory(category) {
  selectedPostCategory.value = category
  loadPosts()
}

function selectResourceCategory(category) {
  selectedResourceCategory.value = category
}

function resourcePreviewImage(resource) {
  if (failedPreviewIds.value.has(resource.id)) return ''
  return resource.cover || resource.preview_image_url || ''
}

function isSiteIconPreview(resource) {
  return !resource.cover && (resource.preview_image_url || '').includes('google.com/s2/favicons')
}

function resourcePreviewLabel(resource) {
  if (resource.preview_site_name) return resource.preview_site_name
  if (isAttachmentOnlyResource(resource)) return '附件资料'
  if (resource.url && resource.attachment) return '网页 + 附件'
  return resource.category || '学习资料'
}

function postFavoriteIcon(post) {
  return post.favorited_by_me ? '⭐' : '☆'
}

function resourceFavoriteIcon(resource) {
  return resource.favorited_by_me ? '⭐' : '☆'
}

function isAttachmentOnlyResource(resource) {
  return Boolean(resource.attachment && !resource.url)
}

function resourceFileType(resource) {
  const source = resource.attachment || resource.url || resource.title || ''
  const extension = String(source).split('?')[0].split('.').pop()?.toUpperCase()
  if (extension && extension.length <= 5 && extension !== String(source).toUpperCase()) return extension
  return resource.attachment ? 'FILE' : 'WEB'
}

function markPreviewFailed(resource) {
  failedPreviewIds.value = new Set([...failedPreviewIds.value, resource.id])
}

function groupByTimeBucket(items) {
  const groups = [
    { key: 'today', label: '今天', items: [] },
    { key: 'week', label: '本周', items: [] },
    { key: 'older', label: '更早', items: [] }
  ]
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const weekStart = todayStart - 6 * 24 * 60 * 60 * 1000

  items.forEach((item) => {
    const timestamp = Date.parse(item.created_at)
    if (Number.isNaN(timestamp)) {
      groups[2].items.push(item)
    } else if (timestamp >= todayStart) {
      groups[0].items.push(item)
    } else if (timestamp >= weekStart) {
      groups[1].items.push(item)
    } else {
      groups[2].items.push(item)
    }
  })

  return groups.filter((group) => group.items.length > 0)
}

function normalizeList(data) {
  return data?.results || data || []
}

async function fetchAllPages(url, params = {}) {
  const items = []
  let nextUrl = url
  let nextParams = { ...params }

  while (nextUrl) {
    const { data } = await http.get(nextUrl, { params: nextParams })
    items.push(...normalizeList(data))
    nextUrl = data?.next || ''
    nextParams = {}
  }

  return items
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
  posts.value = await fetchAllPages('/community/posts/', params)
}

async function loadResources() {
  const params = {}
  if (resourceKeyword.value.trim()) params.search = resourceKeyword.value.trim()
  resources.value = await fetchAllPages('/community/resources/', params)
  if (selectedResourceCategory.value && !resources.value.some((resource) => resource.category === selectedResourceCategory.value)) {
    selectedResourceCategory.value = ''
  }
}

async function loadMine() {
  const [postItems, resourceItems] = await Promise.all([
    fetchAllPages('/community/posts/', { mine: true }),
    fetchAllPages('/community/resources/', { mine: true })
  ])
  myPosts.value = postItems
  myResources.value = resourceItems
}

async function loadFavorites() {
  const [postItems, resourceItems] = await Promise.all([
    fetchAllPages('/community/posts/favorites/'),
    fetchAllPages('/community/resources/favorites/')
  ])
  favoritePosts.value = postItems
  favoriteResources.value = resourceItems
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
.community-page {
  display: grid;
  gap: 18px;
}

.community-hero {
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

.community-hero h2 {
  margin: 0 0 8px;
  color: #0f3f57;
  font-size: 30px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.community-layout {
  display: grid;
  gap: 18px;
  align-items: start;
}

.community-section-nav {
  overflow: hidden;
  padding: 16px;
  border: 1px solid #e0f2fe;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 16px 40px rgba(15, 63, 87, 0.07);
}

.section-panel {
  display: flex;
  align-items: center;
  gap: 16px;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 0;
  flex: 0 0 auto;
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

.section-tree {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  overflow-x: auto;
  padding-bottom: 2px;
}

.section-node {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  width: auto;
  flex: 0 0 auto;
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

.section-node:hover {
  color: #0f766e;
  border-color: #7dd3fc;
  transform: translateY(-1px);
}

.section-node.active {
  color: #fff;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  border-color: transparent;
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.2);
}

.section-dot {
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

.section-node.active .section-dot {
  background: rgba(255, 255, 255, 0.9);
}

.section-connector {
  width: 28px;
  height: 3px;
  flex: 0 0 auto;
  margin: 0 5px;
  background: linear-gradient(#bae6fd, #bbf7d0);
  border-radius: 999px;
}

.section-connector.active {
  background: linear-gradient(#0ea5e9, #0f766e);
}

.community-content,
.content-section {
  display: grid;
  gap: 16px;
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

.content-tools h3 {
  margin: 0 0 6px;
  color: #0f3f57;
}

.inner-layout {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.inner-card-column {
  display: grid;
  gap: 16px;
}

.inner-category-panel {
  position: sticky;
  top: 88px;
  padding: 18px;
  border: 1px solid #e0f2fe;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 16px 40px rgba(15, 63, 87, 0.07);
}

.inner-category-panel .panel-title {
  margin-bottom: 16px;
}

.inner-category-tree {
  display: grid;
  justify-items: start;
}

.inner-category-node {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
  padding: 9px 10px;
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

.inner-category-node:hover {
  color: #0f766e;
  border-color: #7dd3fc;
  transform: translateX(2px);
}

.inner-category-node.active {
  color: #fff;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  border-color: transparent;
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.2);
}

.inner-category-dot {
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

.inner-category-node.active .inner-category-dot {
  background: rgba(255, 255, 255, 0.9);
}

.inner-category-connector {
  width: 3px;
  height: 18px;
  margin-left: 22px;
  background: linear-gradient(#bae6fd, #bbf7d0);
  border-radius: 999px;
}

.inner-category-connector.active {
  width: 4px;
  background: linear-gradient(#0ea5e9, #0f766e);
}

.tool-control {
  width: 190px;
}

.tool-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.resource-search {
  display: flex;
  width: min(560px, 100%);
  gap: 8px;
}

.publish-button {
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.22);
  font-weight: 800;
}

.publish-button:hover {
  border: none;
  background: linear-gradient(135deg, #0284c7, #0d9488);
  box-shadow: 0 14px 28px rgba(14, 165, 233, 0.28);
  transform: translateY(-1px);
}

.post-grid,
.resource-grid,
.compact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.post-card,
.resource-card,
.mini-section-card {
  overflow: hidden;
  border-radius: 22px;
}

.resource-preview {
  position: relative;
  height: 168px;
  margin: -20px -20px 0;
  overflow: hidden;
  background: linear-gradient(135deg, #e0f7fa, #f0fdf4);
}

.resource-preview img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.resource-preview img.site-logo-preview {
  width: 104px;
  height: 104px;
  margin: 32px auto;
  padding: 18px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 28px;
  box-shadow: 0 14px 32px rgba(15, 118, 110, 0.16);
}

.resource-preview-placeholder {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 10px;
  height: 100%;
  color: #0f3f57;
  background:
    radial-gradient(circle at 18% 22%, rgba(255, 255, 255, 0.6), transparent 28%),
    linear-gradient(135deg, #dff7ff, #dcfce7);
}

.resource-preview-placeholder.file-resource {
  background:
    radial-gradient(circle at 18% 22%, rgba(255, 255, 255, 0.62), transparent 28%),
    linear-gradient(135deg, #ecfeff, #d1fae5);
}

.resource-preview-placeholder span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 72px;
  height: 42px;
  padding: 0 14px;
  color: #0f766e;
  background: rgba(255, 255, 255, 0.82);
  border-radius: 14px;
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 1px;
}

.resource-preview-placeholder b {
  font-size: 18px;
}

.resource-preview-label {
  position: absolute;
  left: 14px;
  bottom: 14px;
  max-width: calc(100% - 28px);
  padding: 5px 10px;
  color: #0f3f57;
  background: rgba(255, 255, 255, 0.86);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-title-block {
  min-height: 120px;
  padding: 18px;
  margin: -20px -20px 16px;
  background:
    radial-gradient(circle at 15% 18%, rgba(255, 255, 255, 0.62), transparent 26%),
    linear-gradient(135deg, #e0f7fa, #f0fdf4);
}

.resource-title-block {
  background:
    radial-gradient(circle at 15% 18%, rgba(255, 255, 255, 0.62), transparent 26%),
    linear-gradient(135deg, #ecfeff, #eef2ff);
}

.resource-title-block--with-preview {
  min-height: 112px;
  margin-top: 0;
}

.card-title-block h3 {
  margin: 14px 0 8px;
  color: #0f3f57;
  font-size: 20px;
  line-height: 1.35;
}

.card-title-block p {
  margin: 0;
  color: #3b7188;
  font-size: 12px;
  font-weight: 700;
}

.card-summary {
  min-height: 72px;
  color: #475569;
  line-height: 1.7;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
}

.action-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.emoji-action {
  min-width: 64px;
  height: 32px;
  margin-left: 0;
  color: #31566a;
  border-color: #dbeafe;
  border-radius: 999px;
  background: #f8fafc;
  font-weight: 900;
}

.emoji-action + .emoji-action {
  margin-left: 0;
}

.emoji-action:hover {
  color: #0f766e;
  border-color: #7dd3fc;
  background: #ecfeff;
}

.emoji-action.active {
  color: #fff;
  border-color: transparent;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  box-shadow: 0 10px 20px rgba(14, 165, 233, 0.18);
}

.star-action.active {
  background: linear-gradient(135deg, #f59e0b, #0f766e);
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.18);
}

.go-action,
.download-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 54px;
  height: 32px;
  padding: 0 13px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 1000;
  text-decoration: none;
}

.go-action {
  color: #fff;
  background: linear-gradient(135deg, #0ea5e9, #0f766e);
  box-shadow: 0 10px 20px rgba(14, 165, 233, 0.18);
  letter-spacing: 1px;
}

.download-action {
  color: #0f766e;
  background: #ecfeff;
  border: 1px solid #99f6e4;
}

.danger-action {
  min-width: 54px;
  height: 32px;
  margin-left: 0;
  border-radius: 999px;
  font-weight: 800;
}

.mini-card-grid {
  display: grid;
  gap: 10px;
}

.mini-card {
  display: grid;
  gap: 8px;
  padding: 14px;
  border: 1px solid #e0f2fe;
  border-radius: 16px;
  background: #f8fafc;
}

.cabinet-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
}

.cabinet-card {
  display: grid;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e0f2fe;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 14px 34px rgba(15, 63, 87, 0.06);
}

.cabinet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-radius: 18px;
  background: linear-gradient(135deg, #ecfeff, #f0fdf4);
}

.cabinet-head h4 {
  margin: 0 0 4px;
  color: #0f3f57;
  font-size: 16px;
}

.cabinet-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 38px;
  height: 38px;
  padding: 0 10px;
  color: #0f766e;
  background: rgba(255, 255, 255, 0.86);
  border-radius: 999px;
  font-weight: 900;
}

.timeline-group {
  display: grid;
  gap: 8px;
}

.timeline-label {
  width: fit-content;
  padding: 4px 10px;
  color: #0f766e;
  background: #ecfeff;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.timeline-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e5f3f6;
  border-radius: 16px;
  background: #f8fafc;
}

.timeline-card b {
  display: block;
  margin-bottom: 4px;
  color: #0f3f57;
}

.resource-timeline-card {
  align-items: stretch;
}

.timeline-resource-preview {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 74px;
  min-height: 74px;
  flex: 0 0 74px;
  overflow: hidden;
  color: #0f766e;
  background: linear-gradient(135deg, #ecfeff, #dcfce7);
  border-radius: 16px;
  font-size: 14px;
  font-weight: 900;
}

.timeline-resource-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.timeline-resource-preview img.site-logo-preview {
  width: 52px;
  height: 52px;
  padding: 9px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.88);
  border-radius: 14px;
}

.timeline-resource-body {
  min-width: 0;
  flex: 1;
}

.resource-mini-label {
  display: inline-flex;
  max-width: 100%;
  padding: 3px 8px;
  color: #0f766e;
  background: #ecfeff;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.timeline-resource-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
  flex: 0 0 auto;
}

.compact-empty {
  margin: 0;
  padding: 10px 12px;
  color: #64748b;
  background: #f8fafc;
  border: 1px dashed #bae6fd;
  border-radius: 14px;
  font-size: 13px;
}

.reply {
  padding: 10px 0;
  border-bottom: 1px solid #e5e7eb;
}

@media (max-width: 900px) {
  .community-hero,
  .content-tools {
    align-items: flex-start;
    flex-direction: column;
  }

  .inner-layout {
    grid-template-columns: 1fr;
  }

  .section-panel,
  .inner-category-panel {
    position: static;
  }

  .section-panel {
    align-items: flex-start;
    flex-direction: column;
  }

  .section-tree,
  .inner-category-tree {
    display: flex;
    overflow-x: auto;
    padding-bottom: 4px;
    width: 100%;
  }

  .section-node,
  .inner-category-node {
    width: auto;
    flex: 0 0 auto;
    white-space: nowrap;
  }

  .section-connector,
  .inner-category-connector {
    width: 24px;
    height: 3px;
    flex: 0 0 auto;
    margin: 19px 4px 0;
  }

  .resource-search {
    width: 100%;
  }

  .cabinet-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .hero-actions,
  .tool-actions,
  .resource-search,
  .card-actions {
    align-items: stretch;
    flex-direction: column;
    width: 100%;
  }

  .tool-control {
    width: 100%;
  }

  .post-grid,
  .resource-grid,
  .compact-grid,
  .cabinet-grid {
    grid-template-columns: 1fr;
  }

  .timeline-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .resource-timeline-card {
    flex-direction: column;
  }

  .timeline-resource-preview {
    width: 100%;
    min-height: 120px;
    flex-basis: auto;
  }

  .timeline-resource-actions {
    justify-content: flex-start;
  }
}
</style>
