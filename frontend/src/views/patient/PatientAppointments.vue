<template>
  <div class="appointments-container">
    <div class="header-section">
      <div class="title-with-icon">
        <span class="view-icon">📅</span>
        <h2>Mis Citas</h2>
      </div>
      <button class="btn-primary add-btn" @click="$router.push('/patient/appointments/new')">
        + Agregar nueva cita
      </button>
    </div>

    <div class="tabs-container">
      <button 
        :class="['tab-btn', { active: activeTab === 'upcoming' }]" 
        @click="activeTab = 'upcoming'"
      >
        Próximas <span class="badge" v-if="upcomingAppointments.length">{{ upcomingAppointments.length }}</span>
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'past' }]" 
        @click="activeTab = 'past'"
      >
        Pasadas
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">Cargando citas...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    <div v-else class="appointments-list">
      <div v-if="filteredAppointments.length === 0" class="empty-state glass-card">
        <p>No tienes citas {{ activeTab === 'upcoming' ? 'próximas' : 'pasadas' }}.</p>
      </div>
      
      <div v-for="appt in filteredAppointments" :key="appt.id" class="appointment-card glass-card">
        <div class="card-header">
          <div class="doctor-info">
            <img :src="`https://ui-avatars.com/api/?name=${appt.doctor?.full_name || 'Dr'}&background=E5E7EB&color=4F46E5`" alt="Avatar" class="avatar" />
            <div class="doc-details">
              <h3>{{ appt.doctor?.full_name || 'Doctor(a)' }}</h3>
              <p class="specialty">{{ appt.doctor?.specialty || 'Especialidad General' }}</p>
            </div>
          </div>
          <span :class="['status-badge', appt.status]">{{ formatStatus(appt.status) }}</span>
        </div>
        
        <div class="card-body">
          <div class="datetime">
            <span class="icon">📅</span> {{ formatDate(appt.appointment_date) }}
            <span class="icon ml-3">🕒</span> {{ formatTime(appt.appointment_date) }}
          </div>
          <div class="center-name" v-if="appt.center">
             🏥 {{ appt.center.name }}
          </div>
        </div>

        <div class="card-actions" v-if="activeTab === 'upcoming' && appt.status !== 'cancelada'">
          <button class="btn-outline" @click="confirmCancel(appt)">Cancelar</button>
          <button v-if="appt.status !== 'confirmada'" class="btn-primary" @click="confirmReschedule(appt)">Reprogramar</button>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showCancelModal" class="modal-overlay">
      <div class="modal-content glass-card">
        <h3>¿Cancelar Cita?</h3>
        <p>Estás a punto de cancelar tu cita con <strong>{{ selectedAppt?.doctor?.full_name }}</strong>. Esta acción no se puede deshacer.</p>
        <div class="modal-actions">
          <button class="btn-outline" @click="showCancelModal = false">No, mantener cita</button>
          <button class="btn-danger" @click="executeCancel" :disabled="isProcessing">
            {{ isProcessing ? 'Cancelando...' : 'Sí, cancelar cita' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRescheduleModal" class="modal-overlay">
      <div class="modal-content glass-card">
        <h3>¿Reprogramar Cita?</h3>
        <p>Para reprogramar, deberás seleccionar un nuevo horario. Tu cita actual será cancelada y crearás una nueva.</p>
        <div class="modal-actions">
          <button class="btn-outline" @click="showRescheduleModal = false">Atrás</button>
          <button class="btn-primary" @click="executeReschedule" :disabled="isProcessing">
            {{ isProcessing ? 'Cargando...' : 'Buscar nuevo horario' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const activeTab = ref('upcoming')
const appointments = ref([])
const isLoading = ref(true)
const error = ref('')
const isProcessing = ref(false)

const showCancelModal = ref(false)
const showRescheduleModal = ref(false)
const selectedAppt = ref(null)

const fetchAppointments = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const token = localStorage.getItem('access_token')
    if(!token) throw new Error("No token")
    
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(decodeURIComponent(atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    
    // Fallback in case ID wasn't in token (if user didn't re-login after our JWT update)
    let patientId = payload.id
    if (!patientId) {
      // Intenta obtener me
      // Por simplicidad si no hay ID, sugerimos relogin
      alert("Tu sesión ha expirado o requiere actualización. Por favor inicia sesión nuevamente.")
      router.push('/login')
      return
    }

    const res = await axios.get(`http://localhost:8000/api/v1/appointments/patient/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    appointments.value = res.data
  } catch (err) {
    console.error(err)
    error.value = 'Ocurrió un error al cargar las citas.'
  } finally {
    isLoading.value = false
  }
}

const upcomingAppointments = computed(() => {
  const now = new Date()
  return appointments.value.filter(a => new Date(a.appointment_date) >= now)
})

const pastAppointments = computed(() => {
  const now = new Date()
  return appointments.value.filter(a => new Date(a.appointment_date) < now)
})

const filteredAppointments = computed(() => {
  return activeTab.value === 'upcoming' ? upcomingAppointments.value : pastAppointments.value
})

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

const formatTime = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: true })
}

const formatStatus = (status) => {
  const map = {
    'pendiente': 'PENDIENTE',
    'confirmada': 'CONFIRMADA',
    'completada': 'COMPLETADA',
    'cancelada': 'CANCELADA'
  }
  return map[status] || status.toUpperCase()
}

const confirmCancel = (appt) => {
  selectedAppt.value = appt
  showCancelModal.value = true
}

const executeCancel = async () => {
  if (!selectedAppt.value) return
  isProcessing.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: 'cancelada' },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    selectedAppt.value.status = 'cancelada'
    showCancelModal.value = false
  } catch (err) {
    console.error(err)
    alert("Error al cancelar la cita")
  } finally {
    isProcessing.value = false
  }
}

const confirmReschedule = (appt) => {
  selectedAppt.value = appt
  showRescheduleModal.value = true
}

const executeReschedule = async () => {
  if (!selectedAppt.value) return
  isProcessing.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get(`http://localhost:8000/api/v1/clinics/assignments/lookup?doctor_id=${selectedAppt.value.doctor_id}&center_id=${selectedAppt.value.center_id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const assignmentId = res.data.id
    showRescheduleModal.value = false
    router.push({ path: `/patient/appointments/new/${assignmentId}`, query: { rescheduleId: selectedAppt.value.id } })
  } catch (err) {
    console.error(err)
    alert("Error al acceder a los horarios del doctor.")
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  fetchAppointments()
})
</script>

<style scoped>
.appointments-container {
  max-width: 900px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-with-icon h2 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.8rem;
}

.view-icon {
  font-size: 2rem;
}

.add-btn {
  padding: 0.6rem 1.2rem;
}

.tabs-container {
  display: flex;
  gap: 2rem;
  border-bottom: 2px solid #E5E7EB;
  margin-bottom: 2rem;
}

.tab-btn {
  background: none;
  border: none;
  padding: 0.8rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn.active {
  color: var(--primary-color);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--primary-color);
}

.badge {
  background: #E0E7FF;
  color: var(--primary-color);
  padding: 0.1rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.appointments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.appointment-card {
  padding: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.doctor-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #E5E7EB;
}

.doc-details h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-main);
}

.specialty {
  margin: 0.2rem 0 0 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.status-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.pendiente { background: #FEF3C7; color: #D97706; }
.status-badge.confirmada { background: #D1FAE5; color: #059669; }
.status-badge.completada { background: #DBEAFE; color: #2563EB; }
.status-badge.cancelada { background: #FEE2E2; color: #DC2626; }

.card-body {
  background: #F9FAFB;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.datetime {
  display: flex;
  align-items: center;
  font-weight: 500;
  color: var(--text-main);
  margin-bottom: 0.5rem;
}

.center-name {
  color: var(--text-muted);
  font-size: 0.95rem;
}

.ml-3 {
  margin-left: 1rem;
}

.card-actions {
  display: flex;
  gap: 1rem;
}

.card-actions button {
  flex: 1;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  max-width: 450px;
  width: 90%;
  text-align: center;
}

.modal-content h3 {
  margin-top: 0;
  font-size: 1.5rem;
  color: var(--text-main);
}

.modal-content p {
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 2rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
}

.modal-actions button {
  flex: 1;
}

.btn-danger {
  background: var(--danger-color);
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.btn-danger:hover {
  opacity: 0.9;
}
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
