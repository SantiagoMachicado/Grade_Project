<template>
  <div class="sub-settings-page">
    <div class="header">
      <button class="back-btn" @click="$router.push('/doctor/settings')">
        <span class="back-arrow">←</span> Datos de la Clínica
      </button>
    </div>
    <div class="content glass-card">
      <p>Formulario para gestionar los datos y horarios de las clínicas asociadas.</p>
    </div>
  </div>
</template>

<style scoped>
.sub-settings-page { max-width: 600px; margin: 0 auto; padding-bottom: 2rem; }
.header { margin-bottom: 1.5rem; padding: 0.5rem 0; }
.back-btn { background: none; border: none; font-size: 1.25rem; font-weight: 700; color: #0f172a; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; padding: 0; }
.back-arrow { color: #004e98; font-size: 1.4rem; }
.content { padding: 2rem; background: white; border-radius: 16px; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
</style>
