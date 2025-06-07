import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 加载状态
  const isLoading = ref(false)
  const loadingMessage = ref('')

  // 设置加载状态
  const setLoading = (loading: boolean, message = '') => {
    isLoading.value = loading
    loadingMessage.value = message
  }

  // 应用配置
  const config = ref({
    apiBaseUrl: 'http://localhost:8000',
    theme: 'light',
    language: 'zh'
  })

  // 更新配置
  const updateConfig = (newConfig: Partial<typeof config.value>) => {
    config.value = { ...config.value, ...newConfig }
    // 保存到本地存储
    localStorage.setItem('app-config', JSON.stringify(config.value))
  }

  // 从本地存储加载配置
  const loadConfig = () => {
    const saved = localStorage.getItem('app-config')
    if (saved) {
      try {
        config.value = { ...config.value, ...JSON.parse(saved) }
      } catch (error) {
        console.warn('加载配置失败:', error)
      }
    }
  }

  // 初始化时加载配置
  loadConfig()

  return {
    isLoading,
    loadingMessage,
    config,
    setLoading,
    updateConfig,
    loadConfig
  }
}) 