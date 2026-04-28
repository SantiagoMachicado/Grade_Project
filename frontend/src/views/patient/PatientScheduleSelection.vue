<template>
  <div class="schedule-container">
    <div class="header-section">
      <button @click="$router.go(-1)" class="back-btn">← Volver</button>
      <h2 class="main-title">Perfil del Especialista</h2>
      <div style="width: 70px;"></div> <!-- Spacer -->
    </div>

    <div v-if="isLoading" class="loading-state">Cargando perfil y horarios...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    
    <div v-else class="content-wrapper">
      <!-- Profile Card -->
      <div class="profile-card glass-card">
        <div class="profile-header text-center">
          <img :src="`https://ui-avatars.com/api/?name=${assignment.doctor?.full_name || 'Dr'}&background=E5E7EB&color=4F46E5&size=150`" alt="Avatar" class="profile-avatar" />
          <h2 class="doctor-name">{{ assignment.doctor?.full_name }}</h2>
          <p class="specialty-long">{{ assignment.doctor?.specialty }} - {{ assignment.center?.name }}</p>
          <div class="rating-badge">☆ 4.9 (150+ reseñas)</div>
        </div>

        <p class="bio text-center">{{ assignment.doctor?.bio || 'Más de 15 años de experiencia brindando atención integral con un enfoque en medicina preventiva y diagnóstico avanzado.' }}</p>

        <div class="stats-grid">
          <div class="stat-box">
            <span class="stat-label">PACIENTES</span>
            <span class="stat-value">2k+</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">EXPERIENCIA</span>
            <span class="stat-value">15 años</span>
          </div>
          <div class="stat-box full-width">
            <span class="stat-label">CERTIFICADO</span>
            <span class="stat-value">Board Cert.</span>
          </div>
        </div>
      </div>

      <!-- Schedule Card -->
      <div class="schedule-card glass-card">
        <div class="card-title mb-4">
          <span class="icon">📅</span>
          <h3>Calendario de Disponibilidad</h3>
        </div>

        <div class="section-label">Selecciona una fecha</div>
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
          <div v-if="availableDays.length === 0" class="text-muted">No hay horarios disponibles próximamente.</div>
        </div>

        <div class="section-label mt-4">Horarios disponibles</div>
        <div class="slots-grid">
          <button 
            v-for="slot in currentSlots" 
            :key="slot" 
            :class="['slot-btn', { active: selectedTime === slot }]"
            @click="selectedTime = slot"
          >
            {{ slot }}
          </button>
          <div v-if="currentSlots.length === 0 && selectedDate" class="text-muted">No quedan horas para esta fecha.</div>
          <div v-if="!selectedDate" class="text-muted">Selecciona una fecha arriba.</div>
        </div>

        <button 
          class="btn-primary w-100 mt-5 book-btn" 
          :disabled="!selectedDate || !selectedTime || isBooking"
          @click="bookAppointment"
        >
          {{ isBooking ? 'Procesando...' : (isRescheduling ? 'Actualizar Cita' : 'Reservar Cita') }}
        </button>
        <p class="text-center text-muted mt-2 text-sm">Confirmación inmediata tras la reserva</p>
        
        <div class="divider"></div>
        
        <div class="clinic-contact">
          <div class="phone-icon">📞</div>
          <div>
            <span class="contact-label">ATENCIÓN TELEFÓNICA</span>
            <strong class="contact-number">{{ assignment.center?.phone || '+591 2 2123456' }}</strong>
          </div>
        </div>
      </div>
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
  // Ensure we format in local time to avoid off-by-one errors from UTC
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
  max-width: 1100px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-btn {
  background: white;
  border: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
  color: var(--primary-color);
  font-size: 1.1rem;
}

.main-title {
  margin: 0;
  color: var(--text-main);
  font-size: 1.4rem;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 768px) {
  .content-wrapper {
    grid-template-columns: 350px 1fr;
  }
}

/* Profile Card */
.profile-card {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: max-content;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.doctor-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.4rem;
  color: var(--text-main);
}

.specialty-long {
  margin: 0 0 1rem 0;
  color: var(--primary-color);
  font-weight: 500;
  font-size: 0.95rem;
}

.rating-badge {
  background: #EFF6FF;
  color: var(--primary-color);
  padding: 0.3rem 1rem;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
  margin-bottom: 1.5rem;
}

.bio {
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  width: 100%;
}

.full-width {
  grid-column: 1 / -1;
}

.stat-box {
  background: #F9FAFB;
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.stat-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
}

/* Schedule Card */
.schedule-card {
  padding: 2rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-title h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.3rem;
}

.section-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.mt-4 { margin-top: 1.5rem; }
.mt-5 { margin-top: 2rem; }
.mb-4 { margin-bottom: 1.5rem; }
.text-sm { font-size: 0.85rem; }

.dates-scroll-container {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 1rem;
  /* hide scrollbar */
  scrollbar-width: none;
}
.dates-scroll-container::-webkit-scrollbar {
  display: none;
}

.date-btn {
  min-width: 70px;
  height: 80px;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  background: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  gap: 0.3rem;
}

.date-btn:hover {
  border-color: var(--primary-color);
  background: #F9FAFB;
}

.date-btn.active {
  border-color: var(--primary-color);
  background: #EFF6FF;
}

.date-btn.active .day-name, .date-btn.active .day-number {
  color: var(--primary-color);
}

.day-name {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
}

.day-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-main);
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 1rem;
}

.slot-btn {
  padding: 0.8rem;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-main);
  transition: all 0.2s;
}

.slot-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.slot-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.book-btn {
  padding: 1rem;
  font-size: 1.1rem;
}

.book-btn:disabled {
  background: #9CA3AF;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.divider {
  height: 1px;
  background: #E5E7EB;
  margin: 2rem 0;
}

.clinic-contact {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #F9FAFB;
  padding: 1rem;
  border-radius: 12px;
}

.phone-icon {
  background: #E0E7FF;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.contact-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
}

.contact-number {
  display: block;
  font-size: 1rem;
  color: var(--text-main);
}
</style>
