import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/detection",
  },
  {
    path: "/login",
    name: "login",
    meta: { title: "登录", layout: "auth" },
    component: () => import("../views/LoginPage.vue"),
  },
  {
    path: "/register",
    name: "register",
    meta: { title: "注册", layout: "auth" },
    component: () => import("../views/RegisterPage.vue"),
  },
  {
    path: "/forgot-password",
    name: "forgot-password",
    meta: { title: "找回密码", layout: "auth" },
    component: () => import("../views/ForgotPasswordPage.vue"),
  },
  {
    path: "/detection",
    name: "detection",
    meta: { title: "智能检测", requiresAuth: true },
    component: () => import("../views/DetectionPage.vue"),
  },
  {
    path: "/history",
    name: "history",
    meta: { title: "历史记录", requiresAuth: true },
    component: () => import("../views/HistoryPage.vue"),
  },
  {
    path: "/qa",
    name: "qa",
    meta: { title: "AI 问答", requiresAuth: true },
    component: () => import("../views/QAPage.vue"),
  },
  {
    path: "/targets",
    name: "targets",
    meta: { title: "目标库", requiresAuth: true },
    component: () => import("../views/TargetsPage.vue"),
  },
  {
    path: "/profile",
    name: "profile",
    meta: { title: "个人中心", requiresAuth: true },
    component: () => import("../views/ProfilePage.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to) => {
  const token = localStorage.getItem("token");

  if (to.meta.requiresAuth && !token) {
    return "/login";
  }

  if (to.meta.layout === "auth" && token) {
    return "/detection";
  }

  return true;
});

export default router;
