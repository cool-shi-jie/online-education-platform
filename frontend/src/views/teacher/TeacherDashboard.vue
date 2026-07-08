<template>
  <div class="page">
    <h2>教师中心</h2>
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/teacher/courses')">
          <h3>课程管理</h3>
          <p class="muted">创建课程、维护章节和资料</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/teacher/exams')">
          <h3>考试管理</h3>
          <p class="muted">发布考试、维护题目和选项</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/teacher/progress')">
          <h3>学习情况</h3>
          <p class="muted">查看学生进度和成绩</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/teacher/questions')">
          <h3>处理疑问</h3>
          <p class="muted">按状态筛选并回复课程疑问</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
