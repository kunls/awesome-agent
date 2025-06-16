<template>
  <div class="relative flex size-full min-h-screen flex-col bg-white group/design-root overflow-x-hidden" style='font-family: "Work Sans", "Noto Sans", sans-serif;'>
    <div class="layout-container flex h-full grow flex-col">
      <!-- Header Navigation -->
      <header class="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#f0f2f5] px-10 py-3">
        <div class="flex items-center gap-4 text-[#111418]">
          <div class="size-4">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <g clip-path="url(#clip0_6_330)">
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z"
                  fill="currentColor"
                ></path>
              </g>
              <defs>
                <clipPath id="clip0_6_330"><rect width="48" height="48" fill="white"></rect></clipPath>
              </defs>
            </svg>
          </div>
          <h2 class="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em]">Awesome List Agent</h2>
        </div>
        <div class="flex flex-1 justify-end gap-8">
          <div class="flex items-center gap-9">
            <router-link class="text-[#111418] text-sm font-medium leading-normal hover:text-[#0c7ff2] transition-colors" to="/">主页</router-link>
            <router-link class="text-[#111418] text-sm font-medium leading-normal hover:text-[#0c7ff2] transition-colors" to="/history">我的列表</router-link>
            <router-link class="text-[#111418] text-sm font-medium leading-normal hover:text-[#0c7ff2] transition-colors" to="/settings">设置</router-link>
          </div>
          <div class="flex items-center gap-3">
            <!-- Search Bar for non-home pages -->
            <div v-if="$route.path !== '/'" class="flex items-center">
              <label class="flex flex-col min-w-40 !h-10 max-w-64">
                <div class="flex w-full flex-1 items-stretch rounded-lg h-full">
                  <div
                    class="text-[#60758a] flex border-none bg-[#f0f2f5] items-center justify-center pl-4 rounded-l-lg border-r-0"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20px" height="20px" fill="currentColor" viewBox="0 0 256 256">
                      <path
                        d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"
                      ></path>
                    </svg>
                  </div>
                  <input
                    v-model="quickSearchTerm"
                    @keyup.enter="performQuickSearch"
                    placeholder="快速搜索"
                    class="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#111418] focus:outline-0 focus:ring-0 border-none bg-[#f0f2f5] focus:border-none h-full placeholder:text-[#60758a] px-4 rounded-l-none border-l-0 pl-2 text-sm font-normal leading-normal"
                  />
                </div>
              </label>
            </div>
            
            <!-- Notification Bell -->
            <button
              class="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 bg-[#f0f2f5] text-[#111418] gap-2 text-sm font-bold leading-normal tracking-[0.015em] min-w-0 px-2.5 hover:bg-[#e8eaed] transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20px" height="20px" fill="currentColor" viewBox="0 0 256 256">
                <path
                  d="M221.8,175.94C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,0,0,78.38,0H208a16,16,0,0,0,13.8-24.06ZM128,216a24,24,0,0,1-22.62-16h45.24A24,24,0,0,1,128,216ZM48,184c7.7-13.24,16-43.92,16-80a64,64,0,1,1,128,0c0,36.05,8.28,66.73,16,80Z"
                ></path>
              </svg>
            </button>
            
            <!-- User Avatar -->
            <div
              class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 cursor-pointer hover:ring-2 hover:ring-[#0c7ff2] transition-all"
              style='background-image: url("https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face")'
            ></div>
          </div>
        </div>
      </header>

      <!-- Main Content Area -->
      <div class="flex flex-1 justify-center py-5" :class="[$route.path === '/' ? 'px-40' : 'px-10']">
        <div class="layout-content-container flex flex-col max-w-[960px] flex-1">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const quickSearchTerm = ref('')

const performQuickSearch = () => {
  if (quickSearchTerm.value.trim()) {
    router.push({
      path: '/',
      query: { search: quickSearchTerm.value.trim() }
    })
  }
}
</script>

<style scoped>
/* 添加一些自定义样式 */
.router-link-active {
  color: #0c7ff2 !important;
  font-weight: 600;
}

/* 确保图标在不同状态下的颜色一致 */
svg {
  transition: all 0.2s ease;
}

/* 添加 hover 效果 */
button:hover svg,
.hover\:text-\[\#0c7ff2\]:hover svg {
  transform: scale(1.05);
}

/* 优化搜索框的焦点状态 */
input:focus {
  background-color: #ffffff !important;
  box-shadow: 0 0 0 2px rgba(12, 127, 242, 0.1);
}
</style>
