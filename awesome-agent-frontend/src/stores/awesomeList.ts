import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAppStore } from './app'

export interface AwesomeListItem {
  id: string
  topic: string
  content: string
  keywords: string[]
  totalResults: number
  processingTime: number
  model: string
  createdAt: string
}

export interface GenerateRequest {
  topic: string
  model: string
  maxResults: number
  language: string
}

export const useAwesomeListStore = defineStore('awesomeList', () => {
  const appStore = useAppStore()
  
  // 存储的列表
  const lists = ref<AwesomeListItem[]>([])
  const currentList = ref<AwesomeListItem | null>(null)

  // 计算属性
  const recentLists = computed(() => 
    lists.value
      .slice()
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 6)
  )

  // 生成Awesome List
  const generateAwesomeList = async (request: GenerateRequest): Promise<AwesomeListItem> => {
    try {
      appStore.setLoading(true, '正在连接AI模型...')
      
      const response = await axios.post(
        `${appStore.config.apiBaseUrl}/api/v1/generate_awesome_list_intelligent`,
        {
          topic: request.topic,
          model: request.model,
          max_results: request.maxResults,
          language: request.language
        }
      )

      const newItem: AwesomeListItem = {
        id: generateId(),
        topic: request.topic,
        content: response.data.awesome_list,
        keywords: response.data.keywords,
        totalResults: response.data.total_results,
        processingTime: response.data.processing_time,
        model: response.data.model_used,
        createdAt: new Date().toISOString()
      }

      // 添加到列表
      lists.value.unshift(newItem)
      currentList.value = newItem

      // 保存到本地存储
      saveToLocalStorage()

      return newItem
    } catch (error) {
      console.error('生成失败:', error)
      throw error
    }
  }

  // 获取特定列表
  const getListById = (id: string): AwesomeListItem | null => {
    return lists.value.find(list => list.id === id) || null
  }

  // 删除列表
  const deleteList = (id: string) => {
    const index = lists.value.findIndex(list => list.id === id)
    if (index > -1) {
      lists.value.splice(index, 1)
      if (currentList.value?.id === id) {
        currentList.value = null
      }
      saveToLocalStorage()
    }
  }

  // 保存到本地存储
  const saveToLocalStorage = () => {
    try {
      localStorage.setItem('awesome-lists', JSON.stringify(lists.value))
    } catch (error) {
      console.warn('保存到本地存储失败:', error)
    }
  }

  // 从本地存储加载
  const loadFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('awesome-lists')
      if (saved) {
        lists.value = JSON.parse(saved)
      }
    } catch (error) {
      console.warn('从本地存储加载失败:', error)
    }
  }

  // 生成ID
  const generateId = (): string => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  // 导出为Markdown文件
  const exportToMarkdown = (list: AwesomeListItem) => {
    const content = `# ${list.topic}\n\n${list.content}\n\n---\n*生成时间: ${new Date(list.createdAt).toLocaleString('zh-CN')}*\n*使用模型: ${list.model}*\n*处理时间: ${list.processingTime.toFixed(1)}秒*`
    
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `awesome-${list.topic.toLowerCase().replace(/\s+/g, '-')}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    URL.revokeObjectURL(url)
  }

  // 分享列表
  const shareList = async (list: AwesomeListItem) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Awesome ${list.topic}`,
          text: `查看这个AI生成的${list.topic}资源列表`,
          url: window.location.href
        })
      } catch (error) {
        console.log('分享失败:', error)
        copyToClipboard(window.location.href)
      }
    } else {
      copyToClipboard(window.location.href)
    }
  }

  // 复制到剪贴板
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      // 这里可以显示成功提示
    } catch (error) {
      console.error('复制失败:', error)
    }
  }

  // 初始化时加载数据
  loadFromLocalStorage()

  return {
    lists,
    currentList,
    recentLists,
    generateAwesomeList,
    getListById,
    deleteList,
    exportToMarkdown,
    shareList,
    loadFromLocalStorage
  }
}) 