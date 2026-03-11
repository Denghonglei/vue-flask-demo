<template>
  <div class="bg-neutral-100 font-sans min-h-screen">
    <Navbar title="常见问题" />

    <main class="container mx-auto px-4 py-8 md:py-12">
      <div class="max-w-3xl mx-auto">
        <div class="text-center mb-8">
          <h2 class="text-3xl font-bold text-neutral-700 mb-3">常见问题解答</h2>
          <p class="text-neutral-500">这里整理了大家最常问的问题，希望能帮到您</p>
        </div>

        <!-- 搜索框 -->
        <div class="mb-8">
          <div class="relative">
            <input type="text" id="search-input" v-model="searchKeyword" placeholder="搜索您想了解的问题..."
                   class="w-full px-4 py-3 pl-12 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                   @keypress.enter="searchQAs">
            <i class="fa-solid fa-magnifying-glass absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400"></i>
            <button id="search-button" @click="searchQAs"
                    class="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-primary hover:bg-primary/90 text-white rounded-md transition-all">
              搜索
            </button>
          </div>
        </div>

        <!-- 问答列表 -->
        <div id="qa-list" class="space-y-4 mb-8">
          <div class="bg-white rounded-xl shadow-sm overflow-hidden transition-all hover:shadow-md" v-for="(item, index) in qaList" :key="index">
            <div class="question cursor-pointer p-4 flex justify-between items-center font-medium text-neutral-700"
                 @click="toggleQuestion(index)"
                 :class="{ 'open': activeIndex === index }">
              <span>{{ item.key }}</span>
              <i class="fa-solid fa-chevron-right text-primary transition-transform"></i>
            </div>
            <div class="answer p-4 bg-neutral-50 text-neutral-600 border-t border-neutral-100 leading-relaxed"
                 v-if="activeIndex === index">
              {{ item.value }}
            </div>
          </div>
        </div>

        <!-- 加载更多按钮 -->
        <button id="load-more" @click="loadData" :disabled="loading || noMoreData"
                class="w-full py-3 bg-white hover:bg-neutral-50 border border-neutral-200 rounded-lg text-neutral-600 font-medium transition-all disabled:bg-neutral-100 disabled:text-neutral-400 disabled:cursor-not-allowed">
          <i class="fa-solid fa-spinner fa-spin mr-2" v-if="loading"></i>
          {{ buttonText }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import { usePagination } from '../composables/useRequest'
import { getQuestions } from '../services/api'

const activeIndex = ref(null)

// 使用分页Hook，自动管理列表、分页、搜索状态
const {
  list,
  loading,
  total,
  searchKeyword,
  handleSearch,
  reload,
  changePage
} = usePagination(getQuestions, {
  pageSize: 10,
  immediate: true
})

// 转换数据格式，适配页面显示
const qaList = computed(() => {
  return list.value.map(item => ({
    key: item.title,
    value: item.content
  }))
})

const noMoreData = computed(() => {
  return qaList.value.length >= total.value
})

const buttonText = computed(() => {
  if (loading.value) return '加载中...'
  if (noMoreData.value) return '没有更多数据了'
  return '加载更多'
})

const loadData = async () => {
  if (loading.value || noMoreData.value) return
  await changePage(1)
}

const searchQAs = () => {
  handleSearch(searchKeyword.value)
}

const toggleQuestion = (index) => {
  activeIndex.value = activeIndex.value === index ? null : index
}
</script>

<style scoped>
/* 三角符号样式 */
.question i {
  transition: transform 0.3s ease;
}
.question.open i {
  transform: rotate(90deg);
}
</style>