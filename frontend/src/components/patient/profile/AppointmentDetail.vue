<template>
  <div class="detail-view">
    <div class="top-header">
      <button class="icon-btn" @click="emit('back')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <h2 class="header-title">Detalle de Consulta</h2>
      <div style="width: 24px;"></div>
    </div>

    <div class="detail-content" v-if="appointment">
      <div class="detail-card glass-card">
        <div class="detail-doctor-header">
          <div class="doc-avatar">{{ getInitials(appointment.doctor?.full_name) }}</div>
          <div>
            <h3>Dr. {{ appointment.doctor?.full_name }}</h3>
            <p>{{ appointment.doctor?.specialty }}</p>
          </div>
        </div>
        
        <div class="detail-info-grid">
          <div class="info-item">
            <span class="info-label">FECHA Y HORA</span>
            <span class="info-val">{{ formatDateTime(appointment.appointment_date) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">CLÍNICA</span>
            <span class="info-val">{{ appointment.center?.name || 'No registrada' }}</span>
          </div>
        </div>

        <div class="detail-section">
          <h4>DIAGNÓSTICO MÉDICO</h4>
          <div class="detail-box">
            {{ appointment.medical_report || 'Sin reporte.' }}
          </div>
        </div>

        <div class="detail-section">
          <h4>NOTAS PREVIAS (MOTIVO DE CITA)</h4>
          <div class="detail-box notes-box">
            {{ appointment.notes || 'No se proporcionaron notas previas al agendar.' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  appointment: Object
})
const emit = defineEmits(['back'])

const formatDateTime = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute:'2-digit' })
}

const getInitials = (name) => {
  if (!name) return 'U'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}
</script>

<style scoped>
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; }
.icon-btn { background: none; border: none; color: #1e40af; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #eff6ff; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

.detail-view { padding-bottom: 2rem; }
.detail-content { padding: 0.5rem 1rem; box-sizing: border-box; }
.detail-card { background: white; border-radius: 16px; padding: 1.5rem; box-sizing: border-box; box-shadow: 0 4px 15px rgba(0,0,0,0.03); width: 100%; overflow: hidden; }
.detail-doctor-header { display: flex; align-items: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.doc-avatar { width: 60px; height: 60px; border-radius: 50%; background: #eff6ff; color: #0284c7; font-size: 1.5rem; font-weight: bold; display: flex; align-items: center; justify-content: center; margin-right: 1.25rem; }
.detail-doctor-header h3 { margin: 0 0 0.25rem 0; color: #1e293b; font-size: 1.2rem; }
.detail-doctor-header p { margin: 0; color: #64748b; font-size: 0.9rem; }
.detail-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem; }
.info-item { display: flex; flex-direction: column; }
.info-label { font-size: 0.7rem; font-weight: 800; color: #94a3b8; margin-bottom: 0.4rem; }
.info-val { font-size: 0.95rem; font-weight: 600; color: #1e293b; }
.detail-section { margin-bottom: 2rem; }
.detail-section h4 { font-size: 0.8rem; font-weight: 800; color: #0f172a; margin: 0 0 0.75rem 0; }
.detail-box { background: #f8fafc; padding: 1.25rem; border-radius: 12px; font-size: 0.9rem; color: #475569; line-height: 1.6; white-space: pre-wrap; }
.notes-box { background: #fef2f2; color: #991b1b; border: 1px dashed #fca5a5; }

@media (min-width: 860px) {
  .detail-card {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 2rem;
    padding: 2.5rem;
  }
  .detail-doctor-header {
    grid-column: span 2;
  }
  .detail-info-grid {
    grid-column: span 2;
  }
}
</style>
