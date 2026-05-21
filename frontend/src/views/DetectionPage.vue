<template>
  <div class="page">
    <section class="hero">
      <div>
        <div class="hero-badge">Day 3 检测链路</div>
        <h1>单图检测流程已打通</h1>
        <p>
          当前页面支持上传一张遥感影像，调用后端模型完成检测，并展示原图、结果图和识别清单。
        </p>
      </div>
      <div class="hero-actions">
        <el-select
          v-model="selectedModel"
          placeholder="选择后端模型"
          style="width: 320px"
          @change="handleModelChange"
        >
          <el-option
            v-for="item in modelOptions"
            :key="item.object_name"
            :label="item.object_name"
            :value="item.object_name"
          />
        </el-select>
      </div>
    </section>

    <section class="tab-grid">
      <button
        v-for="tab in functionTabs"
        :key="tab.key"
        class="tab-card"
        :class="{ active: activeTab === tab.key }"
        @click="handleTabClick(tab.key)"
      >
        <el-icon :size="18"><component :is="tab.icon" /></el-icon>
        <div>
          <strong>{{ tab.name }}</strong>
          <span>{{ tab.desc }}</span>
        </div>
      </button>
      <input
        ref="fileInputRef"
        class="hidden-input"
        type="file"
        accept="image/*"
        @change="handleFileChange"
      />
    </section>

    <section class="content-grid">
      <div class="preview-panel">
        <div class="panel-head">
          <div>
            <h2>检测预览</h2>
            <span>{{ lastFileName || "请选择一张待检测图片" }}</span>
          </div>
          <el-tag :type="detecting ? 'warning' : detectionResult ? 'success' : 'info'">
            {{ detecting ? "检测中" : detectionResult ? "检测完成" : "待检测" }}
          </el-tag>
        </div>

        <div class="compare-grid">
          <div class="image-card">
            <div v-if="!originalImage" class="image-placeholder">
              <el-icon :size="32"><Picture /></el-icon>
              <span>上传后显示原始图片</span>
            </div>
            <img v-else :src="originalImage" alt="原始图片" class="compare-image" />
            <div class="image-label">原始图片</div>
          </div>

          <div class="image-card">
            <div v-if="!resultImage" class="image-placeholder">
              <el-icon :size="32"><DataLine /></el-icon>
              <span>检测完成后显示结果图</span>
            </div>
            <img v-else :src="resultImage" alt="检测结果" class="compare-image" />
            <div class="image-label">检测结果</div>
          </div>
        </div>
      </div>

      <aside class="side-panel">
        <div class="info-card">
          <div class="info-row">
            <span>后端当前模型</span>
            <strong>{{ currentModelInfo?.object_name || selectedModel || "--" }}</strong>
          </div>
          <div class="info-row">
            <span>模型版本</span>
            <strong>{{ currentModelInfo?.version || "--" }}</strong>
          </div>
          <div class="info-row">
            <span>加载状态</span>
            <strong>{{ currentModelInfo?.loaded ? "已加载" : "未加载" }}</strong>
          </div>
          <div class="info-row">
            <span>目标数</span>
            <strong>{{ detectionResult?.total_objects ?? 0 }}</strong>
          </div>
          <div class="info-row">
            <span>耗时</span>
            <strong>{{ detectionResult?.detection_time ?? "--" }} s</strong>
          </div>
        </div>

        <div class="list-card">
          <div class="card-title">识别清单</div>
          <div v-if="!detectionItems.length" class="empty-box">当前还没有检测结果</div>
          <div v-else class="detection-list">
            <div v-for="(item, index) in detectionItems" :key="index" class="detection-item">
              <span>{{ item.class_name }}</span>
              <strong>{{ (item.confidence * 100).toFixed(1) }}%</strong>
            </div>
          </div>
        </div>

        <div class="list-card">
          <div class="card-title">状态说明</div>
          <p class="summary">{{ summaryText }}</p>
        </div>

        <div class="action-row">
          <el-button @click="handleTabClick('single')">重新检测</el-button>
          <el-button type="primary" @click="goHistory">查看历史</el-button>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElLoading, ElMessage } from "element-plus";
import {
  DataLine,
  Folder,
  Monitor,
  Picture,
  Plus,
} from "@element-plus/icons-vue";
import { detectSingleImage } from "../api/detection";
import { getCurrentModel, getModelList, reloadModel } from "../api/model";

const router = useRouter();
const fileInputRef = ref();
const selectedModel = ref("");
const activeTab = ref("single");
const detecting = ref(false);
const lastFileName = ref("");
const originalImage = ref("");
const resultImage = ref("");
const detectionResult = ref(null);
const modelOptions = ref([]);
const currentModelInfo = ref(null);

const functionTabs = [
  { key: "single", name: "单图检测", desc: "已打通完整流程", icon: Picture },
  { key: "batch", name: "批量检测", desc: "保留入口，后续扩展", icon: Plus },
  { key: "folder", name: "文件夹检测", desc: "保留入口，后续扩展", icon: Folder },
  { key: "video", name: "视频检测", desc: "保留入口，后续扩展", icon: Monitor },
];

const detectionItems = computed(() => detectionResult.value?.boxes || []);

const summaryText = computed(() => {
  if (detecting.value) {
    return "后端正在处理图片，完成后会返回识别框、目标数量和结果图。";
  }

  if (!detectionResult.value) {
    if (currentModelInfo.value?.loaded) {
      return `当前已连接后端模型 ${currentModelInfo.value.object_name}，可以直接上传图片进行真实推理。`;
    }
    return "当前未加载真实模型，检测服务会退回到 mock 结果。";
  }

  return `本次共识别 ${detectionResult.value.total_objects} 个目标，模型为 ${detectionResult.value.model_name}，可继续在历史记录页查看明细。`;
});

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

const loadModelState = async () => {
  const [listResponse, currentResponse] = await Promise.all([getModelList(), getCurrentModel()]);
  modelOptions.value = listResponse.data || [];
  currentModelInfo.value = currentResponse.data || null;

  if (currentModelInfo.value?.object_name) {
    selectedModel.value = currentModelInfo.value.object_name;
    return;
  }

  if (modelOptions.value.length) {
    selectedModel.value = modelOptions.value[0].object_name;
    return;
  }

  selectedModel.value = "mock";
};

const handleModelChange = async (value) => {
  if (!value || value === currentModelInfo.value?.object_name) {
    return;
  }

  const previous = currentModelInfo.value?.object_name || "";
  try {
    const response = await reloadModel({ object_name: value });
    currentModelInfo.value = response.data || null;
    ElMessage.success("模型切换成功");
  } catch {
    selectedModel.value = previous;
  }
};

const handleTabClick = (tabKey) => {
  activeTab.value = tabKey;
  if (tabKey !== "single") {
    ElMessage.info("当前阶段只打通单图检测，其他模式保留入口。");
    return;
  }
  fileInputRef.value?.click();
};

const handleFileChange = async (event) => {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file) {
    return;
  }

  lastFileName.value = file.name;
  originalImage.value = URL.createObjectURL(file);
  const loading = ElLoading.service({
    lock: true,
    text: "正在检测中...",
    background: "rgba(22, 32, 39, 0.36)",
  });

  try {
    detecting.value = true;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", currentModelInfo.value?.object_name || selectedModel.value || "current-model");

    const response = await detectSingleImage(formData);
    if (!response.success || !response.data) {
      throw new Error(response.message || "检测失败");
    }

    detectionResult.value = response.data;
    resultImage.value = resolveBackendUrl(response.data.result_image_url);
    ElMessage.success(`检测完成，共识别 ${response.data.total_objects} 个目标`);
  } catch (error) {
    detectionResult.value = null;
    resultImage.value = "";
    ElMessage.error(error.message || "检测失败");
  } finally {
    detecting.value = false;
    loading.close();
  }
};

const goHistory = () => {
  router.push("/history");
};

onMounted(async () => {
  try {
    await loadModelState();
  } catch {
    selectedModel.value = "mock";
  }
});
</script>

<style scoped>
.page {
  display: grid;
  gap: 24px;
}

.hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(31, 143, 85, 0.1), rgba(31, 143, 85, 0.02)),
    #ffffff;
  box-shadow: var(--shadow-card);
}

.hero-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary-deep);
  font-size: 12px;
  margin-bottom: 12px;
}

.hero h1 {
  margin: 0 0 10px;
  font-size: 32px;
}

.hero p {
  margin: 0;
  max-width: 680px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.tab-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.tab-card {
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.92);
  border-radius: 20px;
  padding: 18px;
  text-align: left;
  display: flex;
  gap: 12px;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.tab-card strong,
.tab-card span {
  display: block;
}

.tab-card strong {
  margin-bottom: 4px;
  font-size: 15px;
}

.tab-card span {
  font-size: 12px;
  color: var(--text-secondary);
}

.tab-card.active,
.tab-card:hover {
  border-color: rgba(31, 143, 85, 0.45);
  transform: translateY(-2px);
  box-shadow: var(--shadow-card);
}

.hidden-input {
  display: none;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
}

.preview-panel,
.info-card,
.list-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  box-shadow: var(--shadow-card);
}

.preview-panel {
  padding: 24px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}

.panel-head h2 {
  margin: 0 0 6px;
}

.panel-head span {
  color: var(--text-secondary);
  font-size: 13px;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.image-card {
  min-height: 360px;
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  background: var(--bg-muted);
}

.compare-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  height: 100%;
  min-height: 360px;
  display: grid;
  place-items: center;
  gap: 10px;
  color: var(--text-light);
}

.image-label {
  position: absolute;
  left: 14px;
  bottom: 14px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(22, 32, 39, 0.72);
  color: #fff;
  font-size: 12px;
}

.side-panel {
  display: grid;
  gap: 16px;
}

.info-card,
.list-card {
  padding: 20px;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(219, 229, 221, 0.9);
}

.info-row:last-child {
  border-bottom: 0;
}

.info-row span {
  color: var(--text-secondary);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
}

.empty-box {
  padding: 18px;
  border-radius: 16px;
  background: var(--bg-muted);
  color: var(--text-secondary);
  font-size: 14px;
}

.detection-list {
  display: grid;
  gap: 10px;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 14px;
  background: var(--bg-muted);
}

.summary {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.action-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 1180px) {
  .tab-grid,
  .compare-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
