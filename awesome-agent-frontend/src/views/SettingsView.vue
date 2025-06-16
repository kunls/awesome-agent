<template>
  <div>
    <!-- Page Header -->
    <div class="flex flex-wrap justify-between gap-3 p-4">
      <p class="text-[#111418] tracking-light text-[32px] font-bold leading-tight min-w-72">设置</p>
    </div>

    <!-- Appearance Section -->
    <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">外观设置</h3>
    <div class="flex flex-wrap gap-3 p-4">
      <label
        v-for="theme in themes"
        :key="theme.value"
        :class="[
          'text-sm font-medium leading-normal flex items-center justify-center rounded-lg border border-[#dbe0e6] px-4 h-11 text-[#111418] cursor-pointer transition-colors',
          settings.theme === theme.value 
            ? 'border-[3px] px-3.5 border-[#0c7ff2] bg-[#eff6ff]' 
            : 'hover:bg-[#f0f2f5]'
        ]"
      >
        {{ theme.label }}
        <input 
          v-model="settings.theme"
          type="radio" 
          :value="theme.value"
          class="invisible absolute" 
        />
      </label>
    </div>

    <!-- AI Model Settings -->
    <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">AI 模型设置</h3>
    <div class="bg-white rounded-lg border border-[#dbe0e6] mx-4 mb-4">
      <div class="p-4 space-y-4">
        <div>
          <label class="block text-sm font-medium text-[#111418] mb-2">默认模型</label>
          <select
            v-model="settings.defaultModel"
            class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
          >
            <option value="gpt">OpenAI GPT-4</option>
            <option value="deepseek">DeepSeek Chat</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-[#111418] mb-2">默认语言</label>
          <select
            v-model="settings.defaultLanguage"
            class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
          >
            <option value="zh">中文</option>
            <option value="en">English</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-[#111418] mb-2">默认结果数量</label>
          <input
            v-model.number="settings.defaultMaxResults"
            type="number"
            min="5"
            max="50"
            class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
          />
        </div>
      </div>
    </div>

    <!-- Notifications Section -->
    <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">通知设置</h3>
    <div class="px-4 space-y-1">
      <div v-for="notification in notificationSettings" :key="notification.key" class="py-3">
        <label class="flex gap-x-3 flex-row items-center">
          <input
            v-model="settings.notifications[notification.key]"
            type="checkbox"
            class="h-5 w-5 rounded border-[#dbe0e6] border-2 bg-transparent text-[#0c7ff2] checked:bg-[#0c7ff2] checked:border-[#0c7ff2] focus:ring-0 focus:ring-offset-0 focus:border-[#dbe0e6] focus:outline-none"
          />
          <div class="flex-1">
            <p class="text-[#111418] text-base font-normal leading-normal">{{ notification.label }}</p>
            <p class="text-[#60758a] text-sm font-normal leading-normal">{{ notification.description }}</p>
          </div>
        </label>
      </div>
    </div>

    <!-- Search Settings -->
    <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">搜索设置</h3>
    <div class="bg-white rounded-lg border border-[#dbe0e6] mx-4 mb-4">
      <div class="p-4 space-y-4">
        <div>
          <label class="flex gap-x-3 py-3 flex-row items-center">
            <input
              v-model="settings.autoSave"
              type="checkbox"
              class="h-5 w-5 rounded border-[#dbe0e6] border-2 bg-transparent text-[#0c7ff2] checked:bg-[#0c7ff2] checked:border-[#0c7ff2] focus:ring-0 focus:ring-offset-0 focus:border-[#dbe0e6] focus:outline-none"
            />
            <div class="flex-1">
              <p class="text-[#111418] text-base font-normal leading-normal">自动保存结果</p>
              <p class="text-[#60758a] text-sm font-normal leading-normal">自动保存搜索结果到历史记录</p>
            </div>
          </label>
        </div>

        <div>
          <label class="flex gap-x-3 py-3 flex-row items-center">
            <input
              v-model="settings.smartSearch"
              type="checkbox"
              class="h-5 w-5 rounded border-[#dbe0e6] border-2 bg-transparent text-[#0c7ff2] checked:bg-[#0c7ff2] checked:border-[#0c7ff2] focus:ring-0 focus:ring-offset-0 focus:border-[#dbe0e6] focus:outline-none"
            />
            <div class="flex-1">
              <p class="text-[#111418] text-base font-normal leading-normal">智能搜索建议</p>
              <p class="text-[#60758a] text-sm font-normal leading-normal">根据搜索历史提供智能建议</p>
            </div>
          </label>
        </div>

        <div>
          <label class="block text-sm font-medium text-[#111418] mb-2">搜索结果缓存时间 (小时)</label>
          <input
            v-model.number="settings.cacheHours"
            type="number"
            min="1"
            max="168"
            class="w-full px-3 py-2 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
          />
        </div>
      </div>
    </div>

    <!-- API Keys Section -->
    <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">API 密钥</h3>
    <div class="bg-white rounded-lg border border-[#dbe0e6] mx-4 mb-4">
      <div class="p-4 space-y-4">
        <div>
          <label class="block text-sm font-medium text-[#111418] mb-2">OpenAI API Key</label>
          <div class="relative">
            <input
              v-model="settings.apiKeys.openai"
              :type="showApiKeys.openai ? 'text' : 'password'"
              placeholder="sk-..."
              class="w-full px-3 py-2 pr-10 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
            />
            <button
              @click="showApiKeys.openai = !showApiKeys.openai"
              class="absolute right-2 top-1/2 transform -translate-y-1/2 text-[#60758a] hover:text-[#111418]"
            >
              <svg v-if="showApiKeys.openai" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-[#111418] mb-2">DeepSeek API Key</label>
          <div class="relative">
            <input
              v-model="settings.apiKeys.deepseek"
              :type="showApiKeys.deepseek ? 'text' : 'password'"
              placeholder="sk-..."
              class="w-full px-3 py-2 pr-10 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
            />
            <button
              @click="showApiKeys.deepseek = !showApiKeys.deepseek"
              class="absolute right-2 top-1/2 transform -translate-y-1/2 text-[#60758a] hover:text-[#111418]"
            >
              <svg v-if="showApiKeys.deepseek" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-[#111418] mb-2">Tavily API Key</label>
          <div class="relative">
            <input
              v-model="settings.apiKeys.tavily"
              :type="showApiKeys.tavily ? 'text' : 'password'"
              placeholder="tvly-..."
              class="w-full px-3 py-2 pr-10 border border-[#dbe0e6] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0c7ff2] focus:border-transparent"
            />
            <button
              @click="showApiKeys.tavily = !showApiKeys.tavily"
              class="absolute right-2 top-1/2 transform -translate-y-1/2 text-[#60758a] hover:text-[#111418]"
            >
              <svg v-if="showApiKeys.tavily" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Management -->
    <h3 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">数据管理</h3>
    <div class="px-4 space-y-2">
      <div class="flex items-center gap-4 bg-white px-4 min-h-[72px] py-2 rounded-lg border border-[#dbe0e6]">
        <div class="text-[#111418] flex items-center justify-center rounded-lg bg-[#f0f2f5] shrink-0 size-12">
          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
            <path d="M224,177.32V78.68a8,8,0,0,0-4.07-6.94l-88-50.54a8,8,0,0,0-7.86,0l-88,50.54A8,8,0,0,0,32,78.68v98.64a8,8,0,0,0,4.07,6.94l88,50.54a8,8,0,0,0,7.86,0l88-50.54A8,8,0,0,0,224,177.32ZM128,32.43,208,78.68v98.64L128,223.57,48,177.32V78.68Z"/>
          </svg>
        </div>
        <div class="flex flex-col justify-center flex-1">
          <p class="text-[#111418] text-base font-medium leading-normal line-clamp-1">导出数据</p>
          <p class="text-[#60758a] text-sm font-normal leading-normal line-clamp-2">导出所有搜索历史和设置</p>
        </div>
        <button
          @click="exportData"
          class="px-4 py-2 bg-[#0c7ff2] text-white rounded-lg hover:bg-[#0a6fd1] transition-colors"
        >
          导出
        </button>
      </div>

      <div class="flex items-center gap-4 bg-white px-4 min-h-[72px] py-2 rounded-lg border border-[#dbe0e6]">
        <div class="text-[#111418] flex items-center justify-center rounded-lg bg-[#f0f2f5] shrink-0 size-12">
          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
            <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,51.31,188.69,80H160ZM200,216H56V40h88V88a8,8,0,0,0,8,8h48V216Z"/>
          </svg>
        </div>
        <div class="flex flex-col justify-center flex-1">
          <p class="text-[#111418] text-base font-medium leading-normal line-clamp-1">导入数据</p>
          <p class="text-[#60758a] text-sm font-normal leading-normal line-clamp-2">从文件导入历史记录和设置</p>
        </div>
        <button
          @click="triggerImport"
          class="px-4 py-2 bg-[#f0f2f5] text-[#111418] rounded-lg hover:bg-[#e8eaed] transition-colors"
        >
          导入
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".json"
          @change="importData"
          class="hidden"
        />
      </div>

      <div class="flex items-center gap-4 bg-white px-4 min-h-[72px] py-2 rounded-lg border border-[#dbe0e6]">
        <div class="text-[#111418] flex items-center justify-center rounded-lg bg-[#fef2f2] shrink-0 size-12">
          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
            <path d="M216,48H40A16,16,0,0,0,24,64V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V64A16,16,0,0,0,216,48ZM40,64H216V88H40ZM40,192V104H216v88Z"/>
          </svg>
        </div>
        <div class="flex flex-col justify-center flex-1">
          <p class="text-[#111418] text-base font-medium leading-normal line-clamp-1">清除所有数据</p>
          <p class="text-[#60758a] text-sm font-normal leading-normal line-clamp-2">删除所有历史记录、书签和设置</p>
        </div>
        <button
          @click="confirmClearData"
          class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
        >
          清除
        </button>
      </div>
    </div>

    <!-- Save Button -->
    <div class="p-4">
      <button
        @click="saveSettings"
        :disabled="isSaving"
        class="w-full bg-[#0c7ff2] text-white py-3 px-6 rounded-lg font-medium hover:bg-[#0a6fd1] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <div v-if="isSaving" class="flex items-center justify-center">
          <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          保存中...
        </div>
        <span v-else>保存设置</span>
      </button>
    </div>

    <!-- Success Toast -->
    <div
      v-if="showSuccessToast"
      class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300"
      :class="showSuccessToast ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'"
    >
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
        设置已保存
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

// Reactive data
const isSaving = ref(false)
const showSuccessToast = ref(false)
const fileInput = ref<HTMLInputElement>()

const showApiKeys = reactive({
  openai: false,
  deepseek: false,
  tavily: false
})

const settings = reactive({
  theme: 'light',
  defaultModel: 'gpt',
  defaultLanguage: 'zh',
  defaultMaxResults: 20,
  autoSave: true,
  smartSearch: true,
  cacheHours: 24,
  notifications: {
    email: false,
    inApp: true,
    completions: true,
    errors: true
  },
  apiKeys: {
    openai: '',
    deepseek: '',
    tavily: ''
  }
})

const themes = [
  { label: '浅色', value: 'light' },
  { label: '深色', value: 'dark' },
  { label: '跟随系统', value: 'system' }
]

const notificationSettings = [
  {
    key: 'email',
    label: '邮件通知',
    description: '通过邮件接收重要更新和完成通知'
  },
  {
    key: 'inApp',
    label: '应用内通知',
    description: '在应用内显示通知消息'
  },
  {
    key: 'completions',
    label: '完成通知',
    description: '当搜索完成时接收通知'
  },
  {
    key: 'errors',
    label: '错误通知',
    description: '当发生错误时接收通知'
  }
]

// Methods
const saveSettings = async () => {
  isSaving.value = true
  
  try {
    // Save to localStorage
    localStorage.setItem('awesomeAgentSettings', JSON.stringify(settings))
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Show success toast
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
    
  } catch (error) {
    console.error('保存设置失败:', error)
  } finally {
    isSaving.value = false
  }
}

const exportData = () => {
  try {
    const data = {
      settings: settings,
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `awesome-agent-data-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('导出数据失败:', error)
  }
}

const triggerImport = () => {
  fileInput.value?.click()
}

const importData = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target?.result as string)
      if (data.settings) {
        Object.assign(settings, data.settings)
        saveSettings()
      }
    } catch (error) {
      console.error('导入数据失败:', error)
    }
  }
  reader.readAsText(file)
}

const confirmClearData = () => {
  if (confirm('确定要清除所有数据吗？此操作不可恢复。')) {
    clearAllData()
  }
}

const clearAllData = () => {
  try {
    localStorage.removeItem('awesomeAgentSettings')
    localStorage.removeItem('awesomeAgentHistory')
    localStorage.removeItem('bookmarkedItems')
    
    // Reset settings to defaults
    Object.assign(settings, {
      theme: 'light',
      defaultModel: 'gpt',
      defaultLanguage: 'zh',
      defaultMaxResults: 20,
      autoSave: true,
      smartSearch: true,
      cacheHours: 24,
      notifications: {
        email: false,
        inApp: true,
        completions: true,
        errors: true
      },
      apiKeys: {
        openai: '',
        deepseek: '',
        tavily: ''
      }
    })
    
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
    
  } catch (error) {
    console.error('清除数据失败:', error)
  }
}

// Lifecycle
onMounted(() => {
  // Load settings from localStorage
  const saved = localStorage.getItem('awesomeAgentSettings')
  if (saved) {
    try {
      const savedSettings = JSON.parse(saved)
      Object.assign(settings, savedSettings)
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
})
</script>

<style scoped>
/* 自定义复选框样式 */
input[type="checkbox"]:checked {
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
}

/* 单选按钮的选中状态 */
input[type="radio"]:checked + label {
  border-width: 3px;
  border-color: #0c7ff2;
  background-color: #eff6ff;
}

/* 输入框焦点状态 */
input:focus, select:focus {
  box-shadow: 0 0 0 2px rgba(12, 127, 242, 0.1);
}

/* 动画效果 */
.transition-colors {
  transition: all 0.2s ease;
}

/* Toast 动画 */
.transform {
  transform-origin: bottom right;
}
</style> 