<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Tailwind 配置 */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-primary: #165DFF;
  --color-secondary: #FF7D00;
  --color-neutral-100: #F5F7FA;
  --color-neutral-200: #E4E7ED;
  --color-neutral-300: #C0C4CC;
  --color-neutral-400: #909399;
  --color-neutral-500: #606266;
  --color-neutral-600: #303133;
}

.transition-custom {
  transition: all 0.3s ease;
}

input:focus {
  outline: 2px solid var(--color-primary) !important;
  outline-offset: 2px;
}
</style>
