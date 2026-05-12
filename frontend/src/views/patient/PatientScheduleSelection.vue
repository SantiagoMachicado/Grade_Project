<template>
  <div class="schedule-container">
    <div class="header-section">
      <button @click="$router.go(-1)" class="icon-btn">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
      </button>
      <h2 class="page-title">Perfil del Especialista</h2>
      <div style="width: 24px;"></div> <!-- Spacer -->
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    
    <div v-else class="content-wrapper">
      <!-- Profile Card -->
      <div class="profile-card">
        <img :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${assignment.doctor?.full_name || 'Dr'}&backgroundColor=e2e8f0&clothing=blazerAndShirt`" alt="Avatar" class="profile-avatar" />
        <h2 class="doctor-name">Dr. {{ assignment.doctor?.full_name }}</h2>
        <p class="specialty-long">{{ assignment.doctor?.specialty }} - {{ assignment.center?.name }}</p>
        
        <div class="stats-grid">
          <div class="stat-box">
            <span class="stat-value">2k+</span>
            <span class="stat-label">Pacientes</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">15</span>
            <span class="stat-label">Años exp.</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">4.9</span>
            <span class="stat-label">Rating</span>
          </div>
        </div>
        
        <div class="bio-section">
          <h3>Sobre mí</h3>
          <p class="bio">{{ assignment.doctor?.bio || 'Especialista comprometido con brindar una atención médica integral y de vanguardia, enfocada en el bienestar del paciente.' }}</p>
        </div>
      </div>

      <!-- Schedule Section -->
      <div class="schedule-card">
        <div class="card-title">
          <h3>Disponibilidad</h3>
        </div>

        <div class="dates-scroll-container">
          <button 
            v-for="day in availableDays" 
            :key="day.date" 
            :class="['date-btn', { active: selectedDate === day.date }]"
            @click="selectDate(day.date)"
          >
            <span class="day-name">{{ formatDayName(day.date) }}</span>
            <span class="day-number">{{ formatDayNumber(day.date) }}</span>
          </button>
          <div v-if="availableDays.length === 0" class="empty-text">No hay horarios disponibles próximamente.</div>
        </div>

        <div class="section-label">Selecciona la hora</div>
        <div class="slots-grid">
          <button 
            v-for="slot in currentSlots" 
            :key="slot.time" 
            :class="['slot-btn', { active: selectedTime === slot.time, disabled: !slot.available }]"
            @click="slot.available ? selectedTime = slot.time : null"
            :disabled="!slot.available"
          >
            {{ slot.time }}
          </button>
          <div v-if="currentSlots.length === 0 && selectedDate" class="empty-text">No hay turnos para esta fecha.</div>
          <div v-if="!selectedDate" class="empty-text">Selecciona una fecha arriba.</div>
        </div>
      </div>
    </div>

    <!-- Fixed Booking Button -->
    <div class="fixed-bottom" v-if="!isLoading && !error">
      <div class="booking-summary" v-if="selectedDate && selectedTime">
        <span>Reserva confirmada para las <strong>{{ selectedTime }}</strong></span>
      </div>
      <button 
        class="book-btn" 
        :disabled="!selectedDate || !selectedTime || isBooking"
        @click="bookAppointment"
      >
        {{ isBooking ? 'Procesando...' : (isRescheduling ? 'Actualizar Cita' : 'Reservar Cita') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const assignmentId = route.params.assignmentId
const rescheduleId = route.query.rescheduleId
const isRescheduling = computed(() => !!rescheduleId)

const assignment = ref(null)
const availableDays = ref([])
const isLoading = ref(true)
const error = ref('')
const isBooking = ref(false)

const selectedDate = ref(null)
const selectedTime = ref(null)

const currentSlots = computed(() => {
  if (!selectedDate.value) return []
  const day = availableDays.value.find(d => d.date === selectedDate.value)
  return day ? day.slots : []
})

const fetchData = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const token = localStorage.getItem('access_token')
    
    // Fetch Assignment Details
    const assignRes = await axios.get(`http://localhost:8000/api/v1/clinics/assignments/${assignmentId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    assignment.value = assignRes.data

    // Fetch Slots
    const slotsRes = await axios.get(`http://localhost:8000/api/v1/clinics/assignments/${assignmentId}/slots`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    availableDays.value = slotsRes.data
    
    // Auto-select first available date
    if (availableDays.value.length > 0) {
      selectedDate.value = availableDays.value[0].date
    }
  } catch (err) {
    console.error(err)
    error.value = 'Ocurrió un error al cargar la información del doctor.'
  } finally {
    isLoading.value = false
  }
}

const selectDate = (date) => {
  selectedDate.value = date
  selectedTime.value = null // reset time selection when date changes
}

const formatDayName = (dateStr) => {
  const d = new Date(dateStr)
  const localDate = new Date(d.getTime() + d.getTimezoneOffset() * 60000)
  return localDate.toLocaleDateString('es-ES', { weekday: 'short' }).toUpperCase()
}

const formatDayNumber = (dateStr) => {
  const d = new Date(dateStr)
  const localDate = new Date(d.getTime() + d.getTimezoneOffset() * 60000)
  return localDate.getDate().toString().padStart(2, '0')
}

const bookAppointment = async () => {
  isBooking.value = true
  try {
    const token = localStorage.getItem('access_token')
    const appointmentDateTime = `${selectedDate.value}T${selectedTime.value}:00`
    
    const payload = {
      appointment_date: appointmentDateTime,
      doctor_id: assignment.value.doctor_id,
      center_id: assignment.value.center_id,
      notes: ""
    }
    
    if (isRescheduling.value) {
      await axios.put(`http://localhost:8000/api/v1/appointments/${rescheduleId}`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      })
      alert("¡Cita reprogramada exitosamente!")
    } else {
      await axios.post('http://localhost:8000/api/v1/appointments/', payload, {
        headers: { Authorization: `Bearer ${token}` }
      })
      alert("¡Cita reservada exitosamente!")
    }
    
    router.push('/patient/appointments')
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || "Error al reservar la cita. Es posible que el horario ya esté ocupado.")
  } finally {
    isBooking.value = false
  }
}

onMounted(() => {
  if (!assignmentId) {
    error.value = 'ID de especialista no proporcionado.'
    isLoading.value = false
    return
  }
  fetchData()
})
</script>

<style scoped>
.schedule-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 8rem 1.5rem; /* bottom padding for fixed button */
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
  margin-bottom: 2rem;
}
.icon-btn {
  background: white;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 12px;
  transition: background 0.2s;
}
.icon-btn:hover { background: #f1f5f9; }
.page-title {
  margin: 0;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 800;
}

/* Profile Card */
.profile-card {
  background: white;
  border-radius: 20px;
  padding: 2rem 1.5rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  margin-bottom: 1.5rem;
}
.profile-avatar {
  width: 100px;
  height: 100px;
  border-radius: 24px;
  background: #f1f5f9;
  object-fit: cover;
  margin-bottom: 1rem;
}
.doctor-name {
  margin: 0 0 0.25rem 0;
  font-size: 1.3rem;
  font-weight: 800;
  color: #1e293b;
}
.specialty-long {
  margin: 0 0 1.5rem 0;
  color: #00bcd4;
  font-weight: 600;
  font-size: 0.9rem;
}

.stats-grid {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1rem 0;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
}
.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}
.stat-value { font-size: 1.1rem; font-weight: 800; color: #1e293b; }
.stat-label { font-size: 0.75rem; color: #64748b; font-weight: 600; }

.bio-section { text-align: left; }
.bio-section h3 { margin: 0 0 0.5rem 0; font-size: 1rem; font-weight: 800; color: #1e293b; }
.bio { color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0; }

/* Schedule Section */
.schedule-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}
.card-title h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
}

.dates-scroll-container {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  padding-bottom: 1rem;
  scrollbar-width: none;
  margin-bottom: 1rem;
}
.dates-scroll-container::-webkit-scrollbar { display: none; }

.date-btn {
  min-width: 65px;
  height: 80px;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  background: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  gap: 0.25rem;
}
.date-btn:hover { border-color: #cbd5e1; }
.date-btn.active {
  border-color: #00bcd4;
  background: #00bcd4;
}
.date-btn.active .day-name, .date-btn.active .day-number { color: white; }

.day-name { font-size: 0.75rem; color: #64748b; font-weight: 600; }
.day-number { font-size: 1.1rem; font-weight: 800; color: #1e293b; }

.section-label { font-size: 0.9rem; font-weight: 700; color: #1e293b; margin-bottom: 1rem; }

.slots-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}
.slot-btn {
  padding: 0.75rem;
  background: white;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.slot-btn:hover:not(.disabled) { border-color: #00bcd4; color: #00bcd4; }
.slot-btn.active { background: #004e98; color: white; border-color: #004e98; }

/* Disabled slot styling */
.slot-btn.disabled {
  background: #f1f5f9;
  color: #cbd5e1;
  border-color: #f1f5f9;
  cursor: not-allowed;
  text-decoration: line-through;
}

.empty-text { color: #64748b; font-size: 0.9rem; grid-column: 1 / -1; text-align: center; padding: 1rem; }

/* Fixed Bottom Button */
.fixed-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 1rem 1.5rem 1.5rem 1.5rem;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.05);
  border-radius: 24px 24px 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 480px;
  margin: 0 auto;
}
.booking-summary { text-align: center; color: #64748b; font-size: 0.85rem; }
.book-btn {
  background: #004e98;
  color: white;
  border: none;
  border-radius: 16px;
  padding: 1rem;
  font-weight: 800;
  font-size: 1.05rem;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
}
.book-btn:disabled { background: #cbd5e1; cursor: not-allowed; }

.loading-state { text-align: center; padding: 4rem 0; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top: 4px solid #00bcd4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
