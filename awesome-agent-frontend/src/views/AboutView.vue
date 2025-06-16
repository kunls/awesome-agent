<template>
  <div>
    <!-- Hero Section -->
    <div class="flex flex-col gap-10 px-4 py-10 @container">
      <div class="flex flex-col gap-4">
        <h1
          class="text-[#111418] text-4xl font-black leading-tight tracking-[-0.033em] @[480px]:text-5xl @[480px]:font-black @[480px]:leading-tight @[480px]:tracking-[-0.033em]"
        >
          关于 Awesome List Agent
        </h1>
        <p class="text-[#60758a] text-base font-normal leading-normal @[480px]:text-lg @[480px]:font-normal @[480px]:leading-normal">
          基于人工智能的学术资源智能整理工具，让知识发现变得简单高效
        </p>
      </div>
    </div>

    <!-- Product Overview -->
    <div class="@container">
      <div class="flex flex-col gap-6 px-4 py-6 @[480px]:gap-8 @[480px]:px-6 @[480px]:py-8">
        <h2 class="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] @[480px]:text-2xl @[480px]:font-bold @[480px]:leading-tight @[480px]:tracking-[-0.015em]">
          产品概述
        </h2>
        
        <div class="grid grid-cols-1 gap-3 @[480px]:grid-cols-2 @[768px]:grid-cols-3">
          <div v-for="feature in features" :key="feature.title" class="flex flex-col gap-3 pb-3">
            <div
              class="w-fit bg-center bg-no-repeat aspect-video bg-cover rounded-xl flex flex-col"
              :style="`background-image: url('${feature.image}');`"
            >
              <div class="flex-1 flex items-end p-4">
                <div class="bg-white/90 backdrop-blur-sm rounded-lg p-3 w-full">
                  <div class="flex items-center gap-3">
                    <div class="text-[#111418] flex items-center justify-center rounded-lg bg-[#f0f2f5] shrink-0 size-10">
                      <component :is="feature.icon" class="w-5 h-5" />
                    </div>
                    <div>
                      <p class="text-[#111418] text-base font-medium leading-normal line-clamp-1">{{ feature.title }}</p>
                      <p class="text-[#60758a] text-sm font-normal leading-normal line-clamp-2">{{ feature.description }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Features -->
    <div class="@container">
      <div class="flex flex-col gap-6 px-4 py-6 @[480px]:gap-8 @[480px]:px-6 @[480px]:py-8">
        <h2 class="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] @[480px]:text-2xl @[480px]:font-bold @[480px]:leading-tight @[480px]:tracking-[-0.015em]">
          核心功能
        </h2>
        
        <div class="grid grid-cols-1 gap-3 @[480px]:grid-cols-2">
          <div v-for="coreFeature in coreFeatures" :key="coreFeature.title" class="flex items-center gap-4 bg-white px-4 min-h-[72px] py-2 rounded-xl border border-[#dce0e5]">
            <div class="text-[#111418] flex items-center justify-center rounded-lg bg-[#f0f2f5] shrink-0 size-12">
              <component :is="coreFeature.icon" class="w-6 h-6" />
            </div>
            <div class="flex flex-col justify-center">
              <p class="text-[#111418] text-base font-medium leading-normal line-clamp-1">{{ coreFeature.title }}</p>
              <p class="text-[#60758a] text-sm font-normal leading-normal line-clamp-2">{{ coreFeature.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Technology Stack -->
    <div class="@container">
      <div class="flex flex-col gap-6 px-4 py-6 @[480px]:gap-8 @[480px]:px-6 @[480px]:py-8">
        <h2 class="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] @[480px]:text-2xl @[480px]:font-bold @[480px]:leading-tight @[480px]:tracking-[-0.015em]">
          技术架构
        </h2>
        
        <div class="flex flex-wrap gap-3">
          <div v-for="tech in technologies" :key="tech.name" class="flex h-8 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-[#f0f2f5] pl-4 pr-4">
            <p class="text-[#111418] text-sm font-medium leading-normal">{{ tech.name }}</p>
            <span class="text-[#60758a] text-xs">{{ tech.version }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics -->
    <div class="@container">
      <div class="flex flex-col gap-6 px-4 py-6 @[480px]:gap-8 @[480px]:px-6 @[480px]:py-8">
        <h2 class="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] @[480px]:text-2xl @[480px]:font-bold @[480px]:leading-tight @[480px]:tracking-[-0.015em]">
          项目数据
        </h2>
        
        <div class="grid grid-cols-2 gap-3 @[480px]:grid-cols-4">
          <div v-for="stat in statistics" :key="stat.label" class="flex flex-col gap-1 rounded-xl border border-[#dce0e5] bg-white p-6">
            <p class="text-[#111418] text-2xl font-bold leading-tight tracking-[-0.015em]">{{ stat.value }}</p>
            <p class="text-[#60758a] text-sm font-normal leading-normal">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Development Progress -->
    <div class="@container">
      <div class="flex flex-col gap-6 px-4 py-6 @[480px]:gap-8 @[480px]:px-6 @[480px]:py-8">
        <h2 class="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] @[480px]:text-2xl @[480px]:font-bold @[480px]:leading-tight @[480px]:tracking-[-0.015em]">
          开发进度
        </h2>
        
        <div class="flex flex-col gap-4">
          <div v-for="progress in developmentProgress" :key="progress.module" class="flex flex-col gap-2">
            <div class="flex justify-between items-center">
              <p class="text-[#111418] text-base font-medium leading-normal">{{ progress.module }}</p>
              <p class="text-[#60758a] text-sm font-normal leading-normal">{{ progress.percentage }}%</p>
            </div>
            <div class="bg-[#f0f2f5] rounded-full h-2 w-full">
              <div 
                class="bg-[#0c7ff2] h-2 rounded-full transition-all duration-500"
                :style="`width: ${progress.percentage}%`"
              ></div>
            </div>
            <p class="text-[#60758a] text-sm font-normal leading-normal">{{ progress.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Information -->
    <div class="@container">
      <div class="flex flex-col gap-6 px-4 py-6 @[480px]:gap-8 @[480px]:px-6 @[480px]:py-8">
        <h2 class="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] @[480px]:text-2xl @[480px]:font-bold @[480px]:leading-tight @[480px]:tracking-[-0.015em]">
          联系我们
        </h2>
        
        <div class="grid grid-cols-1 gap-3 @[480px]:grid-cols-2 @[768px]:grid-cols-3">
          <div v-for="contact in contacts" :key="contact.type" class="flex items-center gap-4 bg-white px-4 min-h-[72px] py-2 rounded-xl border border-[#dce0e5]">
            <div class="text-[#111418] flex items-center justify-center rounded-lg bg-[#f0f2f5] shrink-0 size-12">
              <component :is="contact.icon" class="w-6 h-6" />
            </div>
            <div class="flex flex-col justify-center">
              <p class="text-[#111418] text-base font-medium leading-normal line-clamp-1">{{ contact.type }}</p>
              <p class="text-[#60758a] text-sm font-normal leading-normal line-clamp-2">{{ contact.value }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="@container">
      <div class="flex flex-col gap-6 px-4 py-6 @[480px]:gap-8 @[480px]:px-6 @[480px]:py-8">
        <div class="flex flex-col gap-2 text-center">
          <p class="text-[#60758a] text-sm font-normal leading-normal">
            © 2024 Awesome List Agent. 使用 Vue.js + FastAPI 构建
          </p>
          <p class="text-[#60758a] text-sm font-normal leading-normal">
            开源项目，欢迎贡献代码和反馈意见
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Icons as components
const SearchIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"></path>
  </svg>`
}

const BrainIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M248,124a56.11,56.11,0,0,0-32-50.61V72a48,48,0,0,0-88-26.49A48,48,0,0,0,40,72v1.39a56,56,0,0,0,0,101.22V176a48,48,0,0,0,88,26.49A48,48,0,0,0,216,176v-1.39A56.11,56.11,0,0,0,248,124ZM88,208a32,32,0,0,1-32-32V72a32,32,0,0,1,64,0v32a16,16,0,0,0,16,16h32v64a32,32,0,0,1-32,32Zm144-32a32,32,0,0,1-64,0V104a16,16,0,0,0-16-16H120V72a32,32,0,0,1,64,0v1.39a56.11,56.11,0,0,0,32,50.61v48A56.11,56.11,0,0,0,232,176Z"></path>
  </svg>`
}

const DocumentIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,51.31,188.69,80H160ZM200,216H56V40h88V88a8,8,0,0,0,8,8h48V216Z"></path>
  </svg>`
}

const CodeIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M69.12,94.15,28.5,128l40.62,33.85a8,8,0,1,1-10.24,12.29l-48-40a8,8,0,0,1,0-12.29l48-40a8,8,0,0,1,10.24,12.3Zm176,27.7-48-40a8,8,0,1,0-10.24,12.3L227.5,128l-40.62,33.85a8,8,0,1,0,10.24,12.29l48-40a8,8,0,0,0,0-12.29ZM162.73,32.48a8,8,0,0,0-10.25,4.79l-64,176a8,8,0,0,0,4.79,10.26A8.14,8.14,0,0,0,96,224a8,8,0,0,0,7.52-5.27l64-176A8,8,0,0,0,162.73,32.48Z"></path>
  </svg>`
}

const RocketIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M152,224a8,8,0,0,1-8,8H112a8,8,0,0,1,0-16h32A8,8,0,0,1,152,224ZM128,112a12,12,0,1,0-12-12A12,12,0,0,0,128,112Zm95.62-96.78A22.91,22.91,0,0,0,208,8c-44.25,0-80,22.25-103.87,64.32L83.66,103.85l-40.5,12.18A16,16,0,0,0,37,137.85l1.84,3.26c.67,1.19,1.33,2.37,2,3.51a16,16,0,0,0,22,6.33L80,143.46l16.46,16.46-7.49,17.11a16,16,0,0,0,6.33,22c1.14.64,2.32,1.3,3.51,2l3.26,1.84A16,16,0,0,0,118.15,219l12.18-40.5,31.53-20.47C204.78,134.16,227,99,227,56A22.91,22.91,0,0,0,223.62,15.22ZM208,40a16,16,0,1,1-16,16A16,16,0,0,1,208,40Z"></path>
  </svg>`
}

const StatsIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M232,208a8,8,0,0,1-8,8H32a8,8,0,0,1-8-8V48a8,8,0,0,1,16,0V156.69l50.34-50.35a8,8,0,0,1,11.32,0L128,132.69,180.69,80H160a8,8,0,0,1,0-16h40a8,8,0,0,1,8,8V112a8,8,0,0,1-16,0V91.31L133.66,149.66a8,8,0,0,1-11.32,0L96,123.31,48,171.31V200H224A8,8,0,0,1,232,208Z"></path>
  </svg>`
}

const EmailIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M224,48H32a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A8,8,0,0,0,224,48ZM203.43,64,128,133.15,52.57,64ZM216,192H40V74.19l82.59,75.71a8,8,0,0,0,10.82,0L216,74.19V192Z"></path>
  </svg>`
}

const GithubIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M208.31,75.68A59.78,59.78,0,0,0,202.93,28,8,8,0,0,0,196,24a59.75,59.75,0,0,0-48,24H124A59.75,59.75,0,0,0,76,24a8,8,0,0,0-6.93,4,59.78,59.78,0,0,0-5.38,47.68A58.14,58.14,0,0,0,56,104v8a56.06,56.06,0,0,0,48.44,55.47A39.8,39.8,0,0,0,96,192v8H72a24,24,0,0,1-24-24A40,40,0,0,0,8,136a8,8,0,0,0,0,16,24,24,0,0,1,24,24,40,40,0,0,0,40,40H96v16a8,8,0,0,0,16,0V192a24,24,0,0,1,48,0v40a8,8,0,0,0,16,0V192a39.8,39.8,0,0,0-8.44-24.53A56.06,56.06,0,0,0,216,112v-8A58.14,58.14,0,0,0,208.31,75.68ZM200,112a40,40,0,0,1-40,40H112a40,40,0,0,1-40-40v-8a41.74,41.74,0,0,1,6.9-22.48A8,8,0,0,0,80,73.83a43.81,43.81,0,0,1,.79-33.58,43.88,43.88,0,0,1,32.32,20.06A8,8,0,0,0,119.82,64h32.35a8,8,0,0,0,6.74-3.69,43.87,43.87,0,0,1,32.32-20.06A43.81,43.81,0,0,1,192,73.83a8.09,8.09,0,0,0,1,7.65A41.72,41.72,0,0,1,200,104Z"></path>
  </svg>`
}

const WebIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24ZM101.63,168h52.74C149,186.34,140,202.87,128,215.89,116,202.87,107,186.34,101.63,168ZM98,152a145.72,145.72,0,0,1,0-48h60a145.72,145.72,0,0,1,0,48ZM40,128a87.61,87.61,0,0,1,3.33-24H81.79a161.79,161.79,0,0,0,0,48H43.33A87.61,87.61,0,0,1,40,128ZM154.37,88H101.63C107,69.66,116,53.13,128,40.11,140,53.13,149,69.66,154.37,88Zm19.84,16h38.46a88.15,88.15,0,0,1,0,48H174.21a161.79,161.79,0,0,0,0-48Zm32.16-16H170.94a142.39,142.39,0,0,0-20.26-45A88.37,88.37,0,0,1,206.37,88ZM105.32,43A142.39,142.39,0,0,0,85.06,88H49.63A88.37,88.37,0,0,1,105.32,43ZM49.63,168H85.06a142.39,142.39,0,0,0,20.26,45A88.37,88.37,0,0,1,49.63,168Zm101.05,45a142.39,142.39,0,0,0,20.26-45h35.43A88.37,88.37,0,0,1,150.68,213Z"></path>
  </svg>`
}

// Data
const features = ref([
  {
    title: '智能搜索',
    description: '基于AI的语义搜索',
    image: 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400&h=200&fit=crop',
    icon: SearchIcon
  },
  {
    title: 'AI驱动',
    description: '集成多种大语言模型',
    image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=200&fit=crop',
    icon: BrainIcon
  },
  {
    title: '智能整理',
    description: '自动生成结构化列表',
    image: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=400&h=200&fit=crop',
    icon: DocumentIcon
  }
])

const coreFeatures = ref([
  {
    title: '学术论文搜索',
    description: '从arXiv等权威数据库搜索最新学术论文',
    icon: SearchIcon
  },
  {
    title: '代码仓库发现',
    description: '发现GitHub上相关的高质量开源项目',
    icon: CodeIcon
  },
  {
    title: '智能分类整理',
    description: '自动将搜索结果按类型和重要性分类',
    icon: DocumentIcon
  },
  {
    title: 'Markdown导出',
    description: '生成标准的Awesome List格式文档',
    icon: RocketIcon
  }
])

const technologies = ref([
  { name: 'Vue.js', version: '3.4' },
  { name: 'TypeScript', version: '5.0' },
  { name: 'Tailwind CSS', version: '3.4' },
  { name: 'FastAPI', version: '0.104' },
  { name: 'Python', version: '3.11' },
  { name: 'LangChain', version: '0.1' },
  { name: 'OpenAI', version: 'GPT-4' },
  { name: 'DeepSeek', version: 'Chat' }
])

const statistics = ref([
  { label: '代码行数', value: '5000+' },
  { label: 'API接口', value: '12' },
  { label: '支持模型', value: '2' },
  { label: '完成度', value: '90%' }
])

const developmentProgress = ref([
  {
    module: '后端API服务',
    percentage: 95,
    description: '核心搜索和AI处理功能已完成'
  },
  {
    module: 'Vue.js前端',
    percentage: 85,
    description: '用户界面和交互功能基本完成'
  },
  {
    module: '用户系统',
    percentage: 30,
    description: '用户认证和个人数据管理开发中'
  },
  {
    module: '数据分析',
    percentage: 60,
    description: '搜索统计和用户行为分析功能'
  }
])

const contacts = ref([
  {
    type: '邮箱',
    value: 'contact@awesome-agent.com',
    icon: EmailIcon
  },
  {
    type: 'GitHub',
    value: 'github.com/awesome-agent',
    icon: GithubIcon
  },
  {
    type: '官网',
    value: 'www.awesome-agent.com',
    icon: WebIcon
  }
])
</script>

<style scoped>
/* 渐变背景效果 */
.bg-gradient-to-r {
  background: linear-gradient(to right, #0c7ff2, #1e40af);
}

/* 卡片悬停效果 */
.hover\:scale-105:hover {
  transform: scale(1.05);
}

/* 进度条动画 */
@keyframes progressFill {
  from {
    width: 0%;
  }
  to {
    width: var(--progress-width);
  }
}

/* 平滑过渡 */
.transition-all {
  transition: all 0.3s ease;
}

/* 容器查询支持 */
@container (min-width: 480px) {
  .@\[480px\]\:text-5xl {
    font-size: 3rem;
  }
  
  .@\[480px\]\:text-lg {
    font-size: 1.125rem;
  }
}

@container (min-width: 768px) {
  .@\[768px\]\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style> 