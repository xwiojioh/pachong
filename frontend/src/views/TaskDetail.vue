<template>
  <div class="task-detail-page">
    <div class="detail-header">
      <div>
        <el-button text class="back-button" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回任务列表
        </el-button>
        <h2 class="page-title">{{ task?.name || '任务详情' }}</h2>
      </div>
      <div class="header-actions">
        <el-button type="success" :disabled="task?.status === 'running'" @click="runTask">运行任务</el-button>
        <el-button type="warning" :disabled="task?.status !== 'running'" @click="stopTask">停止任务</el-button>
        <el-dropdown @command="handleExport">
          <el-button type="primary">
            导出数据
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
              <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <el-card v-loading="loading" class="summary-card">
      <el-alert
        v-if="task?.last_error"
        title="最近一次执行错误"
        type="error"
        :description="task.last_error"
        show-icon
        :closable="false"
        class="error-alert"
      />

      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务 ID">{{ task?.id }}</el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <el-tag :type="getStatusType(task)">{{ getStatusText(task) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="请求方式">{{ task?.request_config?.method || 'GET' }}</el-descriptions-item>
        <el-descriptions-item label="数据总量">{{ task?.data_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="目标 URL" :span="2">
          <el-link :href="task?.url" target="_blank" type="primary">{{ task?.url }}</el-link>
        </el-descriptions-item>
        <el-descriptions-item label="最近开始时间">{{ task?.last_run_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="最近完成时间">{{ task?.finished_at || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="progress-wrapper">
        <div class="progress-title">任务进度</div>
        <el-progress
          :percentage="task?.progress || 0"
          :status="getProgressStatus(task)"
          :stroke-width="18"
        />
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="15">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>抓取数据</span>
              <div class="card-actions">
                <el-input
                  v-model="keyword"
                  placeholder="搜索标题、内容或链接"
                  clearable
                  class="search-input"
                  @keyup.enter="searchData"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button @click="searchData">搜索</el-button>
              </div>
            </div>
          </template>

          <el-table :data="dataList" v-loading="dataLoading" stripe max-height="520">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
            <el-table-column prop="content" label="内容" min-width="220" show-overflow-tooltip />
            <el-table-column prop="url" label="URL" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">
                <el-link v-if="row.url" :href="row.url" target="_blank" type="primary">查看链接</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="抓取时间" width="180" />
            <el-table-column label="操作" width="90" fixed="right">
              <template #default="{ row }">
                <el-button type="danger" text @click="deleteDataRow(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="fetchData"
            @current-change="fetchData"
            class="pagination"
          />
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="9">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>执行日志</span>
              <el-button text type="primary" @click="fetchLogs">刷新</el-button>
            </div>
          </template>

          <el-table :data="logs" v-loading="logsLoading" stripe max-height="520">
            <el-table-column label="级别" width="90">
              <template #default="{ row }">
                <el-tag :type="getLogType(row.level)">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="日志内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="170" />
          </el-table>

          <el-pagination
            v-model:current-page="logPage"
            v-model:page-size="logPageSize"
            :total="logTotal"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @size-change="fetchLogs"
            @current-change="fetchLogs"
            class="pagination"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataApi, taskApi } from '@/api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const dataLoading = ref(false)
const logsLoading = ref(false)
const task = ref(null)
const dataList = ref([])
const logs = ref([])
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const logPage = ref(1)
const logPageSize = ref(20)
const logTotal = ref(0)
const refreshTimer = ref(null)

const isRunning = computed(() => task.value?.status === 'running')

const getStatusText = (currentTask) => {
  if (!currentTask) return '-'
  if (currentTask.status === 'running' && currentTask.stop_requested) return '停止中'
  const textMap = {
    pending: '待执行',
    running: '运行中',
    stopped: '已停止',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[currentTask.status] || currentTask.status
}

const getStatusType = (currentTask) => {
  if (!currentTask) return 'info'
  if (currentTask.status === 'running' && currentTask.stop_requested) return 'warning'
  const typeMap = {
    pending: 'info',
    running: 'warning',
    stopped: 'info',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[currentTask.status] || 'info'
}

const getProgressStatus = (currentTask) => {
  if (!currentTask) return undefined
  if (currentTask.status === 'completed') return 'success'
  if (currentTask.status === 'failed') return 'exception'
  return undefined
}

const getLogType = (level) => {
  const map = {
    info: 'info',
    warning: 'warning',
    error: 'danger'
  }
  return map[level] || 'info'
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
      page_size: pageSize.value,
      keyword: keyword.value
    })
    dataList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    dataLoading.value = false
  }
}

const fetchLogs = async () => {
  logsLoading.value = true
  try {
    const res = await taskApi.getTaskLogs(route.params.id, {
      page: logPage.value,
      page_size: logPageSize.value
    })
    logs.value = res.data.list
    logTotal.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    logsLoading.value = false
  }
}

const refreshPage = async () => {
  await Promise.all([fetchTask(), fetchData(), fetchLogs()])
}

const goBack = () => {
  router.push('/tasks')
}

const runTask = async () => {
  try {
    await taskApi.runTask(route.params.id)
    ElMessage.success('任务已启动')
    refreshPage()
  } catch (error) {
    console.error(error)
  }
}

const stopTask = async () => {
  try {
    await taskApi.stopTask(route.params.id)
    ElMessage.success('停止指令已发送')
    refreshPage()
  } catch (error) {
    console.error(error)
  }
}

const handleExport = (format) => {
  taskApi.exportData(route.params.id, {
    format,
    keyword: keyword.value
  })
}

const searchData = () => {
  currentPage.value = 1
  fetchData()
}

const deleteDataRow = async (dataId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条抓取数据吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await dataApi.deleteData(dataId)
    ElMessage.success('删除成功')
    refreshPage()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

onMounted(() => {
  refreshPage()
  refreshTimer.value = window.setInterval(() => {
    if (isRunning.value) {
      refreshPage()
    }
  }, 3000)
})

onUnmounted(() => {
  if (refreshTimer.value) {
    window.clearInterval(refreshTimer.value)
  }
})
</script>

<style scoped>
.task-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.back-button {
  padding-left: 0;
}

.page-title {
  margin: 8px 0 0;
  font-size: 24px;
  color: #111827;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.summary-card,
.content-card {
  border-radius: 16px;
}

.error-alert {
  margin-bottom: 16px;
}

.progress-wrapper {
  margin-top: 20px;
}

.progress-title {
  margin-bottom: 10px;
  font-weight: 600;
  color: #374151;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input {
  width: 240px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .detail-header {
    flex-direction: column;
  }

  .card-header,
  .card-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }
}
</style>
