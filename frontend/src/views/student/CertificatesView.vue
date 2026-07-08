<template>
  <div class="page">
    <div class="certificate-hero">
      <div>
        <h2>我的证书</h2>
        <p class="muted">达到课程优秀线后，系统会自动发放课程结业优秀证书。</p>
      </div>
      <el-tag type="success" size="large">共 {{ certificates.length }} 张</el-tag>
    </div>

    <div v-if="certificates.length" class="certificate-grid">
      <el-card v-for="certificate in certificates" :key="certificate.id" shadow="hover" class="certificate-card">
        <div class="card-ribbon">网页证书</div>
        <div class="card-body">
          <span class="cert-mark">D社</span>
          <h3>{{ certificate.course_title }}</h3>
          <p class="muted">获证人：{{ certificate.student_name }}</p>
          <div class="cert-meta">
            <span>证书编号</span>
            <b>{{ certificate.code }}</b>
          </div>
          <div class="cert-meta">
            <span>颁发时间</span>
            <b>{{ formatDate(certificate.issued_at) }}</b>
          </div>
        </div>
        <div class="card-actions">
          <el-button type="primary" @click="openCertificate(certificate)">查看证书</el-button>
          <el-link v-if="certificate.file" :href="certificate.file" target="_blank" type="primary">下载证书</el-link>
        </div>
      </el-card>
    </div>
    <el-empty v-else description="暂无证书，达到课程优秀线后自动获得证书" />

    <el-dialog v-model="certificateVisible" title="网页虚拟证书" width="760px">
      <div v-if="currentCertificate" class="virtual-certificate">
        <div class="certificate-inner">
          <div class="certificate-topline">D社在线教育平台</div>
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
            <span>认证平台：D社在线教育平台</span>
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
import { onMounted, ref } from 'vue'
import http from '../../api/http'

const certificates = ref([])
const certificateVisible = ref(false)
const currentCertificate = ref(null)

async function load() {
  const { data } = await http.get('/certificates/')
  certificates.value = data.results || data
}

function openCertificate(certificate) {
  currentCertificate.value = certificate
  certificateVisible.value = true
}

function formatDate(value) {
  if (!value) return '暂无'
  return new Date(value).toLocaleDateString('zh-CN')
}

onMounted(load)
</script>

<style scoped>
.certificate-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
}

.certificate-hero h2 {
  margin: 0 0 8px;
}

.certificate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.certificate-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
}

.card-ribbon {
  position: absolute;
  top: 16px;
  right: -34px;
  width: 128px;
  padding: 5px 0;
  color: #fff;
  background: #4f46e5;
  text-align: center;
  font-size: 12px;
  transform: rotate(35deg);
}

.card-body {
  padding-right: 36px;
}

.cert-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  font-weight: 800;
}

.certificate-card h3 {
  margin: 14px 0 8px;
  color: #0f172a;
}

.cert-meta {
  display: grid;
  gap: 4px;
  margin-top: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}

.cert-meta span,
.certificate-info span {
  color: #64748b;
  font-size: 12px;
}

.cert-meta b {
  color: #1e293b;
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-top: 18px;
}

.virtual-certificate {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

.certificate-inner {
  padding: 44px;
  border: 8px double #4f46e5;
  border-radius: 18px;
  background:
    radial-gradient(circle at top left, rgba(79, 70, 229, 0.12), transparent 34%),
    radial-gradient(circle at bottom right, rgba(37, 99, 235, 0.12), transparent 34%),
    #fff;
  text-align: center;
}

.certificate-topline {
  color: #4f46e5;
  font-weight: 800;
  letter-spacing: 6px;
}

.certificate-inner h1 {
  margin: 22px 0;
  color: #172554;
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
  color: #312e81;
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
  background: #eef2ff;
}

.certificate-info b {
  color: #1e1b4b;
}

.certificate-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  color: #475569;
  font-weight: 700;
}

@media (max-width: 720px) {
  .certificate-hero,
  .certificate-footer {
    align-items: flex-start;
    flex-direction: column;
  }

  .certificate-inner {
    padding: 26px;
  }

  .certificate-inner h1 {
    font-size: 26px;
    letter-spacing: 4px;
  }

  .certificate-info {
    grid-template-columns: 1fr;
  }
}
</style>
