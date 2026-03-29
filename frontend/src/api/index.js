
import request from '@/utils/request'

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
  exportData(id) {
    window.open(`/api/tasks/${id}/export`, '_blank')
  }
}
