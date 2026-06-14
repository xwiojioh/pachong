<template>
  <el-container class="layout-container">
    <el-aside v-if="!isMobile" width="248px" class="layout-aside">
      <div class="logo">
        <div class="logo-mark">P</div>
        <div>
          <h3>爬虫系统</h3>
          <span>Data Collector</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="side-menu"
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
        <div class="logo-mark">P</div>
        <div>
          <h3>爬虫系统</h3>
          <span>Data Collector</span>
        </div>
      </div>
      <el-menu :default-active="activeMenu" router class="drawer-menu" @select="drawerVisible = false">
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
            <span class="user-pill">{{ userStore.userInfo?.username || '用户' }}</span>
            <el-button plain size="small" @click="handleLogout">退出</el-button>
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
  background:
    linear-gradient(180deg, #fbfdff 0%, #f8fafc 42%, #f4f7fb 100%);
}

.layout-aside {
  background: #17212b;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 14px 0 32px rgba(15, 23, 42, 0.12);
  transform: translateZ(0);
}

.logo {
  height: 76px;
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-start;
  padding: 0 20px;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-mark {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  background: #dcefed;
  color: #175964;
  font-weight: 900;
}

.logo h3 {
  margin: 0;
  font-size: 17px;
  line-height: 1.2;
}

.logo span {
  display: block;
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.56);
  font-size: 12px;
}

.side-menu {
  padding: 14px 12px;
  border-right: 0;
  background: transparent;
}

.side-menu :deep(.el-menu-item) {
  height: 46px;
  margin-bottom: 6px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.72);
  font-weight: 700;
}

.side-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.side-menu :deep(.el-menu-item.is-active) {
  background: #dcefed;
  color: #175964;
}

.drawer-menu {
  border-right: 0;
}

.el-header {
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #edf1f6;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 72px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.035);
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
  font-weight: 800;
  color: #16202a;
}

.header-subtitle {
  font-size: 12px;
  color: #667085;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-pill {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 7px 10px;
  border: 1px solid #edf1f6;
  border-radius: 999px;
  background: #f8fafc;
  color: #344054;
  font-size: 13px;
  font-weight: 700;
}

.el-main {
  background: transparent;
  padding: 28px;
  overflow-x: hidden;
  perspective: 1400px;
}

:deep(.menu-drawer .el-drawer__body) {
  padding: 0;
}

.mobile-logo {
  background: #17212b;
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

  .user-pill {
    max-width: 110px;
  }
}
</style>
