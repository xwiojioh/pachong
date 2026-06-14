<template>
  <div class="data-page">
    <div class="page-heading">
      <div>
        <div class="page-eyebrow">Dataset</div>
        <h1>采集数据管理</h1>
        <p>检索、筛选和导出已经入库的网页采集结果。</p>
      </div>
      <el-dropdown @command="handleExport">
        <el-button type="primary" size="large">
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

    <div class="summary-grid">
      <div class="summary-card is-primary">
        <div class="summary-label">数据总量</div>
        <div class="summary-value">{{ total }}</div>
        <div class="summary-hint">当前筛选结果</div>
      </div>
      <div class="summary-card is-success">
        <div class="summary-label">任务来源</div>
        <div class="summary-value">{{ taskOptions.length }}</div>
        <div class="summary-hint">可筛选任务</div>
      </div>
      <div class="summary-card is-neutral">
        <div class="summary-label">本页记录</div>
        <div class="summary-value">{{ dataList.length }}</div>
        <div class="summary-hint">当前表格展示</div>
      </div>
    </div>

    <el-card class="page-card table-card">
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
      </div>

      <el-table :data="dataList" v-loading="loading" class="data-table">
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
        <template #empty>
          <div class="empty-state">
            <div class="empty-title">暂无数据</div>
            <div class="empty-text">运行采集任务后，抓取结果会在这里按时间汇总。</div>
          </div>
        </template>
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
  gap: 18px;
}

.page-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  padding: 4px 2px 2px;
}

.page-eyebrow {
  color: #2f6f73;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.page-heading h1 {
  margin: 6px 0 8px;
  color: #16202a;
  font-size: 28px;
  line-height: 1.2;
}

.page-heading p {
  margin: 0;
  color: #667085;
  font-size: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.summary-card {
  min-height: 118px;
  padding: 18px;
  border: 1px solid #dfe7ef;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 16px 36px rgba(20, 40, 60, 0.06);
  position: relative;
  overflow: hidden;
}

.summary-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: #1e6f7a;
}

.summary-card.is-success::before {
  background: #2f9461;
}

.summary-card.is-neutral::before {
  background: #637083;
}

.summary-label {
  color: #667085;
  font-size: 13px;
}

.summary-value {
  margin-top: 8px;
  color: #111827;
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
}

.summary-hint {
  margin-top: 12px;
  color: #738196;
  font-size: 12px;
}

.page-card {
  border: 1px solid #dfe7ef;
  border-radius: 8px;
  box-shadow: 0 18px 50px rgba(20, 40, 60, 0.07);
}

.table-card :deep(.el-card__body) {
  padding: 18px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  padding: 12px;
  border: 1px solid #e6edf4;
  border-radius: 8px;
  background: #f8fafc;
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

.data-table :deep(.el-table__header th) {
  background: #f7fafc;
  color: #506070;
  font-weight: 700;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.empty-state {
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 40px 16px;
}

.empty-title {
  color: #1f2937;
  font-size: 16px;
  font-weight: 800;
}

.empty-text {
  max-width: 360px;
  color: #667085;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 1024px) {
  .page-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-input,
  .toolbar-select {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .page-heading h1 {
    font-size: 24px;
  }
}
</style>
