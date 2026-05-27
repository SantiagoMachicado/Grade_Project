<template>
  <div class="menu-view">
    <div class="top-header">
      <button class="icon-btn" @click="emit('back')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <h2 class="header-title">Mi Perfil</h2>
      <button class="icon-btn">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else-if="patient" class="profile-menu-grid">
      <div class="profile-summary">
        <div class="avatar-wrapper">
          <div class="avatar-circle">
            {{ getInitials(patient.full_name) }}
          </div>
          <button class="edit-avatar-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
          </button>
        </div>
        
        <h3 class="patient-name">{{ patient.full_name }}</h3>
        <p class="patient-email">{{ patient.user.email }}</p>
        <div class="patient-id-badge">ID: {{ String(patient.user_id).padStart(8, '0') }}</div>
      </div>

      <div class="menu-section">
        <div class="section-label">CONFIGURACIÓN DE CUENTA</div>
        
        <div class="menu-list">
          <!-- Información Personal -->
          <button class="menu-item" @click="emit('navigate', 'personal_info')">
            <div class="menu-icon bg-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <div class="menu-text">
              <h4>Información Personal</h4>
              <p>Nombre, Teléfono, Fecha de Nacimiento</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>

          <div class="menu-divider"></div>

          <!-- Historial Médico -->
          <button class="menu-item" @click="emit('navigate', 'medical_history')">
            <div class="menu-icon bg-indigo">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>
            </div>
            <div class="menu-text">
              <h4>Historial Médico</h4>
              <p>Resumen de citas y diagnósticos</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>

          <div class="menu-divider"></div>

          <!-- Notificaciones -->
          <button class="menu-item" @click="emit('navigate', 'notifications')">
            <div class="menu-icon bg-gray">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            </div>
            <div class="menu-text">
              <h4>Notificaciones</h4>
              <p>Alertas de citas y mensajes</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>
        </div>

        <button class="logout-btn" @click="emit('logout')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Cerrar Sesión
        </button>

        <div class="footer-version">
          HOSPITAL CONNECT V1.0.0
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  patient: Object,
  loading: Boolean
})

const emit = defineEmits(['navigate', 'logout', 'back'])

const getInitials = (name) => {
  if (!name) return 'U'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}
</script>

<style scoped>
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; }
.icon-btn { background: none; border: none; color: #1e40af; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #eff6ff; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.profile-summary { background: white; display: flex; flex-direction: column; align-items: center; padding: 1rem 2rem 2rem; border-bottom: 1px solid #f1f5f9; }
.avatar-wrapper { position: relative; margin-bottom: 1rem; }
.avatar-circle { width: 100px; height: 100px; border-radius: 50%; background: #e2e8f0; color: #64748b; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: 700; box-shadow: 0 10px 25px rgba(0,0,0,0.1); background-image: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); border: 4px solid white; }
.edit-avatar-btn { position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background: #0284c7; color: white; border: 3px solid white; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.patient-name { margin: 0 0 0.25rem 0; font-size: 1.4rem; font-weight: 800; color: #1e293b; }
.patient-email { margin: 0 0 0.75rem 0; color: #64748b; font-size: 0.9rem; }
.patient-id-badge { background: #e0f2fe; color: #0369a1; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; }
.menu-section { padding: 2rem 1.5rem; }
.section-label { font-size: 0.75rem; font-weight: 700; color: #94a3b8; letter-spacing: 1px; margin-bottom: 1rem; padding-left: 0.5rem; }
.menu-list { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 2rem; }
.menu-item { display: flex; align-items: center; width: 100%; padding: 1.25rem; background: white; border: none; cursor: pointer; text-align: left; transition: background 0.2s; }
.menu-item:hover { background: #f8fafc; }
.menu-item:active { background: #f1f5f9; }
.menu-divider { height: 1px; background: #f1f5f9; margin: 0 1.25rem; }
.menu-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; }
.bg-blue { background: #e0f2fe; color: #0284c7; }
.bg-indigo { background: #e0e7ff; color: #4f46e5; }
.bg-gray { background: #f1f5f9; color: #475569; }
.menu-text { flex: 1; }
.menu-text h4 { margin: 0 0 0.2rem 0; font-size: 1rem; font-weight: 700; color: #1e293b; }
.menu-text p { margin: 0; font-size: 0.8rem; color: #94a3b8; }
.menu-arrow { color: #cbd5e1; }
.logout-btn { display: flex; align-items: center; justify-content: center; gap: 0.5rem; width: 100%; padding: 1.25rem; background: #fef2f2; color: #ef4444; border: none; border-radius: 16px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.logout-btn:hover { background: #fee2e2; }
.footer-version { text-align: center; margin-top: 2rem; font-size: 0.7rem; color: #cbd5e1; letter-spacing: 2px; font-weight: 700; }
.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top: 4px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (min-width: 860px) {
  .profile-menu-grid {
    display: grid;
    grid-template-columns: 1fr 1.8fr;
    gap: 2rem;
    align-items: start;
    padding: 1.5rem;
  }
  .profile-summary {
    border-bottom: none !important;
    border-right: 1px solid #f1f5f9;
    padding-right: 2rem !important;
    height: 100%;
  }
  .menu-section {
    padding: 0 0 0 1rem !important;
  }
}
</style>
