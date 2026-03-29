
<template>
  <div class="task-detail">
    <el-page-header @back="goBack" content="返回任务列表" />
    
    <el-card v-loading="loading" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>{{ task?.name }}</span>
          <div>
            <el-button type="success" @click="runTask" :disabled="task?.status === 'running'">
              {{ task?.status === 'running' ? '运行中' : '运行任务' }}
            </el-button>
            <el-button type="primary" @click="exportData">导出数据</el-button>
          </div>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务ID">{{ task?.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(task?.status)">{{ getStatusText(task?.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="目标URL" :span="2">
          <el-link :href="task?.url" target="_blank" type="primary">{{ task?.url }}</el-link>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ task?.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ task?.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="数据总数">{{ total }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <el-card style="margin-top: 20px">
      <template #header>
        <span>抓取数据</span>
      </template>
      
      <el-table :data="dataList" v-loading="dataLoading" stripe max-height="500">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column prop="content" label="内容" show-overflow-tooltip />
        <el-table-column prop="url" label="URL" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link v-if="row.url" :href="row.url" target="_blank" type="primary">链接</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="抓取时间" width="180" />
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi } from '@/api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const dataLoading = ref(false)
const task = ref(null)
const dataList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '待执行',
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || status
}

const fetchTask = async () => {
  loading.value = true
  try {
    const res = await taskApi.getTask(route.params.id)
    task.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchData = async () => {
  dataLoading.value = true
  try {
    const res = await taskApi.getTaskData(route.params.id, {
      page: currentPage.value,
      page_size: pageSize.value
    })
    dataList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    dataLoading.value = false
  }
}

const goBack = () => {
  router.push('/tasks')
}

const runTask = async () => {
  try {
    await ElMessageBox.confirm('确定要运行此任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await taskApi.runTask(route.params.id)
    ElMessage.success('任务已启动')
    fetchTask()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const exportData = () => {
  taskApi.exportData(route.params.id)
}

onMounted(() => {
  fetchTask()
  fetchData()
})
</script>

<style scoped>
.task-detail {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
