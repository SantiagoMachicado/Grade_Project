<template>
  <div class="appointments-container">
    <div class="header-section">
      <div class="title-with-icon">
        <span class="view-icon">📅</span>
        <h2>Gestión de Citas</h2>
      </div>
      <p class="subtitle">Próximamente estaremos habilitando la agenda en línea con nuestros especialistas.</p>
    </div>

    <div class="placeholder-content glass-card">
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No tienes citas programadas</h3>
        <p>Aún estamos construyendo esta funcionalidad para que puedas reservar tus horas médicas a través de este portal fácilmente.</p>
        <button class="btn-primary mt-4" disabled>Agendar Turno (Pronto)</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.appointments-container {
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
.mt-4 {
  margin-top: 1.5rem;
}
.btn-primary:disabled {
  background-color: #9CA3AF;
  cursor: not-allowed;
  transform: none;
}
</style>
