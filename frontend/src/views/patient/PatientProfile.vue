<template>
  <div class="profile-container">
    <div class="header-section">
      <div class="title-with-icon">
        <span class="view-icon">👤</span>
        <h2>Mi Perfil Médico</h2>
      </div>
      <p class="subtitle">Tus datos personales e información vital para la atención de calidad.</p>
    </div>

    <div class="placeholder-content glass-card">
      <div class="empty-state">
        <div class="empty-icon">🚧</div>
        <h3>Módulo en construcción</h3>
        <p>Próximamente podrás editar tus datos médicos y personales desde este panel.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 900px;
}
.header-section {
  margin-bottom: 2rem;
}
.title-with-icon {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0.5rem;
}
.title-with-icon h2 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.8rem;
}
.view-icon {
  font-size: 2rem;
}
.subtitle {
  color: var(--text-muted);
  margin: 0;
}
.placeholder-content {
  display: flex;
  justify-content: center;
  padding: 4rem 2rem;
  max-width: 100%;
}
.empty-state {
  text-align: center;
  max-width: 400px;
}
.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}
.empty-state h3 {
  color: var(--text-main);
  margin-bottom: 0.5rem;
}
.empty-state p {
  color: var(--text-muted);
  line-height: 1.5;
}
</style>
