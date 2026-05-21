<template>
  <div class="auth-shell">
    <div class="auth-card">
      <div class="auth-head">
        <span class="eyebrow">Create Account</span>
        <h1>注册账号</h1>
        <p>创建平台账户，直接进入单图检测与历史管理流程。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="3-20 位字符" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password />
        </el-form-item>
        <el-form-item prop="agree">
          <el-checkbox v-model="form.agree">我已阅读并同意服务条款</el-checkbox>
        </el-form-item>
        <el-button class="submit-button" type="primary" @click="handleRegister">
          注册并进入平台
        </el-button>
      </el-form>

      <div class="auth-foot">
        已有账号？
        <router-link to="/login">返回登录</router-link>
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
  email: "",
  password: "",
  confirmPassword: "",
  agree: false,
});

const rules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度需在 3 到 20 位之间", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "邮箱格式不正确", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少 6 位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请再次输入密码", trigger: "blur" },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error("两次输入的密码不一致"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
  agree: [
    {
      validator: (_rule, value, callback) => {
        if (!value) {
          callback(new Error("请先同意服务条款"));
          return;
        }
        callback();
      },
      trigger: "change",
    },
  ],
};

const handleRegister = async () => {
  await formRef.value.validate();
  localStorage.setItem("token", "mock-token");
  localStorage.setItem("username", form.username);
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
  width: min(460px, 100%);
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
  font-size: 14px;
  text-align: center;
  color: var(--text-secondary);
}

.auth-foot a {
  color: var(--primary-color);
}
</style>
