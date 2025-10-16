from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

from utils.config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(15))
    created_at = Column(DateTime, default=datetime.utcnow)

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    address = Column(Text)
    phone = Column(String(15))
    email = Column(String(100))
    availability = Column(Text)
    is_active = Column(Boolean, default=True)

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    description = Column(Text)
    status = Column(String(20), default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)
    google_calendar_event_id = Column(String(100))

def generate_30min_slots(start_time, end_time):
    """Generate 30-minute time slots between start and end time"""
    slots = []
    current_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")
    
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=30)
        slots.append(f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}")
        current_time = slot_end
    
    return slots

def init_db():
    """Initialize database with sample data"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Add sample doctors
    session = SessionLocal()
    
    try:
        # Check if doctors already exist
        if not session.query(Doctor).first():
            sample_doctors = [
                Doctor(
                    name="Dr. Rajesh Kumar",
                    specialization="Cardiologist",
                    city="Delhi",
                    state="Delhi",
                    address="A-101, Medical Complex, Connaught Place, Delhi",
                    phone="+91-11-2345-6789",
                    email="dr.rajesh@cardiocare.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("09:00", "11:00") + generate_30min_slots("14:00", "16:00"),
                        "tuesday": generate_30min_slots("10:00", "12:00") + generate_30min_slots("15:00", "17:00"),
                        "wednesday": generate_30min_slots("09:00", "11:00") + generate_30min_slots("14:00", "16:00"),
                        "thursday": generate_30min_slots("10:00", "12:00") + generate_30min_slots("15:00", "17:00"),
                        "friday": generate_30min_slots("09:00", "11:00"),
                        "saturday": generate_30min_slots("10:00", "13:00")
                    })
                ),
                Doctor(
                    name="Dr. Priya Sharma",
                    specialization="Dermatologist",
                    city="Mumbai",
                    state="Maharashtra",
                    address="B-205, Health Tower, Bandra West, Mumbai",
                    phone="+91-22-3456-7890",
                    email="dr.priya@skinwell.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("10:00", "13:00") + generate_30min_slots("15:00", "18:00"),
                        "tuesday": generate_30min_slots("09:00", "12:00") + generate_30min_slots("14:00", "17:00"),
                        "wednesday": generate_30min_slots("10:00", "13:00"),
                        "thursday": generate_30min_slots("09:00", "12:00") + generate_30min_slots("14:00", "17:00"),
                        "friday": generate_30min_slots("10:00", "13:00") + generate_30min_slots("15:00", "18:00")
                    })
                ),
                Doctor(
                    name="Dr. Amit Patel",
                    specialization="Orthopedic",
                    city="Bangalore",
                    state="Karnataka",
                    address="C-304, Bone Care Center, Koramangala, Bangalore",
                    phone="+91-80-4567-8901",
                    email="dr.amit@bonecare.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("08:00", "11:00") + generate_30min_slots("16:00", "19:00"),
                        "tuesday": generate_30min_slots("09:00", "12:00"),
                        "wednesday": generate_30min_slots("08:00", "11:00") + generate_30min_slots("16:00", "19:00"),
                        "thursday": generate_30min_slots("09:00", "12:00"),
                        "friday": generate_30min_slots("08:00", "11:00") + generate_30min_slots("16:00", "19:00"),
                        "saturday": generate_30min_slots("10:00", "13:00")
                    })
                ),
                Doctor(
                    name="Dr. Anjali Mehta",
                    specialization="Gynecologist",
                    city="Delhi",
                    state="Delhi",
                    address="D-506, Women's Health Center, Saket, Delhi",
                    phone="+91-11-5678-9012",
                    email="dr.anjali@womenshealth.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("09:30", "12:30"),
                        "tuesday": generate_30min_slots("14:00", "17:00"),
                        "wednesday": generate_30min_slots("10:00", "13:00"),
                        "thursday": generate_30min_slots("09:30", "12:30") + generate_30min_slots("15:00", "18:00"),
                        "friday": generate_30min_slots("11:00", "14:00"),
                        "saturday": generate_30min_slots("09:00", "12:00")
                    })
                ),
                Doctor(
                    name="Dr. Sanjay Verma",
                    specialization="Neurologist",
                    city="Mumbai",
                    state="Maharashtra",
                    address="E-707, Neuro Care Institute, Andheri East, Mumbai",
                    phone="+91-22-6789-0123",
                    email="dr.sanjay@neurocare.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("08:30", "11:30"),
                        "tuesday": generate_30min_slots("14:30", "17:30"),
                        "wednesday": generate_30min_slots("09:00", "12:00") + generate_30min_slots("16:00", "19:00"),
                        "thursday": generate_30min_slots("10:30", "13:30"),
                        "friday": generate_30min_slots("08:30", "11:30") + generate_30min_slots("15:00", "18:00")
                    })
                ),
                Doctor(
                    name="Dr. Neha Gupta",
                    specialization="Pediatrician",
                    city="Bangalore",
                    state="Karnataka",
                    address="F-808, Child Care Center, Whitefield, Bangalore",
                    phone="+91-80-7890-1234",
                    email="dr.neha@childcare.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("09:00", "12:00"),
                        "tuesday": generate_30min_slots("14:00", "17:00"),
                        "wednesday": generate_30min_slots("10:00", "13:00"),
                        "thursday": generate_30min_slots("09:00", "12:00") + generate_30min_slots("16:00", "19:00"),
                        "friday": generate_30min_slots("11:00", "14:00"),
                        "saturday": generate_30min_slots("09:00", "13:00")
                    })
                ),
                Doctor(
                    name="Dr. Ravi Menon",
                    specialization="General Physician",
                    city="Delhi",
                    state="Delhi",
                    address="G-909, City Health Clinic, Rajouri Garden, Delhi",
                    phone="+91-11-8901-2345",
                    email="dr.ravi@cityhealth.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("08:00", "13:00") + generate_30min_slots("16:00", "19:00"),
                        "tuesday": generate_30min_slots("09:00", "12:00") + generate_30min_slots("15:00", "18:00"),
                        "wednesday": generate_30min_slots("08:00", "13:00"),
                        "thursday": generate_30min_slots("09:00", "12:00") + generate_30min_slots("16:00", "19:00"),
                        "friday": generate_30min_slots("08:00", "13:00") + generate_30min_slots("15:00", "18:00"),
                        "saturday": generate_30min_slots("10:00", "14:00")
                    })
                ),
                Doctor(
                    name="Dr. Kavita Singh",
                    specialization="Dentist",
                    city="Mumbai",
                    state="Maharashtra",
                    address="H-1010, Dental Care Center, Powai, Mumbai",
                    phone="+91-22-9012-3456",
                    email="dr.kavita@dentalcare.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("09:00", "12:30") + generate_30min_slots("14:30", "18:00"),
                        "tuesday": generate_30min_slots("10:00", "13:00") + generate_30min_slots("15:00", "18:30"),
                        "wednesday": generate_30min_slots("08:30", "12:00"),
                        "thursday": generate_30min_slots("09:30", "13:30") + generate_30min_slots("15:30", "19:00"),
                        "friday": generate_30min_slots("08:00", "11:30") + generate_30min_slots("14:00", "17:30")
                    })
                ),
                Doctor(
                    name="Dr. Arjun Reddy",
                    specialization="Psychiatrist",
                    city="Bangalore",
                    state="Karnataka",
                    address="I-1111, Mind Wellness Center, Indiranagar, Bangalore",
                    phone="+91-80-0123-4567",
                    email="dr.arjun@mindwellness.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("10:00", "13:00"),
                        "tuesday": generate_30min_slots("14:00", "17:00"),
                        "wednesday": generate_30min_slots("09:00", "12:00") + generate_30min_slots("16:00", "19:00"),
                        "thursday": generate_30min_slots("11:00", "14:00"),
                        "friday": generate_30min_slots("09:30", "12:30") + generate_30min_slots("15:30", "18:30"),
                        "saturday": generate_30min_slots("10:00", "13:00")
                    })
                ),
                Doctor(
                    name="Dr. Meera Joshi",
                    specialization="Ophthalmologist",
                    city="Delhi",
                    state="Delhi",
                    address="J-1212, Eye Care Center, Greater Kailash, Delhi",
                    phone="+91-11-1234-5678",
                    email="dr.meera@eyecare.com",
                    availability=json.dumps({
                        "monday": generate_30min_slots("08:30", "11:30") + generate_30min_slots("15:00", "18:00"),
                        "tuesday": generate_30min_slots("09:30", "12:30"),
                        "wednesday": generate_30min_slots("08:00", "11:00") + generate_30min_slots("14:30", "17:30"),
                        "thursday": generate_30min_slots("10:00", "13:00") + generate_30min_slots("16:00", "19:00"),
                        "friday": generate_30min_slots("09:00", "12:00"),
                        "saturday": generate_30min_slots("08:30", "11:30")
                    })
                )
            ]
            
            session.add_all(sample_doctors)
            session.commit()
            print("✅ Sample doctors added to database")
            
            # Print sample availability for verification
            print("\n📋 Sample Doctor Availability (30-minute slots):")
            for doctor in sample_doctors:
                availability = json.loads(doctor.availability)
                print(f"\n👨‍⚕️ Dr. {doctor.name} - {doctor.specialization}")
                for day, slots in availability.items():
                    print(f"   {day.title()}: {len(slots)} slots")
                    if slots:
                        print(f"     Sample: {slots[0]} to {slots[-1]}")
            
        else:
            print("✅ Database already initialized")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add timedelta import for the generate_30min_slots function
from datetime import timedelta