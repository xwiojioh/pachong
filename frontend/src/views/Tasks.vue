<template>
  <div class="tasks-page">
    <el-card class="page-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索任务名称或 URL"
            clearable
            class="toolbar-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="filters.status" placeholder="任务状态" clearable class="toolbar-select">
            <el-option label="待执行" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已停止" value="stopped" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
          <el-button @click="handleSearch">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
      </div>

      <el-table :data="tasks" v-loading="loading" stripe class="task-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="160" />
        <el-table-column label="请求方式" width="110">
          <template #default="{ row }">
            <el-tag type="info">{{ row.request_config?.method || 'GET' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="目标 URL" min-width="240" show-overflow-tooltip />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row)">{{ getStatusText(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" min-width="160">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="getProgressStatus(row)"
              :stroke-width="16"
            />
          </template>
        </el-table-column>
        <el-table-column prop="data_count" label="数据量" width="100" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToDetail(row.id)">查看</el-button>
            <el-button type="success" size="small" :disabled="row.status === 'running'" @click="runTask(row.id)">
              运行
            </el-button>
            <el-button
              type="warning"
              size="small"
              :disabled="row.status !== 'running'"
              @click="stopTask(row.id)"
            >
              停止
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
        class="pagination"
      />
    </el-card>

    <el-dialog v-model="showCreateDialog" title="新建爬虫任务" width="860px" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="110px">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item label="任务名称">
              <el-input
                v-model="createForm.name"
                placeholder="可留空，系统会自动生成任务名称"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="目标 URL" prop="url">
              <el-input
                v-model="createForm.url"
                placeholder="请输入要抓取的网址，例如 https://movie.douban.com/top250"
              >
                <template #append>
                  <el-button :loading="detectionLoading" @click="handleDetectNow">识别</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item label="抓取条数">
              <el-input-number
                v-model="createForm.fetchLimit"
                :min="1"
                :max="200"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="detect-card" v-loading="detectionLoading">
          <div class="detect-header">
            <div>
              <div class="detect-title">系统准备抓取的内容</div>
              <div class="detect-subtitle">
                {{ detectionSummary }}
              </div>
            </div>
            <el-tag :type="detectionTagType">
              {{ detectionTagText }}
            </el-tag>
          </div>

          <div v-if="detectedPreset?.preview_fields?.length" class="detect-fields">
            <el-tag
              v-for="item in detectedPreset.preview_fields"
              :key="item"
              class="field-tag"
            >
              {{ item }}
            </el-tag>
          </div>

          <div class="detect-hint">
            {{ detectionHint }}
          </div>

          <div v-if="effectiveTaskName" class="detect-name">
            自动任务名：{{ effectiveTaskName }}
          </div>

          <div v-if="detectedPreset?.recommended_url" class="detect-actions">
            <el-button text type="primary" @click="useRecommendedUrl">
              改用推荐网址：{{ detectedPreset.recommended_url }}
            </el-button>
          </div>
        </div>

        <div class="advanced-toggle">
          <el-button text type="primary" @click="advancedMode = !advancedMode">
            {{ advancedMode ? '收起高级配置' : '展开高级配置（可选）' }}
          </el-button>
          <span class="advanced-tip">
            高级模式适合你想自己指定字段、请求头、Cookie 或 POST 请求时使用。
          </span>
        </div>

        <el-collapse-transition>
          <div v-show="advancedMode" class="advanced-panel">
            <el-alert
              title="如果你不修改下面的内容，系统会继续沿用上面的智能识别结果。"
              type="info"
              :closable="false"
              show-icon
              class="advanced-info"
            />

            <el-row :gutter="16">
              <el-col :xs="24" :md="12">
                <el-form-item label="加载方式">
                  <el-select v-model="createForm.renderMode" style="width: 100%">
                    <el-option label="自动判断" value="auto" />
                    <el-option label="普通请求" value="request" />
                    <el-option label="动态渲染" value="playwright" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-form-item label="请求方式">
                  <el-select v-model="createForm.method" style="width: 100%">
                    <el-option label="GET" value="GET" />
                    <el-option label="POST" value="POST" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :xs="24" :md="12">
                <el-form-item label="等待策略">
                  <el-select v-model="createForm.waitUntil" style="width: 100%">
                    <el-option label="DOM 就绪" value="domcontentloaded" />
                    <el-option label="网络空闲" value="networkidle" />
                    <el-option label="页面加载完成" value="load" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-form-item label="超时时间(秒)">
                  <el-input-number v-model="createForm.timeout" :min="5" :max="120" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16" v-if="createForm.renderMode === 'playwright' || createForm.renderMode === 'auto'">
              <el-col :xs="24" :md="12">
                <el-form-item label="列表选择器类型">
                  <el-radio-group v-model="createForm.listSelectorType">
                    <el-radio-button
                      v-for="item in selectorTypeOptions"
                      :key="item.value"
                      :label="item.value"
                    >
                      {{ item.label }}
                    </el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-form-item label="模拟手机环境">
                  <el-switch v-model="createForm.emulateMobile" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="列表选择器">
              <el-input
                v-model="createForm.listSelector"
                placeholder="留空表示抓取整个页面；CSS 示例：.item，XPath 示例：//div[@class='item']"
              />
            </el-form-item>

            <el-row :gutter="16" v-if="createForm.renderMode === 'playwright' || createForm.renderMode === 'auto'">
              <el-col :xs="24" :md="12">
                <el-form-item label="等待选择器">
                  <el-input
                    v-model="createForm.waitForSelector"
                    placeholder="例如：.item，留空则只按时间等待"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-form-item label="额外等待(毫秒)">
                  <el-input-number
                    v-model="createForm.waitForTimeoutMs"
                    :min="0"
                    :max="20000"
                    :step="500"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item v-if="createForm.method === 'POST'" label="请求体类型">
              <el-radio-group v-model="createForm.bodyType">
                <el-radio-button label="json">JSON</el-radio-button>
                <el-radio-button label="form">表单</el-radio-button>
                <el-radio-button label="raw">原始文本</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="createForm.method === 'POST'" label="请求体">
              <el-input
                v-model="createForm.body"
                type="textarea"
                :rows="4"
                placeholder='JSON/表单请填写 JSON 字符串，例如：{"page": 1}'
              />
            </el-form-item>

            <div class="section-title">
              <span>请求头</span>
              <el-button text type="primary" @click="addHeader">新增</el-button>
            </div>
            <div v-for="(item, index) in createForm.headers" :key="`header-${index}`" class="kv-row">
              <el-input v-model="item.key" placeholder="Header 名称，例如 Referer" />
              <el-input v-model="item.value" placeholder="Header 值" />
              <el-button type="danger" plain @click="removeHeader(index)">删除</el-button>
            </div>

            <div class="section-title">
              <span>Cookie</span>
              <el-button text type="primary" @click="addCookie">新增</el-button>
            </div>
            <div v-for="(item, index) in createForm.cookies" :key="`cookie-${index}`" class="kv-row">
              <el-input v-model="item.key" placeholder="Cookie 名称" />
              <el-input v-model="item.value" placeholder="Cookie 值" />
              <el-button type="danger" plain @click="removeCookie(index)">删除</el-button>
            </div>

            <div class="section-title">
              <span>字段提取规则</span>
              <el-button text type="primary" @click="addField">新增字段</el-button>
            </div>
            <div v-for="(field, index) in createForm.fields" :key="`field-${index}`" class="field-row">
              <el-input v-model="field.name" placeholder="字段名，例如 title / price / time" />
              <el-select v-model="field.extract_type" placeholder="提取方式">
                <el-option label="文本" value="text" />
                <el-option label="属性" value="attr" />
                <el-option label="HTML" value="html" />
              </el-select>
              <el-select v-model="field.selector_type" placeholder="选择器类型">
                <el-option label="CSS" value="css" />
                <el-option label="XPath" value="xpath" />
              </el-select>
              <el-input v-model="field.selector" placeholder="选择器表达式" />
              <el-input
                v-if="field.extract_type === 'attr'"
                v-model="field.attr"
                placeholder="属性名，例如 href"
              />
              <div v-else class="field-placeholder">无需属性名</div>
              <el-button type="danger" plain @click="removeField(index)">删除</el-button>
            </div>

            <div class="detail-toggle-row">
              <div>
                <div class="detail-title">进入详情页继续抓取</div>
                <div class="detail-subtitle">适合新闻列表页、商品列表页、文章目录页。先抓链接，再进入详情页抓正文。</div>
              </div>
              <el-switch v-model="createForm.detailEnabled" />
            </div>

            <div v-if="createForm.detailEnabled" class="detail-panel">
              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item label="详情链接字段">
                    <el-input v-model="createForm.detailLinkField" placeholder="通常填 url" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item label="最多详情页数">
                    <el-input-number v-model="createForm.detailMaxItems" :min="1" :max="200" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item label="详情页加载方式">
                    <el-select v-model="createForm.detailRenderMode" style="width: 100%">
                      <el-option label="自动判断" value="auto" />
                      <el-option label="普通请求" value="request" />
                      <el-option label="动态渲染" value="playwright" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item label="详情页等待策略">
                    <el-select v-model="createForm.detailWaitUntil" style="width: 100%">
                      <el-option label="DOM 就绪" value="domcontentloaded" />
                      <el-option label="网络空闲" value="networkidle" />
                      <el-option label="页面加载完成" value="load" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item label="详情页超时(秒)">
                    <el-input-number v-model="createForm.detailTimeout" :min="5" :max="120" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item label="详情页模拟手机">
                    <el-switch v-model="createForm.detailEmulateMobile" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="16" v-if="createForm.detailRenderMode === 'playwright' || createForm.detailRenderMode === 'auto'">
                <el-col :xs="24" :md="12">
                  <el-form-item label="详情页等待选择器">
                    <el-input v-model="createForm.detailWaitForSelector" placeholder="例如：#detailContent" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item label="详情页额外等待">
                    <el-input-number
                      v-model="createForm.detailWaitForTimeoutMs"
                      :min="0"
                      :max="20000"
                      :step="500"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="section-title">
                <span>详情页字段规则</span>
                <el-button text type="primary" @click="addDetailField">新增字段</el-button>
              </div>
              <div v-for="(field, index) in createForm.detailFields" :key="`detail-field-${index}`" class="field-row">
                <el-input v-model="field.name" placeholder="字段名，例如 title / content / publish_time" />
                <el-select v-model="field.extract_type" placeholder="提取方式">
                  <el-option label="文本" value="text" />
                  <el-option label="属性" value="attr" />
                  <el-option label="HTML" value="html" />
                </el-select>
                <el-select v-model="field.selector_type" placeholder="选择器类型">
                  <el-option label="CSS" value="css" />
                  <el-option label="XPath" value="xpath" />
                </el-select>
                <el-input v-model="field.selector" placeholder="详情页选择器表达式" />
                <el-input
                  v-if="field.extract_type === 'attr'"
                  v-model="field.attr"
                  placeholder="属性名，例如 href"
                />
                <div v-else class="field-placeholder">无需属性名</div>
                <el-button type="danger" plain @click="removeDetailField(index)">删除</el-button>
              </div>
            </div>
          </div>
        </el-collapse-transition>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">创建任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi } from '@/api'

const router = useRouter()

const createPair = () => ({ key: '', value: '' })
const createField = (name = '') => ({
  name,
  selector: '',
  selector_type: 'css',
  extract_type: 'text',
  attr: 'href'
})
const createDetailField = (name = '') => createField(name)

const createEmptyPreset = () => ({
  name: '',
  description: '输入网址后，系统会自动告诉你将抓取什么内容。',
  preview_fields: [],
  supported: true,
  warning: '',
  recommended_url: ''
})

const selectorTypeOptions = [
  { label: 'CSS', value: 'css' },
  { label: 'XPath', value: 'xpath' }
]

const loading = ref(false)
const createLoading = ref(false)
const detectionLoading = ref(false)
const showCreateDialog = ref(false)
const advancedMode = ref(false)
const createFormRef = ref(null)
const tasks = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const refreshTimer = ref(null)
const detectedPreset = ref(createEmptyPreset())

let detectTimer = null

const filters = reactive({
  keyword: '',
  status: ''
})

const createForm = reactive({
  name: '',
  url: '',
  fetchLimit: 20,
  renderMode: 'auto',
  method: 'GET',
  waitUntil: 'domcontentloaded',
  timeout: 30,
  waitForSelector: '',
  waitForTimeoutMs: 0,
  emulateMobile: false,
  bodyType: 'json',
  body: '',
  listSelector: '',
  listSelectorType: 'css',
  headers: [createPair()],
  cookies: [createPair()],
  fields: [createField('title'), createField('content')],
  detailEnabled: false,
  detailLinkField: 'url',
  detailMaxItems: 20,
  detailRenderMode: 'request',
  detailWaitUntil: 'domcontentloaded',
  detailTimeout: 30,
  detailWaitForSelector: '',
  detailWaitForTimeoutMs: 0,
  detailEmulateMobile: false,
  detailFields: [createDetailField('title'), createDetailField('content')]
})

const createRules = {
  url: [{ required: true, message: '请输入目标 URL', trigger: 'blur' }]
}

const hasRunningTask = computed(() => tasks.value.some(item => item.status === 'running'))

const effectiveTaskName = computed(() => {
  return createForm.name.trim() || detectedPreset.value?.name || ''
})

const detectionSummary = computed(() => {
  if (!createForm.url.trim()) {
    return '先输入网址，系统会自动帮你判断抓什么。'
  }
  return detectedPreset.value?.description || '系统正在识别这个网址适合怎么抓取。'
})

const detectionHint = computed(() => {
  if (!createForm.url.trim()) {
    return '支持已内置的网站规则，也支持普通网页的整页标题和正文抓取。'
  }
  if (detectedPreset.value?.warning) {
    return detectedPreset.value.warning
  }
  return '如果结果不符合你的预期，可以展开高级配置手动修改。'
})

const detectionTagType = computed(() => {
  if (!createForm.url.trim()) return 'info'
  if (detectedPreset.value?.supported === false) return 'warning'
  return detectedPreset.value?.matched ? 'success' : 'info'
})

const detectionTagText = computed(() => {
  if (!createForm.url.trim()) return '等待输入'
  if (detectedPreset.value?.supported === false) return '需手动处理'
  return detectedPreset.value?.matched ? '已识别内置规则' : '使用通用规则'
})

const getStatusText = (task) => {
  if (task.status === 'running' && task.stop_requested) return '停止中'
  const textMap = {
    pending: '待执行',
    running: '运行中',
    stopped: '已停止',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[task.status] || task.status
}

const getStatusType = (task) => {
  if (task.status === 'running' && task.stop_requested) return 'warning'
  const typeMap = {
    pending: 'info',
    running: 'warning',
    stopped: 'info',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[task.status] || 'info'
}

const getProgressStatus = (task) => {
  if (task.status === 'completed') return 'success'
  if (task.status === 'failed') return 'exception'
  return undefined
}

const buildPairObject = (pairs) => {
  const result = {}
  pairs.forEach(item => {
    if (item.key && item.value) {
      result[item.key.trim()] = item.value
    }
  })
  return result
}

const normalizeBodyForForm = (body) => {
  if (body === null || body === undefined || body === '') {
    return ''
  }
  if (typeof body === 'string') {
    return body
  }
  return JSON.stringify(body, null, 2)
}

const resetAdvancedConfig = () => {
  createForm.renderMode = 'auto'
  createForm.method = 'GET'
  createForm.waitUntil = 'domcontentloaded'
  createForm.timeout = 30
  createForm.waitForSelector = ''
  createForm.waitForTimeoutMs = 0
  createForm.emulateMobile = false
  createForm.bodyType = 'json'
  createForm.body = ''
  createForm.listSelector = ''
  createForm.listSelectorType = 'css'
  createForm.headers = [createPair()]
  createForm.cookies = [createPair()]
  createForm.fields = [createField('title'), createField('content')]
  createForm.detailEnabled = false
  createForm.detailLinkField = 'url'
  createForm.detailMaxItems = 20
  createForm.detailRenderMode = 'request'
  createForm.detailWaitUntil = 'domcontentloaded'
  createForm.detailTimeout = 30
  createForm.detailWaitForSelector = ''
  createForm.detailWaitForTimeoutMs = 0
  createForm.detailEmulateMobile = false
  createForm.detailFields = [createDetailField('title'), createDetailField('content')]
}

const cloneField = (field) => ({
  name: field.name || '',
  selector: field.selector || '',
  selector_type: field.selector_type || 'css',
  extract_type: field.extract_type || 'text',
  attr: field.attr || 'href'
})

const applyDetectedPresetToForm = (preset) => {
  if (!preset?.supported) {
    return
  }

  const selectorConfig = preset.selector_config || {}
  const requestConfigForm = preset.request_config_form || {}

  createForm.renderMode = requestConfigForm.render_mode || 'auto'
  createForm.method = requestConfigForm.method || 'GET'
  createForm.waitUntil = requestConfigForm.wait_until || 'domcontentloaded'
  createForm.timeout = requestConfigForm.timeout || 30
  createForm.waitForSelector = requestConfigForm.wait_for_selector || ''
  createForm.waitForTimeoutMs = requestConfigForm.wait_for_timeout_ms || 0
  createForm.emulateMobile = Boolean(requestConfigForm.emulate_mobile)
  createForm.bodyType = requestConfigForm.body_type || 'json'
  createForm.body = normalizeBodyForForm(requestConfigForm.body)
  createForm.listSelector = selectorConfig.list_selector || ''
  createForm.listSelectorType = selectorConfig.list_selector_type || 'css'
  createForm.headers = (requestConfigForm.headers && requestConfigForm.headers.length)
    ? requestConfigForm.headers.map(item => ({ ...item }))
    : [createPair()]
  createForm.cookies = (requestConfigForm.cookies && requestConfigForm.cookies.length)
    ? requestConfigForm.cookies.map(item => ({ ...item }))
    : [createPair()]
  createForm.fields = (selectorConfig.fields && selectorConfig.fields.length)
    ? selectorConfig.fields.map(cloneField)
    : [createField('title'), createField('content')]

  const detailPage = selectorConfig.detail_page || {}
  const detailRequestConfig = detailPage.request_config || {}
  const detailSelectorConfig = detailPage.selector_config || {}
  createForm.detailEnabled = Boolean(detailPage.enabled)
  createForm.detailLinkField = detailPage.link_field || 'url'
  createForm.detailMaxItems = detailPage.max_items || 20
  createForm.detailRenderMode = detailRequestConfig.render_mode || 'request'
  createForm.detailWaitUntil = detailRequestConfig.wait_until || 'domcontentloaded'
  createForm.detailTimeout = detailRequestConfig.timeout || 30
  createForm.detailWaitForSelector = detailRequestConfig.wait_for_selector || ''
  createForm.detailWaitForTimeoutMs = detailRequestConfig.wait_for_timeout_ms || 0
  createForm.detailEmulateMobile = Boolean(detailRequestConfig.emulate_mobile)
  createForm.detailFields = (detailSelectorConfig.fields && detailSelectorConfig.fields.length)
    ? detailSelectorConfig.fields.map(cloneField)
    : [createDetailField('title'), createDetailField('content')]
}

const buildValidFields = () => {
  return createForm.fields
    .filter(field => field.name.trim() && field.selector.trim())
    .map(field => ({
      name: field.name.trim(),
      selector: field.selector.trim(),
      selector_type: field.selector_type,
      extract_type: field.extract_type,
      attr: field.extract_type === 'attr' ? field.attr || 'href' : ''
    }))
}

const buildValidDetailFields = () => {
  return createForm.detailFields
    .filter(field => field.name.trim() && field.selector.trim())
    .map(field => ({
      name: field.name.trim(),
      selector: field.selector.trim(),
      selector_type: field.selector_type,
      extract_type: field.extract_type,
      attr: field.extract_type === 'attr' ? field.attr || 'href' : ''
    }))
}

const parseRequestBody = () => {
  if (createForm.method !== 'POST' || !createForm.body.trim()) {
    return null
  }
  if (createForm.bodyType === 'raw') {
    return createForm.body
  }
  return JSON.parse(createForm.body)
}

const resetCreateForm = () => {
  Object.assign(createForm, {
    name: '',
    url: '',
    fetchLimit: 20,
    renderMode: 'auto',
    method: 'GET',
    waitUntil: 'domcontentloaded',
    timeout: 30,
    waitForSelector: '',
    waitForTimeoutMs: 0,
    emulateMobile: false,
    bodyType: 'json',
    body: '',
    listSelector: '',
    listSelectorType: 'css',
    headers: [createPair()],
    cookies: [createPair()],
    fields: [createField('title'), createField('content')],
    detailEnabled: false,
    detailLinkField: 'url',
    detailMaxItems: 20,
    detailRenderMode: 'request',
    detailWaitUntil: 'domcontentloaded',
    detailTimeout: 30,
    detailWaitForSelector: '',
    detailWaitForTimeoutMs: 0,
    detailEmulateMobile: false,
    detailFields: [createDetailField('title'), createDetailField('content')]
  })
  advancedMode.value = false
  detectedPreset.value = createEmptyPreset()
  detectionLoading.value = false
  if (detectTimer) {
    window.clearTimeout(detectTimer)
    detectTimer = null
  }
  createFormRef.value?.clearValidate()
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await taskApi.getTasks({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: filters.keyword,
      status: filters.status
    })
    tasks.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchTasks()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  handleSearch()
}

const openCreateDialog = () => {
  resetCreateForm()
  showCreateDialog.value = true
}

const addHeader = () => {
  createForm.headers.push(createPair())
}

const removeHeader = (index) => {
  if (createForm.headers.length === 1) {
    createForm.headers[0] = createPair()
    return
  }
  createForm.headers.splice(index, 1)
}

const addCookie = () => {
  createForm.cookies.push(createPair())
}

const removeCookie = (index) => {
  if (createForm.cookies.length === 1) {
    createForm.cookies[0] = createPair()
    return
  }
  createForm.cookies.splice(index, 1)
}

const addField = () => {
  createForm.fields.push(createField())
}

const removeField = (index) => {
  if (createForm.fields.length === 1) {
    createForm.fields[0] = createField()
    return
  }
  createForm.fields.splice(index, 1)
}

const addDetailField = () => {
  createForm.detailFields.push(createDetailField())
}

const removeDetailField = (index) => {
  if (createForm.detailFields.length === 1) {
    createForm.detailFields[0] = createDetailField()
    return
  }
  createForm.detailFields.splice(index, 1)
}

const detectTaskByUrl = async (urlValue = createForm.url) => {
  const normalizedUrl = (urlValue || '').trim()
  if (!normalizedUrl) {
    detectedPreset.value = createEmptyPreset()
    resetAdvancedConfig()
    return null
  }

  detectionLoading.value = true
  try {
    const res = await taskApi.detectTask({ url: normalizedUrl })
    detectedPreset.value = res.data
    if (res.data?.supported) {
      applyDetectedPresetToForm(res.data)
    } else {
      resetAdvancedConfig()
    }
    return res.data
  } catch (error) {
    console.error(error)
    return null
  } finally {
    detectionLoading.value = false
  }
}

const handleDetectNow = async () => {
  await detectTaskByUrl()
}

const useRecommendedUrl = () => {
  if (detectedPreset.value?.recommended_url) {
    createForm.url = detectedPreset.value.recommended_url
  }
}

const handleCreate = async () => {
  if (!createFormRef.value) return

  try {
    await createFormRef.value.validate()

    if (!createForm.url.trim()) {
      ElMessage.error('请输入目标 URL')
      return
    }
    const preset = await detectTaskByUrl()

    if (!advancedMode.value && preset?.supported === false) {
      ElMessage.error(preset.warning || '当前网址不支持简易模式，请展开高级配置手动填写。')
      return
    }

    createLoading.value = true
    const payload = {
      name: createForm.name.trim(),
      url: createForm.url.trim(),
      max_items: createForm.fetchLimit
    }

    if (advancedMode.value) {
      const fields = buildValidFields()
      if (fields.length) {
        payload.selector_config = {
          list_selector: createForm.listSelector.trim(),
          list_selector_type: createForm.listSelectorType,
          fields
        }
        payload.request_config = {
          render_mode: createForm.renderMode,
          method: createForm.method,
          wait_until: createForm.waitUntil,
          timeout: createForm.timeout,
          wait_for_selector: createForm.waitForSelector.trim(),
          wait_for_timeout_ms: createForm.waitForTimeoutMs,
          emulate_mobile: createForm.emulateMobile,
          headers: createForm.headers,
          cookies: createForm.cookies,
          body_type: createForm.bodyType,
          body: parseRequestBody()
        }

        if (createForm.detailEnabled) {
          const detailFields = buildValidDetailFields()
          if (!detailFields.length) {
            ElMessage.error('已开启二级爬取，请至少填写一个详情页字段规则。')
            return
          }
          if (!fields.some(field => field.name === (createForm.detailLinkField.trim() || 'url'))) {
            ElMessage.error('详情链接字段必须先在列表页字段规则里存在，例如 url。')
            return
          }

          payload.selector_config.detail_page = {
            enabled: true,
            link_field: createForm.detailLinkField.trim() || 'url',
            max_items: createForm.detailMaxItems,
            selector_config: {
              list_selector: '',
              list_selector_type: 'css',
              fields: detailFields
            },
            request_config: {
              render_mode: createForm.detailRenderMode,
              method: 'GET',
              wait_until: createForm.detailWaitUntil,
              timeout: createForm.detailTimeout,
              wait_for_selector: createForm.detailWaitForSelector.trim(),
              wait_for_timeout_ms: createForm.detailWaitForTimeoutMs,
              emulate_mobile: createForm.detailEmulateMobile,
              headers: [],
              cookies: [],
              body_type: 'json',
              body: null
            }
          }
        }
      } else if (preset?.supported === false) {
        ElMessage.error('当前网址没有可用的自动规则。使用高级模式时，请至少填写一个字段提取规则。')
        return
      }
    }

    await taskApi.createTask(payload)
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    fetchTasks()
  } catch (error) {
    if (error instanceof SyntaxError) {
      ElMessage.error('请求体 JSON 格式不正确')
    } else {
      console.error(error)
    }
  } finally {
    createLoading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/tasks/${id}`)
}

const runTask = async (id) => {
  try {
    await taskApi.runTask(id)
    ElMessage.success('任务已启动')
    fetchTasks()
  } catch (error) {
    console.error(error)
  }
}

const stopTask = async (id) => {
  try {
    await taskApi.stopTask(id)
    ElMessage.success('停止指令已发送')
    fetchTasks()
  } catch (error) {
    console.error(error)
  }
}

const deleteTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此任务吗？任务日志和抓取数据都会被删除。', '警告', {
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

watch(
  () => createForm.url,
  (value) => {
    if (!showCreateDialog.value) return
    if (detectTimer) {
      window.clearTimeout(detectTimer)
    }
    if (!value.trim()) {
      detectedPreset.value = createEmptyPreset()
      resetAdvancedConfig()
      return
    }
    detectTimer = window.setTimeout(() => {
      detectTaskByUrl(value)
    }, 500)
  }
)

onMounted(() => {
  fetchTasks()
  refreshTimer.value = window.setInterval(() => {
    if (hasRunningTask.value) {
      fetchTasks()
    }
  }, 3000)
})

onUnmounted(() => {
  if (refreshTimer.value) {
    window.clearInterval(refreshTimer.value)
  }
  if (detectTimer) {
    window.clearTimeout(detectTimer)
  }
})
</script>

<style scoped>
.tasks-page {
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
  width: 150px;
}

.task-table {
  width: 100%;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.detect-card {
  margin: 6px 0 16px;
  padding: 16px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #dbeafe;
}

.detect-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.detect-title {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.detect-subtitle {
  margin-top: 6px;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.7;
}

.detect-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.field-tag {
  margin-right: 0;
}

.detect-hint {
  margin-top: 12px;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.7;
}

.detect-name {
  margin-top: 10px;
  font-size: 13px;
  color: #2563eb;
}

.detect-actions {
  margin-top: 10px;
}

.advanced-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.advanced-tip {
  font-size: 12px;
  color: #6b7280;
}

.advanced-panel {
  padding-top: 8px;
}

.advanced-info {
  margin-bottom: 16px;
}

.detail-toggle-row {
  margin-top: 22px;
  padding: 14px 16px;
  border: 1px solid #dbeafe;
  border-radius: 10px;
  background: #f8fbff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.detail-title {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
}

.detail-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: #6b7280;
}

.detail-panel {
  margin-top: 14px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 18px 0 10px;
}

.kv-row,
.field-row {
  display: grid;
  gap: 12px;
  margin-bottom: 12px;
}

.kv-row {
  grid-template-columns: 1fr 1fr 88px;
}

.field-row {
  grid-template-columns: 1fr 110px 120px 2fr 120px 88px;
  align-items: center;
}

.field-placeholder {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  background: #f9fafb;
  border: 1px dashed #d1d5db;
  border-radius: 4px;
}

@media (max-width: 1024px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .detect-header,
  .advanced-toggle,
  .detail-toggle-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .kv-row,
  .field-row {
    grid-template-columns: 1fr;
  }

  .toolbar-input,
  .toolbar-select {
    width: 100%;
  }
}
</style>
