<template>
  <div class="layout">
    <aside class="sidebar">
      <slot name="sidebar" />
    </aside>
    <div class="main">
      <header class="header">
        <slot name="header" />
      </header>
      <main class="content">
        <slot name="content" />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 248px;
  border-right: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
}

.main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.header {
  height: 72px;
  padding: 0 28px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(219, 229, 221, 0.9);
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(12px);
}

.content {
  flex: 1;
  overflow: auto;
  padding: 28px;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 210px;
  }

  .content {
    padding: 20px;
  }
}
</style>
