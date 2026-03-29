
<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>爬虫任务列表</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>
      
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="url" label="目标URL" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToDetail(row.id)">查看</el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="runTask(row.id)"
              :disabled="row.status === 'running'"
            >
              {{ row.status === 'running' ? '运行中' : '运行' }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteTask(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchTasks"
        @current-change="fetchTasks"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <el-dialog v-model="showCreateDialog" title="新建爬虫任务" width="600px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="目标URL" prop="url">
          <el-input v-model="createForm.url" placeholder="请输入目标URL" />
        </el-form-item>
        <el-form-item label="提取配置" prop="selectorConfig">
          <el-input
            v-model="createForm.selectorConfig"
            type="textarea"
            :rows="6"
            placeholder='请输入JSON格式的提取配置，例如：
{
  "list_selector": ".item",
  "fields": {
    "title": {"type": "text", "selector": "h3"},
    "url": {"type": "attr", "selector": "a", "attr": "href"}
  }
}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="createLoading">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const createLoading = ref(false)
const tasks = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showCreateDialog = ref(false)
const createFormRef = ref(null)

const createForm = reactive({
  name: '',
  url: '',
  selectorConfig: ''
})

const createRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  url: [{ required: true, message: '请输入目标URL', trigger: 'blur' }]
}

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

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await taskApi.getTasks({
      page: currentPage.value,
      page_size: pageSize.value
    })
    tasks.value = res.data
    total.value = res.data.length
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/tasks/${id}`)
}

const runTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要运行此任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await taskApi.runTask(id)
    ElMessage.success('任务已启动')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const deleteTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此任务吗？删除后数据将无法恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await taskApi.deleteTask(id)
    ElMessage.success('删除成功')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      createLoading.value = true
      try {
        let selectorConfig = null
        if (createForm.selectorConfig) {
          selectorConfig = JSON.parse(createForm.selectorConfig)
        }
        await taskApi.createTask({
          name: createForm.name,
          url: createForm.url,
          selector_config: selectorConfig
        })
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        createForm.name = ''
        createForm.url = ''
        createForm.selectorConfig = ''
        fetchTasks()
      } catch (error) {
        if (error instanceof SyntaxError) {
          ElMessage.error('JSON格式错误')
        }
        console.error(error)
      } finally {
        createLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.tasks-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
