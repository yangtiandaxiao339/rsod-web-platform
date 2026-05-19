<template>
  <div class="detection-page">
    <h3>遥感图像目标检测对比</h3>

    <!-- 模式切换按钮 -->
    <div class="toggle-buttons">
      <button
        @click="compareMode = 'side'"
        :class="{ active: compareMode === 'side' }"
      >
        并排对比
      </button>
      <button
        @click="compareMode = 'slider'"
        :class="{ active: compareMode === 'slider' }"
      >
        滑块对比
      </button>
    </div>

    <!-- 并排对比模式 -->
    <div v-if="compareMode === 'side'" class="side-by-side">
      <div class="image-card">
        <h4>原图</h4>
        <img :src="originalImage" alt="原图" />
      </div>
      <div class="image-card">
        <h4>AI标注结果</h4>
        <img :src="annotatedImage" alt="标注图" />
      </div>
    </div>

    <!-- 滑块对比模式 -->
    <div v-if="compareMode === 'slider'" class="slider-container">
      <SliderCompare :before="originalImage" :after="annotatedImage" />
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
// 组件路径正确，无需修改
import SliderCompare from "../components/SliderCompare.vue";

// 对比模式（默认并排）
const compareMode = ref("side");

// ✅ 修复：填入测试图片（在线图片，无需本地文件，直接显示）
// 后续你换成自己的图片路径即可
const originalImage = ref("https://picsum.photos/1200/600?random=10");
const annotatedImage = ref("https://picsum.photos/1200/600?random=20");
</script>

<style scoped>
/* ✅ 修复：补充所有缺失的样式 */
.detection-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.toggle-buttons {
  margin: 20px 0;
  display: flex;
  gap: 10px;
}

.toggle-buttons button {
  padding: 8px 16px;
  border: 1px solid #409eff;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.toggle-buttons button.active {
  background: #409eff;
  color: white;
}

.side-by-side {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.image-card {
  flex: 1;
  border: 1px solid #eee;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
}

.image-card img {
  width: 100%;
  height: 400px;
  object-fit: cover;
  border-radius: 4px;
}

.slider-container {
  margin-top: 20px;
}
</style>
