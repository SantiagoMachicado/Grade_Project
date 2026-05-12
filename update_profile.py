import re

with open("frontend/src/views/patient/PatientProfile.vue", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert Medical History and Detail Views
views_html = """
    <!-- MEDICAL HISTORY VIEW -->
    <div v-if="activeView === 'medical_history'" class="history-view">
      <div class="top-header">
        <button class="icon-btn" @click="activeView = 'menu'">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h2 class="header-title">Historial Médico</h2>
        <div style="width: 24px;"></div>
      </div>

      <div v-if="loadingAppointments" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="history-content">
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">CONSULTAS</span>
            <span class="stat-value">{{ completedAppointments.length }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">ÚLTIMA VISITA</span>
            <span class="stat-value">{{ lastVisitDate }}</span>
          </div>
        </div>

        <div class="records-header">
          <h3>Registros Recientes</h3>
        </div>

        <div class="records-list">
          <div v-if="completedAppointments.length === 0" class="empty-records">
            No tienes citas completadas aún.
          </div>
          <div class="record-card" v-for="appt in completedAppointments" :key="appt.id">
            <div class="card-header">
              <div class="icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
              </div>
              <div class="doctor-info">
                <div class="date-text">{{ formatLongDate(appt.appointment_date) }}</div>
                <div class="doctor-name">Dr. {{ appt.doctor?.full_name }}</div>
                <div class="specialty">{{ appt.doctor?.specialty }}</div>
              </div>
              <div class="status-badge">COMPLETADO</div>
            </div>
            
            <div class="card-body">
              <div class="diagnosis-label">DIAGNÓSTICO</div>
              <div class="diagnosis-text">{{ appt.medical_report || 'Sin diagnóstico registrado.' }}</div>
            </div>

            <div class="card-footer">
              <button class="btn btn-primary full-width" @click="openAppointmentDetail(appt)">Ver detalles</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- APPOINTMENT DETAIL VIEW -->
    <div v-if="activeView === 'appointment_detail' && selectedAppointment" class="detail-view">
      <div class="top-header">
        <button class="icon-btn" @click="activeView = 'medical_history'">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h2 class="header-title">Detalle de Consulta</h2>
        <div style="width: 24px;"></div>
      </div>

      <div class="detail-content">
        <div class="detail-card glass-card">
          <div class="detail-doctor-header">
            <div class="doc-avatar">{{ getInitials(selectedAppointment.doctor?.full_name) }}</div>
            <div>
              <h3>Dr. {{ selectedAppointment.doctor?.full_name }}</h3>
              <p>{{ selectedAppointment.doctor?.specialty }}</p>
            </div>
          </div>
          
          <div class="detail-info-grid">
            <div class="info-item">
              <span class="info-label">FECHA Y HORA</span>
              <span class="info-val">{{ formatDateTime(selectedAppointment.appointment_date) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">CLÍNICA</span>
              <span class="info-val">{{ selectedAppointment.center?.name || 'No registrada' }}</span>
            </div>
          </div>

          <div class="detail-section">
            <h4>DIAGNÓSTICO MÉDICO</h4>
            <div class="detail-box">
              {{ selectedAppointment.medical_report || 'Sin reporte.' }}
            </div>
          </div>

          <div class="detail-section">
            <h4>NOTAS PREVIAS (MOTIVO DE CITA)</h4>
            <div class="detail-box notes-box">
              {{ selectedAppointment.notes || 'El paciente no proporcionó notas previas al agendar.' }}
            </div>
          </div>
        </div>
      </div>
    </div>
"""

content = content.replace("    </div>\n\n  </div>\n</template>", "    </div>\n" + views_html + "\n  </div>\n</template>")

# 2. Insert JS Logic
js_state = """
const activeView = ref('menu')
const completedAppointments = ref([])
const loadingAppointments = ref(false)
const lastVisitDate = ref('--')
const selectedAppointment = ref(null)

const formatLongDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' }).toUpperCase()
}

const formatShortDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

const formatDateTime = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute:'2-digit' })
}

const fetchAppointments = async () => {
  if (completedAppointments.value.length > 0) return // already fetched
  loadingAppointments.value = true
  try {
    const token = localStorage.getItem('access_token')
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const patientId = payload.id
    
    const res = await axios.get(`http://localhost:8000/api/v1/appointments/patient/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Filter only completed
    const completed = res.data.filter(a => a.status === 'completada' || a.status === 'confirmada') // we show both for now or just completada? user said completadas
    completedAppointments.value = completed.filter(a => a.status === 'completada').sort((a,b) => new Date(b.appointment_date) - new Date(a.appointment_date))
    
    if (completedAppointments.value.length > 0) {
      lastVisitDate.value = formatShortDate(completedAppointments.value[0].appointment_date)
    }
  } catch (err) {
    console.error("Error fetching appointments", err)
  } finally {
    loadingAppointments.value = false
  }
}

const openMedicalHistory = () => {
  activeView.value = 'medical_history'
  fetchAppointments()
}

const openAppointmentDetail = (appt) => {
  selectedAppointment.value = appt
  activeView.value = 'appointment_detail'
}
"""

content = content.replace("const activeView = ref('menu')", js_state)

# Replace the placeholderAction call for Historial Médico
content = content.replace("@click=\"placeholderAction('Historial Médico')\"", "@click=\"openMedicalHistory\"")

# 3. Add CSS
css_styles = """
/* History View */
.history-view { padding-bottom: 2rem; }
.history-content { padding: 1.5rem; }

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.25rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0284c7;
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.records-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
}

.record-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.card-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.icon-box {
  width: 48px;
  height: 48px;
  background: #eff6ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.doctor-info {
  flex: 1;
}

.date-text {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.doctor-name {
  font-size: 1rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 0.2rem;
}

.specialty {
  font-size: 0.85rem;
  color: #94a3b8;
}

.status-badge {
  background: #dbeafe;
  color: #1e3a8a;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.3rem 0.6rem;
  border-radius: 8px;
  letter-spacing: 0.5px;
}

.card-body {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.diagnosis-label {
  font-size: 0.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.diagnosis-text {
  font-size: 0.85rem;
  color: #475569;
  line-height: 1.5;
}

.empty-records {
  text-align: center;
  color: #94a3b8;
  padding: 2rem;
  background: white;
  border-radius: 12px;
}

/* Detail View */
.detail-content {
  padding: 1.5rem;
}

.detail-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
}

.detail-doctor-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.doc-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #eff6ff;
  color: #0284c7;
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.25rem;
}

.detail-doctor-header h3 {
  margin: 0 0 0.25rem 0;
  color: #1e293b;
  font-size: 1.2rem;
}

.detail-doctor-header p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.detail-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 0.7rem;
  font-weight: 800;
  color: #94a3b8;
  margin-bottom: 0.4rem;
}

.info-val {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e293b;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h4 {
  font-size: 0.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.75rem 0;
}

.detail-box {
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: 12px;
  font-size: 0.9rem;
  color: #475569;
  line-height: 1.6;
  white-space: pre-wrap;
}

.notes-box {
  background: #fef2f2;
  color: #991b1b;
  border: 1px dashed #fca5a5;
}
"""

content = content + "\n" + css_styles

with open("frontend/src/views/patient/PatientProfile.vue", "w", encoding="utf-8") as f:
    f.write(content)
