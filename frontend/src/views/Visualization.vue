<template>
  <div class="visualization-page">
    <div class="page-heading">
      <div>
        <div class="page-eyebrow">Analytics</div>
        <h1>采集数据驾驶舱</h1>
        <p>集中观察任务状态、数据规模和最近 7 天采集趋势。</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card is-primary">
        <div class="stat-label">任务总数</div>
        <div class="stat-value">{{ summary.total_tasks || 0 }}</div>
        <div class="stat-hint">全部采集任务</div>
      </div>
      <div class="stat-card is-success">
        <div class="stat-label">抓取数据总量</div>
        <div class="stat-value">{{ summary.total_records || 0 }}</div>
        <div class="stat-hint">已入库记录</div>
      </div>
      <div class="stat-card is-warning">
        <div class="stat-label">运行中任务</div>
        <div class="stat-value">{{ summary.running_tasks || 0 }}</div>
        <div class="stat-hint">实时执行中</div>
      </div>
      <div class="stat-card is-neutral">
        <div class="stat-label">已完成任务</div>
        <div class="stat-value">{{ summary.completed_tasks || 0 }}</div>
        <div class="stat-hint">成功结束任务</div>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :xl="10">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-title">任务状态分布</div>
          </template>
          <div ref="pieChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :xl="14">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-title">各任务数据量</div>
          </template>
          <div ref="barChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card">
      <template #header>
        <div class="chart-title">近 7 天抓取趋势</div>
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
import { getTaskStatusText } from '@/constants/taskStatus'

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
  const chartTextColor = '#526173'
  const chartAxisColor = '#d9e2ec'

  pieChart?.setOption({
    color: ['#6b778c', '#d58a1f', '#8a96a8', '#2f9461', '#c2413a'],
    tooltip: { trigger: 'item' },
    legend: {
      bottom: 0,
      itemWidth: 9,
      itemHeight: 9,
      textStyle: { color: chartTextColor }
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: ['40%', '68%'],
        center: ['50%', '46%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 3
        },
        data: statusDistribution.map(item => ({
          value: item.count,
          name: getTaskStatusText(item.status)
        }))
      }
    ]
  })

  barChart?.setOption({
    grid: { left: 44, right: 18, top: 26, bottom: 58 },
    color: ['#1e6f7a'],
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: taskDataCounts.map(item => item.name),
      axisLabel: {
        color: chartTextColor,
        interval: 0,
        width: 90,
        overflow: 'truncate'
      },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: chartAxisColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: chartTextColor },
      splitLine: { lineStyle: { color: chartAxisColor, type: 'dashed' } }
    },
    series: [
      {
        type: 'bar',
        data: taskDataCounts.map(item => item.data_count),
        itemStyle: { borderRadius: [6, 6, 0, 0] },
        barMaxWidth: 48
      }
    ]
  })

  lineChart?.setOption({
    grid: { left: 44, right: 24, top: 26, bottom: 42 },
    color: ['#2f9461'],
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dailyCounts.map(item => item.date),
      axisLabel: { color: chartTextColor },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: chartAxisColor } }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: { color: chartTextColor },
      splitLine: { lineStyle: { color: chartAxisColor, type: 'dashed' } }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(47, 148, 97, 0.22)' },
              { offset: 1, color: 'rgba(47, 148, 97, 0)' }
            ]
          }
        },
        data: dailyCounts.map(item => item.count),
        lineStyle: { width: 3 }
      }
    ]
  })
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
  gap: 18px;
}

.page-heading {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.stat-card,
.chart-card {
  border: 1px solid #dfe7ef;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 18px 50px rgba(20, 40, 60, 0.07);
}

.stat-card {
  min-height: 124px;
  padding: 18px;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: #1e6f7a;
}

.stat-card.is-success::before {
  background: #2f9461;
}

.stat-card.is-warning::before {
  background: #d58a1f;
}

.stat-card.is-neutral::before {
  background: #637083;
}

.chart-card :deep(.el-card__header) {
  padding: 16px 18px;
  border-bottom-color: #edf2f7;
}

.chart-card :deep(.el-card__body) {
  padding: 16px 18px 18px;
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
  line-height: 1;
}

.stat-hint {
  margin-top: 14px;
  color: #738196;
  font-size: 12px;
}

.chart-title {
  color: #1f2937;
  font-weight: 800;
}

.chart-box {
  width: 100%;
  height: 340px;
}

.line-chart {
  height: 360px;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .page-heading h1 {
    font-size: 24px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-box,
  .line-chart {
    height: 300px;
  }
}
</style>
