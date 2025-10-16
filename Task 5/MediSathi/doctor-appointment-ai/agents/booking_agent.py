import google.generativeai as genai
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from datetime import datetime, timedelta
import json

from src.utils.config import Config
from src.backend.database import SessionLocal, Doctor, Appointment
from src.backend.calendar_integration import GoogleCalendarManager

genai.configure(api_key=Config.GEMINI_API_KEY)

class BookingAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.calendar_manager = GoogleCalendarManager()
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
    def find_available_doctors(self, symptoms: str, specialization: str = None):
        """Find available doctors based on symptoms"""
        session = SessionLocal()
        
        try:
            # Use Gemini to suggest specialization based on symptoms
            if not specialization:
                prompt = f"""
                Based on the following symptoms: {symptoms}
                Suggest the most appropriate medical specialization. 
                Return only the specialization name.
                """
                response = self.model.generate_content(prompt)
                specialization = response.text.strip()
            
            # Find doctors with matching specialization
            doctors = session.query(Doctor).filter(
                Doctor.specialization.ilike(f"%{specialization}%"),
                Doctor.is_active == True
            ).all()
            
            return {
                "suggested_specialization": specialization,
                "available_doctors": [
                    {
                        "id": doc.id,
                        "name": doc.name,
                        "specialization": doc.specialization,
                        "city": doc.city,
                        "state": doc.state,
                        "address": doc.address
                    }
                    for doc in doctors
                ]
            }
        finally:
            session.close()
    
    def get_available_slots(self, doctor_id: int, date: str = None):
        """Get available time slots for a doctor"""
        session = SessionLocal()
        
        try:
            doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
            if not doctor:
                return {"error": "Doctor not found"}
            
            availability = json.loads(doctor.availability)
            today = datetime.now().date()
            
            if not date:
                date = today.isoformat()
            
            target_date = datetime.fromisoformat(date).date()
            day_name = target_date.strftime("%A").lower()
            
            if day_name not in availability:
                return {"available_slots": []}
            
            # Get existing appointments for that day
            appointments = session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date >= datetime.combine(target_date, datetime.min.time()),
                Appointment.appointment_date < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
            ).all()
            
            booked_slots = [
                app.appointment_date.strftime("%H:%M") 
                for app in appointments
                if app.status == "scheduled"
            ]
            
            available_slots = []
            for slot in availability[day_name]:
                start_time = slot.split("-")[0]
                if start_time not in booked_slots:
                    available_slots.append(slot)
            
            return {
                "doctor_name": doctor.name,
                "date": date,
                "available_slots": available_slots
            }
        finally:
            session.close()
    
    def book_appointment(self, patient_data: dict, doctor_id: int, slot: str, date: str):
        """Book an appointment"""
        session = SessionLocal()
        
        try:
            doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
            if not doctor:
                return {"error": "Doctor not found"}
            
            # Parse slot and create datetime
            start_time_str = slot.split("-")[0]
            appointment_datetime = datetime.fromisoformat(f"{date} {start_time_str}")
            
            # Check if slot is still available
            existing_appointment = session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_datetime,
                Appointment.status == "scheduled"
            ).first()
            
            if existing_appointment:
                return {"error": "Slot already booked"}
            
            # Create appointment
            appointment = Appointment(
                patient_id=1,  # In real scenario, create/retrieve patient
                doctor_id=doctor_id,
                appointment_date=appointment_datetime,
                description=patient_data.get('description', ''),
                status="scheduled"
            )
            
            session.add(appointment)
            session.commit()
            
            # Add to Google Calendar
            event_id = self.calendar_manager.create_appointment_event(
                doctor.name,
                patient_data['name'],
                patient_data['email'],
                appointment_datetime,
                slot,
                patient_data.get('description', '')
            )
            
            if event_id:
                appointment.google_calendar_event_id = event_id
                session.commit()
            
            return {
                "success": True,
                "appointment_id": appointment.id,
                "doctor_name": doctor.name,
                "date": date,
                "time": slot,
                "event_id": event_id
            }
        finally:
            session.close()

    def process_booking_request(self, user_input: str):
        """Process natural language booking request"""
        prompt = f"""
        You are a medical appointment booking assistant. Extract the following information from the user input:
        - Patient name
        - Email
        - Symptoms/description of disease
        - Preferred date (if mentioned)
        - Preferred time (if mentioned)
        - Preferred specialization (if mentioned)
        
        User Input: {user_input}
        
        Return as JSON format with keys: name, email, description, preferred_date, preferred_time, preferred_specialization
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)

booking_agent = BookingAgent()