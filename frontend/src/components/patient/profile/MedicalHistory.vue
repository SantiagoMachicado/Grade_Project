<template>
  <div class="history-view">
    <div class="top-header">
      <button class="icon-btn" @click="emit('back')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <h2 class="header-title">Historial Médico</h2>
      <div style="width: 24px;"></div>
    </div>

    <div v-if="loadingAppointments" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else class="history-content">
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">CONSULTAS</span>
          <span class="stat-value">{{ completedAppointments.length }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">ÚLTIMA VISITA</span>
          <span class="stat-value">{{ lastVisitDate }}</span>
        </div>
      </div>

      <div class="records-header">
        <h3>Registros Recientes</h3>
      </div>

      <div class="records-list">
        <div v-if="completedAppointments.length === 0" class="empty-records">
          No tienes citas completadas aún.
        </div>
        <div class="record-card" v-for="appt in completedAppointments" :key="appt.id">
          <div class="card-header">
            <div class="icon-box">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
            </div>
            <div class="doctor-info">
              <div class="date-text">{{ formatLongDate(appt.appointment_date) }}</div>
              <div class="doctor-name">Dr. {{ appt.doctor?.full_name }}</div>
              <div class="specialty">{{ appt.doctor?.specialty }}</div>
            </div>
            <div class="status-badge">COMPLETADO</div>
          </div>
          
          <div class="card-body">
            <div class="diagnosis-label">DIAGNÓSTICO</div>
            <div class="diagnosis-text">{{ appt.medical_report || 'Sin diagnóstico registrado.' }}</div>
          </div>

          <div class="card-footer">
            <button class="btn btn-primary full-width" @click="emit('select-appointment', appt)">Ver detalles</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['back', 'select-appointment'])

const completedAppointments = ref([])
const loadingAppointments = ref(false)
const lastVisitDate = ref('--')

const formatLongDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' }).toUpperCase()
}

const formatShortDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

const fetchAppointments = async () => {
  loadingAppointments.value = true
  try {
    const token = localStorage.getItem('access_token')
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    
    const res = await axios.get(`http://localhost:8000/api/v1/appointments/patient/${payload.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const completed = res.data.filter(a => a.status === 'completada')
    completedAppointments.value = completed.sort((a,b) => new Date(b.appointment_date) - new Date(a.appointment_date))
    
    if (completedAppointments.value.length > 0) {
      lastVisitDate.value = formatShortDate(completedAppointments.value[0].appointment_date)
    }
  } catch (err) {
    console.error("Error fetching appointments", err)
  } finally {
    loadingAppointments.value = false
  }
}

onMounted(() => {
  fetchAppointments()
})
</script>

<style scoped>
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; }
.icon-btn { background: none; border: none; color: #1e40af; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #eff6ff; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

.history-view { padding-bottom: 2rem; }
.history-content { padding: 1.5rem; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem; }
.stat-card { background: white; padding: 1.25rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); display: flex; flex-direction: column; }
.stat-label { font-size: 0.75rem; font-weight: 700; color: #64748b; margin-bottom: 0.5rem; letter-spacing: 0.5px; }
.stat-value { font-size: 1.5rem; font-weight: 800; color: #0284c7; }
.records-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.records-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; }
.record-card { background: white; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.card-header { display: flex; align-items: flex-start; margin-bottom: 1.5rem; }
.icon-box { width: 48px; height: 48px; background: #eff6ff; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; }
.doctor-info { flex: 1; }
.date-text { font-size: 0.75rem; font-weight: 700; color: #64748b; margin-bottom: 0.25rem; }
.doctor-name { font-size: 1rem; font-weight: 800; color: #1e293b; margin-bottom: 0.2rem; }
.specialty { font-size: 0.85rem; color: #94a3b8; }
.status-badge { background: #dbeafe; color: #1e3a8a; font-size: 0.65rem; font-weight: 800; padding: 0.3rem 0.6rem; border-radius: 8px; letter-spacing: 0.5px; }
.card-body { background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; }
.diagnosis-label { font-size: 0.75rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem; }
.diagnosis-text { font-size: 0.85rem; color: #475569; line-height: 1.5; }
.empty-records { text-align: center; color: #94a3b8; padding: 2rem; background: white; border-radius: 12px; }

.full-width { width: 100%; padding: 1rem; font-size: 1rem; box-sizing: border-box; }
.btn { border-radius: 10px; font-weight: 700; cursor: pointer; border: none; transition: all 0.2s ease; box-sizing: border-box; }
.btn-primary { background: #0284c7; color: white; }
.btn-primary:hover { background: #0369a1; }
.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top: 4px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (min-width: 860px) {
  .records-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  .record-card {
    margin-bottom: 0;
  }
}
</style>
