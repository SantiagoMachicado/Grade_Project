<template>
  <div class="placeholder-container">
    <div class="header-section">
      <div class="title-with-icon">
        <span class="view-icon">👥</span>
        <h2>Lista de Pacientes</h2>
      </div>
      <p class="subtitle">Directorio de pacientes asignados a tu cuenta y sus historiales.</p>
    </div>

    <div class="placeholder-content glass-card">
      <div class="empty-state">
        <div class="empty-icon">🗂️</div>
        <h3>Directorio Próximamente</h3>
        <p>En este módulo podrás revisar diagnósticos, tratamientos e historial clínico de forma centralizada.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.placeholder-container { max-width: 900px; }
.header-section { margin-bottom: 2rem; }
.title-with-icon { display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem; }
.title-with-icon h2 { margin: 0; color: var(--text-main); font-size: 1.8rem; }
.view-icon { font-size: 2rem; }
.subtitle { color: var(--text-muted); margin: 0; }
.placeholder-content { display: flex; justify-content: center; padding: 4rem 2rem; max-width: 100%; }
.empty-state { text-align: center; max-width: 400px; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; opacity: 0.7; }
.empty-state h3 { color: var(--text-main); margin-bottom: 0.5rem; }
.empty-state p { color: var(--text-muted); line-height: 1.5; }
</style>
