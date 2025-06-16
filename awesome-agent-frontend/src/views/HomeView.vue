<template>
  <div class="@container">
    <div class="@[480px]:p-4">
      <div
        class="flex min-h-[480px] flex-col gap-6 bg-cover bg-center bg-no-repeat @[480px]:gap-8 @[480px]:rounded-lg items-center justify-center p-4"
        style='background-image: linear-gradient(rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.4) 100%), url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&h=600&fit=crop")'
      >
        <div class="flex flex-col gap-2 text-center">
          <h1
            class="text-white text-4xl font-black leading-tight tracking-[-0.033em] @[480px]:text-5xl @[480px]:font-black @[480px]:leading-tight @[480px]:tracking-[-0.033em]"
          >
            轻松发现和整理学术资源
          </h1>
          <h2 class="text-white text-sm font-normal leading-normal @[480px]:text-base @[480px]:font-normal @[480px]:leading-normal">
            Awesome List Agent 是您的智能内容整理工具。只需输入您感兴趣的主题，我们将自动搜索相关的文献、代码库、工具等资源，并生成类似 GitHub Awesome Lists 的 Markdown 格式列表。
          </h2>
        </div>
        
        <!-- Main Search Box -->
        <label class="flex flex-col min-w-40 h-14 w-full max-w-[480px] @[480px]:h-16">
          <div class="flex w-full flex-1 items-stretch rounded-lg h-full">
            <div
              class="text-[#60758a] flex border border-[#dbe0e6] bg-white items-center justify-center pl-[15px] rounded-l-lg border-r-0"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20px" height="20px" fill="currentColor" viewBox="0 0 256 256">
                <path
                  d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"
                ></path>
              </svg>
            </div>
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              placeholder="输入主题 (例如: 机器学习, Web开发, Vue.js)"
              class="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#111418] focus:outline-0 focus:ring-0 border border-[#dbe0e6] bg-white focus:border-[#0c7ff2] h-full placeholder:text-[#60758a] px-[15px] rounded-r-none border-r-0 pr-2 rounded-l-none border-l-0 pl-2 text-sm font-normal leading-normal @[480px]:text-base @[480px]:font-normal @[480px]:leading-normal"
            />
            <div class="flex items-center justify-center rounded-r-lg border-l-0 border border-[#dbe0e6] bg-white pr-[7px]">
              <button
                @click="handleSearch"
                :disabled="isGenerating"
                class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 @[480px]:h-12 @[480px]:px-5 bg-[#0c7ff2] text-white text-sm font-bold leading-normal tracking-[0.015em] @[480px]:text-base @[480px]:font-bold @[480px]:leading-normal @[480px]:tracking-[0.015em] hover:bg-[#0a6fd1] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="!isGenerating" class="truncate">搜索</span>
                <div v-else class="flex items-center gap-2">
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span class="truncate">处理中...</span>
                </div>
              </button>
            </div>
          </div>
        </label>
      </div>
    </div>
  </div>

  <!-- Advanced Options -->
  <div class="mt-8 p-4">
    <details class="rounded-lg border border-[#dbe0e6] bg-white">
      <summary class="cursor-pointer p-4 font-medium text-[#111418] hover:bg-[#f0f2f5] transition-colors">
        高级选项
      </summary>
      <div class="p-4 pt-0 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Model Selection -->
          <div>
            <label class="block text-sm font-medium text-[#111418] mb-2">AI 模型</label>
            <select
              v-model="selectedModel"
              class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
            >
              <option value="gpt">OpenAI GPT-4</option>
              <option value="deepseek">DeepSeek Chat</option>
            </select>
          </div>

          <!-- Language Selection -->
          <div>
            <label class="block text-sm font-medium text-[#111418] mb-2">输出语言</label>
            <select
              v-model="selectedLanguage"
              class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
            >
              <option value="zh">中文</option>
              <option value="en">English</option>
            </select>
          </div>

          <!-- Max Results -->
          <div>
            <label class="block text-sm font-medium text-[#111418] mb-2">最大结果数</label>
            <input
              v-model.number="maxResults"
              type="number"
              min="5"
              max="50"
              class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
            />
          </div>

          <!-- Search Mode -->
          <div>
            <label class="block text-sm font-medium text-[#111418] mb-2">搜索模式</label>
            <select
              v-model="searchMode"
              class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
            >
              <option value="traditional">传统搜索 (快速)</option>
              <option value="intelligent">智能搜索 (深度)</option>
            </select>
          </div>
        </div>
      </div>
    </details>
  </div>

  <!-- Quick Start Examples -->
  <div class="mt-8 p-4">
    <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] mb-4">热门搜索示例</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      <button
        v-for="example in examples"
        :key="example.query"
        @click="searchQuery = example.query; handleSearch()"
        class="flex flex-col items-start p-4 rounded-lg border border-[#dbe0e6] bg-white hover:bg-[#f0f2f5] transition-colors text-left"
      >
        <div class="text-[#111418] mb-1" v-html="example.icon"></div>
        <div class="font-medium text-[#111418] text-sm">{{ example.query }}</div>
        <div class="text-[#60758a] text-xs mt-1">{{ example.description }}</div>
      </button>
    </div>
  </div>

  <!-- Progress Display -->
  <div v-if="isGenerating && progress.length > 0" class="mt-8 p-4">
    <div class="bg-white rounded-lg border border-[#dbe0e6] p-6">
      <h3 class="text-[#111418] text-lg font-semibold mb-4">生成进度</h3>
      <div class="space-y-3">
        <div
          v-for="(step, index) in progress"
          :key="index"
          class="flex items-center gap-3"
        >
          <div class="flex-shrink-0">
            <div v-if="step.status === 'completed'" class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <div v-else-if="step.status === 'processing'" class="w-5 h-5 border-2 border-[#0c7ff2] border-t-transparent rounded-full animate-spin"></div>
            <div v-else class="w-5 h-5 bg-gray-300 rounded-full"></div>
          </div>
          <div class="flex-1">
            <div class="text-sm font-medium text-[#111418]">{{ step.title }}</div>
            <div class="text-xs text-[#60758a]">{{ step.description }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Results Display -->
  <div v-if="result && !isGenerating" class="mt-8">
    <ResultView :result="result" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ResultView from './ResultView.vue'
import { useAwesomeListStore } from '@/stores/awesomeList'

const router = useRouter()
const route = useRoute()
const store = useAwesomeListStore()

// Reactive data
const searchQuery = ref('')
const selectedModel = ref('gpt')
const selectedLanguage = ref('zh')
const maxResults = ref(20)
const searchMode = ref('traditional')
const isGenerating = ref(false)
const result = ref(null)

const progress = reactive([
  { title: '主题扩展', description: '分析搜索主题，生成相关关键词', status: 'pending' },
  { title: '资源搜索', description: '在 arXiv、GitHub 等平台搜索相关资源', status: 'pending' },
  { title: '内容筛选', description: '智能筛选和排序搜索结果', status: 'pending' },
  { title: '列表生成', description: '生成结构化的 Awesome List', status: 'pending' }
])

const examples = [
  {
    query: 'Vue.js',
    description: '前端框架相关资源',
    icon: '<svg class="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L1 7l11 5 11-5-11-5z"/><path d="M1 17l11 5 11-5M1 12l11 5 11-5"/></svg>'
  },
  {
    query: '机器学习',
    description: '人工智能和机器学习',
    icon: '<svg class="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>'
  },
  {
    query: 'Python',
    description: 'Python 编程资源',
    icon: '<svg class="w-6 h-6 text-yellow-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'
  },
  {
    query: '深度学习',
    description: '神经网络和深度学习',
    icon: '<svg class="w-6 h-6 text-purple-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>'
  },
  {
    query: 'React',
    description: 'React 生态系统',
    icon: '<svg class="w-6 h-6 text-cyan-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>'
  },
  {
    query: '区块链',
    description: '区块链技术和加密货币',
    icon: '<svg class="w-6 h-6 text-orange-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'
  }
]

// Methods
const resetProgress = () => {
  progress.forEach(step => {
    step.status = 'pending'
  })
}

const updateProgress = (stepIndex: number, status: string) => {
  if (stepIndex < progress.length) {
    progress[stepIndex].status = status
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim() || isGenerating.value) return

  isGenerating.value = true
  result.value = null
  resetProgress()

  try {
    // Update progress steps
    updateProgress(0, 'processing')
    await new Promise(resolve => setTimeout(resolve, 1000))
    updateProgress(0, 'completed')

    updateProgress(1, 'processing')
    await new Promise(resolve => setTimeout(resolve, 2000))
    updateProgress(1, 'completed')

    updateProgress(2, 'processing')
    await new Promise(resolve => setTimeout(resolve, 1500))
    updateProgress(2, 'completed')

    updateProgress(3, 'processing')
    
         // Call the API
     const requestData = {
       topic: searchQuery.value.trim(),
       model: selectedModel.value,
       language: selectedLanguage.value,
       maxResults: maxResults.value
     }

     const response = await store.generateAwesomeList(requestData)
     
     updateProgress(3, 'completed')
     result.value = response as any

    // Navigate to results
    router.push({
      name: 'Result',
      query: {
        topic: searchQuery.value.trim(),
        model: selectedModel.value,
        language: selectedLanguage.value,
        mode: searchMode.value
      }
    })

  } catch (error) {
    console.error('生成失败:', error)
    // Handle error - could show a toast or error message
  } finally {
    isGenerating.value = false
  }
}

// Handle URL query parameter for pre-filling search
onMounted(() => {
  if (route.query.search) {
    searchQuery.value = route.query.search as string
  }
})

// Watch for query changes and auto-search if needed
watch(
  () => route.query.search,
  (newSearch) => {
    if (newSearch && typeof newSearch === 'string') {
      searchQuery.value = newSearch
      handleSearch()
    }
  }
)
</script>

<style scoped>
/* Container queries support */
@container (min-width: 480px) {
  .responsive-text {
    font-size: 1.125rem;
  }
}

/* 优化搜索框的样式 */
.form-input:focus {
  box-shadow: 0 0 0 2px rgba(12, 127, 242, 0.1);
}

/* 示例卡片的 hover 效果 */
button:hover .text-\[\#111418\] {
  color: #0c7ff2;
}

/* 进度指示器动画 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 