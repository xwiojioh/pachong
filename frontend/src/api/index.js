
import request from '@/utils/request'

const buildDownloadUrl = (path, params = {}) => {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value)
    }
  })

  const query = searchParams.toString()
  window.open(`/api${path}${query ? `?${query}` : ''}`, '_blank')
}

export const authApi = {
  login(data) {
    return request({
      url: '/auth/login',
      method: 'post',
      data
    })
  },
  register(data) {
    return request({
      url: '/auth/register',
      method: 'post',
      data
    })
  },
  logout() {
    return request({
      url: '/auth/logout',
      method: 'post'
    })
  },
  getMe() {
    return request({
      url: '/auth/me',
      method: 'get'
    })
  }
}

export const taskApi = {
  getTasks(params) {
    return request({
      url: '/tasks',
      method: 'get',
      params
    })
  },
  detectTask(data) {
    return request({
      url: '/tasks/detect',
      method: 'post',
      data
    })
  },
  createTask(data) {
    return request({
      url: '/tasks',
      method: 'post',
      data
    })
  },
  getTask(id) {
    return request({
      url: `/tasks/${id}`,
      method: 'get'
    })
  },
  runTask(id) {
    return request({
      url: `/tasks/${id}/run`,
      method: 'post'
    })
  },
  stopTask(id) {
    return request({
      url: `/tasks/${id}/stop`,
      method: 'post'
    })
  },
  deleteTask(id) {
    return request({
      url: `/tasks/${id}`,
      method: 'delete'
    })
  },
  getTaskData(id, params) {
    return request({
      url: `/tasks/${id}/data`,
      method: 'get',
      params
    })
  },
  getTaskLogs(id, params) {
    return request({
      url: `/tasks/${id}/logs`,
      method: 'get',
      params
    })
  },
  exportData(id, params = {}) {
    buildDownloadUrl(`/tasks/${id}/export`, params)
  }
}

export const dataApi = {
  getDataList(params) {
    return request({
      url: '/data',
      method: 'get',
      params
    })
  },
  deleteData(id) {
    return request({
      url: `/data/${id}`,
      method: 'delete'
    })
  },
  exportData(params = {}) {
    buildDownloadUrl('/data/export', params)
  }
}

export const analyticsApi = {
  getOverview() {
    return request({
      url: '/analytics/overview',
      method: 'get'
    })
  }
}
