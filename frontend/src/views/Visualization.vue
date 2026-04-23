<template>
  <div class="visualization-page">
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-label">任务总数</div>
          <div class="stat-value">{{ summary.total_tasks || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-label">抓取数据总量</div>
          <div class="stat-value">{{ summary.total_records || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-label">运行中任务</div>
          <div class="stat-value">{{ summary.running_tasks || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-label">已完成任务</div>
          <div class="stat-value">{{ summary.completed_tasks || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :xl="10">
        <el-card class="chart-card">
          <template #header>
            <span>任务状态分布</span>
          </template>
          <div ref="pieChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :xl="14">
        <el-card class="chart-card">
          <template #header>
            <span>各任务数据量</span>
          </template>
          <div ref="barChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card">
      <template #header>
        <span>近 7 天抓取趋势</span>
      </template>
      <div ref="lineChartRef" class="chart-box line-chart"></div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { use } from 'echarts/core'
import * as echarts from 'echarts/core'
import { analyticsApi } from '@/api'

use([TitleComponent, TooltipComponent, LegendComponent, GridComponent, PieChart, BarChart, LineChart, CanvasRenderer])

const summary = ref({})
const pieChartRef = ref(null)
const barChartRef = ref(null)
const lineChartRef = ref(null)

let pieChart = null
let barChart = null
let lineChart = null

const initCharts = () => {
  if (pieChartRef.value && !pieChart) {
    pieChart = echarts.init(pieChartRef.value)
  }
  if (barChartRef.value && !barChart) {
    barChart = echarts.init(barChartRef.value)
  }
  if (lineChartRef.value && !lineChart) {
    lineChart = echarts.init(lineChartRef.value)
  }
}

const renderCharts = (data) => {
  const statusDistribution = data.status_distribution || []
  const taskDataCounts = data.task_data_counts || []
  const dailyCounts = data.daily_counts || []

  pieChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: ['40%', '68%'],
        center: ['50%', '46%'],
        data: statusDistribution.map(item => ({
          value: item.count,
          name: getStatusName(item.status)
        }))
      }
    ]
  })

  barChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: taskDataCounts.map(item => item.name)
    },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data: taskDataCounts.map(item => item.data_count),
        itemStyle: { color: '#409EFF' },
        barMaxWidth: 48
      }
    ]
  })

  lineChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dailyCounts.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        type: 'line',
        smooth: true,
        areaStyle: {},
        data: dailyCounts.map(item => item.count),
        itemStyle: { color: '#67C23A' },
        lineStyle: { width: 3 }
      }
    ]
  })
}

const getStatusName = (status) => {
  const map = {
    pending: '待执行',
    running: '运行中',
    stopped: '已停止',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

const fetchOverview = async () => {
  try {
    const res = await analyticsApi.getOverview()
    summary.value = res.data.summary || {}
    renderCharts(res.data)
  } catch (error) {
    console.error(error)
  }
}

const handleResize = () => {
  pieChart?.resize()
  barChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  initCharts()
  fetchOverview()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  pieChart?.dispose()
  barChart?.dispose()
  lineChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.visualization-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card,
.chart-card {
  border-radius: 16px;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

.stat-value {
  margin-top: 10px;
  font-size: 30px;
  font-weight: 700;
  color: #111827;
}

.chart-box {
  width: 100%;
  height: 340px;
}

.line-chart {
  height: 360px;
}
</style>
