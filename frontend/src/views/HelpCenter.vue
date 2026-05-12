<template>
  <div class="public-page">
    <div class="header">
      <button class="back-btn" @click="$router.back()">
        <span class="back-arrow">←</span> Volver
      </button>
      <h2>Centro de Ayuda</h2>
    </div>
    <div class="content glass-card">
      <p>Bienvenido al Centro de Ayuda público de Hospital Connect.</p>
      <p>Aquí encontrarás respuestas a preguntas frecuentes y manuales de usuario.</p>
    </div>
  </div>
</template>

<style scoped>
.public-page { max-width: 800px; margin: 0 auto; padding: 2rem 1rem; }
.header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.back-btn { background: none; border: none; font-size: 1rem; font-weight: 600; color: #004e98; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; padding: 0; }
.header h2 { margin: 0; color: #0f172a; }
.content { padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.content p { color: #334155; line-height: 1.6; }
</style>
