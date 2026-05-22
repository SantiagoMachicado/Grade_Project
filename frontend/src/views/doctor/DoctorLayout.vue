<template>
  <div class="layout-container">
    <div class="layout-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
    <DoctorSidebar /> <!-- Now acts as bottom nav -->
  </div>
</template>

<script setup>
import DoctorSidebar from '../../components/DoctorSidebar.vue'
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  width: 100vw;
  min-height: 100vh;
  background-color: var(--bg-color);
}

.layout-content {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  /* Espacio extra en la parte inferior para que el bottom nav no tape contenido */
  padding-bottom: 80px; 
}

/* Transiciones suaves entre rutas hijas */
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
