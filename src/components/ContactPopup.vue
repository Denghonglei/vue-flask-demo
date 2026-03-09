<template>
  <div>
    <!-- 小客服图标 -->
    <div class="contact-icon" @click="togglePopup" v-if="!popupOpen">💬</div>

    <!-- 客服弹窗 -->
    <div class="contact-popup" id="contactPopup" v-if="popupOpen" :style="{ left: popupPosition.left + 'px', top: popupPosition.top + 'px' }">
      <div class="popup-header" @mousedown="startDrag">联系客服</div>
      <div class="popup-content space-y-3">
        <p class="text-neutral-600">如有任何问题，请联系我们：</p>
        <div class="flex items-center space-x-2">
          <i class="fa-brands fa-weixin text-green-500"></i>
          <p>客服微信：Jozuuuu</p>
        </div>
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-envelope text-primary"></i>
          <p>客服邮箱：ln80656155@163.com</p>
        </div>
        <button @click="togglePopup" class="w-full mt-2 py-2 bg-neutral-100 hover:bg-neutral-200 rounded-lg text-sm transition-all">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const popupOpen = ref(false)
const isDragging = ref(false)
const popupPosition = reactive({
  left: 20,
  top: 20
})
const offset = reactive({
  x: 0,
  y: 0
})

const togglePopup = () => {
  popupOpen.value = !popupOpen.value
  if (popupOpen.value) {
    // 重置弹窗位置
    popupPosition.left = window.innerWidth - 320
    popupPosition.top = window.innerHeight - 400
  }
}

const startDrag = (e) => {
  e.stopPropagation()
  isDragging.value = true
  offset.x = e.clientX - popupPosition.left
  offset.y = e.clientY - popupPosition.top

  document.addEventListener('mousemove', drag)
  document.addEventListener('mouseup', stopDrag)
}

const drag = (e) => {
  if (isDragging.value) {
    popupPosition.left = e.clientX - offset.x
    popupPosition.top = e.clientY - offset.y
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', drag)
  document.removeEventListener('mouseup', stopDrag)
}
</script>

<style scoped>
/* 小客服图标的样式 */
.contact-icon {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: #165DFF;
  color: white;
  font-size: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.3);
  transition: all 0.3s ease;
}

.contact-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(22, 93, 255, 0.4);
}

/* 弹窗的样式 */
.contact-popup {
  position: fixed;
  width: 300px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

/* 弹窗标题栏的样式，用于拖动 */
.popup-header {
  padding: 12px 16px;
  background-color: #165DFF;
  color: white;
  cursor: move;
  font-weight: 500;
}

/* 弹窗内容区域的样式 */
.popup-content {
  padding: 16px;
}
</style>