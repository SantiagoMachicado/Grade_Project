<template>
  <div class="profile-container">
    <div class="menu-view">
      <div class="top-header">
        <div style="width: 24px"></div>
        <h2 class="header-title">Informes de Gestión</h2>
        <div style="width: 24px"></div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else-if="stats" class="menu-section">
        
        <!-- Patient Acquisition Growth -->
        <div class="chart-card">
          <div class="chart-header">
            <h4>Crecimiento de Pacientes</h4>
            <div class="main-metric">
              <h2>{{ stats.total_active_patients.toLocaleString() }}</h2>
              <span class="metric-label">Activos</span>
            </div>
          </div>
          <div class="chart-container">
            <Line :data="patientChartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Monthly Revenue Distribution -->
        <div class="chart-card">
          <div class="chart-header">
            <h4>Ingresos Promedio</h4>
            <div class="main-metric">
              <h2>Bs. {{ stats.avg_revenue.toLocaleString() }}</h2>
              <span class="metric-trend positive">avg +{{ stats.revenue_growth }}%</span>
            </div>
          </div>
          <div class="chart-container">
            <Line :data="revenueChartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Appointment Success Breakdown -->
        <div class="chart-card success-breakdown">
          <h4>Desglose de Citas</h4>
          
          <div class="progress-item">
            <div class="progress-labels">
              <span>Completadas</span>
              <strong>{{ stats.breakdown.completed_pct }}%</strong>
            </div>
            <div class="progress-track">
              <div class="progress-fill completed" :style="{ width: stats.breakdown.completed_pct + '%' }"></div>
            </div>
          </div>

          <div class="progress-item">
            <div class="progress-labels">
              <span>Canceladas</span>
              <strong>{{ stats.breakdown.cancelled_pct }}%</strong>
            </div>
            <div class="progress-track">
              <div class="progress-fill cancelled" :style="{ width: stats.breakdown.cancelled_pct + '%' }"></div>
            </div>
          </div>

          <div class="progress-item">
            <div class="progress-labels">
              <span>Ausentes</span>
              <strong>{{ stats.breakdown.absent_pct }}%</strong>
            </div>
            <div class="progress-track">
              <div class="progress-fill absent" :style="{ width: stats.breakdown.absent_pct + '%' }"></div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler
)

const loading = ref(true)
const stats = ref(null)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 10,
      cornerRadius: 8,
      displayColors: false
    }
  },
  scales: {
    y: { display: false, min: 0 },
    x: { 
      grid: { display: false, drawBorder: false },
      ticks: { color: '#94a3b8', font: { size: 10, weight: 'bold' } }
    }
  },
  elements: {
    line: { tension: 0.4 }
  }
}

const patientChartData = computed(() => {
  if (!stats.value) return { labels: [], datasets: [] }
  const data = stats.value.chart_data
  return {
    labels: data.map(d => d.month),
    datasets: [{
      data: data.map(d => d.patients),
      borderColor: '#0284c7',
      borderWidth: 3,
      backgroundColor: (context) => {
        const ctx = context.chart.ctx;
        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
        gradient.addColorStop(0, 'rgba(2, 132, 199, 0.2)');
        gradient.addColorStop(1, 'rgba(2, 132, 199, 0)');
        return gradient;
      },
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 6
    }]
  }
})

const revenueChartData = computed(() => {
  if (!stats.value) return { labels: [], datasets: [] }
  const data = stats.value.chart_data
  return {
    labels: data.map(d => d.month),
    datasets: [{
      data: data.map(d => d.revenue),
      borderColor: '#004e98',
      borderWidth: 3,
      backgroundColor: (context) => {
        const ctx = context.chart.ctx;
        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
        gradient.addColorStop(0, 'rgba(0, 78, 152, 0.2)');
        gradient.addColorStop(1, 'rgba(0, 78, 152, 0)');
        return gradient;
      },
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 6
    }]
  }
})

const fetchStats = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const payload = JSON.parse(decodeURIComponent(atob(token.split('.')[1]).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')))
    const doctorId = payload.id
    
    const response = await axios.get(`http://localhost:8000/api/v1/appointments/doctor/${doctorId}/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    stats.value = response.data
  } catch (error) {
    console.error("Error fetching stats", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
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
.top-header { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: white; border-bottom: 1px solid #f1f5f9; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.menu-section { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }

.loading-state { text-align: center; padding: 4rem 0; color: #94a3b8; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top: 4px solid #0284c7; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.chart-header { margin-bottom: 1rem; }
.chart-header h4 { margin: 0 0 0.5rem 0; color: #64748b; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; }
.main-metric { display: flex; align-items: baseline; gap: 0.5rem; }
.main-metric h2 { margin: 0; font-size: 1.8rem; color: #0f172a; font-weight: 800; }
.metric-label { color: #64748b; font-size: 0.85rem; font-weight: 600; }
.metric-trend.positive { color: #10b981; font-size: 0.85rem; font-weight: 700; }

.chart-container {
  height: 180px;
  position: relative;
  margin-top: 1rem;
}

/* Success Breakdown Bars */
.success-breakdown h4 {
  margin: 0 0 1.5rem 0; color: #64748b; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
}

.progress-item {
  margin-bottom: 1.2rem;
}
.progress-item:last-child { margin-bottom: 0; }

.progress-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #475569;
  font-weight: 500;
}
.progress-labels strong { color: #0f172a; font-weight: 800; }

.progress-track {
  width: 100%;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease-out;
}

.progress-fill.completed { background: #0284c7; }
.progress-fill.cancelled { background: #f59e0b; }
.progress-fill.absent { background: #ef4444; }
</style>
