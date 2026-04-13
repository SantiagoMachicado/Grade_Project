from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

def get_gemini_response(history: list, current_message: str) -> str:
    # Initialize the LLM. It automatically looks for GOOGLE_API_KEY
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7
    )
    
    messages = [
        SystemMessage(content="Eres un asistente médico virtual amigable en un portal de salud. Resuelves dudas de pacientes y doctores. Acostumbras ser conciso y recordar que no puedes dar diagnósticos definitivos y deben consultar a su médico.")
    ]
    
    # Populate history for context
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
            
    # Append the newest message
    messages.append(HumanMessage(content=current_message))
    
    # Call Gemini Model
    response = llm.invoke(messages)
    return response.content
