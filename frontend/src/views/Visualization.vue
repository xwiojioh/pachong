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
  GraphicComponent,
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

use([TitleComponent, TooltipComponent, LegendComponent, GridComponent, GraphicComponent, PieChart, BarChart, LineChart, CanvasRenderer])

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
  const statusTotal = statusDistribution.reduce((sum, item) => sum + Number(item.count || 0), 0)
  const chartTextColor = '#667085'
  const chartAxisColor = '#eef2f7'
  const tooltipFormatter = (name, value, unit = '') => `
    <div style="min-width: 132px;">
      <div style="color:#667085;font-size:12px;margin-bottom:6px;">${name}</div>
      <div style="color:#1f2937;font-size:20px;font-weight:800;line-height:1;">${value}${unit}</div>
    </div>
  `

  pieChart?.setOption({
    color: ['#a8b2c1', '#d6a75f', '#c5ccd6', '#80bd73', '#cf7b74'],
    tooltip: {
      trigger: 'item',
      backgroundColor: '#ffffff',
      borderWidth: 0,
      padding: [12, 14],
      extraCssText: 'border-radius: 12px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);',
      formatter: (params) => tooltipFormatter(params.name, params.value, ' 个')
    },
    legend: {
      bottom: 0,
      itemWidth: 8,
      itemHeight: 8,
      itemGap: 16,
      textStyle: {
        color: chartTextColor,
        fontSize: 12,
        fontWeight: 600
      }
    },
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '39%',
        style: {
          text: `${statusTotal}`,
          fill: '#1f2937',
          fontSize: 32,
          fontWeight: 800,
          fontFamily: 'Inter, Roboto, Helvetica, Arial, sans-serif',
          textAlign: 'center'
        }
      },
      {
        type: 'text',
        left: 'center',
        top: '51%',
        style: {
          text: '任务总数',
          fill: '#909399',
          fontSize: 12,
          fontWeight: 600,
          textAlign: 'center'
        }
      }
    ],
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: ['55%', '70%'],
        center: ['50%', '46%'],
        avoidLabelOverlap: true,
        label: { show: false },
        labelLine: { show: false },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 4
        },
        emphasis: {
          scale: true,
          scaleSize: 4
        },
        data: statusDistribution.map(item => ({
          value: item.count,
          name: getTaskStatusText(item.status)
        }))
      }
    ]
  })

  barChart?.setOption({
    grid: { left: 44, right: 18, top: 28, bottom: 58 },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
        shadowStyle: { color: 'rgba(37, 111, 120, 0.06)' }
      },
      backgroundColor: '#ffffff',
      borderWidth: 0,
      padding: [12, 14],
      extraCssText: 'border-radius: 12px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);',
      formatter: (params) => {
        const item = params[0] || {}
        return tooltipFormatter(item.name, item.value || 0, ' 条')
      }
    },
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
      axisLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: chartTextColor },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: chartAxisColor, type: 'dashed' } }
    },
    series: [
      {
        type: 'bar',
        data: taskDataCounts.map(item => item.data_count),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#4aa3ad' },
            { offset: 1, color: '#256f78' }
          ])
        },
        barMaxWidth: 48
      }
    ]
  })

  lineChart?.setOption({
    grid: { left: 44, right: 24, top: 26, bottom: 42 },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
        lineStyle: { color: '#cbd5e1', width: 1, type: 'dashed' }
      },
      backgroundColor: '#ffffff',
      borderWidth: 0,
      padding: [12, 14],
      extraCssText: 'border-radius: 12px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);',
      formatter: (params) => {
        const item = params[0] || {}
        return tooltipFormatter(item.name, item.value || 0, ' 条')
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dailyCounts.map(item => item.date),
      axisLabel: { color: chartTextColor },
      axisTick: { show: false },
      axisLine: { show: false }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: { color: chartTextColor },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: chartAxisColor, type: 'dashed' } }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        showSymbol: false,
        symbolSize: 7,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(82, 155, 46, 0.18)' },
              { offset: 1, color: 'rgba(82, 155, 46, 0)' }
            ]
          }
        },
        data: dailyCounts.map(item => item.count),
        itemStyle: { color: '#529b2e' },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#80bd73' },
            { offset: 1, color: '#529b2e' }
          ])
        }
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
  gap: 24px;
  perspective: 1400px;
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
  gap: 18px;
}

.stat-card,
.chart-card {
  border: 1px solid #edf1f6;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: var(--app-shadow-3d);
  transform: translateZ(0);
}

.stat-card {
  min-height: 126px;
  padding: 22px;
  position: relative;
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.stat-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: #1e6f7a;
}

.stat-card::after,
.chart-card::after {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 42%;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.76), rgba(255, 255, 255, 0));
}

.stat-card > *,
.chart-card :deep(.el-card__header),
.chart-card :deep(.el-card__body) {
  position: relative;
  z-index: 1;
}

.stat-card:hover {
  transform: translateY(-4px) rotateX(1.2deg);
  box-shadow: var(--app-shadow-3d-hover);
}

.chart-card {
  position: relative;
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.chart-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--app-shadow-3d-hover);
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
  padding: 18px 22px;
  border-bottom-color: #f0f3f8;
}

.chart-card :deep(.el-card__body) {
  padding: 18px 22px 22px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-value {
  margin-top: 10px;
  font-family: Inter, Roboto, Helvetica, Arial, sans-serif;
  font-size: 34px;
  font-weight: 800;
  color: #1f2937;
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
