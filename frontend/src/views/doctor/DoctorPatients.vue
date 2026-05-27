<template>
  <div class="profile-container">
    <div class="menu-view">
      <div class="top-header">
        <div style="width: 24px"></div>
        <h2 class="header-title">Mis Pacientes</h2>
        <div style="width: 24px"></div>
      </div>

      <div class="menu-section" style="padding-top: 1rem;">
        <div class="patients-layout-grid">
          <!-- Left Column: Patient List -->
          <div class="patients-list-pane">
            <div v-if="loading" class="loading-state">
              <div class="spinner"></div>
            </div>

            <div class="placeholder-content" v-else-if="appointments.length === 0">
              <div class="empty-state">
                <div class="empty-icon">🗂️</div>
                <h3>Sin pacientes recientes</h3>
                <p>Aquí aparecerán los pacientes de las citas Confirmadas o Completadas.</p>
              </div>
            </div>

            <div class="menu-list" v-else>
              <button 
                v-for="appt in appointments" 
                :key="appt.id" 
                class="menu-item"
                :class="{ active: selectedAppt?.id === appt.id }"
                @click="openPatientModal(appt)"
              >
                <div class="menu-icon bg-blue" style="border-radius: 50%;">
                  {{ getInitials(appt.patient.full_name) }}
                </div>
                <div class="menu-text">
                  <div class="patient-header-row">
                    <h4>{{ appt.patient.full_name }}</h4>
                    <span class="status-badge" :class="appt.status">
                      {{ formatStatus(appt.status) }}
                    </span>
                  </div>
                  <p>{{ calculateAge(appt.patient.birth_date) }} años &bull; Visita: {{ formatDate(appt.appointment_date) }}</p>
                </div>
                <div class="menu-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                </div>
              </button>
            </div>
          </div>

          <!-- Right Column: Patient Details (Desktop inline panel) -->
          <div class="patients-details-pane" v-if="isDesktop">
            <div class="empty-detail-state" v-if="!selectedAppt">
              <div class="empty-icon" style="font-size: 3rem;">👤</div>
              <h4>Selecciona un paciente</h4>
              <p>Haz clic en un paciente de la lista para ver su historial médico y redactar reportes.</p>
            </div>
            <div class="patient-detail-card" v-else>
              <h3>Detalle de Consulta</h3>
              <div class="patient-summary">
                <div class="summary-avatar">{{ getInitials(selectedAppt.patient.full_name) }}</div>
                <div>
                  <h4>{{ selectedAppt.patient.full_name }}</h4>
                  <p>{{ calculateAge(selectedAppt.patient.birth_date) }} años | 📞 {{ selectedAppt.patient.phone || 'No registrado' }}</p>
                </div>
              </div>

              <div class="info-section">
                <h5>Historial Médico del Paciente</h5>
                <div class="info-box">{{ selectedAppt.patient.medical_history || 'Sin registros médicos previos.' }}</div>
              </div>

              <div class="info-section">
                <h5>Motivo de la Cita</h5>
                <div class="info-box">{{ selectedAppt.notes || 'No se proporcionaron notas.' }}</div>
              </div>

              <div class="info-section">
                <h5>Reporte Médico / Diagnóstico</h5>
                <textarea 
                  v-model="editedReport" 
                  placeholder="Escribe aquí el diagnóstico o tratamiento..."
                  rows="4"
                  class="report-textarea"
                ></textarea>
              </div>

              <div class="detail-actions">
                <button 
                  v-if="selectedAppt.status === 'confirmada'" 
                  class="btn btn-danger" 
                  @click="markAsAbsent" 
                  :disabled="saving">
                  Ausente
                </button>
                <button 
                  v-if="selectedAppt.status === 'confirmada'" 
                  class="btn btn-success" 
                  @click="saveAndFinalize" 
                  :disabled="saving">
                  {{ saving ? '...' : 'Finalizar' }}
                </button>
                <button 
                  v-else 
                  class="btn btn-primary" 
                  @click="saveReport" 
                  :disabled="saving">
                  {{ saving ? '...' : 'Actualizar' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Modal Detalle -->
    <div class="modal-backdrop" v-if="!isDesktop && selectedAppt" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Detalle de Consulta</h3>
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
            <h5>Historial Médico del Paciente</h5>
            <div class="info-box">{{ selectedAppt.patient.medical_history || 'Sin registros médicos previos.' }}</div>
          </div>

          <div class="info-section">
            <h5>Motivo de la Cita</h5>
            <div class="info-box">{{ selectedAppt.notes || 'No se proporcionaron notas.' }}</div>
          </div>

          <div class="info-section">
            <h5>Reporte Médico / Diagnóstico</h5>
            <textarea 
              v-model="editedReport" 
              placeholder="Escribe aquí el diagnóstico o tratamiento..."
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
            Ausente
          </button>
          
          <button 
            v-if="selectedAppt.status === 'confirmada'" 
            class="btn btn-success" 
            @click="saveAndFinalize" 
            :disabled="saving">
            {{ saving ? '...' : 'Finalizar' }}
          </button>
          
          <button 
            v-else 
            class="btn btn-primary" 
            @click="saveReport" 
            :disabled="saving">
            {{ saving ? '...' : 'Actualizar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const appointments = ref([])
const loading = ref(true)
const selectedAppt = ref(null)
const editedReport = ref('')
const saving = ref(false)
const isDesktop = ref(false)

const checkWidth = () => {
  isDesktop.value = window.innerWidth >= 860
}

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
  checkWidth()
  window.addEventListener('resize', checkWidth)
  fetchCompletedAppointments()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
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
    'pendiente': 'PEND',
    'confirmada': 'CONF',
    'completada': 'COMP',
    'cancelada': 'CANC',
    'ausente': 'AUS'
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
    if (editedReport.value.trim() !== '') {
      await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/report`, 
        { medical_report: editedReport.value },
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
    }
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: 'completada' },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
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
  if (!confirm("¿Estás seguro de marcar a este paciente como ausente?")) return
  
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (editedReport.value.trim() !== '') {
      await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/report`, 
        { medical_report: editedReport.value },
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
    }
    await axios.patch(`http://localhost:8000/api/v1/appointments/${selectedAppt.value.id}/status`, 
      { status: 'ausente' },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
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
  .patients-layout-grid {
    display: grid;
    grid-template-columns: 1.2fr 1.8fr;
    gap: 2rem;
    align-items: start;
  }
  .patients-details-pane {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    border: 1px solid #f1f5f9;
  }
  .menu-item.active {
    background: #f0f9ff;
    border-left: 4px solid #0284c7;
  }
  .empty-detail-state {
    text-align: center;
    padding: 6rem 2rem;
    color: #94a3b8;
  }
  .empty-detail-state h4 {
    margin: 1rem 0 0.5rem 0;
    color: #1e293b;
    font-size: 1.1rem;
    font-weight: 700;
  }
  .empty-detail-state p {
    font-size: 0.85rem;
    line-height: 1.5;
    margin: 0;
  }
  .patient-detail-card h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.25rem;
    font-weight: 800;
    color: #1e293b;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 0.75rem;
  }
  .detail-actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 1.5rem;
    justify-content: flex-end;
  }
  .detail-actions .btn {
    flex: none;
    min-width: 120px;
  }
}
.menu-view { width: 100%; }
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; border-bottom: 1px solid #f1f5f9; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.menu-section { padding: 1.5rem; }

.menu-list { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.03); display: flex; flex-direction: column; }
.menu-item { display: flex; align-items: center; width: 100%; padding: 1.25rem; background: white; border: none; cursor: pointer; text-align: left; transition: background 0.2s; border-bottom: 1px solid #f1f5f9; }
.menu-item:last-child { border-bottom: none; }
.menu-item:hover { background: #f8fafc; }
.menu-item:active { background: #f1f5f9; }

.menu-icon { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; flex-shrink: 0; font-weight: bold; font-size: 1.1rem; }
.bg-blue { background: #e0f2fe; color: #0284c7; }

.menu-text { flex: 1; }
.patient-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.2rem; }
.menu-text h4 { margin: 0; font-size: 1rem; font-weight: 700; color: #1e293b; }
.menu-text p { margin: 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.3; }
.menu-arrow { color: #cbd5e1; flex-shrink: 0; margin-left: 0.5rem; }

.status-badge { padding: 0.15rem 0.5rem; border-radius: 12px; font-size: 0.65rem; font-weight: 800; letter-spacing: 0.5px; }
.status-badge.confirmada { background: #d1fae5; color: #059669; }
.status-badge.completada { background: #dbeafe; color: #2563eb; }
.status-badge.ausente { background: #f1f5f9; color: #475569; }

.placeholder-content { display: flex; justify-content: center; padding: 4rem 1rem; }
.empty-state { text-align: center; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state h3 { color: #1e293b; margin-bottom: 0.5rem; font-size: 1.1rem; font-weight: 700; }
.empty-state p { color: #64748b; line-height: 1.5; font-size: 0.9rem; }

.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 30px; height: 30px; border: 3px solid #f1f5f9; border-top: 3px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Modal Styles */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; box-sizing: border-box; }
.modal-content { width: 100%; max-width: 440px; background: white; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column; max-height: 90vh; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
.modal-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; line-height: 1; padding: 0; }
.modal-body { padding: 1.5rem; overflow-y: auto; }
.patient-summary { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.summary-avatar { width: 50px; height: 50px; border-radius: 50%; background: #f1f5f9; color: #0284c7; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; flex-shrink: 0; }
.patient-summary h4 { margin: 0 0 0.25rem 0; font-size: 1.1rem; color: #1e293b; }
.patient-summary p { margin: 0; color: #64748b; font-size: 0.85rem; }
.info-section { margin-bottom: 1.5rem; }
.info-section h5 { margin: 0 0 0.5rem 0; color: #0284c7; font-size: 0.9rem; }
.info-box { background: #f8fafc; padding: 1rem; border-radius: 12px; color: #475569; font-size: 0.9rem; line-height: 1.5; border: 1px solid #e2e8f0; }
.report-textarea { width: 100%; padding: 1rem; border: 1px solid #cbd5e1; border-radius: 12px; font-family: inherit; font-size: 0.9rem; resize: vertical; min-height: 80px; color: #1e293b; background: #ffffff; box-sizing: border-box; }
.report-textarea:focus { outline: none; border-color: #0284c7; }
.modal-footer { padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 0.5rem; background: #fafafa; flex-wrap: wrap; }
.btn { padding: 0.6rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s ease; font-size: 0.85rem; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #475569; }
.btn-primary { background: #0284c7; color: white; }
.btn-success { background: #10b981; color: white; }
.btn-danger { background: #ef4444; color: white; }
</style>
