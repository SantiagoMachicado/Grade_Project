<template>
  <div class="glass-card">
    <div class="text-center">
      <h2 class="title">Iniciar Sesión</h2>
      <p class="subtitle">Bienvenido de nuevo al portal de salud</p>
    </div>

    <form @submit.prevent="handleLogin" class="mt-4">
      <div v-if="errorMessage" class="error-msg">
        {{ errorMessage }}
      </div>

      <div class="form-group">
        <label>Correo Electrónico</label>
        <input v-model="email" type="email" placeholder="ejemplo@email.com" required />
      </div>

      <div class="form-group">
        <label>Contraseña</label>
        <input v-model="password" type="password" placeholder="••••••••" required />
      </div>

      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Ingresando...' : 'Iniciar Sesión' }}
      </button>
    </form>

    <div class="footer-links">
      <p>¿No tienes una cuenta? <RouterLink to="/register" class="link-text">Regístrate aquí</RouterLink></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const response = await axios.post('http://localhost:8000/api/v1/auth/login', formData)
    const token = response.data.access_token
    
    // Almacenamos el token
    localStorage.setItem('access_token', token)
    
    // Decodificar el token para saber si es paciente o doctor
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    const payload = JSON.parse(jsonPayload);

    // Redirección según rol
    if (payload.role === 'medico') {
      router.push('/doctor/dashboard')
    } else if (payload.role === 'admin') {
      router.push('/admin-dashboard')
    } else {
      // Por defecto o paciente
      router.push('/patient/dashboard')
    }
    
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value = 'Correo o contraseña incorrectos. Intenta nuevamente.'
    } else {
      errorMessage.value = 'Ocurrió un error al intentar conectarse al servidor.'
    }
    console.error(error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
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
</style>
