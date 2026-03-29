
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const isLoggedIn = ref(false)

  async function login(data) {
    const res = await authApi.login(data)
    userInfo.value = res.data
    isLoggedIn.value = true
    return res
  }

  async function register(data) {
    const res = await authApi.register(data)
    return res
  }

  async function logout() {
    await authApi.logout()
    userInfo.value = null
    isLoggedIn.value = false
  }

  async function fetchUserInfo() {
    try {
      const res = await authApi.getMe()
      userInfo.value = res.data
      isLoggedIn.value = true
    } catch (error) {
      userInfo.value = null
      isLoggedIn.value = false
    }
  }

  return {
    userInfo,
    isLoggedIn,
    login,
    register,
    logout,
    fetchUserInfo
  }
})
