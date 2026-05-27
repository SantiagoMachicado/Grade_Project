<template>
  <div class="crud-container">
    <!-- Header -->
    <div class="crud-header">
      <div>
        <h2>Gestión de Pacientes</h2>
        <p>Administra los expedientes y cuentas de los pacientes.</p>
      </div>
      <button class="btn btn-primary" @click="openCreateDrawer">
        <span class="icon">+</span> Agregar Paciente
      </button>
    </div>

    <!-- Actions & Filters -->
    <div class="filter-section">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Buscar paciente por nombre o email..." 
          class="search-input"
        />
      </div>
      <button class="btn btn-secondary" @click="fetchPatients">Refresh 🔄</button>
    </div>

    <!-- Table -->
    <div class="table-container">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando lista de pacientes...</p>
      </div>
      <div v-else-if="filteredPatients.length === 0" class="empty-state">
        <p>No se encontraron pacientes. ¡Registra uno nuevo para comenzar!</p>
      </div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Teléfono</th>
            <th>Fecha Nacimiento</th>
            <th>Historial Médico Preview</th>
            <th>Email</th>
            <th class="actions-column">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pat in filteredPatients" :key="pat.user_id">
            <td class="id-cell">#{{ pat.user_id }}</td>
            <td class="name-cell">{{ pat.full_name }}</td>
            <td>{{ pat.phone || 'Sin registrar' }}</td>
            <td>{{ formatDate(pat.birth_date) }}</td>
            <td class="bio-cell" :title="pat.medical_history">
              {{ truncateText(pat.medical_history) }}
            </td>
            <td>{{ pat.user?.email || 'N/A' }}</td>
            <td class="actions-cell">
              <button class="btn-action edit-btn" @click="openEditDrawer(pat)" title="Editar">✏️ Editar</button>
              <button class="btn-action delete-btn" @click="confirmDelete(pat)" title="Eliminar">🗑️ Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Slide-over Drawer for Add/Edit -->
    <div :class="['drawer-backdrop', { show: drawerOpen }]" @click.self="closeDrawer">
      <div :class="['drawer-content', { open: drawerOpen }]">
        <div class="drawer-header">
          <h3>{{ isEditing ? 'Editar Ficha Paciente' : 'Registrar Nuevo Paciente' }}</h3>
          <button class="close-btn" @click="closeDrawer">&times;</button>
        </div>
        
        <form @submit.prevent="savePatient" class="drawer-form">
          <!-- Auth details: only for creating -->
          <template v-if="!isEditing">
            <div class="form-group">
              <label>Correo Electrónico *</label>
              <input 
                type="email" 
                v-model="form.email" 
                placeholder="ejemplo@test.com" 
                required 
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label>Contraseña Temporal *</label>
              <input 
                type="password" 
                v-model="form.password" 
                placeholder="Mínimo 8 caracteres" 
                required 
                minlength="8"
                class="form-input"
              />
            </div>
            <div class="divider-form"></div>
          </template>

          <div class="form-group">
            <label>Nombre Completo *</label>
            <input 
              type="text" 
              v-model="form.full_name" 
              placeholder="Ej. Roberto Montenegro" 
              required 
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Teléfono de Contacto</label>
            <input 
              type="tel" 
              v-model="form.phone" 
              placeholder="Ej. +591 70123456" 
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Fecha de Nacimiento</label>
            <input 
              type="date" 
              v-model="form.birth_date" 
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Historial Médico (Alergias, Condiciones, Antecedentes)</label>
            <textarea 
              v-model="form.medical_history" 
              placeholder="Historial clínico inicial..." 
              rows="5"
              class="form-input form-textarea"
            ></textarea>
          </div>

          <div class="drawer-footer">
            <button type="button" class="btn btn-secondary" @click="closeDrawer">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <h3>¿Eliminar Expediente del Paciente?</h3>
        <p>Estás a punto de eliminar a <strong>{{ selectedPat?.full_name }}</strong> de la base de datos. Se borrará su cuenta de usuario, expediente médico e historial de citas. Esta acción no se puede deshacer.</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn btn-danger" @click="executeDelete" :disabled="deleting">
            {{ deleting ? 'Eliminando...' : 'Sí, eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const patients = ref([])
const loading = ref(true)
const saving = ref(false)
const deleting = ref(false)
const searchQuery = ref('')

// Drawer & Modal state
const drawerOpen = ref(false)
const isEditing = ref(false)
const showDeleteModal = ref(false)
const selectedPat = ref(null)

// Form fields
const form = ref({
  user_id: null,
  email: '',
  password: '',
  full_name: '',
  phone: '',
  birth_date: '',
  medical_history: ''
})

const filteredPatients = computed(() => {
  if (!searchQuery.value.trim()) return patients.value
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(p => 
    p.full_name.toLowerCase().includes(query) || 
    (p.user?.email && p.user.email.toLowerCase().includes(query))
  )
})

const fetchPatients = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('http://localhost:8000/api/v1/patients/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    patients.value = res.data
  } catch (err) {
    console.error("Error fetching patients", err)
    alert("Error al cargar la lista de pacientes.")
  } finally {
    loading.value = false
  }
}

const openCreateDrawer = () => {
  isEditing.value = false
  form.value = {
    user_id: null,
    email: '',
    password: '',
    full_name: '',
    phone: '',
    birth_date: '',
    medical_history: ''
  }
  drawerOpen.value = true
}

const openEditDrawer = (pat) => {
  isEditing.value = true
  form.value = {
    user_id: pat.user_id,
    email: pat.user?.email || '',
    password: '',
    full_name: pat.full_name,
    phone: pat.phone || '',
    birth_date: pat.birth_date || '',
    medical_history: pat.medical_history || ''
  }
  drawerOpen.value = true
}

const closeDrawer = () => {
  drawerOpen.value = false
}

const savePatient = async () => {
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    const headers = { Authorization: `Bearer ${token}` }
    
    // empty string birth_date becomes null for database compliance
    const formattedBirthDate = form.value.birth_date || null
    
    if (isEditing.value) {
      // Update
      const res = await axios.put(`http://localhost:8000/api/v1/patients/${form.value.user_id}`, {
        full_name: form.value.full_name,
        phone: form.value.phone,
        birth_date: formattedBirthDate,
        medical_history: form.value.medical_history
      }, { headers })
      
      const idx = patients.value.findIndex(p => p.user_id === form.value.user_id)
      if (idx !== -1) {
        // preserve the user info (email)
        const existingEmail = patients.value[idx].user
        patients.value[idx] = { ...res.data, user: existingEmail }
      }
      closeDrawer()
    } else {
      // Create via Auth register endpoint
      await axios.post('http://localhost:8000/api/v1/auth/register', {
        email: form.value.email,
        password: form.value.password,
        role: "paciente",
        full_name: form.value.full_name,
        phone: form.value.phone,
        birth_date: formattedBirthDate,
        medical_history: form.value.medical_history
      })
      
      // Reload list to get formatted data from database
      await fetchPatients()
      closeDrawer()
    }
  } catch (err) {
    console.error("Error saving patient", err)
    alert(err.response?.data?.detail || "Error al guardar la ficha del paciente. Asegúrese de que el email no esté duplicado.")
  } finally {
    saving.value = false
  }
}

const confirmDelete = (pat) => {
  selectedPat.value = pat
  showDeleteModal.value = true
}

const executeDelete = async () => {
  if (!selectedPat.value) return
  deleting.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.delete(`http://localhost:8000/api/v1/patients/${selectedPat.value.user_id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    patients.value = patients.value.filter(p => p.user_id !== selectedPat.value.user_id)
    showDeleteModal.value = false
  } catch (err) {
    console.error("Error deleting patient", err)
    alert("Error al dar de baja al paciente.")
  } finally {
    deleting.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'Sin registrar'
  const d = new Date(dateStr)
  // Fix timezone issue when displaying date
  const localDate = new Date(d.getTime() + d.getTimezoneOffset() * 60000)
  return localDate.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

const truncateText = (text) => {
  if (!text) return 'Sin antecedentes'
  if (text.length <= 40) return text
  return text.substring(0, 40) + '...'
}

onMounted(() => {
  fetchPatients()
})
</script>

<style scoped>
.crud-container {
  width: 100%;
  max-width: 1100px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header */
.crud-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.crud-header h2 {
  margin: 0 0 0.25rem 0;
  color: #0f172a;
  font-weight: 800;
  font-size: 1.6rem;
}
.crud-header p {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
}

/* Filter Section */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
}
.search-box {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.6rem 1rem;
  gap: 0.75rem;
  flex: 1;
  max-width: 450px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.01);
}
.search-icon {
  color: #94a3b8;
  font-size: 0.95rem;
}
.search-input {
  border: none;
  outline: none;
  width: 100%;
  font-size: 0.9rem;
  color: #1e293b;
}

/* Buttons */
.btn {
  padding: 0.65rem 1.25rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.btn-primary {
  background-color: #004e98;
  color: white;
}
.btn-primary:hover {
  background-color: #003a70;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-secondary {
  background-color: white;
  border-color: #e2e8f0;
  color: #475569;
}
.btn-secondary:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}
.btn-danger {
  background-color: #ef4444;
  color: white;
}
.btn-danger:hover {
  background-color: #dc2626;
}

/* Table */
.table-container {
  background: white;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  overflow: hidden;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.data-table th {
  background-color: #f8fafc;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}
.data-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.9rem;
  color: #334155;
  vertical-align: middle;
}
.data-table tr:last-child td {
  border-bottom: none;
}
.id-cell {
  font-weight: 700;
  color: #64748b;
}
.name-cell {
  font-weight: 700;
  color: #0f172a;
}
.bio-cell {
  color: #64748b;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.actions-column {
  text-align: right;
}
.actions-cell {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
.btn-action {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  transition: all 0.15s ease;
}
.edit-btn {
  color: #0284c7;
  background: #e0f2fe;
}
.edit-btn:hover {
  background: #bae6fd;
}
.delete-btn {
  color: #ef4444;
  background: #fef2f2;
}
.delete-btn:hover {
  background: #fee2e2;
}

/* Loading & Empty States */
.loading-state, .empty-state {
  padding: 4rem 2rem;
  text-align: center;
  color: #64748b;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f1f5f9;
  border-top: 3px solid #004e98;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Slide-over Drawer */
.drawer-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(15, 23, 42, 0.4);
  z-index: 2000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  display: flex;
  justify-content: flex-end;
}
.drawer-backdrop.show {
  opacity: 1;
  visibility: visible;
}
.drawer-content {
  width: 460px;
  background: white;
  height: 100%;
  box-shadow: -10px 0 30px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-content.open {
  transform: translateX(0);
}
.drawer-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.drawer-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: #94a3b8;
  line-height: 1;
}
.close-btn:hover {
  color: #0f172a;
}
.drawer-form {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}
.divider-form {
  height: 1px;
  background-color: #e2e8f0;
  margin: 0.5rem 0;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.form-group label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
}
.form-input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #0f172a;
  outline: none;
  font-family: inherit;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #004e98;
  box-shadow: 0 0 0 3px rgba(0, 78, 152, 0.1);
}
.form-textarea {
  resize: vertical;
  min-height: 120px;
}
.drawer-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2100;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  max-width: 480px;
  width: 90%;
  text-align: left;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
.modal-content h3 { margin-top: 0; font-size: 1.25rem; color: #0f172a; font-weight: 800; }
.modal-content p { color: #64748b; line-height: 1.5; margin-bottom: 2rem; font-size: 0.9rem; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; }
</style>
