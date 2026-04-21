<template>
  <div class="layout-container">
    <PatientSidebar />
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
import PatientSidebar from '../../components/PatientSidebar.vue'
</script>

<style scoped>
.layout-container {
  display: flex;
  width: 100vw;
  /* Compensamos la alineación center global de origin .main-content 
     si queremos expandirlo full width. Pero por ahora lo anidamos fluidamente */
  min-height: calc(100vh - 72px); /* 72px=header aprox */
}

/* Redefinir variables locales si es necesario */
.layout-content {
  flex: 1;
  padding: 2rem;
  background-color: var(--bg-color);
  overflow-y: auto;
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
