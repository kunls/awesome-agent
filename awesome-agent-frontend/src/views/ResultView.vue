<template>
  <div>
    <!-- Page Header -->
    <div class="flex flex-wrap justify-between gap-3 p-4">
      <p class="text-[#111418] tracking-light text-[32px] font-bold leading-tight min-w-72">
        "{{ topic }}" 的精选资源列表
      </p>
      <div class="flex gap-3">
        <button
          @click="downloadMarkdown"
          class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#0c7ff2] text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-[#0a6fd1] transition-colors"
        >
          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"/>
          </svg>
          下载 Markdown
        </button>
        <button
          @click="copyToClipboard"
          class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#f0f2f5] text-[#111418] text-sm font-bold leading-normal tracking-[0.015em] hover:bg-[#e8eaed] transition-colors"
        >
          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/>
            <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"/>
          </svg>
          复制内容
        </button>
      </div>
    </div>



    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="w-8 h-8 border-2 border-[#0c7ff2] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-[#60758a] text-sm">正在加载结果...</p>
      </div>
    </div>

    <!-- Results Content -->
    <div v-else-if="result" class="space-y-6">
      <!-- Keywords -->
      <div v-if="displayKeywords.length > 0" class="px-4">
        <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] mb-3">
          <svg class="w-5 h-5 inline mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M9.243 3.03a1 1 0 01.727 1.213L9.53 6h2.94l.56-2.243a1 1 0 111.94.486L14.53 6H17a1 1 0 110 2h-2.97l-1 4H15a1 1 0 110 2h-2.47l-.56 2.242a1 1 0 11-1.94-.485L10.47 14H7.53l-.56 2.242a1 1 0 11-1.94-.485L5.47 14H3a1 1 0 110-2h2.97l1-4H5a1 1 0 110-2h2.47l.56-2.243a1 1 0 011.213-.727zM9.03 8l-1 4h2.94l1-4H9.03z" clip-rule="evenodd"/>
          </svg>
          相关关键词
        </h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(keyword, index) in displayKeywords"
            :key="`${keyword}-${index}`"
            :class="[
              'px-3 py-1.5 text-sm rounded-full font-medium transition-colors cursor-default',
              getKeywordStyle(index)
            ]"
          >
            {{ keyword }}
          </span>
        </div>
      </div>

      <!-- Markdown Content Display -->
      <div class="bg-white rounded-lg border border-[#dbe0e6] mx-4">
        <div class="p-6">
          <div 
            class="markdown-content prose prose-lg max-w-none"
            v-html="renderedMarkdown"
          ></div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="mt-8 p-4 bg-[#f9fafb] rounded-lg border border-[#f0f2f5] mx-4">
        <h3 class="text-[#111418] text-sm font-medium mb-3">生成信息</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div class="text-[#111418] text-lg font-bold">{{ result.totalResults || 0 }}</div>
            <div class="text-[#60758a] text-xs">搜索结果</div>
          </div>
          <div>
            <div class="text-[#111418] text-lg font-bold">{{ result.model || 'GPT' }}</div>
            <div class="text-[#60758a] text-xs">使用模型</div>
          </div>
          <div>
            <div class="text-[#111418] text-lg font-bold">{{ displayKeywords.length }}</div>
            <div class="text-[#60758a] text-xs">关键词数</div>
          </div>
          <div>
            <div class="text-[#111418] text-lg font-bold">{{ formatTime(result.processingTime) }}</div>
            <div class="text-[#60758a] text-xs">生成用时</div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-between px-4 py-4">
        <router-link
          to="/"
          class="flex items-center text-[#60758a] hover:text-[#111418] transition-colors"
        >
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd"/>
          </svg>
          返回生成新列表
        </router-link>

        <div class="flex items-center space-x-3">
          <button
            @click="regenerate"
            class="px-4 py-2 bg-[#0c7ff2] text-white rounded-lg hover:bg-[#0a6fd1] transition-colors"
          >
            <svg class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/>
            </svg>
            重新生成
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <div class="w-16 h-16 bg-[#f0f2f5] rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-[#60758a]" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
        </svg>
      </div>
      <h3 class="text-[#111418] text-lg font-medium mb-2">暂无结果</h3>
      <p class="text-[#60758a] text-sm">未找到相关的 Awesome List</p>
      <router-link
        to="/"
        class="inline-flex items-center px-4 py-2 bg-[#0c7ff2] text-white rounded-lg hover:bg-[#0a6fd1] transition-colors mt-4"
      >
        返回首页
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAwesomeListStore } from '@/stores/awesomeList'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const store = useAwesomeListStore()

// Reactive data
const isLoading = ref(false)

// Props
interface Props {
  result?: any
}

const props = withDefaults(defineProps<Props>(), {
  result: null
})

// Computed properties
const topic = computed(() => {
  if (route.query.topic) {
    return route.query.topic as string
  }
  if (props.result?.topic) {
    return props.result.topic
  }
  return '未知主题'
})

const result = computed(() => {
  if (props.result) {
    return props.result
  }
  
  // 如果有路由参数ID，尝试从store获取
  if (route.params.id) {
    const list = store.getListById(route.params.id as string)
    return list
  }
  
  // 否则使用当前列表
  return store.currentList
})

const displayKeywords = computed(() => {
  if (!result.value?.keywords) return []
  
  let keywordsArray: string[] = []
  
  // 如果keywords是字符串，尝试解析
  if (typeof result.value.keywords === 'string') {
    const rawKeywords = result.value.keywords.trim()
    
    // 移除各种格式标记和包装
    let cleanKeywords = rawKeywords
      .replace(/```json\s*/g, '')  // 移除 ```json
      .replace(/```\s*/g, '')      // 移除 ```
      .replace(/^json\s*/gi, '')   // 移除开头的 json
      .replace(/`/g, '')           // 移除反引号
      .trim()
    
    // 处理多种可能的格式
    try {
      // 1. 尝试直接解析JSON数组格式
      if (cleanKeywords.startsWith('[') && cleanKeywords.endsWith(']')) {
        const parsed = JSON.parse(cleanKeywords)
        if (Array.isArray(parsed)) {
          keywordsArray = parsed.map((k: any) => String(k).trim()).filter((k: string) => k)
        }
      }
      // 2. 尝试解析JSON对象格式 {"keywords": [...]}
      else if (cleanKeywords.startsWith('{') && cleanKeywords.includes('keywords')) {
        const parsed = JSON.parse(cleanKeywords)
        if (parsed.keywords && Array.isArray(parsed.keywords)) {
          keywordsArray = parsed.keywords.map((k: any) => String(k).trim()).filter((k: string) => k)
        }
      }
      // 3. 如果包含多个JSON对象或混合格式，尝试提取
      else if (cleanKeywords.includes('{') || cleanKeywords.includes('[')) {
        // 提取所有JSON数组
        const jsonArrayMatches = cleanKeywords.match(/\[([^\]]*)\]/g)
        if (jsonArrayMatches) {
          for (const match of jsonArrayMatches) {
            try {
              const parsed = JSON.parse(match)
              if (Array.isArray(parsed)) {
                keywordsArray.push(...parsed.map((k: any) => String(k).trim()).filter((k: string) => k))
              }
            } catch (e) {
              // 忽略解析失败的数组
            }
          }
        }
        
        // 提取JSON对象中的keywords字段
        const jsonObjectMatches = cleanKeywords.match(/\{[^}]*"keywords"[^}]*\}/g)
        if (jsonObjectMatches) {
          for (const match of jsonObjectMatches) {
            try {
              const parsed = JSON.parse(match)
              if (parsed.keywords && Array.isArray(parsed.keywords)) {
                keywordsArray.push(...parsed.keywords.map((k: any) => String(k).trim()).filter((k: string) => k))
              }
            } catch (e) {
              // 忽略解析失败的对象
            }
          }
        }
        
        // 如果上述方法都没找到关键词，尝试手动提取引号内容
        if (keywordsArray.length === 0) {
          const quotedMatches = cleanKeywords.match(/"([^"]+)"/g)
          if (quotedMatches) {
            keywordsArray = quotedMatches.map((match: string) => match.replace(/"/g, '').trim()).filter((k: string) => k)
          }
        }
      }
      // 4. 按行分割处理（处理换行分隔的关键词）
      else {
        const lines = cleanKeywords.split('\n').map((line: string) => line.trim()).filter((line: string) => line)
        for (const line of lines) {
          // 移除列表标记
          const cleanLine = line.replace(/^[-*+]\s*/, '').trim()
          if (cleanLine) {
            keywordsArray.push(cleanLine)
          }
        }
        
        // 如果没有找到换行，尝试逗号分割
        if (keywordsArray.length === 0) {
          keywordsArray = cleanKeywords
            .split(',')
            .map((k: string) => k.trim())
            .filter((k: string) => k.length > 0)
        }
      }
    } catch (e) {
      console.warn('关键词解析失败，使用后备方案:', e)
      // 后备方案：按行和逗号分割
      const lines = cleanKeywords.split(/[\n,]/).map((line: string) => line.trim()).filter((line: string) => line)
      keywordsArray = lines.map((line: string) => line.replace(/^[-*+]\s*/, '').trim()).filter((k: string) => k)
    }
  }
  
  // 如果已经是数组
  if (Array.isArray(result.value.keywords)) {
    keywordsArray = result.value.keywords.map((k: any) => String(k).trim()).filter((k: string) => k)
  }
  
  // 增强的过滤和清理逻辑
  return keywordsArray
    .filter(keyword => {
      if (typeof keyword !== 'string') return false
      const cleaned = keyword.trim()
      
      // 过滤掉空字符串、过短或过长的词
      if (cleaned.length < 1 || cleaned.length > 50) return false
      
      // 过滤掉纯符号和格式标记
      if (/^[{}\[\]"'`,;:\s]*$/.test(cleaned)) return false
      
      // 过滤掉代码相关词汇
      if (/^(json|markdown|code|html|css|js|xml|yaml|sql)$/i.test(cleaned)) return false
      
      // 过滤掉看起来像技术格式的内容
      if (/^[\w-]+:\/\//.test(cleaned)) return false  // URL
      if (/^\{\s*"/.test(cleaned)) return false       // JSON对象开头
      if (/^```/.test(cleaned)) return false          // 代码块标记
      
      // 过滤掉重复的标点符号
      if (/^[.,:;!?]{2,}$/.test(cleaned)) return false
      
      return true
    })
    .map(keyword => {
      // 清理关键词
      return keyword
        .trim()
        .replace(/^[-*+]\s*/, '')  // 移除列表标记
        .replace(/["""'']/g, '')   // 移除各种引号
        .replace(/^(\w+):?\s*/, '$1') // 清理冒号
        .trim()
    })
    .filter(keyword => keyword.length > 0) // 再次过滤空字符串
    // 去重（忽略大小写）
    .filter((keyword, index, array) => 
      array.findIndex((k: string) => k.toLowerCase() === keyword.toLowerCase()) === index
    )
    // 限制数量，避免显示过多关键词
    .slice(0, 10)
})

const renderedMarkdown = computed(() => {
  if (!result.value?.content) return '<p>暂无内容</p>'
  
  try {
    // 配置marked选项
    marked.setOptions({
      gfm: true,
      breaks: true,
    })
    
    return marked(result.value.content)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return `<pre>${result.value.content}</pre>`
  }
})

// Methods
const getKeywordStyle = (index: number) => {
  const styles = [
    'bg-[#eff6ff] text-[#0c7ff2] hover:bg-[#dbeafe]',
    'bg-[#f0f9ff] text-[#0284c7] hover:bg-[#e0f2fe]',
    'bg-[#ecfdf5] text-[#059669] hover:bg-[#dcfce7]',
    'bg-[#fef3c7] text-[#d97706] hover:bg-[#fed7aa]',
    'bg-[#f3e8ff] text-[#7c3aed] hover:bg-[#e9d5ff]',
    'bg-[#fecaca] text-[#dc2626] hover:bg-[#fee2e2]',
    'bg-[#f1f5f9] text-[#64748b] hover:bg-[#e2e8f0]',
    'bg-[#fef2f2] text-[#991b1b] hover:bg-[#fee2e2]'
  ]
  return styles[index % styles.length]
}

const formatTime = (time: number) => {
  if (!time) return '0s'
  if (time < 60) return `${time.toFixed(1)}s`
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes}m ${seconds}s`
}

const downloadMarkdown = () => {
  if (!result.value?.content) return
  
  const filename = `awesome-${topic.value.replace(/\s+/g, '-').toLowerCase()}.md`
  const blob = new Blob([result.value.content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const copyToClipboard = async () => {
  if (!result.value?.content) return
  
  try {
    await navigator.clipboard.writeText(result.value.content)
    // TODO: 显示成功提示
    console.log('内容已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
  }
}

const regenerate = () => {
  if (result.value?.topic) {
    router.push({
      name: 'Home',
      query: { topic: result.value.topic }
    })
  } else {
    router.push({ name: 'Home' })
  }
}

// Lifecycle
onMounted(() => {
  // 如果通过路由参数访问但没有找到对应的列表，显示加载状态
  if (route.params.id && !result.value) {
    isLoading.value = true
    // 尝试重新加载数据
    store.loadFromLocalStorage()
    setTimeout(() => {
      isLoading.value = false
    }, 1000)
  }
})
</script>

<style scoped>
/* Markdown内容样式 */
.markdown-content :deep(h1) {
  @apply text-2xl font-bold text-gray-900 mb-4 mt-6 first:mt-0;
}

.markdown-content :deep(h2) {
  @apply text-xl font-semibold text-gray-800 mb-3 mt-5 first:mt-0;
}

.markdown-content :deep(h3) {
  @apply text-lg font-medium text-gray-700 mb-2 mt-4 first:mt-0;
}

.markdown-content :deep(p) {
  @apply text-gray-600 mb-3 leading-relaxed;
}

.markdown-content :deep(ul) {
  @apply list-disc list-inside mb-4 space-y-1;
}

.markdown-content :deep(ol) {
  @apply list-decimal list-inside mb-4 space-y-1;
}

.markdown-content :deep(li) {
  @apply text-gray-600 leading-relaxed;
}

.markdown-content :deep(a) {
  @apply text-blue-600 hover:text-blue-800 underline;
}

.markdown-content :deep(code) {
  @apply bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm font-mono;
}

.markdown-content :deep(pre) {
  @apply bg-gray-100 text-gray-800 p-4 rounded-lg overflow-x-auto mb-4;
}

.markdown-content :deep(pre code) {
  @apply bg-transparent p-0;
}

.markdown-content :deep(blockquote) {
  @apply border-l-4 border-gray-300 pl-4 italic text-gray-600 mb-4;
}

.markdown-content :deep(table) {
  @apply min-w-full table-auto mb-4;
}

.markdown-content :deep(th) {
  @apply bg-gray-100 px-4 py-2 text-left font-medium text-gray-700;
}

.markdown-content :deep(td) {
  @apply px-4 py-2 text-gray-600 border-b border-gray-200;
}

/* 动画效果 */
.transition-colors {
  transition: all 0.2s ease;
}
</style> 