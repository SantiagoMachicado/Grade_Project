<template>
  <div class="dashboard-wrap">
    <!-- Header -->
    <div class="header-section">
      <div class="profile-header">
        <div class="doctor-avatar">{{ getInitials(doctorName) }}</div>
        <div>
          <span class="greeting">¡Buen día!</span>
          <h2 class="doctor-name">Hola, Dr. {{ doctorName }}</h2>
        </div>
      </div>
      <div class="notification-icon">🔔</div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando panel...</p>
    </div>

    <div v-else-if="dashboardData" class="dashboard-content">
      
      <!-- Resumen de Hoy -->
      <section class="summary-section">
        <h3>Resumen de Hoy</h3>
        <div class="summary-cards">
          <div class="summary-card today-card">
            <div class="card-icon">📅</div>
            <p>Citas hoy</p>
            <h2>{{ dashboardData.today_appointments_count }}</h2>
          </div>
          <div class="summary-card new-card">
            <div class="card-icon blue-icon">👤+</div>
            <p>Pacientes nuevos</p>
            <h2>{{ dashboardData.new_patients_count }}</h2>
          </div>
        </div>
      </section>

      <!-- Próxima Cita -->
      <section class="next-appt-section" v-if="dashboardData.next_appointment">
        <div class="section-header">
          <h3>Próxima cita</h3>
          <span class="time-badge">{{ getRelativeTime(dashboardData.next_appointment.appointment_date) }}</span>
        </div>
        <div class="next-appt-card glass-card">
          <div class="next-appt-info">
            <div class="patient-avatar">{{ getInitials(dashboardData.next_appointment.patient?.full_name) }}</div>
            <div class="appt-details">
              <h4>{{ dashboardData.next_appointment.patient?.full_name || 'Paciente' }}</h4>
              <div class="time-block">
                <span>⏱️</span>
                <strong>{{ formatTime(dashboardData.next_appointment.appointment_date) }}</strong>
              </div>
            </div>
          </div>
          <button class="btn btn-primary full-width" @click="openPatientModal(dashboardData.next_appointment)">Ver cita</button>
        </div>
      </section>

      <!-- Siguientes Citas -->
      <section class="list-section" v-if="dashboardData.upcoming_appointments.length > 0">
        <div class="section-header">
          <h3>Siguientes citas</h3>
        </div>
        <div class="list-container">
          <div 
            v-for="appt in dashboardData.upcoming_appointments" 
            :key="appt.id" 
            class="list-item glass-card"
            @click="openPatientModal(appt)"
          >
            <div class="time-col">
              <strong>{{ formatTime(appt.appointment_date) }}</strong>
              <span class="date-sub">{{ formatDate(appt.appointment_date) }}</span>
            </div>
            <div class="patient-col">
              <h4>{{ appt.patient?.full_name || 'Paciente' }}</h4>
            </div>
            <div class="action-col">
              <span class="chevron">›</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Citas No Confirmadas -->
      <section class="list-section" v-if="dashboardData.unconfirmed_appointments.length > 0">
        <div class="section-header">
          <h3>Citas no confirmadas</h3>
        </div>
        <div class="list-container">
          <div 
            v-for="appt in dashboardData.unconfirmed_appointments" 
            :key="appt.id" 
            class="list-item glass-card pending-card"
            @click="openAgendaModal(appt)"
          >
            <div class="time-col">
              <strong>{{ formatTime(appt.appointment_date) }}</strong>
              <span class="date-sub">{{ formatDate(appt.appointment_date) }}</span>
            </div>
            <div class="patient-col">
              <h4>{{ appt.patient?.full_name || 'Paciente' }}</h4>
            </div>
            <div class="action-col">
              <span class="status-dot"></span>
              <span class="chevron">›</span>
            </div>
          </div>
        </div>
      </section>

    </div>

    <!-- Modal Detalle (DoctorPatients Style) -->
    <div class="modal-backdrop" v-if="showPatientModal && selectedAppt" @click.self="closeModals">
      <div class="modal-content glass-card">
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
            {{ saving ? 'Finalizando...' : 'Finalizar Cita' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Agenda (Approve/Reject Style) -->
    <div class="modal-backdrop" v-if="showAgendaModal && selectedAppt" @click.self="closeModals">
      <div class="modal-content glass-card">
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
                {{ saving ? 'Procesando...' : 'Confirmar' }}
              </button>
              <button class="btn btn-danger" @click="updateStatus('cancelada')" :disabled="saving">
                {{ saving ? 'Procesando...' : 'Cancelar' }}
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
.dashboard-wrap { max-width: 600px; margin: 0 auto; padding-bottom: 3rem; }

/* Header */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.profile-header { display: flex; align-items: center; gap: 1rem; }
.doctor-avatar {
  width: 50px; height: 50px; border-radius: 50%;
  background: #004e98; color: white; font-weight: bold; font-size: 1.2rem;
  display: flex; align-items: center; justify-content: center;
}
.greeting { display: block; font-size: 0.85rem; color: #64748b; }
.doctor-name { margin: 0; font-size: 1.3rem; color: #0f172a; font-weight: 800; }
.notification-icon { font-size: 1.5rem; color: #64748b; cursor: pointer; }

/* Resumen de Hoy */
.summary-section { margin-bottom: 2rem; }
.summary-section h3 { margin: 0 0 1rem 0; font-size: 1.1rem; color: #1e293b; }
.summary-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.summary-card {
  padding: 1.25rem; border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.today-card { background: #004e98; color: white; }
.new-card { background: white; border: 1px solid #e2e8f0; color: #1e293b; }
.card-icon { font-size: 1.2rem; margin-bottom: 0.5rem; }
.blue-icon { color: #004e98; }
.summary-card p { margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9; }
.summary-card h2 { margin: 0; font-size: 2rem; font-weight: 800; color: inherit; }
.new-card h2 { color: #0f172a; }

/* Próxima cita */
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.section-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; }
.time-badge { background: #dcfce7; color: #166534; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 800; }

.next-appt-card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 2rem; }
.next-appt-info { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
.patient-avatar { width: 50px; height: 50px; background: #f1f5f9; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #004e98; }
.appt-details h4 { margin: 0 0 0.2rem 0; font-size: 1.1rem; color: #0f172a; }
.time-block { display: flex; align-items: center; gap: 0.3rem; font-size: 0.9rem; color: #64748b; }

.full-width { width: 100%; display: block; text-align: center; }

/* Lists */
.list-section { margin-bottom: 2rem; }
.list-container { display: flex; flex-direction: column; gap: 0.75rem; }
.list-item { 
  display: flex; align-items: center; padding: 1rem; background: white; 
  border-radius: 12px; border: 1px solid #e2e8f0; cursor: pointer; transition: transform 0.2s;
}
.list-item:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }

.time-col { width: 80px; display: flex; flex-direction: column; border-right: 1px solid #f1f5f9; padding-right: 1rem; margin-right: 1rem; }
.time-col strong { color: #0284c7; font-size: 0.9rem; }
.time-col .date-sub { font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }

.patient-col { flex: 1; }
.patient-col h4 { margin: 0; font-size: 1rem; color: #1e293b; }

.action-col { display: flex; align-items: center; gap: 0.5rem; color: #cbd5e1; }
.chevron { font-size: 1.5rem; line-height: 1; }
.status-dot { width: 8px; height: 8px; background: #f59e0b; border-radius: 50%; }

.pending-card { border-left: 4px solid #f59e0b; }

/* Modals */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { width: 100%; max-width: 500px; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.25rem; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 1.8rem; cursor: pointer; color: #94a3b8; }
.modal-body { padding: 1.5rem; }
.patient-summary { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.summary-avatar { width: 60px; height: 60px; border-radius: 50%; background: #f1f5f9; color: #004e98; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.5rem; }
.patient-summary h4 { margin: 0 0 0.25rem 0; font-size: 1.2rem; color: #1e293b; }
.patient-summary p { margin: 0; color: #64748b; font-size: 0.95rem; }
.info-section { margin-bottom: 1.5rem; }
.info-section h5 { margin: 0 0 0.5rem 0; color: #004e98; font-size: 0.95rem; }
.info-box { background: #f8fafc; padding: 1rem; border-radius: 8px; color: #1e293b; font-size: 0.95rem; border: 1px solid #e2e8f0; }
.report-textarea { width: 100%; padding: 1rem; border: 1px solid #cbd5e1; border-radius: 8px; font-family: inherit; resize: vertical; box-sizing: border-box; }
.modal-footer { padding: 1.25rem 1.5rem; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 0.5rem; background: #fafafa; }
.action-buttons p { margin-top: 0; margin-bottom: 1rem; font-weight: 500; }
.buttons-row { display: flex; gap: 1rem; }

.btn { padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; flex: 1; text-align: center; transition: 0.2s; }
.modal-footer .btn { flex: none; }
.btn-primary { background: #004e98; color: white; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #1e293b; }
.btn-success { background: #10B981; color: white; }
.btn-danger { background: #EF4444; color: white; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #004e98; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
