import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import get_db
from app.core.config import settings

from sqlalchemy.pool import NullPool

# Usamos la base de datos real (Settings.DATABASE_URL) pero ejecutando en transacciones con Rollback
# Usamos NullPool para evitar que asyncpg deje tasks en background que causen errores en Windows
engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Crea una sesión de base de datos para pruebas.
    Envuelve cada prueba en una transacción y hace rollback al final,
    dejando la base de datos intacta.
    """
    connection = await engine.connect()
    transaction = await connection.begin()
    
    # Nested transaction para que los commits de la app usen SAVEPOINTS y no cierren la transacción real
    nested = await connection.begin_nested()
    
    session = AsyncSession(bind=connection, expire_on_commit=False)
    
    @pytest.hookimpl
    def pytest_exception_interact(call):
        # Si la app hace rollback manual, SQLAlchemy emite ROLLBACK TO SAVEPOINT
        pass

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    Cliente HTTP de FastAPI para pruebas, inyectando la sesión de BD transaccional.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
