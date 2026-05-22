<template>
  <div class="profile-container">
    <div class="menu-view">
      <div class="top-header">
        <button class="icon-btn" @click="$router.push('/doctor/settings')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h2 class="header-title">Gestión de Horarios</h2>
        <div style="width: 24px"></div> <!-- Placeholder -->
      </div>

      <div class="menu-section">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando información...</p>
        </div>

        <div v-else class="content-wrapper">
          
          <!-- Add New Schedule Form -->
          <div class="form-card">
            <h3 class="card-title">Agregar Nuevo Horario</h3>
            
            <form @submit.prevent="addSchedule" class="schedule-form">
              <div class="form-group">
                <label>Clínica Asignada</label>
                <select v-model="form.assignment_id" required class="form-input">
                  <option value="" disabled>Selecciona una clínica</option>
                  <option v-for="clinic in clinics" :key="clinic.id" :value="clinic.id">
                    {{ clinic.center?.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Día de la Semana</label>
                <select v-model="form.day_of_week" required class="form-input">
                  <option value="" disabled>Selecciona un día</option>
                  <option v-for="(day, index) in daysOfWeek" :key="index" :value="index">
                    {{ day }}
                  </option>
                </select>
              </div>

              <div class="time-row">
                <div class="form-group">
                  <label>Hora Inicio</label>
                  <input type="time" v-model="form.start_time" required class="form-input" />
                </div>
                <div class="form-group">
                  <label>Hora Fin</label>
                  <input type="time" v-model="form.end_time" required class="form-input" />
                </div>
              </div>

              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                {{ isSubmitting ? 'Agregando...' : 'Guardar Horario' }}
              </button>
            </form>
          </div>

          <!-- Existing Schedules -->
          <div class="schedules-list">
            <h3 class="card-title" style="margin-bottom: 1rem;">Tus Horarios Actuales</h3>
            
            <div v-if="schedules.length === 0" class="empty-state">
              No tienes horarios registrados.
            </div>

            <div v-else class="schedule-grid">
              <div v-for="schedule in schedules" :key="schedule.id" class="schedule-item">
                <div class="schedule-info">
                  <div class="schedule-day">{{ daysOfWeek[schedule.day_of_week] }}</div>
                  <div class="schedule-time">{{ formatTime(schedule.start_time) }} - {{ formatTime(schedule.end_time) }}</div>
                  <div class="schedule-clinic">{{ getClinicName(schedule.assignment_id) }}</div>
                </div>
                <button class="delete-btn" @click="deleteSchedule(schedule.id)" title="Eliminar horario">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                </button>
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

const loading = ref(true)
const isSubmitting = ref(false)
const clinics = ref([])
const schedules = ref([])
const doctorId = ref(null)

const daysOfWeek = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const form = ref({
  assignment_id: '',
  day_of_week: '',
  start_time: '',
  end_time: ''
})

const fetchInitialData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    doctorId.value = payload.id
    
    // Fetch Assignments (Clinics)
    const resClinics = await axios.get(`http://localhost:8000/api/v1/clinics/assignments`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    clinics.value = resClinics.data.filter(a => a.doctor_id === doctorId.value)
    
    // Fetch Schedules
    await fetchSchedules()
    
  } catch (error) {
    console.error("Error fetching data:", error)
  } finally {
    loading.value = false
  }
}

const fetchSchedules = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const resSchedules = await axios.get(`http://localhost:8000/api/v1/clinics/schedules/doctor/${doctorId.value}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Sort schedules by day of week, then time
    schedules.value = resSchedules.data.sort((a, b) => {
      if (a.day_of_week !== b.day_of_week) return a.day_of_week - b.day_of_week
      return a.start_time.localeCompare(b.start_time)
    })
  } catch (error) {
    console.error("Error fetching schedules:", error)
  }
}

const getClinicName = (assignmentId) => {
  const clinic = clinics.value.find(c => c.id === assignmentId)
  return clinic?.center?.name || 'Clínica Desconocida'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  // timeStr comes as "HH:MM:SS" from backend
  const [hours, minutes] = timeStr.split(':')
  let h = parseInt(hours)
  const ampm = h >= 12 ? 'PM' : 'AM'
  h = h % 12
  h = h ? h : 12
  return `${h}:${minutes} ${ampm}`
}

const addSchedule = async () => {
  if (form.value.start_time >= form.value.end_time) {
    alert("La hora de inicio debe ser menor a la hora de fin.")
    return
  }
  
  isSubmitting.value = true
  try {
    const token = localStorage.getItem('access_token')
    
    // Backend expects 'HH:MM:SS', input time gives 'HH:MM'
    const payload = {
      assignment_id: parseInt(form.value.assignment_id),
      day_of_week: parseInt(form.value.day_of_week),
      start_time: `${form.value.start_time}:00`,
      end_time: `${form.value.end_time}:00`,
      is_available: true
    }
    
    await axios.post('http://localhost:8000/api/v1/clinics/schedules/', payload, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Reset form except assignment
    form.value.day_of_week = ''
    form.value.start_time = ''
    form.value.end_time = ''
    
    await fetchSchedules()
  } catch (error) {
    console.error("Error creating schedule:", error)
    alert(error.response?.data?.detail || "Hubo un error al guardar el horario.")
  } finally {
    isSubmitting.value = false
  }
}

const deleteSchedule = async (scheduleId) => {
  if (!confirm("¿Estás seguro de eliminar este horario?")) return
  
  try {
    const token = localStorage.getItem('access_token')
    await axios.delete(`http://localhost:8000/api/v1/clinics/schedules/${scheduleId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    await fetchSchedules()
  } catch (error) {
    console.error("Error deleting schedule:", error)
    alert("Hubo un error al eliminar el horario.")
  }
}

onMounted(() => {
  fetchInitialData()
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
}

.menu-view { width: 100%; }

.top-header { 
  display: flex; align-items: center; justify-content: space-between; 
  padding: 1.5rem; background: white; border-bottom: 1px solid #f1f5f9; 
}

.icon-btn { 
  background: none; border: none; color: #64748b; cursor: pointer; 
  display: flex; align-items: center; justify-content: center; 
  padding: 0.5rem; border-radius: 50%; transition: background 0.2s, color 0.2s; 
  margin-left: -0.5rem;
}
.icon-btn:hover { background: #f1f5f9; color: #1e293b; }

.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

.menu-section { padding: 1.5rem; }

.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { 
  width: 30px; height: 30px; border: 3px solid #f1f5f9; 
  border-top: 3px solid #0284c7; border-radius: 50%; 
  animation: spin 1s linear infinite; margin: 0 auto 1rem auto; 
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.content-wrapper { display: flex; flex-direction: column; gap: 2rem; }

/* Form Card */
.form-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  border: 1px solid #f1f5f9;
}

.card-title { margin: 0 0 1.25rem 0; font-size: 1.05rem; color: #1e293b; font-weight: 700; }

.schedule-form { display: flex; flex-direction: column; gap: 1rem; }

.form-group { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; }
.form-group label { font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }

.form-input {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.95rem;
  color: #1e293b;
  font-family: inherit;
  transition: all 0.2s;
  background: #f8fafc;
}
.form-input:focus { outline: none; border-color: #0284c7; box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1); background: white; }

.time-row { display: flex; gap: 1rem; }

.submit-btn {
  margin-top: 0.5rem;
  background: #0284c7;
  color: white;
  border: none;
  padding: 0.85rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
}
.submit-btn:hover:not(:disabled) { background: #0369a1; }
.submit-btn:disabled { background: #94a3b8; cursor: not-allowed; }

/* Schedules List */
.empty-state { padding: 1rem; background: #f8fafc; border-radius: 12px; color: #64748b; font-size: 0.9rem; text-align: center; border: 1px dashed #cbd5e1; }

.schedule-grid { display: flex; flex-direction: column; gap: 0.75rem; }

.schedule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
  transition: all 0.2s;
}
.schedule-item:hover { border-color: #cbd5e1; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }

.schedule-info { display: flex; flex-direction: column; gap: 0.25rem; }
.schedule-day { font-weight: 700; color: #0284c7; font-size: 0.95rem; }
.schedule-time { font-size: 0.9rem; color: #1e293b; font-weight: 600; }
.schedule-clinic { font-size: 0.8rem; color: #64748b; }

.delete-btn {
  background: #fee2e2;
  color: #ef4444;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.delete-btn:hover { background: #fecaca; transform: scale(1.05); }
</style>
