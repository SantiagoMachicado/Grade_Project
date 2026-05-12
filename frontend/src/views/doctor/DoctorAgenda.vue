<template>
  <div class="agenda-container">
    <div class="header-section">
      <div class="title-with-icon">
        <span class="view-icon">📅</span>
        <h2>Agenda Médica</h2>
      </div>
    </div>

    <!-- Date Selector -->
    <div class="date-selector">
      <div 
        v-for="day in next7Days" 
        :key="day.dateStr"
        :class="['day-item', { active: selectedDate === day.dateStr }]"
        @click="selectDate(day.dateStr)"
      >
        <span class="day-name">{{ day.dayName }}</span>
        <span class="day-number">{{ day.dayNumber }}</span>
      </div>
    </div>

    <!-- Timeline -->
    <div class="timeline-container">
      <div v-if="isLoading" class="loading-state">Cargando agenda...</div>
      <div v-else-if="slots.length === 0" class="empty-state glass-card">
        <p>No tienes turnos de trabajo programados para este día.</p>
      </div>
      <div v-else class="timeline">
        <div v-for="(slot, index) in slots" :key="index" class="timeline-row">
          <div class="time-column">{{ slot.time }}</div>
          
          <div class="card-column">
            <!-- Available Slot -->
            <div v-if="slot.type === 'available'" class="slot-card available-card">
              <span class="center-text">{{ slot.center ? slot.center.name : '' }}</span>
              <span class="status-text">Espacio Disponible</span>
            </div>
            
            <!-- Appointment Slot -->
            <div v-else class="slot-card appointment-card" :class="slot.appointment.status" @click="openActionModal(slot.appointment)">
              <div class="patient-info">
                <img :src="`https://ui-avatars.com/api/?name=${slot.appointment.patient?.full_name || 'Pac'}&background=E5E7EB&color=4F46E5`" alt="Avatar" class="avatar" />
                <div class="details">
                  <h4>{{ slot.appointment.patient?.full_name || 'Paciente' }}</h4>
                  <p class="notes">{{ slot.appointment.notes || 'Consulta General' }}</p>
                </div>
              </div>
              <div class="status-badge" :class="slot.appointment.status">
                {{ formatStatus(slot.appointment.status) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Modal -->
    <div class="modal-backdrop" v-if="selectedAppt" @click.self="closeModal">
      <div class="modal-content glass-card">
        <div class="modal-header">
          <h3>Gestión de Cita</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="patient-summary">
            <div class="summary-avatar">{{ getInitials(selectedAppt.patient?.full_name) }}</div>
            <div>
              <h4>{{ selectedAppt.patient?.full_name || 'Paciente' }}</h4>
              <p>Estado actual: <strong>{{ formatStatus(selectedAppt.status) }}</strong></p>
            </div>
          </div>
          
          <div v-if="selectedAppt.status === 'pendiente'" class="action-buttons">
            <p>¿Deseas confirmar o cancelar esta cita?</p>
            <div class="buttons-row">
              <button class="btn btn-success" @click="updateStatus('confirmada')" :disabled="isUpdating">
                {{ isUpdating ? 'Procesando...' : 'Confirmar Cita' }}
              </button>
              <button class="btn btn-danger" @click="updateStatus('cancelada')" :disabled="isUpdating">
                {{ isUpdating ? 'Procesando...' : 'Cancelar Cita' }}
              </button>
            </div>
          </div>
          <div v-else class="info-box">
            <p>Esta cita está <strong>{{ formatStatus(selectedAppt.status) }}</strong>.</p>
            <p v-if="selectedAppt.status === 'confirmada'">Para redactar el reporte médico y finalizar esta cita, dirígete a la sección <strong>"Mis Pacientes"</strong>.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const next7Days = ref([])
const selectedDate = ref('')
const slots = ref([])
const isLoading = ref(false)
const selectedAppt = ref(null)
const isUpdating = ref(false)

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const openActionModal = (appt) => {
  selectedAppt.value = appt
}

const closeModal = () => {
  selectedAppt.value = null
}

const updateStatus = async (newStatus) => {
  if (!selectedAppt.value) return
  isUpdating.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: newStatus },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    // Update local state
    selectedAppt.value.status = newStatus
    // Refresh agenda
    await fetchAgenda()
    closeModal()
  } catch (error) {
    console.error("Error updating status:", error)
    alert("Hubo un error al actualizar la cita.")
  } finally {
    isUpdating.value = false
  }
}

const getNext7Days = () => {
  const days = []
  const today = new Date()
  for (let i = 0; i < 7; i++) {
    const d = new Date(today)
    d.setDate(d.getDate() + i)
    
    // Format YYYY-MM-DD local time
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    const dateStr = `${yyyy}-${mm}-${dd}`
    
    days.push({
      dateStr,
      dayName: d.toLocaleDateString('es-ES', { weekday: 'short' }).toUpperCase().replace('.', ''),
      dayNumber: d.getDate()
    })
  }
  return days
}

const fetchAgenda = async () => {
  if (!selectedDate.value) return
  isLoading.value = true
  slots.value = []
  try {
    const token = localStorage.getItem('access_token')
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    const res = await axios.get(`http://localhost:8000/api/v1/appointments/doctor/${doctorId}/agenda?date=${selectedDate.value}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    slots.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const selectDate = (dateStr) => {
  selectedDate.value = dateStr
  fetchAgenda()
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

onMounted(() => {
  next7Days.value = getNext7Days()
  selectDate(next7Days.value[0].dateStr)
})
</script>

<style scoped>
.agenda-container {
  max-width: 800px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 2rem;
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

/* Date Selector */
.date-selector {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2.5rem;
  justify-content: center;
  overflow-x: auto;
  padding-bottom: 1rem;
}

.day-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  min-width: 60px;
}

.day-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-muted);
}

.day-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-main);
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.day-item.active .day-name {
  color: var(--primary-color);
}

.day-item.active .day-number {
  background-color: var(--primary-color);
  color: white;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

/* Timeline */
.timeline-container {
  background: #F9FAFB;
  border-radius: 12px;
  padding: 2rem;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.timeline-row {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.time-column {
  width: 50px;
  font-size: 0.95rem;
  color: var(--text-muted);
  font-weight: 500;
  text-align: right;
}

.card-column {
  flex: 1;
}

.slot-card {
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  min-height: 80px;
}

/* Available Card */
.available-card {
  border: 2px dashed #D1D5DB;
  background: transparent;
  color: var(--text-muted);
  justify-content: center;
  flex-direction: column;
  gap: 0.3rem;
}

.center-text {
  font-size: 0.85rem;
  font-weight: 500;
  opacity: 0.7;
}

.status-text {
  font-weight: 600;
  font-size: 1rem;
}

/* Appointment Card */
.appointment-card {
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  border-left: 6px solid var(--primary-color);
}

.appointment-card.confirmada { border-left-color: #10B981; }
.appointment-card.completada { border-left-color: #3B82F6; }
.appointment-card.pendiente { border-left-color: #F59E0B; }

.patient-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.details h4 {
  margin: 0 0 0.3rem 0;
  color: var(--text-main);
  font-size: 1.1rem;
}

.notes {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.status-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}

.status-badge.confirmada { background: #D1FAE5; color: #059669; }
.status-badge.completada { background: #DBEAFE; color: #2563EB; }
.status-badge.pendiente { background: #FEF3C7; color: #D97706; }

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}

.appointment-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.appointment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.06);
}

/* Modal Styles */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 { margin: 0; font-size: 1.25rem; color: var(--text-main); }
.close-btn { background: none; border: none; font-size: 1.8rem; cursor: pointer; color: var(--text-muted); line-height: 1; padding: 0; }
.close-btn:hover { color: var(--text-main); }

.modal-body {
  padding: 1.5rem;
}

.patient-summary {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.summary-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #f1f5f9;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.5rem;
}

.patient-summary h4 { margin: 0 0 0.25rem 0; font-size: 1.2rem; color: var(--text-main); }
.patient-summary p { margin: 0; color: var(--text-muted); font-size: 0.95rem; }

.action-buttons p { margin-top: 0; margin-bottom: 1rem; color: var(--text-main); font-weight: 500; }

.buttons-row {
  display: flex;
  gap: 1rem;
}

.info-box {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  color: var(--text-main);
  font-size: 0.95rem;
  line-height: 1.5;
  border: 1px solid #e2e8f0;
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
  flex: 1;
}

.modal-footer .btn { flex: none; }

.btn-secondary { background: white; border: 1px solid #cbd5e1; color: var(--text-main); }
.btn-secondary:hover { background: #f1f5f9; }

.btn-success { background: #10B981; color: white; }
.btn-success:hover { opacity: 0.9; }
.btn-success:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-danger { background: #EF4444; color: white; }
.btn-danger:hover { opacity: 0.9; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
