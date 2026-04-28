import asyncio
import datetime
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, Doctor, Patient, RoleEnum
from app.models.clinic import MedicalCenter, DoctorMedicalCenter, Schedule
from app.models.appointment import Appointment, AppointmentStatusEnum

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Create Users
        admin_user = User(
            email="admin@test.com",
            password_hash=get_password_hash("admin123"),
            role=RoleEnum.ADMIN
        )
        
        doctor_user = User(
            email="doctor@test.com",
            password_hash=get_password_hash("doctor123"),
            role=RoleEnum.DOCTOR
        )
        
        doctor2_user = User(
            email="elena@test.com",
            password_hash=get_password_hash("doctor123"),
            role=RoleEnum.DOCTOR
        )
        
        doctor3_user = User(
            email="carlos@test.com",
            password_hash=get_password_hash("doctor123"),
            role=RoleEnum.DOCTOR
        )
        
        patient_user = User(
            email="patient@test.com",
            password_hash=get_password_hash("patient123"),
            role=RoleEnum.PATIENT
        )
        
        session.add_all([admin_user, doctor_user, doctor2_user, doctor3_user, patient_user])
        await session.commit()
        await session.refresh(doctor_user)
        await session.refresh(patient_user)

        # Create Doctor and Patient profiles
        doctor_profile = Doctor(
            user_id=doctor_user.id,
            full_name="Dr. Roberto Sanchez",
            specialty="Cardiología",
            license_number="MED-774411",
            bio="Especialista con más de 10 años de experiencia en Cardiología.",
            consultation_fee=250.00
        )
        
        doctor2_profile = Doctor(
            user_id=doctor2_user.id,
            full_name="Dra. Elena Martínez",
            specialty="Pediatría",
            license_number="MED-885522",
            bio="Pediatra enfocada en el desarrollo temprano y nutrición infantil.",
            consultation_fee=200.00
        )
        
        doctor3_profile = Doctor(
            user_id=doctor3_user.id,
            full_name="Dr. Carlos Ruiz",
            specialty="Dermatología",
            license_number="MED-996633",
            bio="Experto en tratamientos de la piel y dermatología estética.",
            consultation_fee=300.00
        )
        patient_profile = Patient(
            user_id=patient_user.id,
            full_name="Ana Lopez",
            birth_date=datetime.date(1992, 5, 14),
            phone="77123456",
            medical_history="Sin alergias conocidas."
        )
        
        session.add_all([doctor_profile, doctor2_profile, doctor3_profile, patient_profile])
        await session.commit()

        # Create Medical Centers in La Paz
        center1 = MedicalCenter(
            name="Hospital de Clínicas Universitarias",
            address="Av. Saavedra, Miraflores, La Paz",
            location="POINT(-68.119271 -16.498877)",
            phone="2224455"
        )
        center2 = MedicalCenter(
            name="Clínica del Sur",
            address="Av. Hernando Siles, Obrajes, La Paz",
            location="POINT(-68.081700 -16.538600)",
            phone="2784000"
        )
        center3 = MedicalCenter(
            name="Centro Médico San Jorge",
            address="Av. Arce, San Jorge, La Paz",
            location="POINT(-68.125000 -16.510000)",
            phone="2430000"
        )
        
        session.add_all([center1, center2, center3])
        await session.commit()
        await session.refresh(center1)
        await session.refresh(center2)
        await session.refresh(center3)
        
        # Create Association: Doctor 1 assigned to Hospital de Clínicas
        assignment1 = DoctorMedicalCenter(
            doctor_id=doctor_profile.user_id,
            center_id=center1.id
        )
        # Doctor 2 assigned to Clínica del Sur
        assignment2 = DoctorMedicalCenter(
            doctor_id=doctor2_profile.user_id,
            center_id=center2.id
        )
        # Doctor 3 assigned to Centro Médico San Jorge
        assignment3 = DoctorMedicalCenter(
            doctor_id=doctor3_profile.user_id,
            center_id=center3.id
        )
        
        session.add_all([assignment1, assignment2, assignment3])
        await session.commit()
        await session.refresh(assignment1)
        await session.refresh(assignment2)
        await session.refresh(assignment3)

        # Create Schedules
        schedules = [
            Schedule(assignment_id=assignment1.id, day_of_week=0, start_time=datetime.time(9, 0), end_time=datetime.time(12, 0), is_available=True),
            Schedule(assignment_id=assignment1.id, day_of_week=2, start_time=datetime.time(14, 0), end_time=datetime.time(18, 0), is_available=True),
            Schedule(assignment_id=assignment1.id, day_of_week=4, start_time=datetime.time(9, 0), end_time=datetime.time(15, 0), is_available=True),
            
            Schedule(assignment_id=assignment2.id, day_of_week=1, start_time=datetime.time(8, 0), end_time=datetime.time(14, 0), is_available=True),
            Schedule(assignment_id=assignment2.id, day_of_week=3, start_time=datetime.time(13, 0), end_time=datetime.time(17, 0), is_available=True),
            
            Schedule(assignment_id=assignment3.id, day_of_week=0, start_time=datetime.time(10, 0), end_time=datetime.time(16, 0), is_available=True),
            Schedule(assignment_id=assignment3.id, day_of_week=4, start_time=datetime.time(10, 0), end_time=datetime.time(16, 0), is_available=True)
        ]
        
        session.add_all(schedules)
        await session.commit()
        
        # Create 1 Appointment for Patient with Doctor at Center1
        appointment_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2)
        appointment = Appointment(
            patient_id=patient_profile.user_id,
            doctor_id=doctor_profile.user_id,
            center_id=center1.id,
            schedule_id=schedules[0].id,
            appointment_date=appointment_date,
            status=AppointmentStatusEnum.PENDING,
            notes="Chequeo cardiológico de rutina."
        )
        
        session.add(appointment)
        await session.commit()
        
        print("Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
