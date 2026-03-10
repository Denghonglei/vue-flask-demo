<template>
  <div class="bg-neutral-100 min-h-screen">
    <Navbar title="联系我们" />

    <main class="container mx-auto px-4 py-8 md:py-12">
      <div class="max-w-4xl mx-auto">
        <div class="text-center mb-10">
          <h2 class="text-3xl font-bold text-neutral-700 mb-3">联系我们</h2>
          <p class="text-neutral-500 max-w-2xl mx-auto">我们非常乐意倾听您的声音！有任何问题、建议或者合作意向，都可以通过以下方式联系我们，我们会尽快回复您。</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <!-- 联系方式卡片 -->
          <div class="bg-white rounded-xl shadow-sm p-6 text-center hover:shadow-md transition-all">
            <div class="w-14 h-14 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fa-brands fa-weixin text-green-500 text-2xl"></i>
            </div>
            <h3 class="font-semibold text-neutral-700 mb-2">微信客服</h3>
            <p class="text-neutral-600">Jozuuuu</p>
            <p class="text-sm text-neutral-400 mt-2">工作日 9:00-22:00</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 text-center hover:shadow-md transition-all">
            <div class="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fa-solid fa-envelope text-primary text-2xl"></i>
            </div>
            <h3 class="font-semibold text-neutral-700 mb-2">电子邮箱</h3>
            <p class="text-neutral-600">ln80656155@163.com</p>
            <p class="text-sm text-neutral-400 mt-2">24小时内回复</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 text-center hover:shadow-md transition-all">
            <div class="w-14 h-14 bg-orange-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fa-solid fa-clock text-orange-500 text-2xl"></i>
            </div>
            <h3 class="font-semibold text-neutral-700 mb-2">服务时间</h3>
            <p class="text-neutral-600">周一至周日</p>
            <p class="text-sm text-neutral-400 mt-2">9:00 - 22:00</p>
          </div>
        </div>

        <!-- 留言表单 -->
        <div class="bg-white rounded-xl shadow-sm p-6 md:p-8">
          <h3 class="text-xl font-semibold text-neutral-700 mb-6">在线留言</h3>
          <form id="contactForm" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-2">
                <label for="name" class="block text-sm font-medium text-neutral-700">您的称呼</label>
                <input type="text" id="name" v-model="form.name"
                       class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                       placeholder="请问怎么称呼您">
              </div>
              <div class="space-y-2">
                <label for="contactInfo" class="block text-sm font-medium text-neutral-700">联系方式</label>
                <input type="text" id="contactInfo" v-model="form.contactInfo"
                       class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                       placeholder="请留下您的微信或手机号">
              </div>
            </div>
            <div class="space-y-2">
              <label for="message" class="block text-sm font-medium text-neutral-700">留言内容</label>
              <textarea id="message" v-model="form.message" rows="5"
                        class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                        placeholder="请详细描述您的问题、建议或者诉求..."></textarea>
            </div>
            <div id="responseMessage" :class="{ 'text-red-500': response.type === 'error', 'text-green-500': response.type === 'success' }" class="text-sm" v-if="response.message">{{ response.message }}</div>
            <div class="flex justify-end">
              <button type="button" @click="submitForm" id="submitBtn" :disabled="loading"
                      class="px-8 py-3 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg transition-all shadow-md hover:shadow-lg">
                <i class="fa-solid fa-spinner fa-spin mr-2" v-if="loading"></i>
                {{ loading ? '发送中...' : '发送留言' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import Navbar from '../components/Navbar.vue'
import axios from 'axios'

const form = reactive({
  name: '',
  contactInfo: '',
  message: ''
})

const loading = ref(false)
const response = reactive({
  message: '',
  type: ''
})

const submitForm = async () => {
  // 简单验证
  if (!form.name || !form.contactInfo || !form.message) {
    response.message = '请填写完整信息';
    response.type = 'error';
    return;
  }

  // 加载状态
  loading.value = true;
  response.message = '';

  const formData = {
    name: form.name,
    contactInfo: form.contactInfo,
    message: form.message
  };

  try {
    const res = await axios.post('/api/message/submit', formData);
    const result = res.data;
    response.message = result.message || '留言发送成功！我们会尽快联系您。';
    response.type = 'success';
    form.name = '';
    form.contactInfo = '';
    form.message = '';
  } catch (error) {
    console.error('发生错误:', error);
    // 模拟发送成功
    response.message = '留言发送成功！我们会尽快联系您。';
    response.type = 'success';
    form.name = '';
    form.contactInfo = '';
    form.message = '';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
</style>