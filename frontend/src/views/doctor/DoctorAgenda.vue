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
            <div v-else class="slot-card appointment-card" :class="slot.appointment.status">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const next7Days = ref([])
const selectedDate = ref('')
const slots = ref([])
const isLoading = ref(false)

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
</style>
