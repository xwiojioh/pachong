
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import {
  ArrowDown,
  ArrowLeft,
  DataAnalysis,
  Document,
  Files,
  Menu,
  Plus,
  Search
} from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

const icons = {
  ArrowDown,
  ArrowLeft,
  DataAnalysis,
  Document,
  Files,
  Menu,
  Plus,
  Search
}

Object.entries(icons).forEach(([name, component]) => {
  app.component(name, component)
})

app.mount('#app')
