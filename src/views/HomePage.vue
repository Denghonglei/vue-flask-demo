<template>
  <div class="bg-neutral-100 min-h-screen">
    <Navbar title="长发估价" />

    <main class="container mx-auto px-4 py-8 md:py-16">
      <!-- 英雄区域 -->
      <section class="text-center mb-16">
        <div class="max-w-3xl mx-auto">
          <h1 class="text-4xl md:text-5xl font-bold text-neutral-700 mb-6">专业长发回收平台</h1>
          <p class="text-xl text-neutral-500 mb-8">公平估价、上门服务、快速打款，让您的长发价值最大化</p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link to="/estimate" class="px-8 py-4 bg-primary hover:bg-primary/90 text-white rounded-lg transition-all font-medium shadow-md hover:shadow-lg">
              立即估价
            </router-link>
            <router-link to="/pre-booking" class="px-8 py-4 border border-primary text-primary hover:bg-primary/5 rounded-lg transition-all font-medium">
              预约上门
            </router-link>
          </div>
        </div>
      </section>

      <!-- 服务优势 -->
      <section class="mb-16">
        <h2 class="text-3xl font-bold text-center text-neutral-700 mb-12">我们的优势</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="bg-white rounded-xl shadow-sm p-6 text-center hover:shadow-md transition-all">
            <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fa-solid fa-ruler-combined text-primary text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-neutral-700 mb-3">公平透明估价</h3>
            <p class="text-neutral-500">根据长度、重量、发质等多维度智能估价，价格公开透明，无隐形消费</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 text-center hover:shadow-md transition-all">
            <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fa-solid fa-house-chimney text-primary text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-neutral-700 mb-3">免费上门服务</h3>
            <p class="text-neutral-500">全国主要城市提供免费上门回收服务，无需出门，轻松完成交易</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 text-center hover:shadow-md transition-all">
            <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fa-solid fa-money-bill-wave text-primary text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-neutral-700 mb-3">快速打款到账</h3>
            <p class="text-neutral-500">验收合格后24小时内打款，安全可靠，保障您的权益</p>
          </div>
        </div>
      </section>

      <!-- 流程步骤 -->
      <section class="mb-16">
        <h2 class="text-3xl font-bold text-center text-neutral-700 mb-12">回收流程</h2>
        <div class="max-w-4xl mx-auto">
          <div class="flex flex-col md:flex-row justify-between items-center">
            <div class="text-center mb-8 md:mb-0">
              <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">1</div>
              <h3 class="text-lg font-semibold text-neutral-700 mb-2">在线估价</h3>
              <p class="text-neutral-500 text-sm">填写头发信息，获取预估价格</p>
            </div>
            <div class="hidden md:block w-24 h-1 bg-neutral-200"></div>
            <div class="text-center mb-8 md:mb-0">
              <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">2</div>
              <h3 class="text-lg font-semibold text-neutral-700 mb-2">预约上门</h3>
              <p class="text-neutral-500 text-sm">提交预约，等待工作人员联系</p>
            </div>
            <div class="hidden md:block w-24 h-1 bg-neutral-200"></div>
            <div class="text-center mb-8 md:mb-0">
              <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">3</div>
              <h3 class="text-lg font-semibold text-neutral-700 mb-2">上门剪发</h3>
              <p class="text-neutral-500 text-sm">专业人员上门，按您要求剪发</p>
            </div>
            <div class="hidden md:block w-24 h-1 bg-neutral-200"></div>
            <div class="text-center">
              <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">4</div>
              <h3 class="text-lg font-semibold text-neutral-700 mb-2">立即打款</h3>
              <p class="text-neutral-500 text-sm">验收合格后立即打款到您账户</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA区域 -->
      <section class="bg-primary/5 rounded-2xl p-8 md:p-12 text-center">
        <h2 class="text-3xl font-bold text-neutral-700 mb-4">准备好出售您的长发了吗？</h2>
        <p class="text-neutral-500 mb-8 max-w-2xl mx-auto">立即使用我们的智能估价计算器，了解您的长发价值</p>
        <router-link to="/estimate" class="px-8 py-4 bg-primary hover:bg-primary/90 text-white rounded-lg transition-all font-medium shadow-md hover:shadow-lg inline-block">
          开始估价
        </router-link>
      </section>
    </main>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
</script>

<style scoped>
</style>