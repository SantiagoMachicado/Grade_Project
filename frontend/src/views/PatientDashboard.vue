<template>
  <div class="dashboard-wrap">
    <div class="welcome-banner patient-banner">
      <h2>Mi Portal de Salud</h2>
      <p>Revisa tus citas, historial médico y encuentra especialistas.</p>
    </div>

    <div class="dashboard-content">
      <div class="stats-card">
        <h3>Mis Citas</h3>
        <p class="stat-number">1</p>
        <button class="action-btn">Agendar Nueva Cita</button>
      </div>
      <div class="stats-card">
        <h3>Recetas Recientes</h3>
        <p class="stat-number">0</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrap {
  width: 100%;
  max-width: 900px;
}
.welcome-banner {
  padding: 2rem;
  border-radius: 12px;
  color: white;
  margin-bottom: 2rem;
}
.patient-banner {
  background: linear-gradient(135deg, #4F46E5, #3730A3);
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}
.welcome-banner h2 { margin-top: 0; }
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.stats-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.stat-number {
  font-size: 3rem;
  font-weight: 800;
  color: #fb923c;
  margin: 0.5rem 0;
}
.action-btn {
  margin-top: 1rem;
  background-color: transparent;
  border: 2px solid var(--primary-color);
  color: var(--primary-color);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.action-btn:hover {
  background-color: var(--primary-color);
  color: white;
}
</style>
