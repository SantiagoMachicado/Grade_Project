import asyncio
import datetime
import random
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, Doctor, Patient, RoleEnum
from app.models.clinic import MedicalCenter, DoctorMedicalCenter, Schedule
from app.models.appointment import Appointment, AppointmentStatusEnum

# Mock data sources
SPECIALTIES = ["Cardiología", "Pediatría", "Dermatología", "Neurología", "Traumatología", "Oftalmología", "Ginecología", "Urología", "Psiquiatría", "Medicina General"]
FIRST_NAMES = ["Roberto", "Elena", "Carlos", "Ana", "Luis", "Maria", "Jorge", "Sofia", "Miguel", "Lucia", "Diego", "Paula", "Fernando", "Laura", "Pedro", "Carmen", "Javier", "Isabel", "Ricardo", "Marta", "Alejandro", "Valentina", "Andres", "Camila"]
LAST_NAMES = ["Sanchez", "Martinez", "Ruiz", "Lopez", "Garcia", "Perez", "Gonzalez", "Gomez", "Fernandez", "Rodriguez", "Diaz", "Alvarez", "Romero", "Torres", "Suarez", "Vargas", "Rojas", "Flores"]
CENTER_NAMES = ["Hospital de Clínicas", "Clínica del Sur", "Centro Médico San Jorge", "Hospital Obrero", "Clínica Alemana", "Centro Médico Cemes", "Clínica Los Andes", "Hospital Materno Infantil", "Clínica Prosalud", "Hospital Arco Iris"]

async def seed_data():
    async with AsyncSessionLocal() as session:
        users_to_add = []
        
        # 1 Admin
        admin_user = User(email="admin@test.com", password_hash=get_password_hash("admin123"), role=RoleEnum.ADMIN)
        users_to_add.append(admin_user)
        
        # 13 Doctors
        doctor_users = []
        for i in range(1, 14):
            # doctor1@test.com ... doctor13@test.com
            doc = User(email=f"doctor{i}@test.com" if i > 1 else "doctor@test.com", password_hash=get_password_hash("doctor123"), role=RoleEnum.DOCTOR)
            doctor_users.append(doc)
            users_to_add.append(doc)
            
        # 20 Patients
        patient_users = []
        for i in range(1, 21):
            pat = User(email=f"patient{i}@test.com" if i > 1 else "patient@test.com", password_hash=get_password_hash("patient123"), role=RoleEnum.PATIENT)
            patient_users.append(pat)
            users_to_add.append(pat)
            
        session.add_all(users_to_add)
        await session.commit()
        
        for u in users_to_add:
            await session.refresh(u)
            
        # Profiles
        doctor_profiles = []
        for i, doc_u in enumerate(doctor_users):
            fname = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            profile = Doctor(
                user_id=doc_u.id,
                full_name=f"{fname}",
                specialty=random.choice(SPECIALTIES),
                license_number=f"MED-{random.randint(10000, 99999)}",
                bio="Especialista con amplia experiencia médica y trato humanizado.",
                consultation_fee=random.choice([150.0, 200.0, 250.0, 300.0])
            )
            doctor_profiles.append(profile)
            
        patient_profiles = []
        for pat_u in patient_users:
            fname = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            profile = Patient(
                user_id=pat_u.id,
                full_name=fname,
                birth_date=datetime.date(random.randint(1950, 2010), random.randint(1, 12), random.randint(1, 28)),
                phone=f"7{random.randint(1000000, 9999999)}",
                medical_history="Ninguna condición preexistente reportada."
            )
            patient_profiles.append(profile)
            
        session.add_all(doctor_profiles + patient_profiles)
        await session.commit()
        
        # 10 Medical Centers
        centers = []
        for i in range(10):
            lon = -68.1 + random.uniform(-0.05, 0.05)
            lat = -16.5 + random.uniform(-0.05, 0.05)
            c = MedicalCenter(
                name=CENTER_NAMES[i],
                address=f"Av. Principal #{random.randint(100, 999)}, La Paz",
                location=f"POINT({lon:.6f} {lat:.6f})",
                phone=f"2{random.randint(100000, 999999)}"
            )
            centers.append(c)
            
        session.add_all(centers)
        await session.commit()
        for c in centers: await session.refresh(c)
        
        # Assignments & Schedules
        assignments = []
        for doc in doctor_profiles:
            # Assign to 1-2 random centers
            assigned_centers = random.sample(centers, random.randint(1, 2))
            for c in assigned_centers:
                assignment = DoctorMedicalCenter(doctor_id=doc.user_id, center_id=c.id)
                assignments.append(assignment)
                
        session.add_all(assignments)
        await session.commit()
        for a in assignments: await session.refresh(a)

        schedules = []
        for assignment in assignments:
            # Add 2-3 schedules per assignment
            for _ in range(random.randint(2, 3)):
                day = random.randint(0, 4) # Mon-Fri
                start_hour = random.randint(8, 14)
                sched = Schedule(
                    assignment_id=assignment.id,
                    day_of_week=day,
                    start_time=datetime.time(start_hour, 0),
                    end_time=datetime.time(start_hour + 4, 0),
                    is_available=True
                )
                schedules.append(sched)
                
        session.add_all(schedules)
        await session.commit()
        
        # Appointments
        appointments = []
        now = datetime.datetime.now(datetime.timezone.utc)
        
        for doc in doctor_profiles:
            doc_assignments = [a for a in assignments if a.doctor_id == doc.user_id]
            if not doc_assignments: continue
            
            # 15 appointments per doctor to populate dashboard metrics
            for _ in range(15):
                pat = random.choice(patient_profiles)
                assignment = random.choice(doc_assignments)
                
                # Determine past or future
                is_past = random.choice([True, False])
                if is_past:
                    # Past appointment: 1 to 150 days ago
                    appt_date = now - datetime.timedelta(days=random.randint(1, 150), hours=random.randint(-5, 5))
                    status = random.choices(
                        [AppointmentStatusEnum.COMPLETED, AppointmentStatusEnum.CANCELLED, AppointmentStatusEnum.ABSENT],
                        weights=[70, 15, 15]
                    )[0]
                else:
                    # Future appointment: 0 to 15 days ahead
                    appt_date = now + datetime.timedelta(days=random.randint(0, 15), hours=random.randint(-5, 5))
                    status = random.choices(
                        [AppointmentStatusEnum.PENDING, AppointmentStatusEnum.CONFIRMED, AppointmentStatusEnum.CANCELLED],
                        weights=[40, 50, 10]
                    )[0]
                    
                appt = Appointment(
                    patient_id=pat.user_id,
                    doctor_id=doc.user_id,
                    center_id=assignment.center_id,
                    appointment_date=appt_date,
                    status=status,
                    notes=random.choice(["Chequeo de rutina.", "Dolor persistente.", "Consulta general.", "Primera visita.", "Control anual."]),
                    medical_report="Paciente estable. Tratamiento recetado." if status == AppointmentStatusEnum.COMPLETED else None
                )
                appointments.append(appt)
                
        session.add_all(appointments)
        await session.commit()
        
        print(f"✅ Base de datos poblada masivamente:")
        print(f"- 1 Administrador")
        print(f"- {len(doctor_users)} Doctores (Emails: doctor@test.com, doctor2@test.com...)")
        print(f"- {len(patient_users)} Pacientes (Emails: patient@test.com, patient2@test.com...)")
        print(f"- {len(centers)} Centros Médicos")
        print(f"- {len(schedules)} Horarios")
        print(f"- {len(appointments)} Citas generadas (Pasadas y Futuras)")

if __name__ == "__main__":
    asyncio.run(seed_data())
