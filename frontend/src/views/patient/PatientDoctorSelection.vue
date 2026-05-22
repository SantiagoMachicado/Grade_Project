<template>
  <div class="selection-container">
    <!-- Header -->
    <div class="header-section">
      <div class="title-row">
        <button @click="$router.go(-1)" class="icon-btn">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        </button>
        <h2 class="page-title">Buscar Médico</h2>
        <div style="width: 24px;"></div> <!-- Spacer -->
      </div>
      <p class="subtitle">Encuentra a los mejores especialistas para cuidar de tu salud.</p>
    </div>

    <!-- Search / Filter Placeholder (Visual solo) -->
    <div class="search-bar">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input type="text" v-model="searchQuery" placeholder="Buscar por especialidad o doctor..." class="search-input" />
    </div>

    <!-- Specialty Chips -->
    <div class="specialties-wrapper" v-if="uniqueSpecialties.length > 1">
      <button 
        v-for="spec in uniqueSpecialties" 
        :key="spec"
        :class="['chip', { active: selectedSpecialty === spec }]"
        @click="selectedSpecialty = spec"
      >
        {{ spec }}
      </button>
    </div>

    <!-- Content -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    
    <div v-else class="doctors-list">
      <div v-if="filteredAssignments.length === 0" class="empty-state">
        <p>No hay doctores disponibles que coincidan con tu búsqueda o filtro.</p>
      </div>

      <div v-for="assign in filteredAssignments" :key="assign.id" class="doctor-card" @click="selectDoctor(assign.id)">
        <div class="doc-header">
          <img :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${assign.doctor?.full_name || 'Doc'}&backgroundColor=e2e8f0&clothing=blazerAndShirt`" alt="Avatar" class="avatar" />
          <div class="doc-info">
            <div class="name-row">
              <h3>{{ assign.doctor?.full_name?.startsWith('Dr') ? '' : 'Dr. ' }}{{ assign.doctor?.full_name }}</h3>
              <div class="rating">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#fbbf24" stroke="#fbbf24" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                <span>4.9</span>
              </div>
            </div>
            <p class="specialty">{{ assign.doctor?.specialty || 'General' }}</p>
          </div>
        </div>
        
        <div class="doc-body">
          <div class="info-row">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00bcd4" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            <span>{{ assign.center?.name }}</span>
          </div>
          <div class="info-row fee" v-if="assign.doctor?.consultation_fee">
             <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2" ry="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
             <span>Consulta: Bs. {{ assign.doctor.consultation_fee }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const assignments = ref([])
const isLoading = ref(true)
const error = ref('')
const searchQuery = ref('')
const selectedSpecialty = ref('Todas')

const uniqueSpecialties = computed(() => {
  const specs = assignments.value.map(a => a.doctor?.specialty).filter(Boolean)
  return ['Todas', ...new Set(specs)]
})

const filteredAssignments = computed(() => {
  let filtered = assignments.value

  // Filtrar por especialidad primero
  if (selectedSpecialty.value !== 'Todas') {
    filtered = filtered.filter(a => a.doctor?.specialty === selectedSpecialty.value)
  }

  // Luego filtrar por búsqueda de texto
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(assign => {
      const docName = (assign.doctor?.full_name || '').toLowerCase()
      const specialty = (assign.doctor?.specialty || '').toLowerCase()
      const center = (assign.center?.name || '').toLowerCase()
      
      return docName.includes(query) || specialty.includes(query) || center.includes(query)
    })
  }
  
  return filtered
})

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
  if (route.query.search) {
    searchQuery.value = route.query.search
  }
  if (route.query.specialty) {
    selectedSpecialty.value = route.query.specialty
  }
  fetchAssignments()
})
</script>

<style scoped>
.selection-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 1.5rem;
  background: #f8fafc;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Header */
.header-section {
  margin-bottom: 1.5rem;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
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
.subtitle {
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}

/* Search Bar */
.search-bar {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 16px;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
  border: 1px solid #f1f5f9;
}
.search-input {
  border: none;
  outline: none;
  background: transparent;
  width: 100%;
  font-size: 0.95rem;
  color: #64748b;
}

/* Specialty Chips */
.specialties-wrapper {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  scrollbar-width: none;
}
.specialties-wrapper::-webkit-scrollbar {
  display: none;
}
.chip {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1.25rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.chip:hover {
  border-color: #cbd5e1;
  color: #1e293b;
}
.chip.active {
  background: #004e98;
  color: white;
  border-color: #004e98;
  box-shadow: 0 4px 10px rgba(0, 78, 152, 0.2);
}

/* Doctors List */
.doctors-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.doctor-card {
  background: white;
  border-radius: 20px;
  padding: 1.25rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  border: 1px solid #f1f5f9;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.doctor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

.doc-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 1rem;
}
.avatar {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: #f1f5f9;
  object-fit: cover;
}
.doc-info {
  flex: 1;
}
.name-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}
.doc-info h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 800;
  color: #1e293b;
}
.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #fef3c7;
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #b45309;
}
.specialty {
  margin: 0;
  font-size: 0.85rem;
  color: #00bcd4;
  font-weight: 600;
}

.doc-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.info-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
}
.info-row.fee {
  color: #10b981;
}

.empty-state { text-align: center; color: #64748b; padding: 3rem 1rem; }
.loading-state { text-align: center; padding: 3rem 0; }
.spinner { width: 30px; height: 30px; border: 3px solid #f1f5f9; border-top: 3px solid #00bcd4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
