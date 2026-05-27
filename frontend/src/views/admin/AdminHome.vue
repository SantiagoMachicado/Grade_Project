<template>
  <div class="dashboard-wrap">
    <div class="welcome-banner admin-banner">
      <h2>Panel Administrativo</h2>
      <p>Bienvenido. Control total sobre usuarios, pacientes y especialistas.</p>
    </div>

    <!-- Stats Grid -->
    <div class="dashboard-content">
      <div class="stats-card">
        <div class="stats-icon">👥</div>
        <div class="stats-info">
          <h3>Total Pacientes</h3>
          <p class="stat-number" v-if="!loading">{{ patientCount }}</p>
          <p class="stat-number loading-stat" v-else>...</p>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">🩺</div>
        <div class="stats-info">
          <h3>Especialistas Activos</h3>
          <p class="stat-number" v-if="!loading">{{ doctorCount }}</p>
          <p class="stat-number loading-stat" v-else>...</p>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">🏥</div>
        <div class="stats-info">
          <h3>Centros Médicos</h3>
          <p class="stat-number" v-if="!loading">{{ clinicCount }}</p>
          <p class="stat-number loading-stat" v-else>...</p>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">⚙️</div>
        <div class="stats-info">
          <h3>Total Usuarios</h3>
          <p class="stat-number" v-if="!loading">{{ totalUsers }}</p>
          <p class="stat-number loading-stat" v-else>...</p>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions-section">
      <h3>Accesos Rápidos</h3>
      <div class="actions-grid">
        <div class="action-card" @click="$router.push('/admin/doctors')">
          <div class="action-emoji">🩺</div>
          <h4>Gestionar Médicos</h4>
          <p>Registrar nuevos especialistas, editar especialidades y tarifas, o dar de baja.</p>
        </div>
        <div class="action-card" @click="$router.push('/admin/patients')">
          <div class="action-emoji">👥</div>
          <h4>Gestionar Pacientes</h4>
          <p>Ver registros de pacientes, historiales médicos asociados y detalles de contacto.</p>
        </div>
        <div class="action-card" @click="$router.push('/admin/clinics')">
          <div class="action-emoji">🏥</div>
          <h4>Gestionar Clínicas</h4>
          <p>Añadir nuevos centros de salud asociados, cambiar direcciones y administrar sucursales.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const doctorCount = ref(0)
const patientCount = ref(0)
const clinicCount = ref(0)
const loading = ref(true)

const totalUsers = computed(() => {
  // Sum of doctors, patients, plus 1 for the admin account itself
  return doctorCount.value + patientCount.value + 1
})

const fetchStats = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const headers = { Authorization: `Bearer ${token}` }

    const [doctorsRes, patientsRes, clinicsRes] = await Promise.all([
      axios.get('http://localhost:8000/api/v1/doctors/', { headers }),
      axios.get('http://localhost:8000/api/v1/patients/', { headers }),
      axios.get('http://localhost:8000/api/v1/clinics/', { headers })
    ])

    doctorCount.value = doctorsRes.data.length
    patientCount.value = patientsRes.data.length
    clinicCount.value = clinicsRes.data.length
  } catch (err) {
    console.error("Error fetching admin stats", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard-wrap {
  width: 100%;
  max-width: 1100px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.welcome-banner {
  padding: 2.5rem;
  border-radius: 20px;
  color: white;
  margin-bottom: 2rem;
}
.admin-banner {
  background: linear-gradient(135deg, #0f172a, #1e293b);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
}
.welcome-banner h2 { 
  margin: 0 0 0.5rem 0; 
  font-size: 1.8rem;
  font-weight: 800;
}
.welcome-banner p {
  margin: 0;
  font-size: 1rem;
  color: #94a3b8;
}
.dashboard-content {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
}
.stats-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  border: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.stats-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stats-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.stat-number {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}
.loading-stat {
  color: #cbd5e1;
}

.quick-actions-section h3 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 1.5rem;
}
.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.action-card {
  background: white;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 2rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 20px rgba(0,0,0,0.01);
}
.action-card:hover {
  transform: translateY(-4px);
  border-color: #cbd5e1;
  box-shadow: 0 10px 25px rgba(0,0,0,0.04);
}
.action-emoji {
  font-size: 2.25rem;
  margin-bottom: 1.25rem;
}
.action-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
}
.action-card p {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.5;
}
</style>
