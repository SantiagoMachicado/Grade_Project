<template>
  <div class="profile-container">
    <div class="menu-view">
      <div class="top-header">
        <button class="icon-btn" @click="$router.push('/doctor/settings')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h2 class="header-title">Datos Profesionales y Clínicas</h2>
        <div style="width: 24px"></div> <!-- Placeholder -->
      </div>

      <div class="menu-section">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando información...</p>
        </div>

        <div v-else class="info-content">
          
          <!-- Datos Profesionales -->
          <div class="info-card">
            <h3 class="card-title">Perfil Profesional</h3>
            
            <div class="info-row">
              <span class="info-label">Especialidad</span>
              <span class="info-value">{{ doctorData.specialty || 'No especificada' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Nro. de Colegiado</span>
              <span class="info-value">{{ doctorData.license_number || 'No registrado' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Tarifa Base de Consulta</span>
              <span class="info-value">{{ doctorData.consultation_fee ? `Bs. ${doctorData.consultation_fee}` : 'No establecida' }}</span>
            </div>
          </div>

          <!-- Clínicas Asignadas -->
          <div class="info-card">
            <h3 class="card-title">Clínicas Asignadas</h3>
            <p class="card-subtitle">Centros médicos donde prestas servicio actualmente.</p>
            
            <div v-if="clinics.length === 0" class="empty-clinics">
              No estás asignado a ninguna clínica en este momento.
            </div>
            
            <div class="clinic-list" v-else>
              <div v-for="assignment in clinics" :key="assignment.id" class="clinic-item">
                <div class="clinic-icon">🏥</div>
                <div class="clinic-details">
                  <h4>{{ assignment.center?.name || 'Clínica' }}</h4>
                  <p>{{ assignment.center?.address || 'Dirección no disponible' }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="readonly-notice">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            <p>Estos datos son de solo lectura y son gestionados por la administración central.</p>
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
const doctorData = ref({})
const clinics = ref([])

const fetchClinicData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    // 1. Obtener perfil profesional del doctor
    const resDoctor = await axios.get(`http://localhost:8000/api/v1/doctors/${doctorId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    doctorData.value = resDoctor.data
    
    // 2. Obtener las asignaciones a clínicas
    const resClinics = await axios.get(`http://localhost:8000/api/v1/clinics/assignments`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Filtramos las asignaciones para mostrar solo las del doctor actual
    clinics.value = resClinics.data.filter(a => a.doctor_id === doctorId)
    
  } catch (error) {
    console.error("Error fetching clinic info:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchClinicData()
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
  transition: max-width 0.3s ease;
}

@media (min-width: 860px) {
  .profile-container {
    max-width: 1000px;
  }
  .info-content {
    display: grid !important;
    grid-template-columns: 1fr 1.2fr;
    gap: 2rem !important;
  }
  .readonly-notice {
    grid-column: span 2;
  }
}

.menu-view { width: 100%; }

.top-header { 
  display: flex; align-items: center; justify-content: space-between; 
  padding: 1.5rem; background: white; border-bottom: 1px solid #f1f5f9; 
}

.icon-btn { 
  background: none; border: none; color: #64748b; cursor: pointer; 
  display: flex; align-items: center; justify-content: center; 
  padding: 0.5rem; border-radius: 50%; transition: background 0.2s, color 0.2s; 
  margin-left: -0.5rem;
}
.icon-btn:hover { background: #f1f5f9; color: #1e293b; }

.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

.menu-section { padding: 1.5rem; }

.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { 
  width: 30px; height: 30px; border: 3px solid #f1f5f9; 
  border-top: 3px solid #0284c7; border-radius: 50%; 
  animation: spin 1s linear infinite; margin: 0 auto 1rem auto; 
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.info-content { display: flex; flex-direction: column; gap: 1.5rem; }

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.card-title { margin: 0 0 1.25rem 0; font-size: 1.05rem; color: #1e293b; font-weight: 700; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem; }
.card-subtitle { margin: -0.75rem 0 1.25rem 0; font-size: 0.85rem; color: #64748b; line-height: 1.4; }

.info-row { display: flex; flex-direction: column; gap: 0.25rem; margin-bottom: 1rem; }
.info-row:last-child { margin-bottom: 0; }
.info-label { font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.info-value { font-size: 1rem; color: #1e293b; font-weight: 500; }

.empty-clinics { padding: 1rem; background: #f8fafc; border-radius: 8px; color: #64748b; font-size: 0.9rem; text-align: center; border: 1px dashed #cbd5e1; }

.clinic-list { display: flex; flex-direction: column; gap: 0.75rem; }
.clinic-item { display: flex; align-items: flex-start; gap: 1rem; padding: 1rem; background: #f8fafc; border-radius: 12px; border: 1px solid #f1f5f9; }
.clinic-icon { font-size: 1.5rem; background: white; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.clinic-details h4 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 0.95rem; font-weight: 700; }
.clinic-details p { margin: 0; color: #64748b; font-size: 0.85rem; line-height: 1.3; }

.readonly-notice { display: flex; align-items: flex-start; gap: 0.5rem; color: #64748b; background: #f1f5f9; padding: 1rem; border-radius: 12px; }
.readonly-notice svg { flex-shrink: 0; color: #0284c7; margin-top: 0.1rem; }
.readonly-notice p { margin: 0; font-size: 0.85rem; line-height: 1.4; }
</style>
