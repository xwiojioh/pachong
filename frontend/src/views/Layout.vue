<template>
  <el-container class="layout-container">
    <el-aside v-if="!isMobile" width="220px" class="layout-aside">
      <div class="logo">
        <h3>爬虫系统</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/tasks">
          <el-icon><Document /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><Files /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="/visualization">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据可视化</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      size="220px"
      :with-header="false"
      class="menu-drawer"
    >
      <div class="logo mobile-logo">
        <h3>爬虫系统</h3>
      </div>
      <el-menu :default-active="activeMenu" router @select="drawerVisible = false">
        <el-menu-item index="/tasks">
          <el-icon><Document /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><Files /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="/visualization">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据可视化</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>

    <el-container>
      <el-header>
        <div class="header-content">
          <div class="header-left">
            <el-button v-if="isMobile" text class="menu-button" @click="drawerVisible = true">
              <el-icon><Menu /></el-icon>
            </el-button>
            <div>
              <div class="header-title">Python爬虫系统</div>
              <div class="header-subtitle">任务采集、数据管理与分析一体化工作台</div>
            </div>
          </div>
          <div class="header-user">
            <span>欢迎，{{ userStore.userInfo?.username }}</span>
            <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isMobile = ref(false)
const drawerVisible = ref(false)

const activeMenu = computed(() => {
  if (route.path.startsWith('/tasks')) return '/tasks'
  if (route.path.startsWith('/data')) return '/data'
  return route.path
})

const updateViewport = () => {
  isMobile.value = window.innerWidth < 900
  if (!isMobile.value) {
    drawerVisible.value = false
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.logout()
    ElMessage.success('退出成功')
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

watch(
  () => route.path,
  () => {
    drawerVisible.value = false
  }
)

onMounted(() => {
  updateViewport()
  window.addEventListener('resize', updateViewport)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewport)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background: #eef3f8;
}

.layout-aside {
  background-color: #545c64;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #434a50;
}

.logo h3 {
  margin: 0;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 72px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.menu-button {
  font-size: 20px;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2a37;
}

.header-subtitle {
  font-size: 12px;
  color: #6b7280;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.el-main {
  background-color: #eef3f8;
  padding: 20px;
}

:deep(.menu-drawer .el-drawer__body) {
  padding: 0;
}

.mobile-logo {
  background: #545c64;
}

@media (max-width: 899px) {
  .el-header {
    padding: 0 14px;
  }

  .header-subtitle {
    display: none;
  }

  .header-user {
    font-size: 13px;
    gap: 8px;
  }

  .el-main {
    padding: 14px;
  }
}
</style>
