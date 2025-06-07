<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">生成历史</h1>
      <button
        v-if="lists.length > 0"
        @click="clearHistory"
        class="px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
      >
        <Trash2 class="w-4 h-4 inline mr-1" />
        清空历史
      </button>
    </div>

    <!-- 筛选和排序 -->
    <div v-if="lists.length > 0" class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <select
          v-model="filterModel"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">所有模型</option>
          <option value="gpt">GPT-4</option>
          <option value="deepseek">DeepSeek</option>
        </select>
        
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索主题..."
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <select
        v-model="sortBy"
        class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="date">按时间排序</option>
        <option value="topic">按主题排序</option>
        <option value="results">按结果数排序</option>
        <option value="time">按处理时间排序</option>
      </select>
    </div>

    <!-- 列表展示 -->
    <div v-if="filteredLists.length > 0" class="space-y-4">
      <div
        v-for="list in filteredLists"
        :key="list.id"
        class="bg-white rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
        @click="viewList(list)"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 mb-1">
                {{ list.topic }}
              </h3>
              <div class="flex items-center space-x-4 text-sm text-gray-600">
                <span class="flex items-center">
                  <Calendar class="w-4 h-4 mr-1" />
                  {{ formatDate(list.createdAt) }}
                </span>
                <span class="flex items-center">
                  <Clock class="w-4 h-4 mr-1" />
                  {{ list.processingTime.toFixed(1) }}秒
                </span>
                <span class="flex items-center">
                  <Database class="w-4 h-4 mr-1" />
                  {{ list.totalResults }}个结果
                </span>
                <span class="flex items-center">
                  <Bot class="w-4 h-4 mr-1" />
                  {{ list.model }}
                </span>
              </div>
            </div>
            
            <div class="flex items-center space-x-2 ml-4">
              <button
                @click.stop="exportList(list)"
                class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title="导出"
              >
                <Download class="w-4 h-4" />
              </button>
              
              <button
                @click.stop="deleteList(list.id)"
                class="p-2 text-gray-400 hover:text-red-600 transition-colors"
                title="删除"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <!-- 关键词预览 -->
          <div class="flex flex-wrap gap-2 mb-3">
            <span
              v-for="keyword in list.keywords.slice(0, 4)"
              :key="keyword"
              class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {{ keyword }}
            </span>
            <span
              v-if="list.keywords.length > 4"
              class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
            >
              +{{ list.keywords.length - 4 }}更多
            </span>
          </div>
          
          <!-- 内容预览 -->
          <div class="text-sm text-gray-600 line-clamp-2">
            {{ getContentPreview(list.content) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="lists.length === 0" class="text-center py-12">
      <div class="text-gray-400 mb-4">
        <History class="w-16 h-16 mx-auto" />
      </div>
      <h2 class="text-xl font-semibold text-gray-900 mb-2">暂无生成历史</h2>
      <p class="text-gray-600 mb-4">开始生成您的第一个Awesome List吧！</p>
      <router-link
        to="/"
        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Plus class="w-4 h-4 mr-1" />
        开始生成
      </router-link>
    </div>

    <!-- 筛选结果为空 -->
    <div v-else class="text-center py-12">
      <div class="text-gray-400 mb-4">
        <Search class="w-16 h-16 mx-auto" />
      </div>
      <h2 class="text-xl font-semibold text-gray-900 mb-2">未找到匹配结果</h2>
      <p class="text-gray-600 mb-4">尝试调整筛选条件或搜索关键词</p>
      <button
        @click="clearFilters"
        class="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
      >
        清除筛选
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Calendar, Clock, Database, Bot, Download, Trash2,
  History, Plus, Search
} from 'lucide-vue-next'
import { useAwesomeListStore } from '../stores/awesomeList'

const router = useRouter()
const awesomeListStore = useAwesomeListStore()

const filterModel = ref('')
const searchQuery = ref('')
const sortBy = ref('date')

const lists = computed(() => awesomeListStore.lists)

const filteredLists = computed(() => {
  let filtered = lists.value

  // 模型筛选
  if (filterModel.value) {
    filtered = filtered.filter(list => 
      list.model.toLowerCase().includes(filterModel.value.toLowerCase())
    )
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(list =>
      list.topic.toLowerCase().includes(query) ||
      list.keywords.some(keyword => keyword.toLowerCase().includes(query))
    )
  }

  // 排序
  filtered = [...filtered].sort((a, b) => {
    switch (sortBy.value) {
      case 'topic':
        return a.topic.localeCompare(b.topic)
      case 'results':
        return b.totalResults - a.totalResults
      case 'time':
        return a.processingTime - b.processingTime
      case 'date':
      default:
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    }
  })

  return filtered
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getContentPreview = (content: string) => {
  // 移除markdown标记并截取前150个字符
  const plainText = content
    .replace(/#{1,6}\s+/g, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/`(.*?)`/g, '$1')
    .replace(/\n+/g, ' ')
    .trim()
  
  return plainText.length > 150 ? plainText.slice(0, 150) + '...' : plainText
}

const viewList = (list: any) => {
  router.push({
    name: 'Result',
    params: { id: list.id }
  })
}

const exportList = (list: any) => {
  awesomeListStore.exportToMarkdown(list)
}

const deleteList = (id: string) => {
  if (confirm('确定要删除这个列表吗？')) {
    awesomeListStore.deleteList(id)
  }
}

const clearHistory = () => {
  if (confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
    // 清空所有列表
    lists.value.forEach(list => awesomeListStore.deleteList(list.id))
  }
}

const clearFilters = () => {
  filterModel.value = ''
  searchQuery.value = ''
  sortBy.value = 'date'
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 