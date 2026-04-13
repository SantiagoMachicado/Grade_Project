from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core import database
from app.models import Base
from app.api.v1.api import api_router
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # En desarrollo, creamos las tablas asíncronamente
    # En producción usar Alembic para migraciones
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Configurar CORS para permitir que el frontend de Vue consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir todos los endpoints v1
app.include_router(api_router, prefix="/api/v1")

