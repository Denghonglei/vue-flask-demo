<template>
  <div class="bg-neutral-100 min-h-screen">
    <Navbar title="长发估价" />

    <main class="container mx-auto px-4 py-8 md:py-16">
      <div class="max-w-md mx-auto bg-white rounded-2xl shadow-lg p-6 md:p-8">
        <h2 class="text-2xl font-bold text-center text-neutral-700 mb-8">长发估值计算器</h2>

        <div class="space-y-6">
          <div class="space-y-2">
            <label for="length" class="block text-sm font-medium text-neutral-700">长度 (cm，输入为5的倍数 例：55)</label>
            <input type="number" id="length" v-model.number="form.length" min="30" max="200" step="5" required @blur="addDetailParam"
                   placeholder="取有效长度，5的倍数"
                   class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all">
          </div>

          <div class="space-y-2">
            <label for="thickness" class="block text-sm font-medium text-neutral-700">皮筋以下围度 (cm，一圈的周长，保留一位小数，例：8.8)</label>
            <input type="number" id="thickness" v-model.number="form.thickness" min="0" max="16" step="0.1" required placeholder="精确到小数点后一位"
                   class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all">
          </div>

          <div class="space-y-2">
            <label class="block text-sm font-medium text-neutral-700">是否烫染?</label>
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
            <label class="block text-sm font-medium text-neutral-700">剪发方式:</label>
            <div class="flex space-x-6">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="radio" v-model="form.method" value="OneCut"
                       class="w-4 h-4 text-primary focus:ring-primary">
                <span>一刀剪</span>
              </label>
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="radio" v-model="form.method" value="Scissors"
                       class="w-4 h-4 text-primary focus:ring-primary">
                <span>去量抽剪</span>
              </label>
            </div>
          </div>

          <div id="detailParams" class="space-y-4">
            <div class="space-y-2" v-for="(item, index) in detailParams" :key="index">
              <label :for="`detail${index}`" class="block text-sm font-medium text-neutral-700">{{ item.label }} cm处的围度 (cm):</label>
              <input type="number" :id="`detail${index}`" v-model.number="item.value" min="0" max="16" step="0.1" required placeholder="精确到小数点后一位"
                     class="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary/20 transition-all">
            </div>
          </div>

          <div id="response" class="text-red-500 text-sm text-center min-h-[20px]">{{ responseMsg }}</div>

          <div class="flex gap-4 pt-4">
            <button @click="reset" class="flex-1 px-4 py-3 border border-neutral-200 rounded-lg text-neutral-700 hover:bg-neutral-50 transition-all font-medium">
              重新输入
            </button>
            <button type="submit" @click="submitForm" id="submitBtn" :disabled="loading"
                    class="flex-1 px-4 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-all font-medium shadow-md hover:shadow-lg">
              <i class="fa-solid fa-spinner fa-spin mr-2" v-if="loading"></i>
              {{ loading ? '计算中...' : '计算估值' }}
            </button>
          </div>
        </div>

        <ContactPopup />
      </div>
    </main>

    <!-- 结果弹窗 -->
    <div id="resultModal"
         class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center transition-all duration-300"
         :class="{ 'opacity-0 invisible': !showResultModal, 'opacity-100 visible': showResultModal }">
      <div class="bg-white rounded-xl shadow-xl p-6 max-w-2xl w-full mx-4 transition-all duration-300"
           :class="{ 'scale-95': !showResultModal, 'scale-100': showResultModal }">
        <div class="mb-6">
          <h3 class="text-xl font-bold text-neutral-600 mb-4">估值结果</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div class="bg-neutral-50 p-4 rounded-lg border border-neutral-100">
              <div class="text-sm text-neutral-400 mb-1">总重量</div>
              <div class="text-2xl font-bold text-neutral-600" id="totalWeight">{{ resultData.weight || '--' }} 克</div>
            </div>
            <div class="bg-primary/5 p-4 rounded-lg border border-primary/10">
              <div class="text-sm text-neutral-400 mb-1">预估总价</div>
              <div class="text-2xl font-bold text-primary" id="totalPrice">¥ {{ resultData.total ? resultData.total.toFixed(1) : '--' }}</div>
            </div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full border-collapse">
              <thead>
              <tr class="bg-neutral-50">
                <th class="py-3 px-4 text-left text-sm font-medium text-neutral-500 border-b">长度（cm）</th>
                <th class="py-3 px-4 text-left text-sm font-medium text-neutral-500 border-b">重量(g)</th>
                <th class="py-3 px-4 text-left text-sm font-medium text-neutral-500 border-b">价格(¥)</th>
              </tr>
              </thead>
              <tbody id="detailsTable">
                <tr class="border-b hover:bg-neutral-50 transition-colors" v-for="(value, length) in resultData.details" :key="length">
                  <td class="py-3 px-4 text-sm">> {{ length }}</td>
                  <td class="py-3 px-4 text-sm">{{ value[0] }}</td>
                  <td class="py-3 px-4 text-sm font-medium text-primary">¥{{ value[2].toFixed(1) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="flex flex-col sm:flex-row justify-end gap-4">
          <button id="confirmBtn" @click="hideModal"
                  class="px-6 py-3 bg-neutral-100 hover:bg-neutral-200 text-neutral-600 font-medium rounded-lg transition-custom order-2 sm:order-1">
            关闭
          </button>
          <button id="redirectBtn" @click="goToBooking"
                  class="px-6 py-3 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg transition-custom shadow-md hover:shadow-lg order-1 sm:order-2">
            预约上门回收
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import ContactPopup from '../components/ContactPopup.vue'
import axios from 'axios'

const router = useRouter()

const form = reactive({
  length: null,
  thickness: null,
  isDyed: false,
  method: 'OneCut'
})

const detailParams = ref([])
const responseMsg = ref('')
const loading = ref(false)
const showResultModal = ref(false)
const resultData = reactive({
  weight: null,
  total: null,
  details: {}
})

const getValidNumber = (num) => {
  return Math.floor(num / 5) * 5;
}

const addDetailParam = () => {
  if (!form.length || form.length < 30 || form.length > 200) {
    responseMsg.value = "请输入有效的长度（30-200cm）";
    return;
  }
  responseMsg.value = "";

  const validLengthValue = getValidNumber(form.length)
  const maxDetailCount = Math.floor(validLengthValue / 10 / 2);

  detailParams.value = []
  for (let i = 0; i < maxDetailCount; i++) {
    detailParams.value.push({
      label: validLengthValue - (maxDetailCount - i) * 10,
      value: null
    })
  }
}

const submitForm = async () => {
  // 基础验证
  if (!form.length || !form.thickness) {
    responseMsg.value = "请填写所有必填字段";
    return;
  }

  const validLength = getValidNumber(form.length);
  if (validLength < 30 || validLength > 200) {
    responseMsg.value = "长度必须在30-200cm之间";
    return;
  }

  if (form.thickness <= 0 || form.thickness > 16) {
    responseMsg.value = "围度必须在0-16cm之间";
    return;
  }

  responseMsg.value = "";

  // 加载状态
  loading.value = true;

  const maxDetailCount = Math.floor(validLength / 10 / 2);
  const details = {};
  for (let i = 0; i < detailParams.value.length; i++) {
    if (detailParams.value[i].value) {
      details[detailParams.value[i].label] = detailParams.value[i].value;
    }
  }

  const data = {
    length: validLength,
    thickness: form.thickness,
    isDyed: form.isDyed,
    method: form.method,
    details: details
  };

  try {
    const response = await axios.post(`/api/hair/estimate`, data)
    renderResult(response.data)
    showModal()
  } catch (error) {
    console.error('Error:', error);
    responseMsg.value = `计算失败，请检查输入是否正确`;
  } finally {
    loading.value = false;
  }
}

const renderResult = (data) => {
  resultData.weight = data.result.weight
  resultData.total = data.result.total
  resultData.details = data.result.details
}

const showModal = () => {
  showResultModal.value = true
}

const hideModal = () => {
  showResultModal.value = false
}

const goToBooking = () => {
  hideModal()
  router.push('/pre-booking')
}

const reset = () => {
  form.length = null
  form.thickness = null
  form.isDyed = false
  form.method = 'OneCut'
  detailParams.value = []
  responseMsg.value = ''
}
</script>

<style scoped>
.transition-custom {
  transition: all 0.3s ease;
}

input:focus {
  outline: 2px solid #165DFF !important;
  outline-offset: 2px;
}
</style>