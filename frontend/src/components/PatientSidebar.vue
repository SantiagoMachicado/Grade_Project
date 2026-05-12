<template>
  <nav class="bottom-nav">
    <RouterLink to="/patient/dashboard" class="nav-item" active-class="active">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
      <span>Inicio</span>
    </RouterLink>

    <RouterLink to="/map" class="nav-item" active-class="active">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
      <span>Mapa</span>
    </RouterLink>

    <RouterLink to="/chat" class="nav-item" active-class="active">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
      <span>Mensajes</span>
    </RouterLink>

    <RouterLink to="/patient/appointments" class="nav-item" active-class="active" :class="{ 'active': $route.path.includes('/patient/appointments') }">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
      <span>Mis Citas</span>
    </RouterLink>

    <RouterLink to="/patient/profile" class="nav-item" active-class="active">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
      <span>Perfil</span>
    </RouterLink>
  </nav>
</template>

<script setup>
// No logic needed, links handle navigation automatically
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 65px;
  background-color: white;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom);
  box-shadow: 0 -2px 10px rgba(0,0,0,0.02);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #94a3b8;
  flex: 1;
  height: 100%;
  transition: all 0.2s;
  gap: 4px;
}

.nav-item span {
  font-size: 0.65rem;
  font-weight: 700;
}

.nav-item .icon {
  width: 24px;
  height: 24px;
  transition: transform 0.2s;
}

.nav-item.active {
  color: #004e98;
}

.nav-item.active .icon {
  stroke-width: 2.5;
}

.nav-item:active .icon {
  transform: scale(0.9);
}

@media (min-width: 768px) {
  .bottom-nav {
    max-width: 480px;
    margin: 0 auto;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 20px 20px 0 0;
    border-left: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
  }
}
</style>
