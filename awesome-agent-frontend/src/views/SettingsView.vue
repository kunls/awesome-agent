<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <h1 class="text-2xl font-bold text-gray-900">系统设置</h1>

    <!-- API配置 -->
    <div class="bg-white rounded-xl shadow-sm border p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">API 配置</h2>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            后端API地址
          </label>
          <input
            v-model="tempConfig.apiBaseUrl"
            type="url"
            placeholder="http://localhost:8000"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="text-sm text-gray-500 mt-1">
            Awesome List Agent 后端服务的地址
          </p>
        </div>
      </div>
    </div>

    <!-- 界面设置 -->
    <div class="bg-white rounded-xl shadow-sm border p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">界面设置</h2>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            语言
          </label>
          <select
            v-model="tempConfig.language"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="zh">中文</option>
            <option value="en">English</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            主题
          </label>
          <div class="grid grid-cols-2 gap-3">
            <label class="relative flex cursor-pointer">
              <input
                v-model="tempConfig.theme"
                type="radio"
                value="light"
                class="sr-only"
              />
              <div
                :class="[
                  'w-full p-4 border-2 rounded-lg transition-all',
                  tempConfig.theme === 'light'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <div class="text-center">
                  <Sun class="w-6 h-6 mx-auto mb-2 text-gray-600" />
                  <div class="font-medium text-gray-900">浅色模式</div>
                </div>
              </div>
            </label>

            <label class="relative flex cursor-pointer">
              <input
                v-model="tempConfig.theme"
                type="radio"
                value="dark"
                class="sr-only"
              />
              <div
                :class="[
                  'w-full p-4 border-2 rounded-lg transition-all',
                  tempConfig.theme === 'dark'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <div class="text-center">
                  <Moon class="w-6 h-6 mx-auto mb-2 text-gray-600" />
                  <div class="font-medium text-gray-900">深色模式</div>
                </div>
              </div>
            </label>
          </div>
          <p class="text-sm text-gray-500 mt-2">
            深色模式功能正在开发中
          </p>
        </div>
      </div>
    </div>

    <!-- 数据管理 -->
    <div class="bg-white rounded-xl shadow-sm border p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">数据管理</h2>
      
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <div class="font-medium text-gray-900">本地数据</div>
            <div class="text-sm text-gray-500">
              {{ lists.length }}个已生成的列表，占用约{{ storageSize }}存储空间
            </div>
          </div>
          <button
            @click="exportAllData"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <Download class="w-4 h-4 inline mr-1" />
            导出数据
          </button>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <div class="font-medium text-gray-900">清除数据</div>
            <div class="text-sm text-gray-500">
              删除所有本地存储的数据和设置
            </div>
          </div>
          <button
            @click="clearAllData"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <Trash2 class="w-4 h-4 inline mr-1" />
            清除所有数据
          </button>
        </div>
      </div>
    </div>

    <!-- 系统信息 -->
    <div class="bg-white rounded-xl shadow-sm border p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">系统信息</h2>
      
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div class="text-gray-500">版本</div>
          <div class="font-medium">v0.1.0</div>
        </div>
        <div>
          <div class="text-gray-500">构建时间</div>
          <div class="font-medium">{{ buildTime }}</div>
        </div>
        <div>
          <div class="text-gray-500">浏览器</div>
          <div class="font-medium">{{ browserInfo }}</div>
        </div>
        <div>
          <div class="text-gray-500">本地存储</div>
          <div class="font-medium">{{ localStorageSupport ? '支持' : '不支持' }}</div>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="flex items-center justify-between">
      <button
        @click="resetToDefaults"
        class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
      >
        恢复默认设置
      </button>
      
      <div class="flex items-center space-x-3">
        <button
          @click="cancelChanges"
          class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          取消
        </button>
        <button
          @click="saveSettings"
          :disabled="!hasChanges"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          保存设置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Sun, Moon, Download, Trash2 } from 'lucide-vue-next'
import { useAppStore } from '../stores/app'
import { useAwesomeListStore } from '../stores/awesomeList'

const appStore = useAppStore()
const awesomeListStore = useAwesomeListStore()

const tempConfig = ref({ ...appStore.config })

const lists = computed(() => awesomeListStore.lists)

const hasChanges = computed(() => {
  return JSON.stringify(tempConfig.value) !== JSON.stringify(appStore.config)
})

const storageSize = computed(() => {
  try {
    const data = localStorage.getItem('awesome-lists') || ''
    const sizeInBytes = new Blob([data]).size
    return sizeInBytes < 1024 
      ? `${sizeInBytes}B`
      : sizeInBytes < 1024 * 1024
      ? `${(sizeInBytes / 1024).toFixed(1)}KB`
      : `${(sizeInBytes / (1024 * 1024)).toFixed(1)}MB`
  } catch {
    return '未知'
  }
})

const buildTime = computed(() => {
  return new Date().toLocaleDateString('zh-CN')
})

const browserInfo = computed(() => {
  const ua = navigator.userAgent
  if (ua.includes('Chrome')) return 'Chrome'
  if (ua.includes('Firefox')) return 'Firefox'
  if (ua.includes('Safari')) return 'Safari'
  if (ua.includes('Edge')) return 'Edge'
  return '其他'
})

const localStorageSupport = computed(() => {
  try {
    localStorage.setItem('test', 'test')
    localStorage.removeItem('test')
    return true
  } catch {
    return false
  }
})

const saveSettings = () => {
  appStore.updateConfig(tempConfig.value)
  // 显示保存成功提示
  console.log('设置已保存')
}

const cancelChanges = () => {
  tempConfig.value = { ...appStore.config }
}

const resetToDefaults = () => {
  if (confirm('确定要恢复默认设置吗？')) {
    tempConfig.value = {
      apiBaseUrl: 'http://localhost:8000',
      theme: 'light',
      language: 'zh'
    }
  }
}

const exportAllData = () => {
  try {
    const data = {
      lists: lists.value,
      config: appStore.config,
      exportTime: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `awesome-agent-data-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出失败:', error)
  }
}

const clearAllData = () => {
  if (confirm('确定要清除所有数据吗？此操作不可恢复，包括：\n- 所有生成的列表\n- 所有个人设置\n- 本地存储的所有数据')) {
    try {
      localStorage.clear()
      location.reload() // 重新加载页面以重置状态
    } catch (error) {
      console.error('清除数据失败:', error)
    }
  }
}

onMounted(() => {
  // 页面加载时重新同步配置
  tempConfig.value = { ...appStore.config }
})
</script> 