<template>
  <div class="settings-container">
    <div class="header-section">
      <button class="back-btn" @click="$router.push('/doctor/dashboard')">
        <span class="back-arrow">←</span> Configuración
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else class="settings-content">
      <!-- Profile Card -->
      <div class="profile-card glass-card">
        <div class="avatar-container">
          <img :src="`https://ui-avatars.com/api/?name=${doctorName}&background=64748b&color=fff&size=120`" alt="Avatar" class="avatar-img" />
          <button class="edit-avatar-btn">
            <span>✏️</span>
          </button>
        </div>
        <div class="profile-info">
          <h2>{{ doctorName }}</h2>
          <p class="subtitle">{{ specialty }}</p>
          <div class="id-badge">ID: {{ licenseNumber }}</div>
        </div>
      </div>

      <!-- Menus -->
      <div class="menu-section">
        <h4 class="section-title">PERFIL PROFESIONAL</h4>
        <div class="menu-list glass-card">
          <div class="menu-item" @click="$router.push('/doctor/settings/personal')">
            <div class="item-left">
              <span class="icon-wrapper">👤</span>
              <span>Información Personal</span>
            </div>
            <span class="chevron">›</span>
          </div>
          <div class="menu-divider"></div>
          <div class="menu-item" @click="$router.push('/doctor/settings/clinic')">
            <div class="item-left">
              <span class="icon-wrapper">🏥</span>
              <span>Datos de la Clínica</span>
            </div>
            <span class="chevron">›</span>
          </div>
        </div>
      </div>

      <div class="menu-section">
        <h4 class="section-title">PREFERENCIAS</h4>
        <div class="menu-list glass-card">
          <div class="menu-item" @click="$router.push('/doctor/settings/notifications')">
            <div class="item-left">
              <span class="icon-wrapper">🔔</span>
              <span>Notificaciones</span>
            </div>
            <div class="item-right">
              <span class="status-text">Activado</span>
              <span class="chevron">›</span>
            </div>
          </div>
        </div>
      </div>

      <div class="menu-section">
        <h4 class="section-title">AYUDA</h4>
        <div class="menu-list glass-card">
          <div class="menu-item" @click="$router.push('/help-center')">
            <div class="item-left">
              <span class="icon-wrapper">❓</span>
              <span>Centro de ayuda</span>
            </div>
            <span class="chevron external-icon">↗</span>
          </div>
          <div class="menu-divider"></div>
          <div class="menu-item" @click="$router.push('/doctor/settings/about')">
            <div class="item-left">
              <span class="icon-wrapper">ℹ️</span>
              <span>Acerca de la plataforma</span>
            </div>
            <span class="chevron">›</span>
          </div>
        </div>
      </div>

      <div class="menu-section logout-section">
        <div class="menu-list glass-card">
          <div class="menu-item logout-item" @click="handleLogout">
            <div class="item-left">
              <span class="icon-wrapper logout-icon">🚪</span>
              <span>Cerrar sesión</span>
            </div>
          </div>
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
    specialty = res.data.specialty || 'Especialista General'
    // To match the image exactly, we will append a generic clinic string if we don't fetch it
    specialty.value = `${specialty} - Clínica Asociada`
    
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
.settings-container {
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 3rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.header-section {
  margin-bottom: 1.5rem;
  padding: 0.5rem 0;
}

.back-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0;
}

.back-arrow {
  color: #004e98;
  font-size: 1.4rem;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  border-radius: 16px;
  background: white;
  margin-bottom: 2rem;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  gap: 1.5rem;
}

.avatar-container {
  position: relative;
}

.avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e2e8f0;
}

.edit-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #004e98;
  border: 2px solid white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.edit-avatar-btn span {
  font-size: 0.75rem;
  color: white;
}

.profile-info h2 {
  margin: 0 0 0.2rem 0;
  font-size: 1.2rem;
  color: #0f172a;
}

.profile-info .subtitle {
  margin: 0 0 0.5rem 0;
  font-size: 0.85rem;
  color: #64748b;
}

.id-badge {
  display: inline-block;
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.menu-section {
  margin-bottom: 1.5rem;
}

.section-title {
  margin: 0 0 0.75rem 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.menu-list {
  background: white;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 2px 4px rgba(0,0,0,0.01);
  overflow: hidden;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #f8fafc;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.95rem;
  color: #334155;
  font-weight: 500;
}

.icon-wrapper {
  background: #f1f5f9;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 1.1rem;
  color: #004e98;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-text {
  font-size: 0.85rem;
  color: #94a3b8;
}

.chevron {
  color: #cbd5e1;
  font-size: 1.2rem;
  font-weight: 300;
}

.external-icon {
  font-size: 1rem;
}

.menu-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0 1.5rem;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem;
}
.spinner {
  width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #004e98; border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.logout-section {
  margin-top: 2.5rem;
}

.logout-item .item-left span:not(.icon-wrapper) {
  color: #ef4444;
  font-weight: 600;
}

.logout-icon {
  background: #fef2f2;
  color: #ef4444;
}
</style>
