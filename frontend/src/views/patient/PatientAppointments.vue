<template>
  <div class="appointments-container">
    <!-- Header -->
    <div class="header-section">
      <button class="icon-btn" @click="$router.push('/patient/dashboard')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
      </button>
      <h2 class="page-title">Mis Citas</h2>
      <button class="icon-btn" @click="$router.push('/patient/profile?view=notifications')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
      </button>
    </div>

    <!-- Tabs -->
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

    <!-- Content -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    
    <div v-else class="appointments-list">
      <div v-if="filteredAppointments.length === 0" class="empty-state">
        <p>No tienes citas {{ activeTab === 'upcoming' ? 'próximas' : 'pasadas' }}.</p>
      </div>
      
      <div v-for="appt in filteredAppointments" :key="appt.id" class="appointment-card">
        
        <div class="card-top">
          <div class="doctor-info">
            <img :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${appt.doctor?.full_name || 'Doc'}&backgroundColor=e2e8f0&clothing=blazerAndShirt`" alt="Doctor Avatar" class="avatar" />
            <div class="doc-details">
              <h3>Dr. {{ appt.doctor?.full_name || 'No asignado' }}</h3>
              <p class="specialty">{{ appt.doctor?.specialty || 'Medicina General' }}</p>
            </div>
          </div>
          <span :class="['status-badge', appt.status]">{{ formatStatus(appt.status) }}</span>
        </div>
        
        <div class="card-datetime">
          <div class="datetime-item">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#004e98" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <span>{{ formatDate(appt.appointment_date) }}</span>
          </div>
          <div class="datetime-item">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#004e98" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span>{{ formatTime(appt.appointment_date) }}</span>
          </div>
        </div>

        <div class="card-actions" v-if="activeTab === 'upcoming' && appt.status !== 'cancelada'">
          <button class="btn-cancel" @click="confirmCancel(appt)">Cancelar</button>
          <button v-if="appt.status !== 'confirmada'" class="btn-reschedule" @click="confirmReschedule(appt)">Reprogramar</button>
        </div>
        
      </div>
    </div>

    <!-- Floating Action Button -->
    <button class="fab-btn" @click="$router.push('/patient/appointments/new')">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
    </button>

    <!-- Modals -->
    <div v-if="showCancelModal" class="modal-overlay">
      <div class="modal-content">
        <h3>¿Cancelar Cita?</h3>
        <p>Estás a punto de cancelar tu cita con el <strong>Dr. {{ selectedAppt?.doctor?.full_name }}</strong>. Esta acción no se puede deshacer.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showCancelModal = false">Mantener cita</button>
          <button class="btn-danger" @click="executeCancel" :disabled="isProcessing">
            {{ isProcessing ? 'Cancelando...' : 'Sí, cancelar' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRescheduleModal" class="modal-overlay">
      <div class="modal-content">
        <h3>¿Reprogramar Cita?</h3>
        <p>Para reprogramar, deberás seleccionar un nuevo horario. Tu cita actual será cancelada y crearás una nueva.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showRescheduleModal = false">Atrás</button>
          <button class="btn-reschedule" @click="executeReschedule" :disabled="isProcessing" style="flex: 1;">
            {{ isProcessing ? 'Cargando...' : 'Buscar horario' }}
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
    
    let patientId = payload.id
    if (!patientId) {
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
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
}

const formatStatus = (status) => {
  const map = {
    'pendiente': 'PENDIENTE',
    'confirmada': 'CONFIRMADA',
    'completada': 'COMPLETADA',
    'cancelada': 'CANCELADA',
    'ausente': 'AUSENTE'
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
  max-width: 480px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 6rem 1.5rem; /* bottom padding for FAB */
  background: #f8fafc;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  position: relative;
}

/* Header */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.icon-btn {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0.5rem;
}
.page-title {
  margin: 0;
  color: #004e98;
  font-size: 1.25rem;
  font-weight: 800;
}

/* Tabs */
.tabs-container {
  display: flex;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 1.5rem;
}
.tab-btn {
  flex: 1;
  background: none;
  border: none;
  padding: 0.75rem 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: color 0.2s;
}
.tab-btn.active {
  color: #004e98;
}
.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #004e98;
  border-radius: 3px 3px 0 0;
}
.badge {
  background: #e0e7ff;
  color: #004e98;
  padding: 0.1rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

/* Cards List */
.appointments-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.appointment-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  border: 1px solid #f1f5f9;
}

/* Card Top */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}
.doctor-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #f1f5f9;
  object-fit: cover;
}
.doc-details h3 {
  margin: 0 0 0.2rem 0;
  font-size: 1.05rem;
  font-weight: 800;
  color: #1e293b;
}
.specialty {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
}

/* Status Badge */
.status-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.status-badge.pendiente { background: #fff7ed; color: #ea580c; }
.status-badge.confirmada { background: #ecfdf5; color: #10b981; }
.status-badge.completada { background: #eff6ff; color: #3b82f6; }
.status-badge.cancelada { background: #fef2f2; color: #ef4444; }
.status-badge.ausente { background: #f1f5f9; color: #475569; }

/* Card Date/Time */
.card-datetime {
  background: #f8fafc;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}
.datetime-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #475569;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Card Actions */
.card-actions {
  display: flex;
  gap: 0.75rem;
}
.btn-cancel {
  flex: 1;
  background: white;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 0.75rem;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-cancel:hover { background: #f1f5f9; border-color: #94a3b8; }

.btn-reschedule {
  flex: 1;
  background: #004e98;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.75rem;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-reschedule:hover { background: #003a70; }

/* FAB Button */
.fab-btn {
  position: fixed;
  bottom: 85px;
  right: calc(50% - 240px + 2rem);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #004e98;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(0, 78, 152, 0.4);
  cursor: pointer;
  transition: transform 0.2s;
  z-index: 100;
}
@media (max-width: 480px) {
  .fab-btn {
    right: 2rem;
  }
}
.fab-btn:hover {
  transform: scale(1.05);
  background: #003a70;
}

/* Empty & Loading States */
.empty-state { text-align: center; color: #64748b; padding: 3rem 1rem; }
.loading-state { text-align: center; padding: 3rem 0; }
.spinner { width: 30px; height: 30px; border: 3px solid #f1f5f9; border-top: 3px solid #004e98; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
.modal-content h3 { margin-top: 0; font-size: 1.25rem; color: #0f172a; font-weight: 800; }
.modal-content p { color: #64748b; line-height: 1.5; margin-bottom: 2rem; font-size: 0.95rem; }
.modal-actions { display: flex; gap: 1rem; }
.btn-danger {
  flex: 1;
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}
.btn-danger:hover { background: #dc2626; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
