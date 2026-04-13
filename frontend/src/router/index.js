import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientDashboard from '../views/PatientDashboard.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
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
      path: '/patient-dashboard',
      name: 'patient-dashboard',
      component: PatientDashboard,
      meta: { requiresAuth: true, role: 'paciente' }
    },
    {
      path: '/doctor-dashboard',
      name: 'doctor-dashboard',
      component: DoctorDashboard,
      meta: { requiresAuth: true, role: 'medico' }
    },
    {
      path: '/admin-dashboard',
      name: 'admin-dashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatView,
      meta: { requiresAuth: true }
    }
  ]
})

// Simple Route Guard to protect auth routes and role-based redirects
router.beforeEach((to, from) => {
  const token = localStorage.getItem('access_token')
  let userRole = null

  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      userRole = payload.role
    } catch (e) {
      console.error('Invalid token payload')
    }
  }

  if (to.meta.requiresAuth && !token) {
    return '/login'
  } else if (to.meta.requiresAuth && to.meta.role && to.meta.role !== userRole) {
    // If they go to wrong dashboard based on role, send them back to login
    return '/login'
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    // If logged in already, send to correct dashboard
    if (userRole === 'paciente') return '/patient-dashboard'
    else if (userRole === 'medico') return '/doctor-dashboard'
    else if (userRole === 'admin') return '/admin-dashboard'
    else return '/'
  }
  
  return true
})

export default router
