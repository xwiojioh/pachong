
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true
})

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      if (res.code === 401) {
        window.location.hash = '#/login'
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    const responseData = error.response?.data
    const message = responseData?.message || error.message || '网络错误'
    ElMessage.error(message)
    if (responseData?.code === 401) {
      window.location.hash = '#/login'
    }
    return Promise.reject(error)
  }
)

export default request
