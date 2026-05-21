<template>
  <div class="page">
    <section class="head-card">
      <div>
        <h1>目标库</h1>
        <p>展示平台支持的目标类别与说明，当前数据来自后端目标列表接口。</p>
      </div>
      <div class="stats">
        <div class="stat">
          <strong>{{ targets.length }}</strong>
          <span>目标总数</span>
        </div>
        <div class="stat">
          <strong>{{ filteredTargets.length }}</strong>
          <span>筛选结果</span>
        </div>
      </div>
    </section>

    <section class="toolbar">
      <el-input v-model="searchQuery" placeholder="搜索目标名称或描述" clearable />
    </section>

    <section class="card-grid">
      <article v-if="loading" class="target-card empty-card">正在加载目标库...</article>
      <article v-else-if="!filteredTargets.length" class="target-card empty-card">
        没有匹配到目标类别
      </article>
      <article v-for="target in filteredTargets" :key="target.id" class="target-card">
        <div class="target-top">
          <div>
            <h3>{{ target.chinese_name }}</h3>
            <span>{{ target.name }}</span>
          </div>
          <el-tag effect="plain">可检测</el-tag>
        </div>
        <p>{{ target.description || "暂无描述" }}</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { getTargetList } from "../api/detection";

const loading = ref(false);
const searchQuery = ref("");
const targets = ref([]);

const filteredTargets = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase();
  if (!keyword) {
    return targets.value;
  }
  return targets.value.filter((item) =>
    [item.name, item.chinese_name, item.description].join(" ").toLowerCase().includes(keyword),
  );
});

const loadTargets = async () => {
  loading.value = true;
  try {
    const response = await getTargetList();
    targets.value = response.data || [];
  } catch {
    targets.value = [];
    ElMessage.error("目标库加载失败");
  } finally {
    loading.value = false;
  }
};

onMounted(loadTargets);
</script>

<style scoped>
.page {
  display: grid;
  gap: 20px;
}

.head-card,
.toolbar,
.target-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  box-shadow: var(--shadow-card);
}

.head-card {
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.head-card h1 {
  margin: 0 0 8px;
}

.head-card p {
  margin: 0;
  color: var(--text-secondary);
}

.stats {
  display: flex;
  gap: 12px;
}

.stat {
  min-width: 112px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--bg-muted);
  text-align: center;
}

.stat strong,
.stat span {
  display: block;
}

.stat strong {
  font-size: 24px;
}

.stat span {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.toolbar {
  padding: 18px 24px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.target-card {
  padding: 20px;
}

.target-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.target-top h3 {
  margin: 0 0 6px;
}

.target-top span,
.target-card p {
  color: var(--text-secondary);
}

.target-card p {
  margin: 0;
  line-height: 1.7;
}

.empty-card {
  text-align: center;
  color: var(--text-secondary);
}

@media (max-width: 1180px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
