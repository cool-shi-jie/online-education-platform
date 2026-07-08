<template>
  <div class="page">
    <h2>管理后台</h2>
    <el-row :gutter="16">
      <el-col :span="8"><el-card shadow="hover" @click="$router.push('/admin/users')"><h3>用户管理</h3></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" @click="$router.push('/admin/content')"><h3>课程与论坛</h3></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" @click="$router.push('/certificates')"><h3>证书记录</h3></el-card></el-col>
    </el-row>
  </div>
</template>
