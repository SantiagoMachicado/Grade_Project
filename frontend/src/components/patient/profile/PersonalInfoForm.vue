<template>
  <div class="edit-view">
    <div class="top-header">
      <button class="icon-btn" @click="emit('back')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <h2 class="header-title">Información Personal</h2>
      <div style="width: 24px;"></div>
    </div>

    <div class="edit-form glass-card">
      <div class="form-group">
        <label>Nombre Completo</label>
        <input type="text" v-model="editForm.full_name" class="form-input" />
      </div>
      
      <div class="form-group">
        <label>Teléfono</label>
        <input type="tel" v-model="editForm.phone" class="form-input" />
      </div>

      <div class="form-group">
        <label>Fecha de Nacimiento</label>
        <input type="date" v-model="editForm.birth_date" class="form-input" />
      </div>

      <button class="btn btn-primary full-width" @click="saveProfile" :disabled="saving">
        {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  patient: Object
})

const emit = defineEmits(['back', 'update'])
const saving = ref(false)

const editForm = ref({
  full_name: '',
  phone: '',
  birth_date: '',
  medical_history: ''
})

const initForm = () => {
  if (props.patient) {
    editForm.value = {
      full_name: props.patient.full_name || '',
      phone: props.patient.phone || '',
      birth_date: props.patient.birth_date || '',
      medical_history: props.patient.medical_history || ''
    }
  }
}

watch(() => props.patient, initForm, { deep: true })
onMounted(initForm)

const saveProfile = async () => {
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    
    await axios.put(`http://localhost:8000/api/v1/patients/${payload.id}`, editForm.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    emit('update')
    emit('back')
  } catch (err) {
    console.error("Error guardando perfil", err)
    alert("Hubo un error al guardar los cambios.")
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; }
.icon-btn { background: none; border: none; color: #1e40af; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #eff6ff; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

.edit-view { padding-bottom: 2rem; }
.edit-form { margin: 1rem; padding: 1.5rem 2rem; background: white; border-radius: 16px; box-sizing: border-box; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #64748b; margin-bottom: 0.5rem; text-align: left; }
.form-input { width: 100%; padding: 0.75rem 1rem; border: 1px solid #e2e8f0; border-radius: 10px; font-family: inherit; font-size: 0.95rem; color: #1e293b; background: #ffffff; transition: all 0.2s; box-sizing: border-box; text-align: left; }
.form-input:focus { outline: none; border-color: #0284c7; box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1); }
.full-width { width: 100%; margin-top: 1rem; padding: 1rem; font-size: 1rem; box-sizing: border-box; }
.btn { border-radius: 10px; font-weight: 700; cursor: pointer; border: none; transition: all 0.2s ease; box-sizing: border-box; }
.btn-primary { background: #0284c7; color: white; }
.btn-primary:hover { background: #0369a1; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
