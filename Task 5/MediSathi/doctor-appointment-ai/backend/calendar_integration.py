from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import pickle
import os

from src.utils.config import Config

class GoogleCalendarManager:
    def __init__(self):
        self.calendar_id = Config.GOOGLE_CALENDAR_ID
        self.service = self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        # This is a simplified version - you'll need to implement proper OAuth flow
        # For now, using service account or simplified approach
        try:
            # Using service account credentials
            from google.oauth2 import service_account
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            SERVICE_ACCOUNT_FILE = 'credentials/google_credentials.json'
            
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            
            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            print(f"Calendar authentication failed: {e}")
            return None
    
    def create_appointment_event(self, doctor_name: str, patient_name: str, 
                               patient_email: str, appointment_time: datetime, 
                               slot: str, description: str = ""):
        """Create calendar event for appointment"""
        try:
            if not self.service:
                return None
            
            end_time = appointment_time + timedelta(hours=1)  # 1-hour appointment
            
            event = {
                'summary': f'Appointment: {doctor_name} - {patient_name}',
                'description': f'Patient: {patient_name}\nEmail: {patient_email}\nSymptoms: {description}',
                'start': {
                    'dateTime': appointment_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': [
                    {'email': patient_email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return event.get('id')
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None
    
    def get_available_slots(self, date: datetime):
        """Get available slots from calendar"""
        try:
            if not self.service:
                return []
            
            start_time = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_time = datetime(date.year, date.month, date.day, 23, 59, 59)
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Calculate available slots (simplified)
            all_slots = [
                "09:00-10:00", "10:00-11:00", "11:00-12:00",
                "14:00-15:00", "15:00-16:00", "16:00-17:00"
            ]
            
            booked_slots = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                slot = start_time.strftime("%H:%M") + "-" + (start_time + timedelta(hours=1)).strftime("%H:%M")
                booked_slots.append(slot)
            
            available_slots = [slot for slot in all_slots if slot not in booked_slots]
            return available_slots
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []