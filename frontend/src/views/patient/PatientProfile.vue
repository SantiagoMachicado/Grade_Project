<template>
  <div class="profile-container">
    <ProfileMenu 
      v-if="activeView === 'menu'" 
      :patient="patient" 
      :loading="loading"
      @navigate="activeView = $event" 
      @logout="handleLogout" 
      @back="goBack"
    />
    
    <PersonalInfoForm 
      v-else-if="activeView === 'personal_info'" 
      :patient="patient" 
      @back="activeView = 'menu'" 
      @update="fetchProfile" 
    />
    
    <MedicalHistory 
      v-else-if="activeView === 'medical_history'" 
      @back="activeView = 'menu'" 
      @select-appointment="openAppointmentDetail" 
    />
    
    <AppointmentDetail 
      v-else-if="activeView === 'appointment_detail'" 
      :appointment="selectedAppointment" 
      @back="activeView = 'medical_history'" 
    />

    <Notifications 
      v-else-if="activeView === 'notifications'" 
      @back="activeView = 'menu'" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

import ProfileMenu from '../../components/patient/profile/ProfileMenu.vue'
import PersonalInfoForm from '../../components/patient/profile/PersonalInfoForm.vue'
import MedicalHistory from '../../components/patient/profile/MedicalHistory.vue'
import AppointmentDetail from '../../components/patient/profile/AppointmentDetail.vue'
import Notifications from '../../components/patient/profile/Notifications.vue'

const router = useRouter()
const route = useRoute()
const patient = ref(null)
const loading = ref(true)

const activeView = ref('menu')
const selectedAppointment = ref(null)

const fetchProfile = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const patientId = payload.id
    
    const res = await axios.get(`http://localhost:8000/api/v1/patients/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    patient.value = res.data
  } catch (err) {
    console.error("Error cargando perfil", err)
  } finally {
    loading.value = false
  }
}

const openAppointmentDetail = (appt) => {
  selectedAppointment.value = appt
  activeView.value = 'appointment_detail'
}

const goBack = () => {
  router.back()
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  router.push('/login')
}

onMounted(() => {
  if (route.query.view) {
    activeView.value = route.query.view
  }
  fetchProfile()
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
}
</style>
