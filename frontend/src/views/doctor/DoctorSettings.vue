<template>
  <div class="profile-container">
    <div class="menu-view">
      <div class="top-header">
        <button class="icon-btn" @click="$router.push('/doctor/dashboard')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h2 class="header-title">Configuración</h2>
        <div style="width: 24px"></div> <!-- Placeholder para balancear el header -->
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="profile-summary">
        <div class="avatar-wrapper">
          <div class="avatar-circle">
            {{ getInitials(doctorName) }}
          </div>
          <button class="edit-avatar-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
          </button>
        </div>
        
        <h3 class="patient-name">{{ doctorName }}</h3>
        <p class="patient-email">{{ specialty }}</p>
        <div class="patient-id-badge">ID: {{ licenseNumber }}</div>
      </div>

      <div class="menu-section" v-if="!loading">
        <div class="section-label">PERFIL PROFESIONAL</div>
        
        <div class="menu-list">
          <button class="menu-item" @click="$router.push('/doctor/settings/personal')">
            <div class="menu-icon bg-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <div class="menu-text">
              <h4>Información Personal</h4>
              <p>Datos personales y contacto</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>

          <div class="menu-divider"></div>

          <button class="menu-item" @click="$router.push('/doctor/settings/clinic')">
            <div class="menu-icon bg-indigo">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
            </div>
            <div class="menu-text">
              <h4>Datos de la Clínica</h4>
              <p>Información del centro médico</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>

          <div class="menu-divider"></div>

          <button class="menu-item" @click="$router.push('/doctor/settings/schedules')">
            <div class="menu-icon bg-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="menu-text">
              <h4>Gestión de Horarios</h4>
              <p>Disponibilidad por clínica</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>
        </div>

        <div class="section-label">PREFERENCIAS Y AYUDA</div>
        <div class="menu-list">
          <button class="menu-item" @click="$router.push('/doctor/settings/notifications')">
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
          
          <div class="menu-divider"></div>

          <button class="menu-item" @click="$router.push('/help-center')">
            <div class="menu-icon bg-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </div>
            <div class="menu-text">
              <h4>Centro de Ayuda</h4>
              <p>Soporte y preguntas frecuentes</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>

          <div class="menu-divider"></div>

          <button class="menu-item" @click="$router.push('/doctor/settings/about')">
            <div class="menu-icon bg-indigo">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            </div>
            <div class="menu-text">
              <h4>Acerca de la plataforma</h4>
              <p>Versión y términos de uso</p>
            </div>
            <div class="menu-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </button>
        </div>

        <button class="logout-btn" @click="handleLogout">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Cerrar Sesión
        </button>

        <div class="footer-version">
          MEDICAL PLATFORM V1.0.0
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const doctorName = ref('')
const specialty = ref('')
const licenseNumber = ref('')

const getInitials = (name) => {
  if (!name) return 'Dr'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const fetchDoctorInfo = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    const res = await axios.get(`http://localhost:8000/api/v1/doctors/${doctorId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    doctorName.value = res.data.full_name || 'Dr. Médico'
    let fetchedSpecialty = res.data.specialty || 'Especialista General'
    specialty.value = `${fetchedSpecialty} - Clínica Asociada`
    licenseNumber.value = res.data.license_number || '12345678'
  } catch (err) {
    console.error(err)
    doctorName.value = 'Dr. Alejandro Smith'
    specialty.value = 'Cardiólogo - Clínica Santa María'
    licenseNumber.value = '12345678'
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  router.push('/login')
}

onMounted(() => {
  fetchDoctorInfo()
})
</script>

<style scoped>
.profile-container {
  max-width: 480px;
  margin: 0 auto;
  background: #fafafa;
  min-height: 80vh;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.05);
  overflow: hidden;
  position: relative;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  margin-bottom: 2rem;
}
.menu-view {
  width: 100%;
}
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; }
.icon-btn { background: none; border: none; color: #1e40af; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #eff6ff; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.profile-summary { background: white; display: flex; flex-direction: column; align-items: center; padding: 1rem 2rem 2rem; border-bottom: 1px solid #f1f5f9; }
.avatar-wrapper { position: relative; margin-bottom: 1rem; }
.avatar-circle { width: 100px; height: 100px; border-radius: 50%; background: #e2e8f0; color: #64748b; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: 700; box-shadow: 0 10px 25px rgba(0,0,0,0.1); background-image: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); border: 4px solid white; }
.edit-avatar-btn { position: absolute; bottom: 0; right: 0; width: 32px; height: 32px; border-radius: 50%; background: #0284c7; color: white; border: 3px solid white; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.patient-name { margin: 0 0 0.25rem 0; font-size: 1.4rem; font-weight: 800; color: #1e293b; text-align: center; }
.patient-email { margin: 0 0 0.75rem 0; color: #64748b; font-size: 0.9rem; text-align: center; }
.patient-id-badge { background: #e0f2fe; color: #0369a1; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; }
.menu-section { padding: 2rem 1.5rem; }
.section-label { font-size: 0.75rem; font-weight: 700; color: #94a3b8; letter-spacing: 1px; margin-bottom: 1rem; padding-left: 0.5rem; margin-top: 1rem; }
.section-label:first-child { margin-top: 0; }
.menu-list { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 1.5rem; }
.menu-item { display: flex; align-items: center; width: 100%; padding: 1.25rem; background: white; border: none; cursor: pointer; text-align: left; transition: background 0.2s; }
.menu-item:hover { background: #f8fafc; }
.menu-item:active { background: #f1f5f9; }
.menu-divider { height: 1px; background: #f1f5f9; margin: 0 1.25rem; }
.menu-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; flex-shrink: 0; }
.bg-blue { background: #e0f2fe; color: #0284c7; }
.bg-indigo { background: #e0e7ff; color: #4f46e5; }
.bg-gray { background: #f1f5f9; color: #475569; }
.menu-text { flex: 1; }
.menu-text h4 { margin: 0 0 0.2rem 0; font-size: 1rem; font-weight: 700; color: #1e293b; }
.menu-text p { margin: 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.3; }
.menu-arrow { color: #cbd5e1; flex-shrink: 0; }
.logout-btn { display: flex; align-items: center; justify-content: center; gap: 0.5rem; width: 100%; padding: 1.25rem; background: #fef2f2; color: #ef4444; border: none; border-radius: 16px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: all 0.2s; margin-top: 1rem; }
.logout-btn:hover { background: #fee2e2; }
.footer-version { text-align: center; margin-top: 2rem; font-size: 0.7rem; color: #cbd5e1; letter-spacing: 2px; font-weight: 700; }
.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top: 4px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
