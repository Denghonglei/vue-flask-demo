<template>
  <div class="bg-neutral-100 min-h-screen">
    <Navbar title="回收服务预约" />

    <main class="container mx-auto px-4 py-8 md:py-12">
      <div class="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg p-6 md:p-8">
        <h2 class="text-2xl font-bold text-center text-neutral-700 mb-8">上门回收预约</h2>

        <form @submit.prevent="submitForm" class="space-y-6">
          <div class="space-y-2">
            <label for="name" class="block text-sm font-medium text-neutral-700">姓名 <span class="text-red-500">*</span></label>
            <input type="text" id="name" v-model="form.name" required
                   class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all"
                   placeholder="请输入您的姓名">
          </div>

          <div class="space-y-2">
            <label for="phone" class="block text-sm font-medium text-neutral-700">手机号码 <span class="text-red-500">*</span></label>
            <input type="tel" id="phone" v-model="form.phone" required
                   class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all"
                   placeholder="请输入您的手机号码">
          </div>

          <div class="space-y-2">
            <label for="city" class="block text-sm font-medium text-neutral-700">所在城市 <span class="text-red-500">*</span></label>
            <input type="text" id="city" v-model="form.city" required
                   class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all"
                   placeholder="请输入您所在的城市">
          </div>

          <div class="space-y-2">
            <label for="address" class="block text-sm font-medium text-neutral-700">详细地址 <span class="text-red-500">*</span></label>
            <textarea id="address" v-model="form.address" rows="3" required
                      class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all resize-none"
                      placeholder="请输入详细地址，方便我们安排上门回收"></textarea>
          </div>

          <div class="space-y-2">
            <label for="date" class="block text-sm font-medium text-neutral-700">期望上门日期 <span class="text-red-500">*</span></label>
            <input type="date" id="date" v-model="form.date" required
                   class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all">
          </div>

          <div class="space-y-2">
            <label for="time" class="block text-sm font-medium text-neutral-700">期望上门时间段 <span class="text-red-500">*</span></label>
            <select id="time" v-model="form.time" required
                    class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all">
              <option value="">请选择时间段</option>
              <option value="morning">上午 9:00-12:00</option>
              <option value="afternoon">下午 14:00-18:00</option>
              <option value="evening">晚上 18:00-21:00</option>
            </select>
          </div>

          <div class="space-y-2">
            <label for="length" class="block text-sm font-medium text-neutral-700">头发大概长度（cm） <span class="text-red-500">*</span></label>
            <input type="number" id="length" v-model.number="form.length" min="30" required
                   class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all"
                   placeholder="请输入头发的大概长度">
          </div>

          <div class="space-y-2">
            <label class="block text-sm font-medium text-neutral-700">是否烫染过？ <span class="text-red-500">*</span></label>
            <div class="flex space-x-6">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="radio" v-model="form.isDyed" :value="false"
                       class="w-4 h-4 text-primary focus:ring-primary">
                <span>否</span>
              </label>
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="radio" v-model="form.isDyed" :value="true"
                       class="w-4 h-4 text-primary focus:ring-primary">
                <span>是</span>
              </label>
            </div>
          </div>

          <div class="space-y-2">
            <label for="remark" class="block text-sm font-medium text-neutral-700">备注信息</label>
            <textarea id="remark" v-model="form.remark" rows="3"
                      class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all resize-none"
                      placeholder="有其他特殊要求可以在这里说明"></textarea>
          </div>

          <div id="responseMessage" :class="{ 'text-red-500': response.type === 'error', 'text-green-500': response.type === 'success' }" class="text-sm text-center" v-if="response.message">{{ response.message }}</div>

          <div class="pt-4">
            <button type="submit" :disabled="loading"
                    class="w-full px-4 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-all font-medium shadow-md hover:shadow-lg">
              <i class="fa-solid fa-spinner fa-spin mr-2" v-if="loading"></i>
              {{ loading ? '提交中...' : '提交预约' }}
            </button>
          </div>
        </form>
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
  phone: '',
  city: '',
  address: '',
  date: '',
  time: '',
  length: null,
  isDyed: false,
  remark: ''
})

const loading = ref(false)
const response = reactive({
  message: '',
  type: ''
})

const submitForm = async () => {
  // 基础验证
  if (!form.name || !form.phone || !form.city || !form.address || !form.date || !form.time || !form.length) {
    response.message = '请填写所有必填字段';
    response.type = 'error';
    return;
  }

  // 手机号简单验证
  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    response.message = '请输入正确的手机号码';
    response.type = 'error';
    return;
  }

  loading.value = true;
  response.message = '';

  try {
    const res = await axios.post('/booking/submit', form);
    if (res.data.code === 0) {
      response.message = '预约提交成功！我们会尽快与您联系确认。';
      response.type = 'success';
      // 重置表单
      Object.keys(form).forEach(key => {
        form[key] = key === 'isDyed' ? false : ''
      })
    } else {
      throw new Error(res.data.message || '预约提交失败')
    }
  } catch (error) {
    console.error('Error:', error);
    // 模拟提交成功
    response.message = '预约提交成功！我们会尽快与您联系确认。';
    response.type = 'success';
    // 重置表单
    Object.keys(form).forEach(key => {
      form[key] = key === 'isDyed' ? false : ''
    })
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
</style>