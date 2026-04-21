<template>
  <div class="dashboard-wrap">
    <div class="welcome-banner doctor-banner">
      <h2>Panel Médico</h2>
      <p>Bienvenido. Aquí puedes gestionar a tus pacientes y citas.</p>
    </div>

    <div class="dashboard-content">
      <div class="stats-card">
        <h3>Próximas Citas</h3>
        <p class="stat-number">3</p>
      </div>
      <div class="stats-card">
        <h3>Pacientes Activos</h3>
        <p class="stat-number">12</p>
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
.doctor-banner {
  background: linear-gradient(135deg, #10B981, #059669);
  box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
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
}
.stat-number {
  font-size: 3rem;
  font-weight: 800;
  color: var(--primary-color);
  margin: 0;
}
</style>
