<template>
  <div class="auth-shell">
    <div class="auth-card">
      <div class="auth-head">
        <span class="eyebrow">RSOD Detection Platform</span>
        <h1>登录平台</h1>
        <p>进入智能检测、历史记录和目标库工作台。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
          />
        </el-form-item>
        <div class="auth-row">
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
          <router-link to="/forgot-password">忘记密码？</router-link>
        </div>
        <el-button class="submit-button" type="primary" @click="handleLogin">
          登录
        </el-button>
      </el-form>

      <div class="auth-foot">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const formRef = ref();

const form = reactive({
  username: "",
  password: "",
  remember: true,
});

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const handleLogin = async () => {
  await formRef.value.validate();
  localStorage.setItem("token", "mock-token");
  localStorage.setItem("username", form.username || "Demo");
  router.push("/detection");
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
  background: rgba(255, 255, 255, 0.92);
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
  line-height: 1.6;
}

.auth-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 6px 0 18px;
  font-size: 14px;
}

.submit-button {
  width: 100%;
  height: 44px;
}

.auth-foot {
  margin-top: 18px;
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
}

.auth-foot a,
.auth-row a {
  color: var(--primary-color);
}
</style>
