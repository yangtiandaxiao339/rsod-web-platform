<template>
  <div class="auth-shell">
    <div class="auth-card">
      <div class="auth-head">
        <span class="eyebrow">Password Reset</span>
        <h1>找回密码</h1>
        <p>输入注册邮箱，流程上模拟发送重置链接。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入注册邮箱" />
        </el-form-item>
        <el-button class="submit-button" type="primary" @click="handleSubmit">
          发送重置链接
        </el-button>
      </el-form>

      <div class="auth-foot">
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const formRef = ref();

const form = reactive({
  email: "",
});

const rules = {
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "邮箱格式不正确", trigger: "blur" },
  ],
};

const handleSubmit = async () => {
  await formRef.value.validate();
  ElMessage.success("已模拟发送重置链接");
  router.push("/login");
};
</script>

<style scoped>
.auth-shell {
  min-height: 100%;
  display: grid;
  place-items: center;
  padding: 32px;
}

.auth-card {
  width: min(420px, 100%);
  padding: 32px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: var(--shadow-card);
}

.auth-head {
  margin-bottom: 24px;
}

.eyebrow {
  display: inline-block;
  font-size: 12px;
  color: var(--primary-deep);
  background: var(--primary-soft);
  border-radius: 999px;
  padding: 6px 10px;
}

.auth-head h1 {
  margin: 14px 0 8px;
  font-size: 28px;
}

.auth-head p {
  margin: 0;
  color: var(--text-secondary);
}

.submit-button {
  width: 100%;
  height: 44px;
}

.auth-foot {
  margin-top: 18px;
  text-align: center;
}

.auth-foot a {
  color: var(--primary-color);
}
</style>
