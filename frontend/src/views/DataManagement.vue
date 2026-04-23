<template>
  <div class="data-page">
    <el-card class="page-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索标题、内容或链接"
            clearable
            class="toolbar-input"
            @keyup.enter="searchData"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="filters.taskId" placeholder="选择任务" clearable class="toolbar-select">
            <el-option
              v-for="item in taskOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-button @click="searchData">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>
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

      <el-table :data="dataList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="所属任务" width="160">
          <template #default="{ row }">
            <el-tag type="info">{{ row.task_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="content" label="内容" min-width="220" show-overflow-tooltip />
        <el-table-column prop="url" label="链接" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link v-if="row.url" :href="row.url" target="_blank" type="primary">打开链接</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="抓取时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
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
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataApi, taskApi } from '@/api'

const loading = ref(false)
const dataList = ref([])
const taskOptions = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive({
  keyword: '',
  taskId: ''
})

const fetchTaskOptions = async () => {
  try {
    const res = await taskApi.getTasks({
      page: 1,
      page_size: 1000
    })
    taskOptions.value = res.data.list
  } catch (error) {
    console.error(error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await dataApi.getDataList({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: filters.keyword,
      task_id: filters.taskId
    })
    dataList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const searchData = () => {
  currentPage.value = 1
  fetchData()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.taskId = ''
  searchData()
}

const handleExport = (format) => {
  dataApi.exportData({
    format,
    keyword: filters.keyword,
    task_id: filters.taskId
  })
}

const deleteDataRow = async (dataId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条数据吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await dataApi.deleteData(dataId)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchTaskOptions()
  fetchData()
})
</script>

<style scoped>
.data-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-card {
  border-radius: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-input {
  width: 260px;
}

.toolbar-select {
  width: 180px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-input,
  .toolbar-select {
    width: 100%;
  }
}
</style>
