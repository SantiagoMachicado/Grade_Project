<template>
  <aside class="doctor-sidebar">
    <div class="sidebar-header">
      <h3>Panel Médico</h3>
    </div>
    <nav class="sidebar-nav">
      <RouterLink to="/doctor/dashboard" class="nav-item" active-class="active">
        <span class="icon">🏠</span> Inicio
      </RouterLink>
      <RouterLink to="/doctor/agenda" class="nav-item" active-class="active">
        <span class="icon">📅</span> Agenda
      </RouterLink>
      <RouterLink to="/doctor/patients" class="nav-item" active-class="active">
        <span class="icon">👥</span> Mis Pacientes
      </RouterLink>
      <RouterLink to="/doctor/reports" class="nav-item" active-class="active">
        <span class="icon">📊</span> Informes
      </RouterLink>
      <RouterLink to="/doctor/settings" class="nav-item" active-class="active">
        <span class="icon">⚙️</span> Ajustes
      </RouterLink>
      
      <div class="divider"></div>
      <p class="nav-subtitle">Comunicaciones</p>
      
      <RouterLink to="/chat" class="nav-item">
        <span class="icon">💬</span> Mensajes
      </RouterLink>
      
      <div class="spacer"></div>
      
      <button @click="handleLogout" class="nav-item logout-item">
        <span class="icon">🚪</span> Cerrar Sesión
      </button>
    </nav>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('access_token')
  router.push('/login')
}
</script>

<style scoped>
.doctor-sidebar {
  width: 260px;
  background-color: var(--card-bg);
  border-right: 1px solid #E5E7EB;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
}

.sidebar-header {
  margin-bottom: 2rem;
  padding-left: 0.5rem;
  color: var(--text-main);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-muted);
  font-weight: 500;
  transition: all 0.2s;
}

.nav-item .icon {
  margin-right: 12px;
  font-size: 1.2rem;
}

.nav-item:hover {
  background-color: #ECFDF5; /* Verde claro para hover médico */
  color: #10B981;
}

.nav-item.active {
  background-color: #D1FAE5; /* Fondo verde activo */
  color: #059669; /* Texto verde oscuro */
  font-weight: 600;
}

.divider {
  height: 1px;
  background-color: #E5E7EB;
  margin: 1.5rem 0 1rem 0;
}

.nav-subtitle {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #9CA3AF;
  font-weight: 600;
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  letter-spacing: 0.05em;
}

.spacer {
  flex: 1;
}

.logout-item {
  margin-top: auto;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  color: var(--danger-color);
  font-family: inherit;
  font-size: inherit;
}

.logout-item:hover {
  background-color: #FEE2E2;
  color: #DC2626;
}
</style>
