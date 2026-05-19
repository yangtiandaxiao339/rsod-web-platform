// router/index.js
import { createRouter, createWebHistory } from "vue-router";
import index from "../views/Detection.vue"; // 你的检测⻚⾯
// 路由配置
const routes = [
  {
    path: "/",
    name: "Detection",
    component: index, // 默认打开就是检测⻚⾯
  },
];
// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
});
export default router;
