<template>
  <div class="page">
    <h2>用户管理</h2>
    <el-table :data="users">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role" label="角色" />
      <el-table-column prop="is_active" label="启用" />
      <el-table-column prop="date_joined" label="注册时间" />
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../../api/http'

const users = ref([])

async function load() {
  const { data } = await http.get('/users/')
  users.value = data.results || data
}

onMounted(load)
</script>
