<template>
  <div class="profile-container">
    <div class="menu-view">
      <div class="top-header">
        <div style="width: 24px"></div>
        <h2 class="header-title">Agenda Médica</h2>
        <div style="width: 24px"></div>
      </div>

      <div class="menu-section" style="padding-top: 1rem;">
        <div class="agenda-grid">
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
            <div v-if="isLoading" class="loading-state">
              <div class="spinner"></div>
            </div>
            <div v-else-if="slots.length === 0" class="empty-state">
              <div class="empty-icon">🏖️</div>
              <p>No tienes turnos programados para este día.</p>
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
                      <img :src="`https://ui-avatars.com/api/?name=${slot.appointment.patient?.full_name || 'Pac'}&background=e0f2fe&color=0284c7`" alt="Avatar" class="avatar" />
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
        </div>
      </div>
    </div>

    <!-- Action Modal -->
    <div class="modal-backdrop" v-if="selectedAppt" @click.self="closeModal">
      <div class="modal-content">
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
                {{ isUpdating ? 'Procesando...' : 'Confirmar' }}
              </button>
              <button class="btn btn-danger" @click="updateStatus('cancelada')" :disabled="isUpdating">
                {{ isUpdating ? 'Procesando...' : 'Cancelar' }}
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
    selectedAppt.value.status = newStatus
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
  
  .agenda-grid {
    display: grid;
    grid-template-columns: 1fr 2.5fr;
    gap: 2rem;
    align-items: start;
  }

  .date-selector {
    flex-direction: column !important;
    overflow-x: visible !important;
    gap: 0.5rem !important;
    background: white;
    padding: 1.25rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    border: 1px solid #f1f5f9;
  }

  .day-item {
    flex-direction: row !important;
    justify-content: space-between;
    width: 100%;
    padding: 0.6rem 1rem !important;
    border-radius: 12px;
    box-sizing: border-box;
  }

  .day-item.active .day-number {
    box-shadow: none !important;
  }

  .day-number {
    width: 32px !important;
    height: 32px !important;
    font-size: 0.95rem !important;
  }
}

.menu-view { width: 100%; }
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; border-bottom: 1px solid #f1f5f9; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.menu-section { padding: 1.5rem; }

/* Date Selector */
.date-selector {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scrollbar-width: none; /* Firefox */
}
.date-selector::-webkit-scrollbar { display: none; } /* Chrome */

.day-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  padding: 0.5rem;
  min-width: 50px;
}
.day-name { font-size: 0.8rem; font-weight: 600; color: #94a3b8; }
.day-number { font-size: 1.1rem; font-weight: 700; color: #1e293b; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 50%; transition: all 0.2s; }
.day-item.active .day-name { color: #0284c7; }
.day-item.active .day-number { background-color: #0284c7; color: white; box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3); }

/* Timeline */
.timeline-container {
  background: white;
  border-radius: 16px;
  padding: 1.5rem 1rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.timeline { display: flex; flex-direction: column; gap: 1rem; }
.timeline-row { display: flex; gap: 1rem; align-items: stretch; }
.time-column { width: 40px; font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-align: right; padding-top: 0.5rem; }
.card-column { flex: 1; }

.slot-card { border-radius: 12px; padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; min-height: 70px; background: #f8fafc; }

/* Available Card */
.available-card { border: 2px dashed #e2e8f0; background: transparent; color: #94a3b8; justify-content: center; align-items: center; }
.center-text { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.status-text { font-weight: 700; font-size: 0.9rem; }

/* Appointment Card */
.appointment-card { background: white; border: 1px solid #f1f5f9; box-shadow: 0 2px 8px rgba(0,0,0,0.02); border-left: 4px solid #0284c7; cursor: pointer; transition: transform 0.2s; }
.appointment-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

.appointment-card.confirmada { border-left-color: #10b981; }
.appointment-card.completada { border-left-color: #3b82f6; }
.appointment-card.pendiente { border-left-color: #f59e0b; }

.patient-info { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
.avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.details h4 { margin: 0 0 0.1rem 0; color: #1e293b; font-size: 0.95rem; font-weight: 700; }
.notes { margin: 0; color: #64748b; font-size: 0.8rem; line-height: 1.2; }

.status-badge { align-self: flex-start; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.5px; }
.status-badge.confirmada { background: #d1fae5; color: #059669; }
.status-badge.completada { background: #dbeafe; color: #2563eb; }
.status-badge.pendiente { background: #fef3c7; color: #d97706; }

.empty-state { text-align: center; padding: 3rem 1rem; color: #94a3b8; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }

.loading-state { text-align: center; padding: 3rem 0; color: #94a3b8; }
.spinner { width: 30px; height: 30px; border: 3px solid #f1f5f9; border-top: 3px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Modal Styles */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; box-sizing: border-box; }
.modal-content { width: 100%; max-width: 400px; background: white; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
.modal-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; line-height: 1; padding: 0; }
.modal-body { padding: 1.5rem; }
.patient-summary { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.summary-avatar { width: 50px; height: 50px; border-radius: 50%; background: #f1f5f9; color: #0284c7; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
.patient-summary h4 { margin: 0 0 0.25rem 0; font-size: 1.1rem; color: #1e293b; }
.patient-summary p { margin: 0; color: #64748b; font-size: 0.85rem; }
.action-buttons p { margin-top: 0; margin-bottom: 1rem; color: #1e293b; font-weight: 600; font-size: 0.95rem; }
.buttons-row { display: flex; gap: 0.75rem; }
.info-box { background: #f8fafc; padding: 1rem; border-radius: 12px; color: #475569; font-size: 0.9rem; line-height: 1.5; border: 1px solid #e2e8f0; }
.info-box p { margin: 0 0 0.5rem 0; }
.info-box p:last-child { margin-bottom: 0; }
.modal-footer { padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; background: #fafafa; }
.btn { padding: 0.6rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s ease; font-size: 0.9rem; flex: 1; }
.modal-footer .btn { flex: none; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #475569; }
.btn-success { background: #10b981; color: white; }
.btn-danger { background: #ef4444; color: white; }
</style>
