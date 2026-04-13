<template>
  <div class="dashboard-wrap">
    <div class="welcome-banner admin-banner">
      <h2>Panel Administrativo</h2>
      <p>Bienvenido. Control total sobre usuarios, pacientes y especialistas.</p>
    </div>

    <div class="dashboard-content">
      <div class="stats-card">
        <h3>Total Usuarios</h3>
        <p class="stat-number">25</p>
      </div>
      <div class="stats-card">
        <h3>Especialistas Activos</h3>
        <p class="stat-number">4</p>
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
.admin-banner {
  background: linear-gradient(135deg, #111827, #374151);
  box-shadow: 0 10px 15px -3px rgba(17, 24, 39, 0.3);
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
  color: #EF4444;
  margin: 0;
}
</style>
