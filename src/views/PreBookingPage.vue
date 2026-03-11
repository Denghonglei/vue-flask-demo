<template>
  <div class="bg-neutral-100 min-h-screen">
    <Navbar title="回收服务预约" />

    <main class="container mx-auto px-4 py-8 md:py-12">
      <div class="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg p-6 md:p-8">
        <h2 class="text-2xl font-bold text-center text-neutral-700 mb-8">回收服务预约</h2>

        <!-- 回收类型切换 -->
        <div class="flex rounded-lg overflow-hidden border border-neutral-200 mb-8">
          <button type="button"
                  class="flex-1 py-3 px-4 font-medium transition-all"
                  :class="{ 'bg-primary text-white': bookingType === 'door', 'bg-white text-neutral-600 hover:bg-neutral-50': bookingType !== 'door' }"
                  @click="bookingType = 'door'">
            <i class="fa-solid fa-house mr-2"></i>上门回收
          </button>
          <button type="button"
                  class="flex-1 py-3 px-4 font-medium transition-all"
                  :class="{ 'bg-primary text-white': bookingType === 'express', 'bg-white text-neutral-600 hover:bg-neutral-50': bookingType !== 'express' }"
                  @click="bookingType = 'express'">
            <i class="fa-solid fa-truck mr-2"></i>快递回收
          </button>
        </div>

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

          <!-- 上门回收专属字段 -->
          <template v-if="bookingType === 'door'">
            <div class="space-y-2">
              <label for="city" class="block text-sm font-medium text-neutral-700">所在城市 <span class="text-red-500">*</span></label>
              <input type="text" id="city" v-model="form.city" :required="bookingType === 'door'"
                     class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all"
                     placeholder="请输入您所在的城市">
            </div>

            <div class="space-y-2">
              <label for="address" class="block text-sm font-medium text-neutral-700">详细地址 <span class="text-red-500">*</span></label>
              <textarea id="address" v-model="form.address" rows="3" :required="bookingType === 'door'"
                        class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all resize-none"
                        placeholder="请输入详细地址，方便我们安排上门回收"></textarea>
            </div>

            <div class="space-y-2">
              <label for="date" class="block text-sm font-medium text-neutral-700">期望上门日期 <span class="text-red-500">*</span></label>
              <input type="date" id="date" v-model="form.date" :required="bookingType === 'door'"
                     class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all">
            </div>

            <div class="space-y-2">
              <label for="time" class="block text-sm font-medium text-neutral-700">期望上门时间段 <span class="text-red-500">*</span></label>
              <select id="time" v-model="form.time" :required="bookingType === 'door'"
                      class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all">
                <option value="">请选择时间段</option>
                <option value="morning">上午 9:00-12:00</option>
                <option value="afternoon">下午 14:00-18:00</option>
                <option value="evening">晚上 18:00-21:00</option>
              </select>
            </div>
          </template>

          <!-- 快递回收专属字段 -->
          <template v-if="bookingType === 'express'">
            <div class="space-y-2">
              <label for="express_company" class="block text-sm font-medium text-neutral-700">快递公司 <span class="text-red-500">*</span></label>
              <input type="text" id="express_company" v-model="form.express_company" :required="bookingType === 'express'"
                     class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all"
                     placeholder="请输入快递公司名称">
            </div>

            <div class="space-y-2">
              <label for="tracking_number" class="block text-sm font-medium text-neutral-700">快递单号 <span class="text-red-500">*</span></label>
              <input type="text" id="tracking_number" v-model="form.tracking_number" :required="bookingType === 'express'"
                     class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all"
                     placeholder="请输入快递单号">
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-medium text-neutral-700">是否已知晓回收规则？ <span class="text-red-500">*</span></label>
              <div class="flex space-x-6">
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input type="radio" v-model="form.is_know_rules" :value="true" :required="bookingType === 'express'"
                         class="w-4 h-4 text-primary focus:ring-primary">
                  <span>是，已了解</span>
                </label>
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input type="radio" v-model="form.is_know_rules" :value="false" :required="bookingType === 'express'"
                         class="w-4 h-4 text-primary focus:ring-primary">
                  <span>否，需要说明</span>
                </label>
              </div>
            </div>

            <div class="p-4 bg-orange-50 border border-orange-200 rounded-lg text-sm text-orange-700">
              <i class="fa-solid fa-info-circle mr-2"></i>
              快递回收说明：请将头发妥善包装后寄出，我们收到后会在24小时内完成检测并打款。
            </div>
          </template>

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
import { reactive, ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import axios from 'axios'

const bookingType = ref('door') // door: 上门回收, express: 快递回收

const form = reactive({
  name: '',
  phone: '',
  // 上门回收字段
  city: '',
  address: '',
  date: '',
  time: '',
  // 快递回收字段
  express_company: '',
  tracking_number: '',
  is_know_rules: null,
  // 公共字段
  length: null,
  isDyed: false,
  remark: ''
})

// 页面加载时自动设置默认预约时间为最近可预约时间段
onMounted(() => {
  const now = new Date()
  const hour = now.getHours()
  let defaultDate = now.toISOString().split('T')[0] // 默认今天
  let defaultTime = 'morning'

  if (hour < 9) {
    // 9点前，默认今天上午
    defaultTime = 'morning'
  } else if (hour < 14) {
    // 9点-14点，默认今天下午
    defaultTime = 'afternoon'
  } else if (hour < 18) {
    // 14点-18点，默认今天晚上
    defaultTime = 'evening'
  } else {
    // 18点后，默认明天上午
    const tomorrow = new Date(now)
    tomorrow.setDate(tomorrow.getDate() + 1)
    defaultDate = tomorrow.toISOString().split('T')[0]
    defaultTime = 'morning'
  }

  form.date = defaultDate
  form.time = defaultTime
})

const loading = ref(false)
const response = reactive({
  message: '',
  type: ''
})

const submitForm = async () => {
  // 基础验证
  let requiredFields = ['name', 'phone', 'length'];

  if (bookingType.value === 'door') {
    requiredFields = requiredFields.concat(['city', 'address', 'date', 'time']);
  } else {
    requiredFields = requiredFields.concat(['express_company', 'tracking_number', 'is_know_rules']);
  }

  const missingFields = requiredFields.filter(field => !form[field]);
  if (missingFields.length > 0) {
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
    const submitData = {
      ...form,
      type: bookingType.value // 提交预约类型
    };
    const res = await axios.post('/api/pre-book', submitData);
    if (res.data.success) {
      const orderNo = res.data.data.orderNo;
      response.message = bookingType.value === 'door'
        ? `预约提交成功！您的订单号：${orderNo}，我们会尽快与您联系确认上门时间。`
        : `快递信息提交成功！您的订单号：${orderNo}，我们收到快递后会第一时间处理。`;
      response.type = 'success';
      // 重置表单
      Object.keys(form).forEach(key => {
        form[key] = (key === 'isDyed' || key === 'is_know_rules') ? false : ''
      })
    } else {
      throw new Error(res.data.message || '提交失败')
    }
  } catch (error) {
    console.error('Error:', error);
    response.message = error.response?.data?.message || error.message || '提交失败，请稍后重试';
    response.type = 'error';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
</style>