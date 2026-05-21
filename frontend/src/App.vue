<template>
  <router-view v-if="isAuthPage" />
  <MainLayout v-else>
    <template #sidebar>
      <Sidebar />
    </template>
    <template #header>
      <Header />
    </template>
    <template #content>
      <router-view />
    </template>
  </MainLayout>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import Header from "./components/Header.vue";
import Sidebar from "./components/Sidebar.vue";
import MainLayout from "./layouts/MainLayout.vue";

const route = useRoute();
const isAuthPage = computed(() => route.meta.layout === "auth");
</script>
