<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="brand">Medical Platform</div>
      
      <div class="hero-image">
        <div class="icon-circle">
          <svg viewBox="0 0 24 24" width="40" height="40" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="medical-icon">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            <line x1="12" y1="11" x2="12" y2="17"></line>
            <line x1="9" y1="14" x2="15" y2="14"></line>
          </svg>
        </div>
      </div>

      <h1 class="main-title">Tu salud, a un toque de distancia</h1>
      <p class="subtitle">Gestiona tus citas médicas de forma rápida y segura.</p>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div v-if="errorMessage" class="error-msg">{{ errorMessage }}</div>

        <div class="form-group">
          <label>Correo electrónico</label>
          <input v-model="email" type="email" placeholder="ejemplo@correo.com" required />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <div class="password-input">
            <input :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="Ingrese su contraseña" required />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
              <svg v-else viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
            </button>
          </div>
        </div>

        <div class="forgot-password">
          <a href="#">¿Olvidaste tu contraseña?</a>
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          <span>{{ isLoading ? 'Ingresando...' : 'Entrar' }}</span>
          <svg v-if="!isLoading" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </button>

        <div class="divider">
          <span>O INGRESA CON</span>
        </div>

        <button type="button" class="btn-google">
          <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
          <span>Google</span>
        </button>
      </form>

      <div class="footer-links">
        <span>¿Aún no tienes cuenta?</span> <RouterLink to="/register" class="link-text">Crear cuenta</RouterLink>
      </div>
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
const showPassword = ref(false)
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
    
    localStorage.setItem('access_token', token)
    
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    const payload = JSON.parse(jsonPayload);

    if (payload.role === 'medico') {
      router.push('/doctor/dashboard')
    } else if (payload.role === 'admin') {
      router.push('/admin/dashboard')
    } else {
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.auth-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8fafc;
  font-family: 'Inter', sans-serif;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background-color: #f8fafc; /* Coincide con el fondo para que no se vea como una tarjeta blanca separada si no se quiere, aunque la imagen lo muestra como un contenedor suave */
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brand {
  font-size: 1rem;
  font-weight: 800;
  color: #004e98;
  margin-bottom: 2rem;
}

.hero-image {
  width: 100%;
  height: 180px;
  background-color: #e0f2fe;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}

.icon-circle {
  width: 80px;
  height: 80px;
  background-color: #dbeafe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.medical-icon {
  color: #004e98;
}

.main-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  text-align: center;
  margin: 0 0 0.75rem 0;
  line-height: 1.2;
}

.subtitle {
  color: #64748b;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.auth-form {
  width: 100%;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.85rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input::placeholder {
  color: #94a3b8;
}

.form-group input:focus {
  border-color: #004e98;
}

.password-input {
  position: relative;
  display: flex;
  align-items: center;
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  display: flex;
}

.forgot-password {
  text-align: right;
  margin-bottom: 1.5rem;
}

.forgot-password a {
  font-size: 0.8rem;
  font-weight: 600;
  color: #004e98;
  text-decoration: none;
}

.btn-primary {
  width: 100%;
  background-color: #004e98;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #003a70;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 2rem 0;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e2e8f0;
}

.divider span {
  padding: 0 1rem;
}

.btn-google {
  width: 100%;
  background-color: white;
  border: 1px solid #e2e8f0;
  padding: 0.85rem;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
  margin-bottom: 2rem;
}

.btn-google:hover {
  background-color: #f8fafc;
}

.footer-links {
  text-align: center;
  font-size: 0.9rem;
  color: #64748b;
}

.link-text {
  color: #004e98;
  font-weight: 700;
  text-decoration: none;
}

.error-msg {
  background-color: #fef2f2;
  color: #ef4444;
  padding: 0.75rem;
  border-radius: 10px;
  margin-bottom: 1.5rem;
  font-size: 0.85rem;
  text-align: center;
  border: 1px solid #fca5a5;
}
</style>
