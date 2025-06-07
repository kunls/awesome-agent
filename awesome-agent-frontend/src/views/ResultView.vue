<template>
  <div v-if="currentList" class="space-y-6">
    <!-- 头部信息 -->
    <div class="bg-white rounded-xl shadow-sm border p-6">
      <div class="flex items-start justify-between mb-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">
            {{ currentList.topic }}
          </h1>
          <div class="flex items-center space-x-4 text-sm text-gray-600">
            <span class="flex items-center">
              <Clock class="w-4 h-4 mr-1" />
              {{ formatDate(currentList.createdAt) }}
            </span>
            <span class="flex items-center">
              <Zap class="w-4 h-4 mr-1" />
              {{ currentList.processingTime.toFixed(1) }}秒
            </span>
            <span class="flex items-center">
              <Database class="w-4 h-4 mr-1" />
              {{ currentList.totalResults }}个结果
            </span>
            <span class="flex items-center">
              <Bot class="w-4 h-4 mr-1" />
              {{ currentList.model }}
            </span>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <button
            @click="copyContent"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="复制内容"
          >
            <Copy class="w-4 h-4" />
          </button>
          
          <button
            @click="exportMarkdown"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="导出Markdown"
          >
            <Download class="w-4 h-4" />
          </button>
          
          <button
            @click="shareList"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="分享"
          >
            <Share2 class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- 关键词 -->
      <div v-if="validKeywords.length > 0" class="flex flex-wrap gap-2">
        <span
          v-for="keyword in validKeywords"
          :key="keyword"
          class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
        >
          {{ keyword }}
        </span>
      </div>
      <div v-else class="text-sm text-gray-500">
        暂无关键词
      </div>
    </div>

    <!-- 视图切换 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <button
          @click="viewMode = 'preview'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            viewMode === 'preview'
              ? 'bg-blue-600 text-white'
              : 'text-gray-700 hover:bg-gray-100'
          ]"
        >
          <Eye class="w-4 h-4 inline mr-1" />
          预览
        </button>
        
        <button
          @click="viewMode = 'markdown'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            viewMode === 'markdown'
              ? 'bg-blue-600 text-white'
              : 'text-gray-700 hover:bg-gray-100'
          ]"
        >
          <Code class="w-4 h-4 inline mr-1" />
          Markdown
        </button>
      </div>

      <div class="text-sm text-gray-500">
        共 {{ contentStats.lines }} 行 • {{ contentStats.words }} 词 • {{ contentStats.chars }} 字符
      </div>
    </div>

    <!-- 内容展示 -->
    <div class="bg-white rounded-xl shadow-sm border">
      <!-- 预览模式 -->
      <div v-if="viewMode === 'preview'" class="p-6">
        <div 
          class="markdown-content prose prose-lg max-w-none"
          v-html="renderedMarkdown"
        ></div>
      </div>

      <!-- Markdown模式 -->
      <div v-else class="relative">
        <pre class="p-6 bg-gray-50 text-sm font-mono overflow-x-auto rounded-xl"><code>{{ currentList.content }}</code></pre>
        
        <button
          @click="copyMarkdown"
          class="absolute top-4 right-4 p-2 bg-white border border-gray-200 text-gray-500 hover:text-gray-700 rounded-lg transition-colors"
          title="复制Markdown"
        >
          <Copy class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex items-center justify-between">
      <router-link
        to="/"
        class="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft class="w-4 h-4 mr-1" />
        返回生成新列表
      </router-link>

      <div class="flex items-center space-x-3">
        <button
          @click="regenerate"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw class="w-4 h-4 inline mr-1" />
          重新生成
        </button>
      </div>
    </div>
  </div>

  <!-- 加载状态 -->
  <div v-else-if="isLoading" class="flex items-center justify-center py-12">
    <div class="text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600">正在加载...</p>
    </div>
  </div>

  <!-- 未找到 -->
  <div v-else class="text-center py-12">
    <div class="text-gray-400 mb-4">
      <FileX class="w-16 h-16 mx-auto" />
    </div>
    <h2 class="text-xl font-semibold text-gray-900 mb-2">未找到列表</h2>
    <p class="text-gray-600 mb-4">请检查链接是否正确，或者重新生成。</p>
    <router-link
      to="/"
      class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
    >
      <ArrowLeft class="w-4 h-4 mr-1" />
      返回首页
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import {
  Clock, Zap, Database, Bot, Copy, Download, Share2,
  Eye, Code, ArrowLeft, RefreshCw, FileX
} from 'lucide-vue-next'
import { useAwesomeListStore } from '../stores/awesomeList'
import { useAppStore } from '../stores/app'

const route = useRoute()
const router = useRouter()
const awesomeListStore = useAwesomeListStore()
const appStore = useAppStore()

const viewMode = ref<'preview' | 'markdown'>('preview')

const currentList = computed(() => {
  const id = route.params.id as string
  return awesomeListStore.getListById(id)
})

const isLoading = computed(() => appStore.isLoading)

const validKeywords = computed(() => {
  if (!currentList.value?.keywords) return []
  
  let keywords = currentList.value.keywords
  
  // 如果keywords是字符串，尝试解析JSON或提取关键词
  if (typeof keywords === 'string') {
    // 完全清理markdown标记和无关字符
    let cleanedString = keywords
      .replace(/```json/g, '')
      .replace(/```/g, '')
      .replace(/\n/g, ' ')
      .trim()
    
    // 如果清理后为空，直接返回空数组
    if (!cleanedString || cleanedString === 'json') {
      return []
    }
    
    try {
      // 查找JSON对象或数组
      const jsonMatch = cleanedString.match(/\{[^}]*\}|\[[^\]]*\]/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        if (parsed.keywords && Array.isArray(parsed.keywords)) {
          keywords = parsed.keywords
        } else if (Array.isArray(parsed)) {
          keywords = parsed
        }
      } else {
        return []
      }
    } catch (error) {
      // 如果所有解析都失败，返回空数组
      return []
    }
  }
  
  // 确保keywords是数组且每个元素都是字符串
  if (Array.isArray(keywords)) {
    return keywords.filter(keyword => 
      typeof keyword === 'string' && 
      keyword.trim().length > 0 &&
      keyword.length < 50 && // 过滤异常长的文本
      !keyword.includes('```') // 确保不包含markdown标记
    )
  }
  
  return []
})

const renderedMarkdown = computed(() => {
  if (!currentList.value) return ''
  return marked(currentList.value.content)
})

const contentStats = computed(() => {
  if (!currentList.value) return { lines: 0, words: 0, chars: 0 }
  
  const content = currentList.value.content
  const lines = content.split('\n').length
  const words = content.split(/\s+/).filter(word => word.length > 0).length
  const chars = content.length
  
  return { lines, words, chars }
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const copyContent = async () => {
  if (!currentList.value) return
  
  try {
    await navigator.clipboard.writeText(currentList.value.content)
    // 显示成功提示
  } catch (error) {
    console.error('复制失败:', error)
  }
}

const copyMarkdown = () => {
  copyContent()
}

const exportMarkdown = () => {
  if (currentList.value) {
    awesomeListStore.exportToMarkdown(currentList.value)
  }
}

const shareList = () => {
  if (currentList.value) {
    awesomeListStore.shareList(currentList.value)
  }
}

const regenerate = () => {
  if (currentList.value) {
    router.push({
      name: 'Home',
      query: { topic: currentList.value.topic }
    })
  }
}

onMounted(() => {
  // 如果没有找到列表，可能需要从服务器加载
  if (!currentList.value) {
    // 这里可以添加从服务器获取列表的逻辑
  }
})
</script>

<style scoped>
.markdown-content {
  /* Markdown渲染样式在全局CSS中定义 */
}
</style> 