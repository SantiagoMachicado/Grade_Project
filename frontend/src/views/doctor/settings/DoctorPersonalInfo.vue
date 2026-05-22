<template>
  <div class="profile-container">
    <div class="menu-view">
      <div class="top-header">
        <button class="icon-btn" @click="$router.push('/doctor/settings')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h2 class="header-title">Información Personal</h2>
        <div style="width: 24px"></div> <!-- Placeholder -->
      </div>

      <div class="menu-section">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando datos...</p>
        </div>

        <form v-else @submit.prevent="savePersonalInfo" class="settings-form">
          
          <div class="form-group">
            <label>Nombre Completo</label>
            <input 
              type="text" 
              v-model="form.full_name" 
              placeholder="Ej. Dr. Juan Pérez" 
              required
            />
          </div>

          <div class="form-group">
            <label>Correo Electrónico (Solo Lectura)</label>
            <input 
              type="email" 
              v-model="form.email" 
              disabled 
              class="disabled-input"
            />
          </div>

          <div class="form-group">
            <label>Acerca de mí (Biografía)</label>
            <textarea 
              v-model="form.bio" 
              placeholder="Breve descripción de tu trayectoria, experiencia, etc."
              rows="4"
            ></textarea>
            <small class="hint">Esta información podría ser visible para los pacientes al reservar.</small>
          </div>

          <div v-if="successMessage" class="success-msg">
            {{ successMessage }}
          </div>
          <div v-if="errorMessage" class="error-msg">
            {{ errorMessage }}
          </div>

          <div class="action-footer">
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const form = reactive({
  full_name: '',
  email: '',
  bio: ''
})

const fetchDoctorData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    const res = await axios.get(`http://localhost:8000/api/v1/doctors/${doctorId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    form.full_name = res.data.full_name || ''
    form.email = res.data.user?.email || ''
    form.bio = res.data.bio || ''
  } catch (error) {
    console.error("Error fetching doctor info:", error)
    errorMessage.value = "Error al cargar la información."
  } finally {
    loading.value = false
  }
}

const savePersonalInfo = async () => {
  saving.value = true
  successMessage.value = ''
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('access_token')
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    // El backend espera UserUpdate, solo enviamos los campos permitidos y modificados
    const updateData = {
      full_name: form.full_name,
      bio: form.bio
    }

    await axios.put(`http://localhost:8000/api/v1/doctors/${doctorId}`, updateData, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    successMessage.value = "Información actualizada correctamente."
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error("Error updating info:", error)
    errorMessage.value = "Hubo un problema al guardar los cambios."
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchDoctorData()
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

.menu-view {
  width: 100%;
}

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

.settings-form {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { font-size: 0.85rem; font-weight: 600; color: #475569; }

.form-group input, 
.form-group textarea {
  padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-family: inherit;
  font-size: 0.95rem;
  color: #1e293b;
  outline: none;
  transition: border-color 0.2s;
  background: #ffffff;
}

.form-group input:focus, 
.form-group textarea:focus {
  border-color: #0284c7;
}

.disabled-input {
  background: #f8fafc !important;
  color: #94a3b8 !important;
  cursor: not-allowed;
}

.hint { font-size: 0.75rem; color: #94a3b8; margin-top: 0.2rem; }

.action-footer { margin-top: 1rem; }

.btn-primary {
  width: 100%;
  background: #0284c7;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) { background: #0369a1; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

.success-msg { background: #dcfce7; color: #166534; padding: 0.75rem; border-radius: 8px; font-size: 0.85rem; text-align: center; }
.error-msg { background: #fee2e2; color: #b91c1c; padding: 0.75rem; border-radius: 8px; font-size: 0.85rem; text-align: center; }
</style>
