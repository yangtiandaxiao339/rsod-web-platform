<template>
  <div class="header-shell">
    <div>
      <div class="crumb">工作台 / {{ pageTitle }}</div>
      <div class="headline">{{ pageHeadline }}</div>
    </div>
    <div class="user">
      <el-tag effect="plain" type="success">联调已打通</el-tag>
      <div class="user-card">
        <el-avatar :size="36">{{ username.slice(0, 1).toUpperCase() }}</el-avatar>
        <div>
          <strong>{{ username }}</strong>
          <span>平台用户</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const username = computed(() => localStorage.getItem("username") || "Demo");
const pageTitle = computed(() => route.meta.title || "概览");

const pageHeadlineMap = {
  "/detection": "上传遥感影像并查看检测结果",
  "/history": "查看历史任务与检测明细",
  "/qa": "围绕遥感识别场景的 AI 问答",
  "/targets": "平台支持的目标类别与说明",
  "/profile": "账户信息与平台使用概览",
};

const pageHeadline = computed(() => pageHeadlineMap[route.path] || "RSOD 平台");
</script>

<style scoped>
.header-shell {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.crumb {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.headline {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
}

.user-card strong,
.user-card span {
  display: block;
}

.user-card strong {
  font-size: 13px;
}

.user-card span {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
