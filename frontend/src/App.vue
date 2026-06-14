<template>
  <router-view />
</template>

<script setup>
</script>

<style>
:root {
  --app-bg: #f8fafc;
  --app-surface: #ffffff;
  --app-surface-soft: #f6f8fb;
  --app-border: #edf1f6;
  --app-border-soft: #f0f3f8;
  --app-text: #1f2937;
  --app-muted: #909399;
  --app-primary: #256f78;
  --app-primary-strong: #1f5f67;
  --app-success: #529b2e;
  --app-warning: #b88230;
  --app-danger: #b2524b;
  --app-radius: 12px;
  --app-radius-sm: 8px;
  --app-shadow: 0 4px 12px rgba(15, 23, 42, 0.03), 0 1px 3px rgba(15, 23, 42, 0.05);
  --app-shadow-3d: 0 18px 36px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.92);
  --app-shadow-3d-hover: 0 24px 48px rgba(15, 23, 42, 0.11), 0 8px 18px rgba(37, 111, 120, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.96);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: Inter, Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
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
  border-radius: var(--app-radius-sm);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background-color 0.18s ease;
}

.el-button:not(.el-button--primary):not(.is-text):not(.is-link) {
  color: #475467;
  border-color: #e5eaf1;
  background: #ffffff;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.el-button:not(.el-button--primary):not(.is-text):not(.is-link):hover {
  transform: translateY(-1px);
  color: var(--app-primary);
  border-color: #d7e7ea;
  background: #f7fbfb;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.07), inset 0 1px 0 rgba(255, 255, 255, 0.96);
}

.el-button:not(.is-disabled):active {
  transform: translateY(0);
}

.el-button.is-text,
.el-button.is-link {
  font-weight: 700;
}

.el-button--primary {
  --el-button-bg-color: var(--app-primary);
  --el-button-border-color: var(--app-primary);
  --el-button-hover-bg-color: var(--app-primary-strong);
  --el-button-hover-border-color: var(--app-primary-strong);
  --el-button-active-bg-color: var(--app-primary-strong);
  --el-button-active-border-color: var(--app-primary-strong);
  box-shadow: 0 10px 20px rgba(37, 111, 120, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.24);
}

.el-button--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 28px rgba(37, 111, 120, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.28);
}

.el-input__wrapper,
.el-select__wrapper {
  border-radius: var(--app-radius-sm);
  box-shadow: 0 0 0 1px #e5eaf1 inset, inset 0 1px 0 rgba(255, 255, 255, 0.92);
  transition: box-shadow 0.18s ease, transform 0.18s ease;
}

.el-input__wrapper:hover,
.el-select__wrapper:hover {
  box-shadow: 0 0 0 1px #d7e7ea inset;
}

.el-input__wrapper.is-focus,
.el-select__wrapper.is-focused {
  box-shadow: 0 0 0 1px var(--app-primary) inset, 0 0 0 3px rgba(37, 111, 120, 0.08);
  transform: translateY(-1px);
}

.el-card {
  --el-card-border-radius: var(--app-radius);
  border-color: var(--app-border);
  box-shadow: var(--app-shadow);
  transform: translateZ(0);
}

.el-table {
  --el-table-header-bg-color: var(--app-surface-soft);
  --el-table-border-color: var(--app-border-soft);
  --el-table-row-hover-bg-color: #f9fbfd;
  color: #344054;
  font-size: 13px;
}

.el-table::before,
.el-table__inner-wrapper::before {
  height: 0;
}

.el-table th.el-table__cell {
  background: #f6f8fb;
  color: #667085;
  font-size: 12px;
  font-weight: 800;
}

.el-table th.el-table__cell,
.el-table td.el-table__cell {
  border-bottom: 1px solid #eef2f7;
}

.el-tag {
  border: 0;
  border-radius: 999px;
  font-weight: 700;
}

.el-tag--success {
  --el-tag-bg-color: #e1f3d8;
  --el-tag-text-color: #529b2e;
}

.el-tag--warning {
  --el-tag-bg-color: #f8edda;
  --el-tag-text-color: #a66b1f;
}

.el-tag--danger {
  --el-tag-bg-color: #fbe5e3;
  --el-tag-text-color: #b2524b;
}

.el-tag--info {
  --el-tag-bg-color: #eef2f7;
  --el-tag-text-color: #667085;
}

.el-tag--primary {
  --el-tag-bg-color: #e4f2f4;
  --el-tag-text-color: #256f78;
}

.el-dialog {
  border-radius: var(--app-radius);
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.16);
  overflow: hidden;
}

.el-dialog__header {
  padding: 22px 24px 12px;
}

.el-dialog__body {
  padding: 18px 24px 8px;
}

.el-dialog__footer {
  padding: 14px 24px 22px;
}

.el-progress-bar__outer {
  background-color: #eef2f7;
}

.el-pagination {
  --el-pagination-button-bg-color: #ffffff;
  --el-pagination-hover-color: var(--app-primary);
}
</style>
