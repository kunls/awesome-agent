# Awesome List Agent 前端设置指南

## 1. 创建Vue3项目环境

请在项目根目录下执行以下命令：

```bash
# 创建Vue3项目
npm create vue@latest frontend

# 选择以下选项：
# ✔ Project name: frontend
# ✔ Add TypeScript? Yes
# ✔ Add JSX Support? No
# ✔ Add Vue Router for Single Page Application development? Yes
# ✔ Add Pinia for state management? Yes
# ✔ Add Vitest for Unit Testing? No
# ✔ Add an End-to-End Testing Solution? No
# ✔ Add ESLint for code quality? Yes
# ✔ Add Prettier for code formatting? Yes

# 进入前端目录
cd frontend

# 安装依赖
npm install

# 安装Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 安装额外依赖
npm install marked axios lucide-vue-next
```

## 2. 配置Tailwind CSS

修改 `frontend/tailwind.config.js`：
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
```

在 `frontend/src/style.css` 中添加：
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 自定义样式 */
.markdown-content {
  @apply prose prose-lg max-w-none;
}

.markdown-content h1 {
  @apply text-3xl font-bold text-gray-900 mb-4;
}

.markdown-content h2 {
  @apply text-2xl font-semibold text-gray-800 mb-3;
}

.markdown-content h3 {
  @apply text-xl font-medium text-gray-700 mb-2;
}

.markdown-content ul {
  @apply list-disc list-inside mb-4;
}

.markdown-content li {
  @apply mb-1;
}

.markdown-content a {
  @apply text-blue-600 hover:text-blue-800 underline;
}

.markdown-content p {
  @apply mb-4 text-gray-700;
}

.markdown-content code {
  @apply bg-gray-100 px-1 py-0.5 rounded text-sm font-mono;
}
```

## 3. 启动开发

设置完成后，运行：
```bash
cd frontend
npm run dev
```

前端将在 `http://localhost:5173` 运行
后端在 `http://localhost:8000` 运行

## 4. 核心功能

前端将包含以下页面和功能：
- 🏠 主页：主题输入和模型选择
- 📝 生成页面：显示生成过程和结果
- 💾 历史记录：查看之前生成的列表
- ⚙️ 设置：API配置和偏好设置
- 📊 统计：使用统计和性能数据

## 5. 技术栈

- **Vue 3** + **TypeScript** - 前端框架
- **Tailwind CSS** - 样式框架  
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP客户端
- **Marked** - Markdown渲染
- **Lucide Vue** - 图标库 