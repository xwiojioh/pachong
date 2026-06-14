<template>
  <router-view />
</template>

<script setup>
</script>

<style>
:root {
  --app-bg: #eef3f6;
  --app-surface: #ffffff;
  --app-surface-soft: #f8fafc;
  --app-border: #dfe7ef;
  --app-border-soft: #e8eef5;
  --app-text: #16202a;
  --app-muted: #667085;
  --app-primary: #1e6f7a;
  --app-primary-strong: #175964;
  --app-success: #2f9461;
  --app-warning: #d58a1f;
  --app-danger: #c2413a;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: var(--app-text);
  background: var(--app-bg);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

body {
  min-width: 320px;
}

.el-button {
  font-weight: 700;
}

.el-button--primary {
  --el-button-bg-color: var(--app-primary);
  --el-button-border-color: var(--app-primary);
  --el-button-hover-bg-color: var(--app-primary-strong);
  --el-button-hover-border-color: var(--app-primary-strong);
  --el-button-active-bg-color: var(--app-primary-strong);
  --el-button-active-border-color: var(--app-primary-strong);
}

.el-input__wrapper,
.el-select__wrapper {
  border-radius: 8px;
}

.el-card {
  --el-card-border-radius: 8px;
  border-color: var(--app-border);
}

.el-table {
  --el-table-header-bg-color: var(--app-surface-soft);
  --el-table-border-color: var(--app-border-soft);
  color: #344054;
}
</style>
