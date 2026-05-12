from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import jwt

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Patient, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_patient(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Patient:
    if current_user.role != RoleEnum.PATIENT.value:
        raise HTTPException(status_code=403, detail="Permisos insuficientes. Se requiere rol paciente.")
    result = await db.execute(select(Patient).where(Patient.user_id == current_user.id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="Perfil de paciente no encontrado")
    return patient

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permisos insuficientes. Se requiere rol administrador.")
    return current_user

async def get_current_doctor(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != RoleEnum.DOCTOR.value:
        raise HTTPException(status_code=403, detail="Permisos insuficientes. Se requiere rol médico.")
    from app.models.user import Doctor
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalars().first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Perfil de médico no encontrado")
    return doctor
