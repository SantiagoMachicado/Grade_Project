# Salud Digital Bolivia - Portal Médico

Este es un proyecto Full-Stack (Backend con FastAPI + Frontend con Vue 3) para la gestión de citas médicas, agendas de doctores y visualización geoespacial de clínicas con inteligencia artificial (Gemini).

## Requisitos Previos (Para la nueva PC)

Para ejecutar este proyecto en una máquina nueva, necesitarás tener instalados:

1. **Python 3.10+** (Asegúrate de marcar "Add Python to PATH" durante la instalación).
2. **Node.js v18+** (Viene con npm incluido).
3. **PostgreSQL** (Servidor de Base de Datos).
4. **PostGIS** (Extensión espacial para PostgreSQL). Debes instalar la extensión PostGIS en tu servidor PostgreSQL para soportar los campos `Geometry` de Leaflet.

## Paso 1: Configurar la Base de Datos

1. Abre tu administrador de PostgreSQL (ej. pgAdmin o psql).
2. Crea una base de datos llamada `salud_digital`.
3. Activa la extensión PostGIS en esa base de datos ejecutando el siguiente query:
   ```sql
   CREATE EXTENSION postgis;
   ```
4. Si tu usuario de postgres o contraseña son diferentes a `postgres:nimda`, deberás crear un archivo `.env` en la carpeta raíz del proyecto (`d:\Grade_Project\.env`) e indicar tu cadena de conexión y tu API KEY de Gemini:
   ```env
   DATABASE_URL="postgresql+asyncpg://tu_usuario:tu_contraseña@localhost:5432/salud_digital"
   GOOGLE_API_KEY="tu_api_key_de_google_gemini"
   ```

## Paso 2: Instalación del Backend (FastAPI)

1. Abre una terminal en la carpeta principal del proyecto (`d:\Grade_Project`).
2. Crea un entorno virtual para no ensuciar tu sistema:
   ```bash
   python -m venv venv
   ```
3. Activa el entorno virtual:
   - En Windows: `.\venv\Scripts\activate`
   - En Mac/Linux: `source venv/bin/activate`
4. Instala todas las dependencias del servidor:
   ```bash
   pip install -r requirements.txt
   ```
5. Prepara la base de datos con las tablas y datos de prueba:
   ```bash
   python reset_db.py
   python seed_db.py
   ```
6. Enciende el servidor backend:
   ```bash
   uvicorn app.main:app --reload
   ```
   *(El servidor correrá en `http://localhost:8000`)*

## Paso 3: Instalación del Frontend (Vue 3)

1. Abre **otra terminal nueva** (mantén el servidor de FastAPI corriendo en la anterior).
2. Entra a la carpeta del frontend:
   ```bash
   cd frontend
   ```
3. Instala los paquetes de Node:
   ```bash
   npm install
   ```
4. Levanta el servidor de desarrollo del frontend:
   ```bash
   npm run dev
   ```
   *(El servidor de Vue te indicará una URL como `http://localhost:5173`, haz clic ahí o ábrela en tu navegador).*

## ¡Listo para probar!

Ya puedes iniciar sesión en el portal. Algunas credenciales creadas en el archivo `seed_db.py` son:
- **Paciente:** `patient@test.com` (Pass: `patient123`)
- **Doctores:** `doctor@test.com`, `elena@test.com`, `carlos@test.com` (Pass: `doctor123`)
- **Admin:** `admin@test.com` (Pass: `admin123`)
