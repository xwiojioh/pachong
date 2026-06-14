export const TASK_STATUS_META = {
  pending: {
    text: '待执行',
    tagType: 'info',
    tone: 'neutral'
  },
  running: {
    text: '运行中',
    tagType: 'warning',
    tone: 'warning'
  },
  stopped: {
    text: '已停止',
    tagType: 'info',
    tone: 'neutral'
  },
  completed: {
    text: '已完成',
    tagType: 'success',
    tone: 'success'
  },
  failed: {
    text: '失败',
    tagType: 'danger',
    tone: 'danger'
  }
}

export const getTaskStatusText = (taskOrStatus) => {
  const status = typeof taskOrStatus === 'string' ? taskOrStatus : taskOrStatus?.status
  if (status === 'running' && taskOrStatus?.stop_requested) {
    return '停止中'
  }
  return TASK_STATUS_META[status]?.text || status || '-'
}

export const getTaskStatusType = (taskOrStatus) => {
  const status = typeof taskOrStatus === 'string' ? taskOrStatus : taskOrStatus?.status
  if (status === 'running' && taskOrStatus?.stop_requested) {
    return 'warning'
  }
  return TASK_STATUS_META[status]?.tagType || 'info'
}

export const getTaskStatusTone = (taskOrStatus) => {
  const status = typeof taskOrStatus === 'string' ? taskOrStatus : taskOrStatus?.status
  if (status === 'running' && taskOrStatus?.stop_requested) {
    return 'warning'
  }
  return TASK_STATUS_META[status]?.tone || 'neutral'
}

export const getTaskProgressStatus = (task) => {
  if (!task) return undefined
  if (task.status === 'completed') return 'success'
  if (task.status === 'failed') return 'exception'
  return undefined
}
