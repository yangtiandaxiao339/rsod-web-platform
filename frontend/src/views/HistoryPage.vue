<template>
  <div class="page">
    <section class="head-card">
      <div>
        <h1>历史记录</h1>
        <p>展示后端返回的检测任务列表，并支持查看单次检测详情。</p>
      </div>
      <el-button @click="loadHistory">刷新数据</el-button>
    </section>

    <section class="toolbar">
      <el-input v-model="searchQuery" placeholder="按模型名或标签搜索" clearable />
    </section>

    <section class="history-list">
      <div v-if="loading" class="empty-card">正在加载历史记录...</div>
      <div v-else-if="!filteredRecords.length" class="empty-card">暂无检测历史</div>

      <article v-for="record in filteredRecords" :key="record.id" class="history-card">
        <img :src="resolveBackendUrl(record.result_image_url)" alt="检测结果图" class="thumb" />
        <div class="record-main">
          <div class="record-top">
            <strong>{{ record.model_name }}</strong>
            <span>{{ formatTime(record.created_at) }}</span>
          </div>
          <div class="record-meta">
            <span>检测目标数：{{ record.total_objects }}</span>
            <span>ID：{{ record.id }}</span>
          </div>
          <div class="tag-list">
            <el-tag v-for="label in record.labels" :key="label" effect="plain">
              {{ label }}
            </el-tag>
          </div>
        </div>
        <div class="record-actions">
          <el-button @click="viewDetail(record.id)">查看详情</el-button>
          <el-button type="primary" plain @click="openResult(record.result_image_url)">
            打开结果图
          </el-button>
        </div>
      </article>
    </section>

    <el-dialog v-model="detailVisible" title="检测详情" width="720px">
      <div v-if="detailLoading">正在读取详情...</div>
      <div v-else-if="detailData" class="detail-grid">
        <img :src="resolveBackendUrl(detailData.result_image_url)" alt="详情结果图" class="detail-image" />
        <div class="detail-panel">
          <div class="detail-row">
            <span>检测 ID</span>
            <strong>{{ detailData.detection_id }}</strong>
          </div>
          <div class="detail-row">
            <span>模型</span>
            <strong>{{ detailData.model_name }}</strong>
          </div>
          <div class="detail-row">
            <span>目标数</span>
            <strong>{{ detailData.total_objects }}</strong>
          </div>
          <div class="detail-row">
            <span>耗时</span>
            <strong>{{ detailData.detection_time }} s</strong>
          </div>

          <div class="box-list">
            <div v-for="(box, index) in detailData.boxes" :key="index" class="box-item">
              <span>{{ box.class_name }}</span>
              <strong>{{ (box.confidence * 100).toFixed(1) }}%</strong>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { getDetectionDetail, getDetectionHistory } from "../api/detection";

const loading = ref(false);
const detailLoading = ref(false);
const detailVisible = ref(false);
const detailData = ref(null);
const searchQuery = ref("");
const records = ref([]);

const getBackendBaseUrl = () => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
  return apiBase.replace(/\/api\/?$/, "");
};

const resolveBackendUrl = (path) => {
  if (!path) {
    return "";
  }
  if (/^https?:\/\//.test(path)) {
    return path;
  }
  return new URL(path, getBackendBaseUrl()).href;
};

const formatTime = (value) => {
  if (!value) {
    return "--";
  }
  return new Date(value).toLocaleString("zh-CN");
};

const filteredRecords = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase();
  if (!keyword) {
    return records.value;
  }

  return records.value.filter((record) => {
    const haystack = [record.model_name, ...(record.labels || [])].join(" ").toLowerCase();
    return haystack.includes(keyword);
  });
});

const loadHistory = async () => {
  loading.value = true;
  try {
    const response = await getDetectionHistory();
    records.value = response.data || [];
  } catch {
    records.value = [];
    ElMessage.error("历史记录加载失败");
  } finally {
    loading.value = false;
  }
};

const viewDetail = async (id) => {
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    const response = await getDetectionDetail(id);
    detailData.value = response.data || null;
  } catch {
    detailData.value = null;
    ElMessage.error("读取详情失败");
  } finally {
    detailLoading.value = false;
  }
};

const openResult = (path) => {
  window.open(resolveBackendUrl(path), "_blank", "noopener,noreferrer");
};

onMounted(loadHistory);
</script>

<style scoped>
.page {
  display: grid;
  gap: 20px;
}

.head-card,
.toolbar,
.empty-card,
.history-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  box-shadow: var(--shadow-card);
}

.head-card,
.toolbar {
  padding: 22px 24px;
}

.head-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.head-card h1 {
  margin: 0 0 8px;
}

.head-card p {
  margin: 0;
  color: var(--text-secondary);
}

.empty-card {
  padding: 28px;
  color: var(--text-secondary);
}

.history-list {
  display: grid;
  gap: 16px;
}

.history-card {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) auto;
  gap: 18px;
  padding: 18px;
}

.thumb {
  width: 100%;
  height: 132px;
  object-fit: cover;
  border-radius: 16px;
  background: var(--bg-muted);
}

.record-main {
  min-width: 0;
}

.record-top,
.record-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  align-items: center;
}

.record-top {
  margin-bottom: 10px;
}

.record-top span,
.record-meta {
  color: var(--text-secondary);
  font-size: 13px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.record-actions {
  display: grid;
  align-content: center;
  gap: 10px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 18px;
}

.detail-image {
  width: 100%;
  border-radius: 18px;
  background: var(--bg-muted);
}

.detail-panel {
  display: grid;
  gap: 10px;
}

.detail-row,
.box-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--bg-muted);
}

.detail-row span {
  color: var(--text-secondary);
}

.box-list {
  display: grid;
  gap: 8px;
  margin-top: 8px;
}

@media (max-width: 1100px) {
  .history-card,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
