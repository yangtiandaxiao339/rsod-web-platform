<template>
  <div class="page">
    <section class="profile-card">
      <div class="profile-main">
        <el-avatar :size="84">{{ username.slice(0, 1).toUpperCase() }}</el-avatar>
        <div>
          <h1>{{ username }}</h1>
          <p>当前为演示账户，登录态通过本地存储维护。</p>
        </div>
      </div>
      <el-button type="primary" plain>编辑资料</el-button>
    </section>

    <section class="stats-grid">
      <article v-for="card in stats" :key="card.label" class="stat-card">
        <strong>{{ card.value }}</strong>
        <span>{{ card.label }}</span>
      </article>
    </section>

    <section class="profile-card">
      <div>
        <h2>当前后端模型</h2>
        <p v-if="currentModel?.loaded">
          {{ currentModel.object_name }} / v{{ currentModel.version || "--" }}
        </p>
        <p v-else>当前没有加载真实模型，服务会退回到 mock 模式。</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { getCurrentModel } from "../api/model";

const username = computed(() => localStorage.getItem("username") || "Demo");
const currentModel = ref(null);

const stats = [
  { label: "总检测次数", value: "128" },
  { label: "累计检测目标", value: "892" },
  { label: "检测成功率", value: "98.5%" },
  { label: "连续使用天数", value: "12" },
];

onMounted(async () => {
  try {
    const response = await getCurrentModel();
    currentModel.value = response.data || null;
  } catch {
    currentModel.value = null;
  }
});
</script>

<style scoped>
.page {
  display: grid;
  gap: 20px;
}

.profile-card,
.stat-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  box-shadow: var(--shadow-card);
}

.profile-card {
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.profile-card h2 {
  margin: 0 0 8px;
}

.profile-main {
  display: flex;
  align-items: center;
  gap: 18px;
}

.profile-main h1 {
  margin: 0 0 8px;
}

.profile-main p,
.profile-card p {
  margin: 0;
  color: var(--text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 24px;
  text-align: center;
}

.stat-card strong,
.stat-card span {
  display: block;
}

.stat-card strong {
  font-size: 32px;
  color: var(--primary-color);
}

.stat-card span {
  margin-top: 8px;
  color: var(--text-secondary);
}

@media (max-width: 1180px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
