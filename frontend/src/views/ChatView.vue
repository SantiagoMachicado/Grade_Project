<template>
  <div class="responsive-dashboard-container chat-view-container">
    
    <!-- Header -->
    <div class="top-header">
      <button class="icon-btn" @click="$router.go(-1)">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <div class="header-titles">
        <h2 class="header-title">Asistente de Salud Virtual</h2>
        <span class="header-subtitle">Gemini 2.5 Flash</span>
      </div>
      <div style="width: 24px"></div> <!-- Placeholder for centering -->
    </div>

    <!-- Chat Body -->
    <div class="chat-body" ref="chatBox">
      
      <div class="message-wrapper" v-for="(msg, index) in localHistory" :key="index">
        
        <div :class="['message', msg.role === 'user' ? 'message-user' : 'message-ai']">
          
          <!-- AI Avatar -->
          <div class="avatar ai-avatar" v-if="msg.role === 'assistant'">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          </div>

          <div class="message-content">
            <div class="sender-name">{{ msg.role === 'user' ? 'Tú' : 'AI Agent' }}</div>
            
            <div class="message-bubble">
              {{ msg.content }}
            </div>

            <!-- ACTION CARD (Intent Detected) -->
            <div class="intent-card" v-if="msg.action && !msg.action.cancelled">
              <div class="intent-header">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                <span>INTENCIÓN DETECTADA: BUSCAR MÉDICO</span>
              </div>
              <div class="intent-body">
                <div class="intent-row">
                  <span class="intent-label">Acción</span>
                  <span class="intent-value">Ver Mapa de Clínicas</span>
                </div>
                <div class="intent-row">
                  <span class="intent-label">Especialidad</span>
                  <span class="intent-value">{{ msg.action.specialty }}</span>
                </div>
              </div>
              <div class="intent-actions">
                <button class="btn-confirm" @click="confirmAction(msg.action)">Confirmar</button>
              </div>
              <button class="btn-continue" @click="cancelAction(index)">
                No gracias, continuar conversando
              </button>
            </div>

            <div class="timestamp">{{ msg.time || getCurrentTime() }} <svg v-if="msg.role==='user'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg></div>
          </div>

          <!-- User Avatar -->
          <div class="avatar user-avatar" v-if="msg.role === 'user'">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          </div>

        </div>
      </div>

      <!-- Suggested Prompts (Only show if no user messages yet) -->
      <div class="suggested-prompts" v-if="localHistory.length === 1 && !isTyping">
        <button class="prompt-chip" @click="sendSuggested('Quiero agendar una cita médica')">
          📅 Agendar cita médica
        </button>
        <button class="prompt-chip" @click="sendSuggested('¿Cuáles son las clínicas disponibles?')">
          🏥 Ver clínicas cercanas
        </button>
        <button class="prompt-chip" @click="sendSuggested('¿Qué especialidades médicas tienen disponibles?')">
          ❤️ Especialidades disponibles
        </button>
      </div>

      <!-- Typing indicator -->
      <div class="message-wrapper" v-if="isTyping">
        <div class="message message-ai">
          <div class="avatar ai-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          </div>
          <div class="message-content">
            <div class="sender-name">AI Agent</div>
            <div class="message-bubble typing-bubble">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Input Area -->
    <div class="chat-footer">
      <form @submit.prevent="sendMessage" class="input-wrapper">
        <input 
          v-model="newMessage" 
          type="text" 
          placeholder="Escribe tu mensaje..." 
          :disabled="isTyping"
          ref="inputField"
          required 
        />
        <button type="button" class="action-btn mic-btn" title="Voz (Demo)">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
        </button>
        <button type="submit" class="action-btn send-btn" :disabled="isTyping || !newMessage.trim()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        </button>
      </form>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const inputField = ref(null)

const getCurrentTime = () => {
  const now = new Date();
  let hours = now.getHours();
  let minutes = now.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; 
  minutes = minutes < 10 ? '0' + minutes : minutes;
  return hours + ':' + minutes + ' ' + ampm;
}

const localHistory = ref([
  { role: 'assistant', content: '¿Cómo puedo ayudarte a agendar hoy?', time: getCurrentTime() }
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

const confirmAction = (action) => {
  if (action.type === 'map') {
    router.push({ path: '/map', query: { specialty: action.specialty } })
  }
}

const sendSuggested = (text) => {
  newMessage.value = text;
  sendMessage();
}

const cancelAction = (index) => {
  // Mark the action as cancelled so the card disappears
  if (localHistory.value[index] && localHistory.value[index].action) {
    localHistory.value[index].action.cancelled = true;
  }
  // Focus the input so the user can type what they actually want
  if (inputField.value) {
    inputField.value.focus();
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return

  const userMsg = { role: 'user', content: newMessage.value.trim(), time: getCurrentTime() }
  
  // Guardamos un clon del historial SIN el nuevo mensaje, para enviarlo como contexto
  // Y filtramos propiedades extrañas para el backend
  const historyForBackend = localHistory.value.map(m => ({ role: m.role, content: m.content }))
  
  localHistory.value.push(userMsg)
  
  const textToSend = newMessage.value.trim()
  newMessage.value = ''
  isTyping.value = true
  scrollToBottom()

  try {
    const token = localStorage.getItem('access_token')
    
    const response = await axios.post('http://localhost:8000/api/v1/chat/', {
      history: historyForBackend,
      message: textToSend
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    let aiResponse = response.data.response;
    let actionObj = null;
    
    // Check if the AI wants to redirect to the map
    const actionRegex = /\[ACTION:MAP:(.*?)\]/i;
    const match = aiResponse.match(actionRegex);
    if (match) {
      const targetSpecialty = match[1].trim();
      aiResponse = aiResponse.replace(actionRegex, '').trim();
      actionObj = { type: 'map', specialty: targetSpecialty, cancelled: false };
    }

    localHistory.value.push({ 
      role: 'assistant', 
      content: aiResponse, 
      time: getCurrentTime(),
      action: actionObj
    })
    
  } catch (error) {
    console.error(error)
    let errText = "Ocurrió un error al contactar al asistente."
    if (error.response?.data?.detail) {
      errText = `Error de IA: ${error.response.data.detail}`
    }
    localHistory.value.push({ role: 'assistant', content: errText, time: getCurrentTime() })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
/* Main Container matching the dashboard styles */
.chat-view-container {
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  height: 90vh; /* Fixed height to allow scrolling */
  padding: 0;
  overflow: hidden;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.05);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  border: 1px solid #f1f5f9;
}

/* Header */
.top-header { 
  display: flex; align-items: center; justify-content: space-between; 
  padding: 1.25rem 1.5rem; background: white; border-bottom: 1px solid #f1f5f9; 
  z-index: 10;
}
.icon-btn { 
  background: none; border: none; color: #64748b; cursor: pointer; 
  display: flex; align-items: center; justify-content: center; 
  padding: 0.5rem; border-radius: 50%; transition: background 0.2s; 
  margin-left: -0.5rem;
}
.icon-btn:hover { background: #f1f5f9; color: #1e293b; }
.header-titles { text-align: center; }
.header-title { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.header-subtitle { font-size: 0.75rem; color: #94a3b8; font-weight: 600; }

/* Chat Body */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  scroll-behavior: smooth;
}
.chat-body::-webkit-scrollbar { width: 6px; }
.chat-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

.message-wrapper {
  display: flex;
  width: 100%;
}

.message {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
}

.message-user {
  margin-left: auto;
  flex-direction: row;
}

.message-ai {
  margin-right: auto;
  flex-direction: row;
}

/* Avatars */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ai-avatar { background: #e0f2fe; color: #0284c7; }
.user-avatar { background: #e2e8f0; color: #475569; }

/* Suggested Prompts */
.suggested-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.5rem;
  margin-left: 3.5rem; /* Aligns with the AI message bubble */
}

.prompt-chip {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 0.6rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #0284c7;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.prompt-chip:hover {
  background: #f0f9ff;
  border-color: #bae6fd;
  transform: translateY(-1px);
}

/* Message Content area */
.message-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.message-user .message-content { align-items: flex-end; }
.message-ai .message-content { align-items: flex-start; }

.sender-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  margin: 0 0.25rem;
}

/* Bubbles */
.message-bubble {
  padding: 1rem 1.25rem;
  border-radius: 20px;
  line-height: 1.5;
  font-size: 0.95rem;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.message-user .message-bubble {
  background: #004e98;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-ai .message-bubble {
  background: white;
  color: #1e293b;
  border-bottom-left-radius: 4px;
}

/* Intent Card */
.intent-card {
  margin-top: 0.5rem;
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
  width: 280px;
}

.intent-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #06b6d4; /* Cyan color matching the image style */
  font-weight: 800;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  margin-bottom: 1rem;
}

.intent-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.intent-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f8fafc;
}

.intent-label { color: #64748b; }
.intent-value { font-weight: 700; color: #004e98; }

.intent-actions {
  display: flex;
  gap: 0.5rem;
}

.intent-actions button {
  flex: 1;
  padding: 0.6rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-confirm { background: #06b6d4; color: white; }
.btn-confirm:hover { background: #0891b2; }

.btn-continue {
  margin-top: 0.75rem;
  width: 100%;
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: underline;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0;
}
.btn-continue:hover {
  color: #64748b;
}

/* Timestamp */
.timestamp {
  font-size: 0.65rem;
  color: #94a3b8;
  margin: 0.2rem 0.5rem 0 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Typing Indicator */
.typing-bubble { display: flex; gap: 4px; padding: 1.25rem 1.5rem; align-items: center; }
.dot { width: 6px; height: 6px; background: #cbd5e1; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); background: #94a3b8; } }

/* Input Footer */
.chat-footer {
  padding: 1rem 1.5rem;
  background: white;
  border-top: 1px solid #f1f5f9;
  z-index: 10;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 50px;
  padding: 0.5rem 0.5rem 0.5rem 1.5rem;
  border: 1px solid #e2e8f0;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper:focus-within {
  border-color: #0284c7;
  background: white;
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.95rem;
  color: #1e293b;
  font-family: inherit;
}
.input-wrapper input::placeholder { color: #94a3b8; }

.action-btn {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.mic-btn { color: #94a3b8; margin-right: 0.25rem; }
.mic-btn:hover { color: #0284c7; background: #f1f5f9; }

.send-btn { background: #004e98; color: white; }
.send-btn:hover:not(:disabled) { background: #003a70; }
.send-btn:disabled { background: #cbd5e1; cursor: not-allowed; }

</style>
