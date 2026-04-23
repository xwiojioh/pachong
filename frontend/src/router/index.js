
import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/tasks',
    children: [
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/Tasks.vue')
      },
      {
        path: 'tasks/:id',
        name: 'TaskDetail',
        component: () => import('@/views/TaskDetail.vue')
      },
      {
        path: 'data',
        name: 'DataManagement',
        component: () => import('@/views/DataManagement.vue')
      },
      {
        path: 'visualization',
        name: 'Visualization',
        component: () => import('@/views/Visualization.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (!userStore.isLoggedIn && to.path !== '/login') {
    await userStore.fetchUserInfo()
    if (!userStore.isLoggedIn) {
      return next('/login')
    }
  }
  
  if (userStore.isLoggedIn && to.path === '/login') {
    return next('/')
  }
  
  next()
})

export default router
