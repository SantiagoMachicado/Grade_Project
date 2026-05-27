<template>
  <div class="notifications-view">
    <div class="top-header">
      <button class="icon-btn" @click="emit('back')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <h2 class="header-title">Notificaciones</h2>
      <div style="width: 24px;"></div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else class="notifications-content">
      <div v-if="newNotifications.length === 0 && recentNotifications.length === 0" class="empty-state">
        <div class="icon-wrapper">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
        </div>
        <h3>Sin notificaciones</h3>
        <p>No tienes recordatorios recientes.</p>
      </div>

      <div v-if="newNotifications.length > 0" class="notification-section">
        <div class="section-header">
          <span class="section-title">NUEVAS</span>
          <span class="badge blue-badge">{{ newNotifications.length }} Sin leer</span>
        </div>
        
        <div class="notification-list">
          <div class="notif-card new-card" v-for="(notif, index) in newNotifications" :key="'new-'+index">
            <div class="notif-icon bg-blue-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="notif-body">
              <div class="notif-title-row">
                <h4>{{ notif.title }}</h4>
                <span class="notif-time">{{ notif.relativeTime }}</span>
              </div>
              <p class="notif-text">{{ notif.message }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="recentNotifications.length > 0" class="notification-section">
        <div class="section-header">
          <span class="section-title">RECIENTES</span>
        </div>
        
        <div class="notification-list">
          <div class="notif-card" v-for="(notif, index) in recentNotifications" :key="'recent-'+index">
            <div class="notif-icon bg-gray-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="notif-body">
              <div class="notif-title-row">
                <h4 class="text-gray">{{ notif.title }}</h4>
                <span class="notif-time">{{ notif.relativeTime }}</span>
              </div>
              <p class="notif-text">{{ notif.message }}</p>
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

const emit = defineEmits(['back'])
const loading = ref(true)

const newNotifications = ref([])
const recentNotifications = ref([])

const getRelativeTime = (date) => {
  const now = new Date()
  const diffInMs = now - date
  const diffInMins = Math.floor(diffInMs / 60000)
  const diffInHours = Math.floor(diffInMins / 60)
  const diffInDays = Math.floor(diffInHours / 24)

  if (diffInMins < 60) return `${diffInMins}m atrás`
  if (diffInHours < 24) return `${diffInHours}h atrás`
  if (diffInDays === 1) return `Ayer`
  return `${diffInDays}d atrás`
}

const formatTime = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}
const formatDay = (dateStr) => {
  const d = new Date(dateStr)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  if (d.getDate() === today.getDate() && d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear()) {
    return 'hoy'
  }
  if (d.getDate() === tomorrow.getDate() && d.getMonth() === tomorrow.getMonth() && d.getFullYear() === tomorrow.getFullYear()) {
    return 'mañana'
  }
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    
    const res = await axios.get(`http://localhost:8000/api/v1/appointments/patient/${payload.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const allNotifications = []
    const now = new Date()

    res.data.forEach(appt => {
      const apptDate = new Date(appt.appointment_date)
      const centerName = appt.center?.name || 'la clínica'
      const doctorName = appt.doctor?.full_name ? `Dr. ${appt.doctor.full_name}` : 'el médico asignado'
      const specialty = appt.doctor?.specialty ? ` de ${appt.doctor.specialty.toLowerCase()}` : ''
      
      const dayText = formatDay(appt.appointment_date)
      const timeText = formatTime(appt.appointment_date)

      // Si se envió la de 24h
      if (appt.notified_24h) {
        const notifDate = new Date(apptDate.getTime() - (24 * 60 * 60 * 1000))
        if (notifDate <= now) {
          allNotifications.push({
            title: "Recordatorio de Cita",
            message: `Tu cita médica${specialty} está programada para ${dayText} a las ${timeText} en ${centerName}.`,
            time: notifDate,
            relativeTime: getRelativeTime(notifDate),
            type: '24h'
          })
        }
      }

      // Si se envió la de 3h
      if (appt.notified_3h) {
        const notifDate = new Date(apptDate.getTime() - (3 * 60 * 60 * 1000))
        if (notifDate <= now) {
          allNotifications.push({
            title: "¡Tu cita es pronto!",
            message: `Último recordatorio: Tu cita con el ${doctorName} es ${dayText} a las ${timeText}. Te esperamos.`,
            time: notifDate,
            relativeTime: getRelativeTime(notifDate),
            type: '3h'
          })
        }
      }
    })

    // Ordenar de más reciente a más antigua
    allNotifications.sort((a, b) => b.time - a.time)

    // Filtrar Nuevas (últimas 24 horas) y Recientes (últimos 7 días pero más de 24 horas)
    const msIn24h = 24 * 60 * 60 * 1000
    const msIn7d = 7 * 24 * 60 * 60 * 1000

    newNotifications.value = allNotifications.filter(n => (now - n.time) <= msIn24h)
    recentNotifications.value = allNotifications.filter(n => {
      const diff = now - n.time
      return diff > msIn24h && diff <= msIn7d
    })

  } catch (err) {
    console.error("Error fetching notifications", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; }
.icon-btn { background: none; border: none; color: #1e40af; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #eff6ff; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

.notifications-content { padding: 1.5rem; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-left: 0.5rem; }
.section-title { font-size: 0.75rem; font-weight: 800; color: #64748b; letter-spacing: 1px; }
.badge { font-size: 0.7rem; font-weight: 700; padding: 0.25rem 0.75rem; border-radius: 12px; }
.blue-badge { background: #0284c7; color: white; }

.notification-section { margin-bottom: 2rem; }

.notification-list { display: flex; flex-direction: column; gap: 1rem; }

.notif-card { display: flex; background: white; border-radius: 16px; padding: 1.25rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.new-card { border: 1px solid #e0f2fe; background: #fafcff; }

.notif-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 1.25rem; }
.bg-blue-light { background: #e0f2fe; }
.bg-gray-light { background: #f1f5f9; }

.notif-body { flex: 1; }
.notif-title-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.25rem; }
.notif-title-row h4 { margin: 0; font-size: 1rem; font-weight: 700; color: #1e293b; }
.notif-title-row h4.text-gray { color: #64748b; }
.notif-time { font-size: 0.75rem; color: #94a3b8; font-weight: 600; }
.notif-text { margin: 0; font-size: 0.85rem; color: #475569; line-height: 1.5; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; text-align: center; }
.icon-wrapper { background: #f1f5f9; width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #94a3b8; margin-bottom: 1.5rem; }
.empty-state h3 { margin: 0 0 0.5rem 0; color: #1e293b; font-size: 1.2rem; }
.empty-state p { color: #64748b; font-size: 0.95rem; line-height: 1.5; margin: 0; }

.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top: 4px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (min-width: 860px) {
  .notification-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
}
</style>
