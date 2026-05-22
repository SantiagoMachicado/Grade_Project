import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientLayout from '../views/patient/PatientLayout.vue'
import PatientHome from '../views/patient/PatientHome.vue'
import PatientAppointments from '../views/patient/PatientAppointments.vue'
import PatientProfile from '../views/patient/PatientProfile.vue'
import DoctorLayout from '../views/doctor/DoctorLayout.vue'
import DoctorHome from '../views/doctor/DoctorHome.vue'
import DoctorAgenda from '../views/doctor/DoctorAgenda.vue'
import DoctorPatients from '../views/doctor/DoctorPatients.vue'
import DoctorReports from '../views/doctor/DoctorReports.vue'
import DoctorSettings from '../views/doctor/DoctorSettings.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import AdminHome from '../views/admin/AdminHome.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/patient',
      component: PatientLayout,
      meta: { requiresAuth: true, role: 'paciente' },
      children: [
        { path: 'dashboard', name: 'patient-dashboard', component: PatientHome },
        { path: 'appointments', name: 'patient-appointments', component: PatientAppointments },
        { path: 'appointments/new', name: 'patient-new-appointment', component: () => import('../views/patient/PatientDoctorSelection.vue') },
        { path: 'appointments/new/:assignmentId', name: 'patient-schedule-selection', component: () => import('../views/patient/PatientScheduleSelection.vue') },
        { path: 'profile', name: 'patient-profile', component: PatientProfile }
      ]
    },
    {
      path: '/doctor',
      component: DoctorLayout,
      meta: { requiresAuth: true, role: 'medico' },
      children: [
        { path: 'dashboard', name: 'doctor-dashboard', component: DoctorHome },
        { path: 'agenda', name: 'doctor-agenda', component: DoctorAgenda },
        { path: 'patients', name: 'doctor-patients', component: DoctorPatients },
        { path: 'reports', name: 'doctor-reports', component: DoctorReports },
        { path: 'settings', name: 'doctor-settings', component: DoctorSettings },
        { path: 'settings/personal', name: 'doctor-settings-personal', component: () => import('../views/doctor/settings/DoctorPersonalInfo.vue') },
        { path: 'settings/clinic', name: 'doctor-settings-clinic', component: () => import('../views/doctor/settings/DoctorClinicInfo.vue') },
        { path: 'settings/schedules', name: 'doctor-settings-schedules', component: () => import('../views/doctor/settings/DoctorSchedules.vue') },
        { path: 'settings/notifications', name: 'doctor-settings-notifications', component: () => import('../views/doctor/settings/DoctorNotifications.vue') },
        { path: 'settings/about', name: 'doctor-settings-about', component: () => import('../views/doctor/settings/DoctorAbout.vue') }
      ]
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        { path: 'dashboard', name: 'admin-dashboard', component: AdminHome }
      ]
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatView,
      meta: { requiresAuth: true }
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('../views/ClinicsMapView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/help-center',
      name: 'help-center',
      component: () => import('../views/HelpCenter.vue')
    }
  ]
})

// Simple Route Guard to protect auth routes and role-based redirects
router.beforeEach((to, from) => {
  let token = localStorage.getItem('access_token')
  let userRole = null

  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      userRole = payload.role
      
      // Check if token is expired
      const currentTime = Math.floor(Date.now() / 1000)
      if (payload.exp && payload.exp < currentTime) {
        throw new Error('Token expired')
      }
    } catch (e) {
      console.error('Invalid or expired token payload')
      localStorage.removeItem('access_token')
      token = null
      userRole = null
    }
  }

  if (to.meta.requiresAuth && !token) {
    return '/login'
  } else if (to.meta.requiresAuth && to.meta.role && to.meta.role !== userRole) {
    // If they go to wrong dashboard based on role, send them back to login
    return '/login'
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    // If logged in already, send to correct dashboard
    if (userRole === 'paciente') return '/patient/dashboard'
    else if (userRole === 'medico') return '/doctor/dashboard'
    else if (userRole === 'admin') return '/admin/dashboard'
    else {
      localStorage.removeItem('access_token')
      return '/login'
    }
  }
  
  return true
})

export default router
