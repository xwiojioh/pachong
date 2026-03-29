<template>
  <div class="visualization">
    <el-card>
      <template #header>
        <span>数据可视化</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>任务状态分布</span>
            </template>
            <div ref="pieChartRef" style="width: 100%; height: 300px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>各任务数据量</span>
            </template>
            <div ref="barChartRef" style="width: 100%; height: 300px"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { taskApi } from '@/api'

const pieChartRef = ref(null)
const barChartRef = ref(null)

let pieChart = null
let barChart = null

const initCharts = () => {
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      title: { text: '任务状态分布', left: 'center' },
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [
        {
          name: '任务状态',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 0, name: '待执行' },
            { value: 0, name: '运行中' },
            { value: 0, name: '已完成' },
            { value: 0, name: '失败' }
          ]
        }
      ]
    })
  }

  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    barChart.setOption({
      title: { text: '各任务数据量', left: 'center' },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', data: ['暂无数据'] },
      yAxis: { type: 'value' },
      series: [{ data: [0], type: 'bar', itemStyle: { color: '#409EFF' } }]
    })
  }
}

const fetchData = async () => {
  try {
    const res = await taskApi.getTasks({ page: 1, page_size: 100 })
    const tasks = res.data.list || res.data || []
    
    const statusCount = {
      pending: 0,
      running: 0,
      completed: 0,
      failed: 0
    }
    
    const taskNames = []
    const dataCounts = []
    
    tasks.forEach(task => {
      if (statusCount[task.status] !== undefined) {
        statusCount[task.status]++
      }
      taskNames.push(task.name)
      dataCounts.push(task.data_count || 0)
    })
    
    if (pieChart) {
      pieChart.setOption({
        series: [{
          data: [
            { value: statusCount.pending, name: '待执行' },
            { value: statusCount.running, name: '运行中' },
            { value: statusCount.completed, name: '已完成' },
            { value: statusCount.failed, name: '失败' }
          ]
        }]
      })
    }
    
    if (barChart && taskNames.length > 0) {
      barChart.setOption({
        xAxis: { data: taskNames },
        series: [{ data: dataCounts, type: 'bar', itemStyle: { color: '#409EFF' } }]
      })
    }
  } catch (error) {
    console.error(error)
  }
}

const handleResize = () => {
  pieChart?.resize()
  barChart?.resize()
}

onMounted(() => {
  initCharts()
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  pieChart?.dispose()
  barChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.visualization {
  height: 100%;
}
</style>