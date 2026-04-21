<template>
  <div class="layout-container">
    <DoctorSidebar />
    <div class="layout-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import DoctorSidebar from '../../components/DoctorSidebar.vue'
</script>

<style scoped>
.layout-container {
  display: flex;
  width: 100vw;
  min-height: calc(100vh - 72px);
}

.layout-content {
  flex: 1;
  padding: 2rem;
  background-color: var(--bg-color);
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
