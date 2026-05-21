<template>
  <div class="page">
    <section class="head-card">
      <h1>AI 问答</h1>
      <p>当前使用前端模拟回答，后续可以替换成真实大模型接口。</p>
    </section>

    <section class="chat-card">
      <div class="message-list">
        <article
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="message.role"
        >
          <div class="bubble">{{ message.content }}</div>
        </article>
      </div>

      <div class="input-row">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          placeholder="输入关于遥感目标检测、模型选择或结果解读的问题"
        />
        <el-button type="primary" :loading="sending" @click="handleSend">
          发送
        </el-button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from "vue";

const question = ref("");
const sending = ref(false);
const messages = ref([
  {
    id: 1,
    role: "assistant",
    content: "你好，我可以解释检测结果、目标类别，以及单图检测流程。",
  },
]);

const buildAnswer = (text) => {
  if (text.includes("模型")) {
    return "当前平台支持读取后端已加载的模型信息，训练后的 RSOD 权重可以通过模型管理接口重新加载。";
  }
  if (text.includes("结果")) {
    return "检测结果包含识别框列表、目标数量、耗时、模型名，以及结果图地址。";
  }
  if (text.includes("历史")) {
    return "历史记录页会从后端读取检测任务列表，并支持查看单次任务详情。";
  }
  return "当前问答页使用前端模拟回答，下一步可以替换成真实 LLM 服务。";
};

const handleSend = async () => {
  const text = question.value.trim();
  if (!text) {
    return;
  }

  messages.value.push({
    id: Date.now(),
    role: "user",
    content: text,
  });

  question.value = "";
  sending.value = true;

  setTimeout(() => {
    messages.value.push({
      id: Date.now() + 1,
      role: "assistant",
      content: buildAnswer(text),
    });
    sending.value = false;
  }, 500);
};
</script>

<style scoped>
.page {
  display: grid;
  gap: 20px;
}

.head-card,
.chat-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  box-shadow: var(--shadow-card);
}

.head-card {
  padding: 24px;
}

.head-card h1 {
  margin: 0 0 8px;
}

.head-card p {
  margin: 0;
  color: var(--text-secondary);
}

.chat-card {
  min-height: 560px;
  padding: 20px;
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 18px;
}

.message-list {
  display: grid;
  gap: 12px;
  align-content: start;
}

.message {
  display: flex;
}

.message.assistant {
  justify-content: flex-start;
}

.message.user {
  justify-content: flex-end;
}

.bubble {
  max-width: min(680px, 100%);
  padding: 14px 16px;
  border-radius: 18px;
  line-height: 1.7;
}

.assistant .bubble {
  background: var(--bg-muted);
}

.user .bubble {
  color: #fff;
  background: linear-gradient(135deg, var(--primary-color), #39b971);
}

.input-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
}
</style>
