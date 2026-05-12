<template>
  <div class="patients-wrapper">
    <div class="header-section">
      <div class="title-with-icon">
        <span class="view-icon">👥</span>
        <h2>Mis Pacientes</h2>
      </div>
      <p class="subtitle">Historial clínico de pacientes que has atendido recientemente.</p>
    </div>

    <!-- Lista de pacientes -->
    <div class="patients-list" v-if="!loading && appointments.length > 0">
      <div 
        v-for="appt in appointments" 
        :key="appt.id" 
        class="patient-card glass-card"
        @click="openPatientModal(appt)"
      >
        <div class="patient-avatar">
          {{ getInitials(appt.patient.full_name) }}
        </div>
        <div class="patient-info">
          <div class="patient-header-row">
            <h3>{{ appt.patient.full_name }}</h3>
            <span class="status-badge" :class="appt.status">
              {{ formatStatus(appt.status) }}
            </span>
          </div>
          <p class="patient-meta">
            {{ calculateAge(appt.patient.birth_date) }} años &nbsp;&bull;&nbsp; Visita: {{ formatDate(appt.appointment_date) }}
          </p>
        </div>
        <div class="card-arrow">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </div>
      </div>
    </div>
    
    <div class="placeholder-content glass-card" v-if="!loading && appointments.length === 0">
      <div class="empty-state">
        <div class="empty-icon">🗂️</div>
        <h3>Sin pacientes recientes</h3>
        <p>Aquí aparecerán los pacientes de las citas Confirmadas o Completadas.</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando pacientes...</p>
    </div>

    <!-- Modal Detalle -->
    <div class="modal-backdrop" v-if="selectedAppt" @click.self="closeModal">
      <div class="modal-content glass-card">
        <div class="modal-header">
          <h3>Detalle de la Consulta</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="patient-summary">
            <div class="summary-avatar">{{ getInitials(selectedAppt.patient.full_name) }}</div>
            <div>
              <h4>{{ selectedAppt.patient.full_name }}</h4>
              <p>{{ calculateAge(selectedAppt.patient.birth_date) }} años | 📞 {{ selectedAppt.patient.phone || 'No registrado' }}</p>
            </div>
          </div>

          <div class="info-section">
            <h5>Historial Médico del Paciente (Alergias, Condiciones)</h5>
            <div class="info-box">{{ selectedAppt.patient.medical_history || 'Sin registros médicos previos.' }}</div>
          </div>

          <div class="info-section">
            <h5>Motivo de la Cita (Notas del Paciente)</h5>
            <div class="info-box">{{ selectedAppt.notes || 'No se proporcionaron notas al agendar.' }}</div>
          </div>

          <div class="info-section">
            <h5>Reporte Médico / Diagnóstico</h5>
            <textarea 
              v-model="editedReport" 
              placeholder="Escribe aquí el diagnóstico, tratamiento recetado o notas de esta sesión..."
              rows="3"
              class="report-textarea"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">Cerrar</button>
          
          <button 
            v-if="selectedAppt.status === 'confirmada'" 
            class="btn btn-danger" 
            @click="markAsAbsent" 
            :disabled="saving">
            Marcar Ausente
          </button>
          
          <button 
            v-if="selectedAppt.status === 'confirmada'" 
            class="btn btn-success" 
            @click="saveAndFinalize" 
            :disabled="saving">
            {{ saving ? 'Finalizando...' : 'Finalizar Cita' }}
          </button>
          
          <button 
            v-else 
            class="btn btn-primary" 
            @click="saveReport" 
            :disabled="saving">
            {{ saving ? 'Actualizando...' : 'Actualizar Reporte' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const appointments = ref([])
const loading = ref(true)
const selectedAppt = ref(null)
const editedReport = ref('')
const saving = ref(false)

const fetchCompletedAppointments = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    const response = await axios.get(`http://localhost:8000/api/v1/appointments/doctor/${doctorId}?status=confirmada,completada,ausente&limit=30`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    appointments.value = response.data
  } catch (error) {
    console.error("Error fetching patients", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCompletedAppointments()
})

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const calculateAge = (birthDateStr) => {
  if (!birthDateStr) return '--'
  const today = new Date()
  const birthDate = new Date(birthDateStr)
  let age = today.getFullYear() - birthDate.getFullYear()
  const m = today.getMonth() - birthDate.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatStatus = (status) => {
  if (!status) return ''
  const map = {
    'pendiente': 'PENDIENTE',
    'confirmada': 'CONFIRMADA',
    'completada': 'COMPLETADA',
    'cancelada': 'CANCELADA',
    'ausente': 'AUSENTE'
  }
  return map[status] || status.toUpperCase()
}

const openPatientModal = (appt) => {
  selectedAppt.value = appt
  editedReport.value = appt.medical_report || ''
}

const closeModal = () => {
  selectedAppt.value = null
  editedReport.value = ''
}

const saveReport = async () => {
  if (!selectedAppt.value) return
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/report`, 
      { medical_report: editedReport.value },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    selectedAppt.value.medical_report = editedReport.value
    const idx = appointments.value.findIndex(a => a.id === selectedAppt.value.id)
    if (idx !== -1) {
      appointments.value[idx].medical_report = editedReport.value
    }
    closeModal()
  } catch (error) {
    console.error("Error saving report", error)
    alert("No se pudo guardar el reporte.")
  } finally {
    saving.value = false
  }
}

const saveAndFinalize = async () => {
  if (!selectedAppt.value) return
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    
    // 1. Guardar el reporte médico
    if (editedReport.value.trim() !== '') {
      await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/report`, 
        { medical_report: editedReport.value },
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
    }
    
    // 2. Cambiar estado a completada
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: 'completada' },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    // Recargar la lista
    await fetchCompletedAppointments()
    closeModal()
  } catch (error) {
    console.error("Error finalizing appointment", error)
    alert("Hubo un error al finalizar la cita.")
  } finally {
    saving.value = false
  }
}

const markAsAbsent = async () => {
  if (!selectedAppt.value) return
  if (!confirm("¿Estás seguro de marcar a este paciente como ausente? La cita quedará cerrada.")) return
  
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    
    // 1. Guardar el reporte médico si escribió algo (ej: notas del porqué no vino)
    if (editedReport.value.trim() !== '') {
      await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/report`, 
        { medical_report: editedReport.value },
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
    }

    // 2. Cambiar estado a ausente
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: 'ausente' },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    // Recargar la lista
    await fetchCompletedAppointments()
    closeModal()
  } catch (error) {
    console.error("Error marking as absent", error)
    alert("Hubo un error al actualizar la cita.")
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.patients-wrapper { max-width: 900px; margin: 0 auto; padding-bottom: 2rem; }
.header-section { margin-bottom: 2rem; }
.title-with-icon { display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem; }
.title-with-icon h2 { margin: 0; color: var(--text-main); font-size: 1.8rem; }
.view-icon { font-size: 2rem; }
.subtitle { color: var(--text-muted); margin: 0; }

.patients-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.patient-card {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.patient-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.06);
  border-color: var(--primary-color);
}

.patient-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2rem;
  margin-right: 1.25rem;
}

.patient-info {
  flex: 1;
}

.patient-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.patient-info h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.1rem;
}

.status-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-badge.confirmada { background: #D1FAE5; color: #059669; }
.status-badge.completada { background: #DBEAFE; color: #2563EB; }
.status-badge.ausente { background: #f1f5f9; color: #475569; }

.patient-meta {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.card-arrow {
  color: #cbd5e1;
  transition: color 0.2s ease;
}

.patient-card:hover .card-arrow {
  color: var(--primary-color);
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
  max-width: 600px;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
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
  overflow-y: auto;
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

.info-section {
  margin-bottom: 1.5rem;
}

.info-section h5 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
  font-size: 0.95rem;
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

.report-textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 80px;
  color: #1e293b;
  background: #ffffff;
  box-sizing: border-box;
}

.report-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: #fafafa;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn-secondary { background: white; border: 1px solid #cbd5e1; color: var(--text-main); }
.btn-secondary:hover { background: #f1f5f9; }

.btn-primary { background: var(--primary-color); color: white; }
.btn-primary:hover { opacity: 0.9; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-success { background: #10B981; color: white; }
.btn-success:hover { opacity: 0.9; }
.btn-success:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-danger { background: #ef4444; color: white; }
.btn-danger:hover { background: #dc2626; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.placeholder-content { display: flex; justify-content: center; padding: 4rem 2rem; max-width: 100%; }
.empty-state { text-align: center; max-width: 400px; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; opacity: 0.7; }
.empty-state h3 { color: var(--text-main); margin-bottom: 0.5rem; }
.empty-state p { color: var(--text-muted); line-height: 1.5; }

.loading-state { text-align: center; padding: 4rem 0; color: var(--text-muted); }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
