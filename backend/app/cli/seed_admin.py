"""Seed demo data: admin, doctor, patient, doctor profile, availability, sample appointment.

Usage:
    python -m app.cli.seed_admin

Creates:
    admin@example.com (admin)
    doctor@example.com (doctor) with profile and availability
    patient@example.com (patient) with a sample appointment
    
Development password for all: Password123!
"""

import os
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.doctor_profile import DoctorProfile
from app.models.availability import DoctorAvailability
from app.models.appointment import Appointment, AppointmentStatus
from app.repositories.user import get_user_by_email


DEV_PASSWORD = "Password123!"


def main() -> None:
    db = SessionLocal()
    try:
        # --- Admin ---
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", DEV_PASSWORD)
        admin_name = os.environ.get("ADMIN_FULL_NAME", "Admin User")

        admin = get_user_by_email(db, admin_email)
        if not admin:
            admin = User(
                email=admin_email,
                hashed_password=hash_password(admin_password),
                full_name=admin_name,
                role=UserRole.admin,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Admin created: {admin.email} (id={admin.id})")
        else:
            print(f"Admin already exists: {admin.email} (id={admin.id})")

        # --- Doctor ---
        doctor_email = "doctor@example.com"
        doctor_user = get_user_by_email(db, doctor_email)
        if not doctor_user:
            doctor_user = User(
                email=doctor_email,
                hashed_password=hash_password(DEV_PASSWORD),
                full_name="Dr. Sarah Johnson",
                role=UserRole.doctor,
            )
            db.add(doctor_user)
            db.commit()
            db.refresh(doctor_user)
            print(f"Doctor user created: {doctor_user.email} (id={doctor_user.id})")
        else:
            print(f"Doctor user exists: {doctor_user.email} (id={doctor_user.id})")

        # Doctor Profile
        from sqlalchemy import select
        doctor_profile = db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == doctor_user.id)
        ).scalar_one_or_none()

        if not doctor_profile:
            doctor_profile = DoctorProfile(
                user_id=doctor_user.id,
                specialization="General Medicine",
                bio="Board-certified general practitioner with 10+ years of experience. "
                    "Specializing in preventive care, chronic disease management, and family medicine.",
                consultation_duration_minutes=30,
            )
            db.add(doctor_profile)
            db.commit()
            db.refresh(doctor_profile)
            print(f"Doctor profile created: {doctor_profile.id}")

            # Add availability: Mon-Fri, 9:00-12:00 and 14:00-17:00
            for day in range(5):  # Mon to Fri
                for start_h, end_h in [(9, 12), (14, 17)]:
                    avail = DoctorAvailability(
                        doctor_id=doctor_profile.id,
                        day_of_week=day,
                        start_time=time(start_h, 0),
                        end_time=time(end_h, 0),
                    )
                    db.add(avail)
            db.commit()
            print("Doctor availability created (Mon-Fri, 9-12 and 14-17)")
        else:
            print(f"Doctor profile exists: {doctor_profile.id}")

        # Add second doctor
        doctor2_email = "doctor2@example.com"
        doctor2_user = get_user_by_email(db, doctor2_email)
        if not doctor2_user:
            doctor2_user = User(
                email=doctor2_email,
                hashed_password=hash_password(DEV_PASSWORD),
                full_name="Dr. Michael Chen",
                role=UserRole.doctor,
            )
            db.add(doctor2_user)
            db.commit()
            db.refresh(doctor2_user)

            doctor2_profile = DoctorProfile(
                user_id=doctor2_user.id,
                specialization="Cardiology",
                bio="Expert cardiologist with focus on heart failure management, "
                    "cardiac imaging, and preventive cardiology.",
                consultation_duration_minutes=45,
            )
            db.add(doctor2_profile)
            db.commit()
            db.refresh(doctor2_profile)

            for day in range(5):
                avail = DoctorAvailability(
                    doctor_id=doctor2_profile.id,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(16, 0),
                )
                db.add(avail)
            db.commit()
            print(f"Doctor 2 created: {doctor2_user.email}")
        else:
            print(f"Doctor 2 exists: {doctor2_user.email}")

        # --- Patient ---
        patient_email = "patient@example.com"
        patient = get_user_by_email(db, patient_email)
        if not patient:
            patient = User(
                email=patient_email,
                hashed_password=hash_password(DEV_PASSWORD),
                full_name="Jane Smith",
                role=UserRole.patient,
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            print(f"Patient created: {patient.email} (id={patient.id})")

            # Create sample appointment for tomorrow at 10:00
            tomorrow = date.today() + timedelta(days=1)
            if tomorrow.weekday() >= 5:
                tomorrow += timedelta(days=(7 - tomorrow.weekday()))
            start = datetime.combine(tomorrow, time(10, 0), tzinfo=timezone.utc)
            end = start + timedelta(minutes=doctor_profile.consultation_duration_minutes)

            appt = Appointment(
                patient_id=patient.id,
                doctor_id=doctor_profile.id,
                start_time=start,
                end_time=end,
                reason="Annual health checkup",
            )
            db.add(appt)
            db.commit()
            print(f"Sample appointment created for {start.date()}")
        else:
            print(f"Patient exists: {patient.email} (id={patient.id})")

        print("\n=== Demo Credentials ===")
        print(f"Admin:   admin@example.com / {DEV_PASSWORD}")
        print(f"Doctor:  doctor@example.com / {DEV_PASSWORD}")
        print(f"Doctor2: doctor2@example.com / {DEV_PASSWORD}")
        print(f"Patient: patient@example.com / {DEV_PASSWORD}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
