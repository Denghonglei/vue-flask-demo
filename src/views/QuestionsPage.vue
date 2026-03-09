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
import { ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import axios from 'axios'

const searchKeyword = ref('')
const qaList = ref([])
const currentPage = ref(1)
const pageSize = 10
const loading = ref(false)
const noMoreData = ref(false)
const activeIndex = ref(null)

const buttonText = ref('加载更多')

onMounted(() => {
  loadData()
})

const fetchData = async (page, searchWord = '') => {
  try {
    const response = await axios.get(`/api/list-questions?page=${page}&pageSize=${pageSize}&search=${encodeURIComponent(searchWord)}`);
    if (response.data.code === 0) {
      return response.data.data;
    } else {
      console.error('接口返回错误：', response.data.message);
      return [];
    }
  } catch (error) {
    console.error('数据获取失败:', error);
    // 开发环境模拟数据
    return [
      {key: "长发回收的流程是什么？", value: "首先您可以使用我们的估价计算器预估价格，然后选择上门回收或者快递回收，我们收到头发验收后会立即打款。"},
      {key: "头发多长可以卖？", value: "我们回收长度30cm以上的健康长发，越长价格越高。"},
      {key: "烫染过的头发可以回收吗？", value: "烫染过的头发也可以回收，只是价格会比原生发稍低一些。"},
      {key: "剪发方式有什么区别？", value: "一刀剪是齐根剪下，能获得最重的重量；抽剪是剪取长发保留短发，不影响发型。"},
      {key: "款项多久能到账？", value: "我们收到头发验收合格后，会在24小时内打款到您指定的账户。"}
    ];
  }
}

const loadData = async () => {
  if (loading.value) return

  loading.value = true
  buttonText.value = '加载中...'

  const data = await fetchData(currentPage.value, searchKeyword.value)
  if (data.length > 0) {
    qaList.value.push(...data)
    currentPage.value++
    if (data.length < pageSize) {
      noMoreData.value = true
      buttonText.value = '没有更多数据了'
    } else {
      buttonText.value = '加载更多'
    }
  } else {
    noMoreData.value = true
    buttonText.value = '没有更多数据了'
  }

  loading.value = false
}

const searchQAs = async () => {
  if (loading.value) return

  qaList.value = []
  currentPage.value = 1
  noMoreData.value = false
  loading.value = true
  buttonText.value = '搜索中...'

  const data = await fetchData(currentPage.value, searchKeyword.value)
  qaList.value = data
  currentPage.value++

  if (data.length === 0) {
    noMoreData.value = true
    buttonText.value = '没有相关数据'
  } else if (data.length < pageSize) {
    noMoreData.value = true
    buttonText.value = '没有更多数据了'
  } else {
    buttonText.value = '加载更多'
  }

  loading.value = false
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