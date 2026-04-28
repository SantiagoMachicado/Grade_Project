<template>
  <div class="standalone-wrapper">
    <div class="chat-container glass-card">
    <div class="chat-header">
      <div class="title-row">
        <button @click="$router.go(-1)" class="back-btn">← Volver</button>
        <h2>Asistente de Salud Virtual</h2>
      </div>
      <p>Consultas y ayuda inteligente (Gemini 2.5 Flash)</p>
    </div>

    <!-- Mensajes -->
    <div class="chat-box" ref="chatBox">
      <div 
        v-for="(msg, index) in localHistory" 
        :key="index"
        :class="['message', msg.role === 'user' ? 'message-user' : 'message-ai']"
      >
        <div class="message-bubble">
          {{ msg.content }}
        </div>
      </div>
      
      <!-- Indicador de carga -->
      <div v-if="isTyping" class="message message-ai">
        <div class="message-bubble typing-indicator">
          <span>.</span><span>.</span><span>.</span>
        </div>
      </div>
    </div>

    <!-- Formulario de Chat -->
    <form @submit.prevent="sendMessage" class="chat-input-area">
      <input 
        v-model="newMessage" 
        type="text" 
        placeholder="Escribe tu consulta médica aquí..." 
        :disabled="isTyping"
        required 
      />
      <button type="submit" class="send-btn" :disabled="isTyping || !newMessage.trim()">
        Enviar
      </button>
    </form>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// La memoria se almacena sólo en la sesión del cliente por simplicidad del prototipo
const localHistory = ref([
  { role: 'assistant', content: '¡Hola! Soy tu asistente médico virtual. ¿En qué puedo ayudarte hoy?' }
])
const newMessage = ref('')
const isTyping = ref(false)
const chatBox = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return

  // 1. Agregar el mensaje del usuario a la vista
  const userMsg = { role: 'user', content: newMessage.value.trim() }
  // Filtramos la data en bruto que el backend espera (para omitir el saludo inicial si se requiere o pasarlo como contexto)
  // En nuestro backend get_gemini_response ya sabe concatenar "history", así que se lo enviamos
  
  // Guardamos un clon del historial SIN el nuevo mensaje, para enviarlo como contexto
  const historyForBackend = localHistory.value.filter(m => m.role !== 'system') // Si tuviéramos
  
  localHistory.value.push(userMsg)
  
  const textToSend = newMessage.value.trim()
  newMessage.value = ''
  isTyping.value = true
  scrollToBottom()

  try {
    const token = localStorage.getItem('access_token')
    
    // 2. Hacer la llamada POST al backend
    const response = await axios.post('http://localhost:8000/api/v1/chat/', {
      history: historyForBackend, // Se envía todo lo que hablaron hoy
      message: textToSend
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    // 3. Añadir la respuesta de la IA a la memoria local y vista
    let aiResponse = response.data.response;
    let targetSpecialty = null;
    
    const actionRegex = /\[ACTION:MAP:(.*?)\]/i;
    const match = aiResponse.match(actionRegex);
    if (match) {
      targetSpecialty = match[1].trim();
      // Remove the action tag from the visible response
      aiResponse = aiResponse.replace(actionRegex, '').trim();
    }

    localHistory.value.push({ role: 'assistant', content: aiResponse })
    
    if (targetSpecialty) {
      setTimeout(() => {
        router.push({ path: '/map', query: { specialty: targetSpecialty } })
      }, 2500); // 2.5 second delay so the user can read the response
    }
    
  } catch (error) {
    console.error(error)
    let errText = "Ocurrió un error al contactar al asistente."
    
    if (error.response?.data?.detail) {
      errText = `Error de IA: ${error.response.data.detail}`
    }
    
    localHistory.value.push({ role: 'assistant', content: errText })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.standalone-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background-color: var(--bg-color);
}
.chat-container {
  display: flex;
  flex-direction: column;
  height: 80vh; /* Pantalla casi completa */
  max-width: 800px;
  width: 100%;
  padding: 0;
  overflow: hidden;
}

.chat-header {
  background: var(--primary-color);
  color: white;
  padding: 1.5rem;
  text-align: center;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  position: relative;
}

.back-btn {
  position: absolute;
  left: 0;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: white;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chat-header h2 {
  margin: 0;
}
.chat-header p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #fcfcfc;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  width: 100%;
}
.message-user {
  justify-content: flex-end;
}
.message-ai {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  line-height: 1.5;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  white-space: pre-wrap;
}

.message-user .message-bubble {
  background: var(--primary-color);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-ai .message-bubble {
  background: white;
  color: var(--text-main);
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
}

.chat-input-area {
  display: flex;
  padding: 1.25rem;
  background: white;
  border-top: 1px solid #e5e7eb;
  gap: 1rem;
}

.chat-input-area input {
  flex: 1;
  padding: 0.8rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 1rem;
}
.chat-input-area input:focus {
  border-color: var(--primary-color);
}

.send-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Typing animation */
.typing-indicator span {
  display: inline-block;
  animation: blink 1.4s infinite reverse;
  font-size: 1.5rem;
  line-height: 1;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0% { opacity: 0.2; }
  20% { opacity: 1; }
  100% { opacity: 0.2; }
}
</style>
