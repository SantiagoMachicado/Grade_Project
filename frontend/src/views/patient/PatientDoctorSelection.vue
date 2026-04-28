<template>
  <div class="selection-container">
    <div class="header-section">
      <div class="title-row">
        <button @click="$router.go(-1)" class="back-btn">← Volver</button>
        <div class="title-with-icon">
          <span class="view-icon">👨‍⚕️</span>
          <h2>Selecciona un Especialista</h2>
        </div>
      </div>
      <p class="subtitle">Elige el doctor y el centro médico de tu preferencia para continuar con el agendamiento.</p>
    </div>

    <div v-if="isLoading" class="loading-state">Cargando doctores disponibles...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    
    <div v-else class="doctors-grid">
      <div v-if="assignments.length === 0" class="empty-state glass-card" style="grid-column: 1 / -1;">
        <p>No hay doctores disponibles en este momento.</p>
      </div>

      <div v-for="assign in assignments" :key="assign.id" class="doctor-card glass-card">
        <div class="doc-header">
          <img :src="`https://ui-avatars.com/api/?name=${assign.doctor?.full_name || 'Dr'}&background=E5E7EB&color=4F46E5`" alt="Avatar" class="avatar" />
          <div class="doc-info">
            <h3>{{ assign.doctor?.full_name }}</h3>
            <span class="badge">{{ assign.doctor?.specialty }}</span>
          </div>
        </div>
        
        <div class="doc-body">
          <p class="bio">{{ assign.doctor?.bio || 'Sin descripción disponible.' }}</p>
          
          <div class="clinic-info">
            <span class="icon">🏥</span>
            <div class="clinic-text">
              <strong>{{ assign.center?.name }}</strong>
              <p class="address">{{ assign.center?.address }}</p>
            </div>
          </div>
          
          <div class="fee-info" v-if="assign.doctor?.consultation_fee">
             💳 Tarifa: <strong>Bs. {{ assign.doctor.consultation_fee }}</strong>
          </div>
        </div>
        
        <button class="btn-primary w-100" @click="selectDoctor(assign.id)">
          Ver Horarios Disponibles
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const assignments = ref([])
const isLoading = ref(true)
const error = ref('')

const fetchAssignments = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('http://localhost:8000/api/v1/clinics/assignments', {
      headers: { Authorization: `Bearer ${token}` }
    })
    assignments.value = res.data
  } catch (err) {
    console.error(err)
    error.value = 'Ocurrió un error al cargar la lista de doctores.'
  } finally {
    isLoading.value = false
  }
}

const selectDoctor = (assignmentId) => {
  router.push(`/patient/appointments/new/${assignmentId}`)
}

onMounted(() => {
  fetchAssignments()
})
</script>

<style scoped>
.selection-container {
  max-width: 1000px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 2rem;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 0.5rem;
}

.back-btn {
  background: white;
  border: 1px solid #E5E7EB;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-muted);
  transition: all 0.2s;
}

.back-btn:hover {
  background: #F3F4F6;
  color: var(--text-main);
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

.subtitle {
  color: var(--text-muted);
  margin: 0 0 0 6rem; /* Align with title roughly */
}

.doctors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.doctor-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.doc-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #E5E7EB;
}

.doc-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: var(--text-main);
}

.badge {
  background: #E0E7FF;
  color: var(--primary-color);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: inline-block;
}

.doc-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 1.5rem;
}

.bio {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.clinic-info {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: #F9FAFB;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.clinic-text strong {
  display: block;
  font-size: 0.95rem;
  color: var(--text-main);
}

.address {
  margin: 0.2rem 0 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.fee-info {
  font-size: 0.95rem;
  color: var(--text-main);
}

.w-100 {
  width: 100%;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}
</style>
