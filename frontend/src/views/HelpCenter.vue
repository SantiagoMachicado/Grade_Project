<template>
  <div class="responsive-help-container">
    
    <!-- Header -->
    <div class="top-header">
      <button class="icon-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <h2 class="header-title">Centro de Ayuda</h2>
      <div style="width: 24px"></div> <!-- Placeholder for centering -->
    </div>

    <!-- Search Hero -->
    <div class="search-hero">
      <h2>¿En qué te podemos ayudar?</h2>
      <div class="search-bar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input type="text" placeholder="Busca problemas, guías, etc..." disabled />
      </div>
    </div>

    <div class="help-content">
      
      <div class="help-grid">
        
        <!-- Left Column: FAQ -->
        <div class="grid-col-left">
          <section class="faq-section">
            <h3 class="section-title">Preguntas Frecuentes</h3>
            
            <div class="faq-category">
              <h4>Para Pacientes</h4>
              <div class="accordion">
                <div 
                  v-for="(faq, index) in patientFaqs" 
                  :key="'p'+index"
                  class="accordion-item"
                  :class="{ active: activeFaq === 'p'+index }"
                >
                  <div class="accordion-header" @click="toggleFaq('p'+index)">
                    <span class="faq-question">{{ faq.question }}</span>
                    <span class="faq-icon">
                      <svg v-if="activeFaq === 'p'+index" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg>
                      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    </span>
                  </div>
                  <div class="accordion-body" v-show="activeFaq === 'p'+index">
                    <p>{{ faq.answer }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="faq-category">
              <h4>Para Médicos</h4>
              <div class="accordion">
                <div 
                  v-for="(faq, index) in doctorFaqs" 
                  :key="'d'+index"
                  class="accordion-item"
                  :class="{ active: activeFaq === 'd'+index }"
                >
                  <div class="accordion-header" @click="toggleFaq('d'+index)">
                    <span class="faq-question">{{ faq.question }}</span>
                    <span class="faq-icon">
                      <svg v-if="activeFaq === 'd'+index" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg>
                      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    </span>
                  </div>
                  <div class="accordion-body" v-show="activeFaq === 'd'+index">
                    <p>{{ faq.answer }}</p>
                  </div>
                </div>
              </div>
            </div>

          </section>
        </div>

        <!-- Right Column: Support & Links -->
        <div class="grid-col-right">
          
          <section class="support-section">
            <h3 class="section-title">Soporte Directo</h3>
            
            <div class="support-cards">
              
              <div class="support-card whatsapp">
                <div class="support-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                </div>
                <div class="support-text">
                  <h4>Chat por WhatsApp</h4>
                  <p>Lunes a Viernes, 8:00 a 18:00 hrs.</p>
                </div>
                <button class="btn btn-whatsapp">Contactar</button>
              </div>

              <div class="support-card email">
                <div class="support-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                </div>
                <div class="support-text">
                  <h4>Correo Electrónico</h4>
                  <p>soporte@hospitalconnect.com</p>
                </div>
                <button class="btn btn-secondary">Enviar Mensaje</button>
              </div>

              <div class="support-card phone">
                <div class="support-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                </div>
                <div class="support-text">
                  <h4>Línea Gratuita</h4>
                  <p>Emergencias técnicas 24/7</p>
                  <h4 class="phone-number">0800-123-4567</h4>
                </div>
              </div>

            </div>
          </section>

          <section class="legal-section">
            <h3 class="section-title">Legal y Privacidad</h3>
            <div class="legal-links">
              <a href="#">Términos y Condiciones de Uso</a>
              <a href="#">Políticas de Privacidad</a>
              <a href="#">Tratamiento de Datos Médicos</a>
            </div>
          </section>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeFaq = ref(null)

const toggleFaq = (id) => {
  if (activeFaq.value === id) {
    activeFaq.value = null
  } else {
    activeFaq.value = id
  }
}

const patientFaqs = [
  {
    question: '¿Cómo agendar una nueva cita médica?',
    answer: 'Dirígete a la sección "Agendar Cita" desde el menú principal. Selecciona la clínica, luego al especialista de tu preferencia y elige el horario disponible que más te convenga. Finalmente confirma tu solicitud.'
  },
  {
    question: '¿Qué pasa si necesito cancelar mi cita?',
    answer: 'Puedes cancelar tu cita desde "Mis Citas". Selecciona la cita pendiente y presiona el botón rojo "Cancelar". Te recomendamos hacerlo con al menos 24 horas de anticipación.'
  },
  {
    question: '¿Cómo puedo ver el diagnóstico que dejó el doctor?',
    answer: 'Una vez finalizada la consulta, ve al historial en "Mis Citas". Al abrir el detalle de una cita "Completada", verás las notas y el reporte médico en la sección de diagnóstico.'
  }
]

const doctorFaqs = [
  {
    question: '¿Cómo marco a un paciente como ausente?',
    answer: 'Desde tu Agenda o tu lista de Pacientes de hoy, abre los detalles de la cita confirmada. Allí encontrarás el botón rojo "Ausente" para notificar que el paciente no se presentó.'
  },
  {
    question: '¿Dónde registro el reporte médico?',
    answer: 'Al seleccionar la cita de un paciente (ya sea desde la Agenda o "Mis Pacientes"), verás un área de texto para ingresar tu diagnóstico. Luego presiona "Finalizar Cita" para guardarlo definitivamente.'
  },
  {
    question: '¿Cómo actualizo los datos de mi perfil?',
    answer: 'Ve a la sección "Ajustes" > "Información Personal" para modificar tu nombre o biografía. Los datos profesionales (como especialidad y tarifa) deben ser gestionados por el administrador de la clínica.'
  }
]
</script>

<style scoped>
/* Responsive Container matching the general portal style */
.responsive-help-container {
  max-width: 1000px;
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

/* Header */
.top-header { 
  display: flex; align-items: center; justify-content: space-between; 
  padding: 1.5rem 2rem; background: white; border-bottom: 1px solid #f1f5f9; 
}
.icon-btn { 
  background: none; border: none; color: #64748b; cursor: pointer; 
  display: flex; align-items: center; justify-content: center; 
  padding: 0.5rem; border-radius: 50%; transition: background 0.2s, color 0.2s; 
  margin-left: -0.5rem;
}
.icon-btn:hover { background: #f1f5f9; color: #1e293b; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

/* Search Hero */
.search-hero {
  background: linear-gradient(135deg, #0284c7 0%, #004e98 100%);
  padding: 3rem 2rem;
  text-align: center;
  color: white;
}
.search-hero h2 { margin: 0 0 1.5rem 0; font-size: 1.8rem; font-weight: 800; }

.search-bar {
  max-width: 500px;
  margin: 0 auto;
  background: white;
  border-radius: 50px;
  display: flex;
  align-items: center;
  padding: 0.5rem 1.5rem;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.search-bar svg { color: #94a3b8; }
.search-bar input {
  flex: 1; border: none; outline: none; padding: 0.8rem 1rem;
  font-size: 1rem; font-family: inherit; color: #1e293b; background: transparent;
}
.search-bar input::placeholder { color: #94a3b8; }

/* Layout Content */
.help-content { padding: 1.5rem; }

/* RESPONSIVE GRID */
.help-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 860px) {
  .help-content { padding: 2.5rem; }
  .help-grid { grid-template-columns: 1.2fr 0.8fr; gap: 3rem; }
}

.section-title { margin: 0 0 1.25rem 0; font-size: 1rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

/* FAQ Accordion */
.faq-category { margin-bottom: 2rem; }
.faq-category h4 { margin: 0 0 1rem 0.5rem; color: #0284c7; font-size: 1.1rem; font-weight: 700; }

.accordion { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); overflow: hidden; border: 1px solid #f1f5f9; }
.accordion-item { border-bottom: 1px solid #f1f5f9; }
.accordion-item:last-child { border-bottom: none; }

.accordion-header {
  padding: 1.25rem 1.5rem; display: flex; justify-content: space-between; align-items: center;
  cursor: pointer; background: white; transition: background 0.2s;
}
.accordion-header:hover { background: #f8fafc; }
.faq-question { font-weight: 600; color: #1e293b; font-size: 0.95rem; line-height: 1.4; padding-right: 1rem; }
.faq-icon { color: #94a3b8; display: flex; align-items: center; }

.accordion-item.active .faq-question { color: #0284c7; }
.accordion-item.active .faq-icon { color: #0284c7; }

.accordion-body { padding: 0 1.5rem 1.25rem 1.5rem; background: white; }
.accordion-body p { margin: 0; color: #64748b; font-size: 0.9rem; line-height: 1.6; }

/* Support Cards */
.support-section { margin-bottom: 2rem; }
.support-cards { display: flex; flex-direction: column; gap: 1rem; }

.support-card {
  background: white; border-radius: 16px; padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #f1f5f9;
  display: flex; flex-direction: column; gap: 1rem;
}
.support-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.support-text h4 { margin: 0 0 0.2rem 0; color: #1e293b; font-size: 1.05rem; }
.support-text p { margin: 0; color: #64748b; font-size: 0.85rem; }
.phone-number { margin: 0.5rem 0 0 0 !important; color: #0284c7 !important; font-size: 1.3rem !important; font-weight: 800; }

.support-card.whatsapp .support-icon { background: #dcfce7; color: #16a34a; }
.support-card.email .support-icon { background: #e0f2fe; color: #0284c7; }
.support-card.phone .support-icon { background: #fef3c7; color: #d97706; }

.btn { padding: 0.8rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer; border: none; transition: 0.2s; font-size: 0.9rem; width: 100%; text-align: center; }
.btn-whatsapp { background: #16a34a; color: white; }
.btn-whatsapp:hover { background: #15803d; }
.btn-secondary { background: #f1f5f9; color: #1e293b; }
.btn-secondary:hover { background: #e2e8f0; }

/* Legal Links */
.legal-section { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }
.legal-links { display: flex; flex-direction: column; gap: 0.75rem; }
.legal-links a { color: #64748b; text-decoration: none; font-size: 0.9rem; transition: color 0.2s; font-weight: 500; }
.legal-links a:hover { color: #0284c7; text-decoration: underline; }

</style>
