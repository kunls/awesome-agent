<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-2">
              <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">A</span>
              </div>
              <span class="text-xl font-bold text-gray-900">Awesome Agent</span>
            </router-link>
          </div>

          <!-- 桌面导航 -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link
              to="/"
              class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600': $route.name === 'Home' }"
            >
              <Home class="w-4 h-4 inline mr-1" />
              首页
            </router-link>
            
            <router-link
              to="/history"
              class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600': $route.name === 'History' }"
            >
              <Clock class="w-4 h-4 inline mr-1" />
              历史
            </router-link>
            
            <router-link
              to="/settings"
              class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600': $route.name === 'Settings' }"
            >
              <Settings class="w-4 h-4 inline mr-1" />
              设置
            </router-link>
          </div>

          <!-- 移动端菜单按钮 -->
          <div class="md:hidden flex items-center">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="text-gray-700 hover:text-blue-600 p-2"
            >
              <Menu v-if="!mobileMenuOpen" class="w-6 h-6" />
              <X v-else class="w-6 h-6" />
            </button>
          </div>
        </div>

        <!-- 移动端导航 -->
        <div v-if="mobileMenuOpen" class="md:hidden py-4 space-y-2">
          <router-link
            to="/"
            @click="mobileMenuOpen = false"
            class="block text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600': $route.name === 'Home' }"
          >
            <Home class="w-4 h-4 inline mr-2" />
            首页
          </router-link>
          
          <router-link
            to="/history"
            @click="mobileMenuOpen = false"
            class="block text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600': $route.name === 'History' }"
          >
            <Clock class="w-4 h-4 inline mr-2" />
            历史
          </router-link>
          
          <router-link
            to="/settings"
            @click="mobileMenuOpen = false"
            class="block text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600': $route.name === 'Settings' }"
          >
            <Settings class="w-4 h-4 inline mr-2" />
            设置
          </router-link>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>

    <!-- 全局加载遮罩 -->
    <div
      v-if="isLoading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-sm mx-4">
        <div class="flex items-center space-x-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <div>
            <div class="font-medium text-gray-900">正在处理...</div>
            <div class="text-sm text-gray-600">{{ loadingMessage || '请稍候' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stagewise Toolbar (Development Only) -->
    <StagewiseToolbar v-if="isDevelopment" :config="stagewiseConfig" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Home, Clock, Settings, Menu, X } from 'lucide-vue-next'
import { useAppStore } from './stores/app'
import { StagewiseToolbar } from '@stagewise/toolbar-vue'

const appStore = useAppStore()

const mobileMenuOpen = ref(false)

const isLoading = computed(() => appStore.isLoading)
const loadingMessage = computed(() => appStore.loadingMessage)

// Stagewise configuration (development only)
const stagewiseConfig = {
  plugins: []
}

const isDevelopment = import.meta.env.DEV
</script>

<style>
/* 全局样式已在main.css中定义 */
</style>
