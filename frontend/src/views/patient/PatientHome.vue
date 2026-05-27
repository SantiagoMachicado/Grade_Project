<template>
  <div class="home-container">
    <!-- Header -->
    <div class="home-header">
      <div class="user-info">
        <div class="avatar">{{ getInitials(patient?.full_name) }}</div>
        <div class="greeting-text">
          <span class="welcome-back">Bienvenido de nuevo</span>
          <h1 class="user-name">Hola, {{ getFirstName(patient?.full_name) }}</h1>
        </div>
      </div>
      <button class="notif-btn" @click="$router.push('/patient/profile?view=notifications')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
      </button>
    </div>

    <div class="home-layout-grid">
      <!-- Left Column: Navigation and Actions -->
      <div class="left-column">
        <h2 class="main-question">¿En qué podemos<br>ayudarte hoy?</h2>

        <div class="actions-grid">
          <button class="action-card btn-cyan" @click="$router.push('/patient/appointments/new')">
            <div class="icon-wrapper cyan-light">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <span>Buscar Médicos</span>
          </button>

          <button class="action-card btn-dark" @click="$router.push('/chat')">
            <div class="icon-wrapper dark-light">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00d1b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>
            </div>
            <span>Hablar con IA</span>
          </button>
        </div>
      </div>

      <!-- Right Column: Upcoming Appointments -->
      <div class="right-column">
        <div class="upcoming-section">
          <div class="section-header">
            <h3>Próximas citas</h3>
            <button class="view-all-btn" @click="$router.push('/patient/appointments')">Ver todas</button>
          </div>

          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
          </div>
          
          <div v-else-if="upcomingAppointment" class="appointment-card">
            <div class="doc-info">
              <img class="doc-avatar" :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${upcomingAppointment.doctor?.full_name || 'Doc'}&backgroundColor=e2e8f0&clothing=blazerAndShirt`" alt="Doctor Avatar">
              <div>
                <h4>Dr. {{ upcomingAppointment.doctor?.full_name || 'No asignado' }}</h4>
                <p class="specialty">{{ upcomingAppointment.doctor?.specialty || 'Medicina General' }}</p>
              </div>
            </div>

            <div class="time-row">
              <div class="time-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <span>{{ formatRelativeDay(upcomingAppointment.appointment_date) }}</span>
              </div>
              <div class="time-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span>{{ formatTime(upcomingAppointment.appointment_date) }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button class="btn-reschedule" @click="$router.push('/patient/appointments/new')">Reagendar</button>
              <button class="btn-details" @click="$router.push('/patient/profile?view=medical_history')">Ver detalles</button>
            </div>
          </div>

          <div v-else class="empty-appointment">
            <p>No tienes citas próximas agendadas.</p>
            <button class="btn-details" @click="$router.push('/patient/appointments/new')">Agendar ahora</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const patient = ref(null)
const upcomingAppointment = ref(null)
const loading = ref(true)

const getInitials = (name) => {
  if (!name) return 'P'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const getFirstName = (name) => {
  if (!name) return 'Paciente'
  return name.split(' ')[0]
}

const formatRelativeDay = (dateStr) => {
  const d = new Date(dateStr)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  if (d.getDate() === today.getDate() && d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear()) {
    return 'Hoy'
  }
  if (d.getDate() === tomorrow.getDate() && d.getMonth() === tomorrow.getMonth() && d.getFullYear() === tomorrow.getFullYear()) {
    return 'Mañana'
  }
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

const formatTime = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
}

const fetchData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const patientId = payload.id

    // Obtener información del paciente
    const profileRes = await axios.get(`http://localhost:8000/api/v1/patients/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    patient.value = profileRes.data

    // Obtener citas
    const apptsRes = await axios.get(`http://localhost:8000/api/v1/appointments/patient/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const now = new Date()
    const futureAppointments = apptsRes.data
      .filter(a => a.status === 'confirmada')
      .map(a => ({ ...a, parsedDate: new Date(a.appointment_date) }))
      .filter(a => a.parsedDate > now)
      .sort((a, b) => a.parsedDate - b.parsedDate)
      
    if (futureAppointments.length > 0) {
      upcomingAppointment.value = futureAppointments[0]
    }

  } catch (err) {
    console.error("Error fetching patient home data", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 1.5rem;
  background: #ffffff;
  min-height: 80vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  transition: max-width 0.3s ease;
}

@media (min-width: 860px) {
  .home-container {
    max-width: 1000px;
    background: #fafafa;
    border-radius: 24px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
    padding: 2rem;
  }
  .home-layout-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 2.5rem;
    align-items: start;
  }
  .upcoming-section {
    background: white;
    padding: 1.5rem;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    border: 1px solid #f1f5f9;
  }
  .appointment-card {
    box-shadow: none !important;
    border: 1px solid #e2e8f0 !important;
  }
}

/* Header */
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #fcebd7; /* Light beige matching image */
  color: #a17852;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}
.greeting-text {
  display: flex;
  flex-direction: column;
}
.welcome-back {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}
.user-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
}
.notif-btn {
  background: #f1f5f9;
  border: none;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}
.notif-btn:hover { background: #e2e8f0; }

/* Main Question */
.main-question {
  font-size: 1.7rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.25;
  margin-bottom: 2rem;
}

/* Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2.5rem;
}
.action-card {
  border: none;
  border-radius: 20px;
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.action-card span {
  font-weight: 700;
  font-size: 0.95rem;
  color: white;
}

.btn-cyan {
  background: #00bcd4; /* Cyan solid */
}
.icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cyan-light { background: rgba(255,255,255,0.25); }

.btn-dark {
  background: #111827; /* Dark blue/black */
}
.dark-light { background: rgba(255,255,255,0.1); }

/* Upcoming Section */
.upcoming-section {
  display: flex;
  flex-direction: column;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.section-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
}
.view-all-btn {
  background: none;
  border: none;
  color: #00bcd4;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
}

.appointment-card {
  background: white;
  border: 1px solid #f1f5f9;
  border-radius: 20px;
  padding: 1.25rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}
.doc-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.doc-avatar {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: #334155;
  display: flex;
  align-items: center;
  justify-content: center;
}
.doc-info h4 { margin: 0 0 0.25rem 0; font-size: 1rem; font-weight: 800; color: #1e293b; }
.specialty { margin: 0; font-size: 0.8rem; color: #00bcd4; font-weight: 600; }

.time-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}
.time-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
}

.card-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.btn-reschedule {
  background: #e6fbfc;
  color: #00bcd4;
  border: none;
  border-radius: 12px;
  padding: 0.75rem;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-reschedule:hover { background: #cffafe; }

.btn-details {
  background: #00bcd4;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-details:hover { background: #0891b2; }

.empty-appointment {
  background: #f8fafc;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  color: #64748b;
}
.empty-appointment p { margin-bottom: 1rem; font-size: 0.9rem; }

.loading-state { text-align: center; padding: 2rem 0; }
.spinner { width: 30px; height: 30px; border: 3px solid #f1f5f9; border-top: 3px solid #00bcd4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
