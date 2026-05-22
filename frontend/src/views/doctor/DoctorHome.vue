<template>
  <div class="responsive-dashboard-container">
    
    <!-- Top Header Style from the new design -->
    <div class="top-header">
      <div class="profile-header">
        <div class="doctor-avatar">{{ getInitials(doctorName) }}</div>
        <div>
          <span class="greeting">¡Buen día!</span>
          <h2 class="doctor-name">Hola, Dr. {{ doctorName }}</h2>
        </div>
      </div>
      <div class="notification-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando panel...</p>
    </div>

    <div v-else-if="dashboardData" class="dashboard-content">
      
      <!-- Responsive Grid Container -->
      <div class="dashboard-grid">
        
        <!-- Left Column: Summaries & Next Appointment -->
        <div class="grid-col-left">
          
          <!-- Resumen de Hoy -->
          <section class="summary-section">
            <h3 class="section-title">Resumen de Hoy</h3>
            <div class="summary-cards">
              <div class="summary-card today-card">
                <div class="card-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                </div>
                <div class="card-text">
                  <p>Citas hoy</p>
                  <h2>{{ dashboardData.today_appointments_count }}</h2>
                </div>
              </div>
              <div class="summary-card new-card">
                <div class="card-icon blue-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
                </div>
                <div class="card-text">
                  <p>Pacientes nuevos</p>
                  <h2>{{ dashboardData.new_patients_count }}</h2>
                </div>
              </div>
            </div>
          </section>

          <!-- Próxima Cita -->
          <section class="next-appt-section" v-if="dashboardData.next_appointment">
            <div class="section-header">
              <h3 class="section-title">Próxima cita</h3>
              <span class="time-badge">{{ getRelativeTime(dashboardData.next_appointment.appointment_date) }}</span>
            </div>
            <div class="next-appt-card">
              <div class="next-appt-info">
                <div class="patient-avatar">{{ getInitials(dashboardData.next_appointment.patient?.full_name) }}</div>
                <div class="appt-details">
                  <h4>{{ dashboardData.next_appointment.patient?.full_name || 'Paciente' }}</h4>
                  <div class="time-block">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    <strong>{{ formatTime(dashboardData.next_appointment.appointment_date) }}</strong>
                  </div>
                </div>
              </div>
              <button class="btn btn-primary full-width" @click="openPatientModal(dashboardData.next_appointment)">Ver detalle de la cita</button>
            </div>
          </section>

        </div>

        <!-- Right Column: Lists -->
        <div class="grid-col-right">
          
          <!-- Siguientes Citas -->
          <section class="list-section" v-if="dashboardData.upcoming_appointments.length > 0">
            <div class="section-header">
              <h3 class="section-title">Siguientes citas de hoy</h3>
            </div>
            <div class="menu-list">
              <div 
                v-for="appt in dashboardData.upcoming_appointments" 
                :key="appt.id" 
                class="menu-item"
                @click="openPatientModal(appt)"
              >
                <div class="time-col">
                  <strong>{{ formatTime(appt.appointment_date) }}</strong>
                  <span class="date-sub">{{ formatDate(appt.appointment_date) }}</span>
                </div>
                <div class="menu-text">
                  <h4>{{ appt.patient?.full_name || 'Paciente' }}</h4>
                  <p>Consulta General</p>
                </div>
                <div class="menu-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                </div>
              </div>
            </div>
          </section>

          <!-- Citas No Confirmadas -->
          <section class="list-section" v-if="dashboardData.unconfirmed_appointments.length > 0">
            <div class="section-header">
              <h3 class="section-title">Solicitudes Pendientes</h3>
            </div>
            <div class="menu-list pending-list">
              <div 
                v-for="appt in dashboardData.unconfirmed_appointments" 
                :key="appt.id" 
                class="menu-item"
                @click="openAgendaModal(appt)"
              >
                <div class="time-col pending-time">
                  <strong>{{ formatTime(appt.appointment_date) }}</strong>
                  <span class="date-sub">{{ formatDate(appt.appointment_date) }}</span>
                </div>
                <div class="menu-text">
                  <h4>{{ appt.patient?.full_name || 'Paciente' }}</h4>
                  <p class="pending-badge">Por confirmar</p>
                </div>
                <div class="menu-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                </div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>

    <!-- Modal Detalle (DoctorPatients Style) -->
    <div class="modal-backdrop" v-if="showPatientModal && selectedAppt" @click.self="closeModals">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Detalle de la Consulta</h3>
          <button class="close-btn" @click="closeModals">&times;</button>
        </div>
        <div class="modal-body">
          <div class="patient-summary">
            <div class="summary-avatar">{{ getInitials(selectedAppt.patient?.full_name) }}</div>
            <div>
              <h4>{{ selectedAppt.patient?.full_name || 'Paciente' }}</h4>
              <p>Fecha: {{ formatDate(selectedAppt.appointment_date) }} a las {{ formatTime(selectedAppt.appointment_date) }}</p>
            </div>
          </div>
          <div class="info-section">
            <h5>Motivo de la Cita (Notas)</h5>
            <div class="info-box">{{ selectedAppt.notes || 'No se proporcionaron notas al agendar.' }}</div>
          </div>
          <div class="info-section">
            <h5>Reporte Médico / Diagnóstico</h5>
            <textarea 
              v-model="editedReport" 
              placeholder="Escribe aquí el diagnóstico o notas de esta sesión..."
              rows="3"
              class="report-textarea"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModals">Cerrar</button>
          <button class="btn btn-danger" @click="markAsAbsent" :disabled="saving">Ausente</button>
          <button class="btn btn-success" @click="saveAndFinalize" :disabled="saving">
            {{ saving ? '...' : 'Finalizar Cita' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Agenda (Approve/Reject Style) -->
    <div class="modal-backdrop" v-if="showAgendaModal && selectedAppt" @click.self="closeModals">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Gestión de Cita Pendiente</h3>
          <button class="close-btn" @click="closeModals">&times;</button>
        </div>
        <div class="modal-body">
          <div class="patient-summary">
            <div class="summary-avatar">{{ getInitials(selectedAppt.patient?.full_name) }}</div>
            <div>
              <h4>{{ selectedAppt.patient?.full_name || 'Paciente' }}</h4>
              <p>Solicita: {{ formatDate(selectedAppt.appointment_date) }} - {{ formatTime(selectedAppt.appointment_date) }}</p>
            </div>
          </div>
          <div class="action-buttons">
            <p>¿Deseas confirmar o cancelar esta solicitud de cita?</p>
            <div class="buttons-row">
              <button class="btn btn-success" @click="updateStatus('confirmada')" :disabled="saving">
                {{ saving ? '...' : 'Confirmar' }}
              </button>
              <button class="btn btn-danger" @click="updateStatus('cancelada')" :disabled="saving">
                {{ saving ? '...' : 'Cancelar' }}
              </button>
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
const dashboardData = ref(null)
const loading = ref(true)
const doctorName = ref('')

const showPatientModal = ref(false)
const showAgendaModal = ref(false)
const selectedAppt = ref(null)
const editedReport = ref('')
const saving = ref(false)

const getInitials = (name) => {
  if (!name) return 'Dr'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const formatTime = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
}

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' }).replace('.', '')
}

const getRelativeTime = (dateStr) => {
  const diffMs = new Date(dateStr) - new Date()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 0) return 'EN CURSO'
  if (diffMins < 60) return `EN ${diffMins} MIN`
  return `EN ${Math.floor(diffMins/60)} HR`
}

const fetchDashboard = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    const userRes = await axios.get(`http://localhost:8000/api/v1/doctors/${doctorId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    doctorName.value = userRes.data.full_name || 'Doctor'

    const response = await axios.get(`http://localhost:8000/api/v1/appointments/doctor/${doctorId}/dashboard`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    dashboardData.value = response.data
  } catch (error) {
    console.error("Error fetching dashboard", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboard()
})

// Modals logic
const openPatientModal = (appt) => {
  selectedAppt.value = appt
  editedReport.value = ''
  showPatientModal.value = true
}

const openAgendaModal = (appt) => {
  selectedAppt.value = appt
  showAgendaModal.value = true
}

const closeModals = () => {
  showPatientModal.value = false
  showAgendaModal.value = false
  selectedAppt.value = null
  editedReport.value = ''
}

const updateStatus = async (newStatus) => {
  if (!selectedAppt.value) return
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: newStatus },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    await fetchDashboard()
    closeModals()
  } catch (error) {
    console.error("Error updating status:", error)
    alert("Error al actualizar la cita.")
  } finally {
    saving.value = false
  }
}

const saveAndFinalize = async () => {
  if (!selectedAppt.value) return
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (editedReport.value.trim() !== '') {
      await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/report`, 
        { medical_report: editedReport.value },
        { headers: { Authorization: `Bearer ${token}` } }
      )
    }
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: 'completada' },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    await fetchDashboard()
    closeModals()
  } catch (error) {
    console.error("Error finalizing appointment", error)
    alert("Error al finalizar la cita.")
  } finally {
    saving.value = false
  }
}

const markAsAbsent = async () => {
  if (!selectedAppt.value) return
  if (!confirm("¿Marcar paciente como ausente?")) return
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (editedReport.value.trim() !== '') {
      await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/report`, 
        { medical_report: editedReport.value },
        { headers: { Authorization: `Bearer ${token}` } }
      )
    }
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: 'ausente' },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    await fetchDashboard()
    closeModals()
  } catch (error) {
    console.error("Error marking absent", error)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* Responsive Container matching the profile style but flexible width */
.responsive-dashboard-container {
  max-width: 1000px; /* Expanded for desktop */
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

/* Header matches the new style perfectly */
.top-header { 
  display: flex; align-items: center; justify-content: space-between; 
  padding: 1.5rem 2rem; background: white; border-bottom: 1px solid #f1f5f9; 
}
.profile-header { display: flex; align-items: center; gap: 1rem; }
.doctor-avatar {
  width: 50px; height: 50px; border-radius: 50%;
  background: #e0f2fe; color: #0284c7; font-weight: bold; font-size: 1.2rem;
  display: flex; align-items: center; justify-content: center;
}
.greeting { display: block; font-size: 0.85rem; color: #64748b; margin-bottom: 0.1rem; }
.doctor-name { margin: 0; font-size: 1.2rem; color: #1e293b; font-weight: 800; }
.notification-icon { color: #94a3b8; cursor: pointer; transition: color 0.2s; display: flex; align-items: center; justify-content: center; padding: 0.5rem; border-radius: 50%; }
.notification-icon:hover { background: #f1f5f9; color: #0284c7; }

/* Dashboard Layout */
.dashboard-content { padding: 1.5rem; }

/* RESPONSIVE GRID */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

/* Tablet & Desktop */
@media (min-width: 860px) {
  .dashboard-content { padding: 2rem; }
  .dashboard-grid { grid-template-columns: 1fr 1fr; gap: 2.5rem; }
}

.section-title { margin: 0 0 1rem 0; font-size: 0.9rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding-left: 0.5rem; }

/* Resumen de Hoy */
.summary-section { margin-bottom: 2rem; }
.summary-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.summary-card {
  padding: 1.25rem; border-radius: 16px;
  background: white; box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  display: flex; flex-direction: column; gap: 0.5rem;
  transition: transform 0.2s;
}
.summary-card:hover { transform: translateY(-3px); }
.today-card { background: #0284c7; color: white; }
.new-card { background: white; border: 1px solid #f1f5f9; }
.card-icon { font-size: 1.5rem; margin-bottom: 0.5rem; opacity: 0.9; }
.blue-icon { color: #0284c7; }
.card-text p { margin: 0 0 0.2rem 0; font-size: 0.85rem; font-weight: 500; opacity: 0.9; }
.card-text h2 { margin: 0; font-size: 2.2rem; font-weight: 800; color: inherit; line-height: 1; }
.new-card .card-text h2 { color: #1e293b; }

/* Próxima cita */
.next-appt-section { margin-bottom: 2rem; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.section-header .section-title { margin: 0; }
.time-badge { background: #dcfce7; color: #059669; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px; }

.next-appt-card { background: white; padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; }
.next-appt-info { display: flex; align-items: center; gap: 1.25rem; margin-bottom: 1.5rem; }
.patient-avatar { width: 55px; height: 55px; background: #e0f2fe; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; color: #0284c7; }
.appt-details h4 { margin: 0 0 0.3rem 0; font-size: 1.15rem; color: #1e293b; font-weight: 700; }
.time-block { display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem; color: #64748b; }
.time-block svg { color: #0284c7; }

.full-width { width: 100%; display: block; text-align: center; }

/* Lists (Reusing the menu-list style from other components) */
.list-section { margin-bottom: 2rem; }
.menu-list { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.03); display: flex; flex-direction: column; }
.menu-item { display: flex; align-items: center; width: 100%; padding: 1.25rem; background: white; border: none; cursor: pointer; text-align: left; transition: background 0.2s; border-bottom: 1px solid #f1f5f9; }
.menu-item:last-child { border-bottom: none; }
.menu-item:hover { background: #f8fafc; }
.menu-item:active { background: #f1f5f9; }

.time-col { display: flex; flex-direction: column; padding-right: 1.25rem; margin-right: 1rem; border-right: 1px solid #f1f5f9; align-items: flex-end; min-width: 65px; }
.time-col strong { color: #0284c7; font-size: 0.9rem; }
.time-col .date-sub { font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; margin-top: 0.2rem; }

.menu-text { flex: 1; }
.menu-text h4 { margin: 0 0 0.2rem 0; font-size: 1rem; font-weight: 700; color: #1e293b; }
.menu-text p { margin: 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.3; }

.menu-arrow { color: #cbd5e1; flex-shrink: 0; margin-left: 0.5rem; transition: color 0.2s; }
.menu-item:hover .menu-arrow { color: #0284c7; }

/* Pending List Customization */
.pending-list .menu-item { border-left: 4px solid #f59e0b; }
.pending-time strong { color: #f59e0b; }
.pending-badge { display: inline-block; background: #fef3c7; color: #d97706 !important; padding: 0.15rem 0.5rem; border-radius: 12px; font-size: 0.7rem !important; font-weight: 700; margin-top: 0.3rem !important; }

/* Modals */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; box-sizing: border-box; }
.modal-content { width: 100%; max-width: 440px; background: white; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column; max-height: 90vh; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
.modal-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; line-height: 1; padding: 0; }
.modal-body { padding: 1.5rem; overflow-y: auto; }
.patient-summary { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.summary-avatar { width: 50px; height: 50px; border-radius: 50%; background: #f1f5f9; color: #0284c7; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; flex-shrink: 0; }
.patient-summary h4 { margin: 0 0 0.25rem 0; font-size: 1.1rem; color: #1e293b; }
.patient-summary p { margin: 0; color: #64748b; font-size: 0.85rem; }
.info-section { margin-bottom: 1.5rem; }
.info-section h5 { margin: 0 0 0.5rem 0; color: #0284c7; font-size: 0.9rem; }
.info-box { background: #f8fafc; padding: 1rem; border-radius: 12px; color: #475569; font-size: 0.9rem; line-height: 1.5; border: 1px solid #e2e8f0; }
.report-textarea { width: 100%; padding: 1rem; border: 1px solid #cbd5e1; border-radius: 12px; font-family: inherit; font-size: 0.9rem; resize: vertical; min-height: 80px; color: #1e293b; background: #ffffff; box-sizing: border-box; }
.report-textarea:focus { outline: none; border-color: #0284c7; }
.modal-footer { padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 0.5rem; background: #fafafa; flex-wrap: wrap; }
.action-buttons p { margin-top: 0; margin-bottom: 1rem; color: #1e293b; font-weight: 600; font-size: 0.95rem; text-align: center; }
.buttons-row { display: flex; gap: 0.75rem; width: 100%; }

.btn { padding: 0.6rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s ease; font-size: 0.85rem; flex: 1; text-align: center; }
.modal-footer .btn { flex: none; }
.btn-primary { background: #0284c7; color: white; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #475569; }
.btn-success { background: #10b981; color: white; }
.btn-danger { background: #ef4444; color: white; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 30px; height: 30px; border: 3px solid #f1f5f9; border-top: 3px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
