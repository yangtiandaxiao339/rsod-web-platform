<template>
  <div class="sidebar-shell">
    <div class="brand">
      <div class="brand-mark">
        <el-icon :size="20"><Monitor /></el-icon>
      </div>
      <div class="brand-text">
        <strong>RSOD 平台</strong>
        <span>遥感目标智能检测</span>
      </div>
    </div>

    <nav class="menu">
      <button
        v-for="item in menuList"
        :key="item.path"
        class="menu-item"
        :class="{ active: route.path === item.path }"
        @click="router.push(item.path)"
      >
        <el-icon :size="18"><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </button>
    </nav>

    <div class="footer">
      <el-button class="logout-button" text @click="handleLogout">
        退出登录
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import {
  ChatDotRound,
  Clock,
  DataLine,
  Monitor,
  Picture,
  User,
} from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();

const menuList = [
  { path: "/detection", label: "智能检测", icon: Picture },
  { path: "/history", label: "历史记录", icon: Clock },
  { path: "/qa", label: "AI 问答", icon: ChatDotRound },
  { path: "/targets", label: "目标库", icon: DataLine },
  { path: "/profile", label: "个人中心", icon: User },
];

const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  router.push("/login");
};
</script>

<style scoped>
.sidebar-shell {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px 16px 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px 20px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, var(--primary-color), #39b971);
  box-shadow: 0 10px 24px rgba(31, 143, 85, 0.3);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-text strong {
  font-size: 15px;
}

.brand-text span {
  font-size: 12px;
  color: var(--text-secondary);
}

.menu {
  flex: 1;
  display: grid;
  gap: 10px;
}

.menu-item {
  width: 100%;
  border: 0;
  background: transparent;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 14px;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    transform 0.2s ease,
    color 0.2s ease;
}

.menu-item:hover {
  background: var(--primary-soft);
  transform: translateX(2px);
}

.menu-item.active {
  background: linear-gradient(135deg, var(--primary-soft), rgba(31, 143, 85, 0.14));
  color: var(--primary-deep);
  font-weight: 600;
}

.footer {
  padding: 14px 10px 0;
  border-top: 1px solid var(--border-color);
}

.logout-button {
  width: 100%;
  justify-content: flex-start;
}
</style>
