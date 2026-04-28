<template>
  <div class="auth-wrapper">
    <div class="glass-card">
    <div class="text-center">
      <h2 class="title">Crear Cuenta</h2>
      <p class="subtitle">Únete a nuestra plataforma de salud</p>
    </div>

    <form @submit.prevent="handleRegister" class="mt-4">
      <div v-if="errorMessage" class="error-msg">
        {{ errorMessage }}
      </div>

      <div class="form-group">
        <label>Nombre Completo</label>
        <input v-model="form.full_name" type="text" placeholder="Ej. Juan Pérez" required />
      </div>

      <div class="form-group">
        <label>Correo Electrónico</label>
        <input v-model="form.email" type="email" placeholder="ejemplo@email.com" required />
      </div>

      <div class="form-group">
        <label>Contraseña</label>
        <input v-model="form.password" type="password" placeholder="••••••••" required minlength="8" />
        <small class="hint">Al menos 8 caracteres</small>
      </div>

      <div class="form-group">
        <label>Tipo de Usuario</label>
        <select v-model="form.role" required>
          <option value="paciente">Paciente</option>
          <option value="medico">Médico / Doctor</option>
        </select>
      </div>

      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Registrando...' : 'Registrarme' }}
      </button>
    </form>

    <div class="footer-links">
      <p>¿Ya tienes cuenta? <RouterLink to="/login" class="link-text">Inicia sesión</RouterLink></p>
    </div>
  </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoading = ref(false)
const errorMessage = ref('')

const form = reactive({
  full_name: '',
  email: '',
  password: '',
  role: 'paciente' // Default
})

const handleRegister = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    // Al post de registro de FastAPI le enviamos un JSON según tu esquema "UserCreate"
    const response = await axios.post('http://localhost:8000/api/v1/auth/register', form)
    
    alert('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.')
    router.push('/login')
  } catch (error) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'Ocurrió un error en el servidor.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background-color: var(--bg-color);
}
.title {
  font-size: 1.8rem;
  color: var(--text-main);
  margin-bottom: 0.5rem;
  margin-top: 0;
}
.subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-bottom: 2rem;
}
.text-center {
  text-align: center;
}
.error-msg {
  background-color: #FEE2E2;
  color: var(--danger-color);
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  text-align: center;
  border: 1px solid #FCA5A5;
}
.footer-links {
  margin-top: 2rem;
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-muted);
}
.hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}
</style>
