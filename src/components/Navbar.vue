<template>
  <header class="sticky top-0 z-50 bg-white shadow-sm transition-all duration-300" id="navbar">
    <div class="container mx-auto px-4 py-3 flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <i class="fa-solid fa-recycle text-primary text-2xl"></i>
        <h1 class="text-xl font-bold text-neutral-600">{{ title }}</h1>
      </div>
      <nav class="hidden md:flex space-x-6">
        <router-link to="/" class="text-neutral-500 hover:text-primary transition-colors" :class="{ 'text-primary font-medium': $route.path === '/' }">首页</router-link>
        <router-link to="/estimate" class="text-neutral-500 hover:text-primary transition-colors" :class="{ 'text-primary font-medium': $route.path === '/estimate' }">估价</router-link>
        <router-link to="/pre-booking" class="text-neutral-500 hover:text-primary transition-colors" :class="{ 'text-primary font-medium': $route.path === '/pre-booking' }">预约上门</router-link>
        <router-link to="/questions" class="text-neutral-500 hover:text-primary transition-colors" :class="{ 'text-primary font-medium': $route.path === '/questions' }">常见问题</router-link>
        <router-link to="/contact" class="text-neutral-500 hover:text-primary transition-colors" :class="{ 'text-primary font-medium': $route.path === '/contact' }">联系我们</router-link>
      </nav>
      <button class="md:hidden text-neutral-600 focus:outline-none" @click="toggleMenu">
        <i class="fa-solid fa-bars text-xl" v-if="!menuOpen"></i>
        <i class="fa-solid fa-times text-xl" v-else></i>
      </button>
    </div>
    <!-- 移动端菜单 -->
    <div class="md:hidden bg-white shadow-md absolute w-full left-0 top-full transform -translate-y-full opacity-0 transition-all duration-300 z-40"
         :class="{ 'opacity-0 -translate-y-full pointer-events-none': !menuOpen, 'opacity-100 translate-y-0 pointer-events-auto': menuOpen }"
         id="mobileMenu">
      <div class="container mx-auto px-4 py-2 flex flex-col space-y-3">
        <router-link to="/" class="py-2 px-4 hover:bg-neutral-100 rounded-lg transition-colors" :class="{ 'bg-primary/10 text-primary font-medium': $route.path === '/' }">首页</router-link>
        <router-link to="/estimate" class="py-2 px-4 hover:bg-neutral-100 rounded-lg transition-colors" :class="{ 'bg-primary/10 text-primary font-medium': $route.path === '/estimate' }">估价</router-link>
        <router-link to="/pre-booking" class="py-2 px-4 hover:bg-neutral-100 rounded-lg transition-colors" :class="{ 'bg-primary/10 text-primary font-medium': $route.path === '/pre-booking' }">预约上门</router-link>
        <router-link to="/questions" class="py-2 px-4 hover:bg-neutral-100 rounded-lg transition-colors" :class="{ 'bg-primary/10 text-primary font-medium': $route.path === '/questions' }">常见问题</router-link>
        <router-link to="/contact" class="py-2 px-4 hover:bg-neutral-100 rounded-lg transition-colors" :class="{ 'bg-primary/10 text-primary font-medium': $route.path === '/contact' }">联系我们</router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '长发估价'
  }
})

const menuOpen = ref(false)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}
</script>

<style scoped>
/* 导航栏样式已经通过Tailwind实现 */
</style>