import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import os

from utils.config import Config

class GoogleSheetsManager:
    def __init__(self):
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.creds = None
        self.client = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Define the scope
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Use service account credentials
            creds_path = 'credentials/google_credentials.json'
            if os.path.exists(creds_path):
                self.creds = Credentials.from_service_account_file(creds_path, scopes=scope)
                self.client = gspread.authorize(self.creds)
                print("✅ Google Sheets authentication successful")
            else:
                print("❌ Google credentials file not found. Using mock mode.")
                self.client = None
                
        except Exception as e:
            print(f"❌ Google Sheets authentication failed: {e}")
            self.client = None
    
    def add_appointment_record(self, appointment_data: dict):
        """Add appointment record to Google Sheets"""
        try:
            if not self.client:
                print("📝 Mock: Appointment data would be added to Google Sheets")
                print(f"📝 Data: {appointment_data}")
                return {"status": "success", "message": "Mock - Record would be added to sheet"}
            
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(self.sheet_id)
            worksheet = spreadsheet.sheet1
            
            # Prepare data row
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                appointment_data.get('appointment_id', 'N/A'),
                appointment_data.get('patient_name', 'N/A'),
                appointment_data.get('patient_email', 'N/A'),
                appointment_data.get('patient_phone', 'N/A'),
                appointment_data.get('doctor_name', 'N/A'),
                appointment_data.get('doctor_specialization', 'N/A'),
                appointment_data.get('appointment_date', 'N/A'),
                appointment_data.get('appointment_time', 'N/A'),
                appointment_data.get('symptoms', 'N/A'),
                appointment_data.get('status', 'scheduled'),
                appointment_data.get('clinic_address', 'N/A'),
                appointment_data.get('doctor_phone', 'N/A')
            ]
            
            # Append the row
            worksheet.append_row(row)
            print(f"✅ Appointment record added to Google Sheets: {appointment_data['appointment_id']}")
            return {"status": "success", "message": "Record added to sheet"}
            
        except Exception as e:
            print(f"❌ Error adding to Google Sheets: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_appointment_records(self, date: str = None):
        """Get appointment records from Google Sheets"""
        try:
            if not self.client:
                print("📝 Mock: Returning sample appointment data")
                return [
                    {
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Appointment ID": "APT001",
                        "Patient Name": "Sample Patient",
                        "Patient Email": "sample@email.com",
                        "Doctor Name": "Dr. Sample Doctor",
                        "Date": "2024-01-15",
                        "Time": "10:00-10:30",
                        "Status": "scheduled"
                    }
                ]
            
            spreadsheet = self.client.open_by_key(self.sheet_id)
            worksheet = spreadsheet.sheet1
            records = worksheet.get_all_records()
            
            if date:
                records = [r for r in records if r.get('Date', '').startswith(date)]
            
            return records
            
        except Exception as e:
            print(f"❌ Error reading from Google Sheets: {e}")
            return []
    
    def create_sheet_if_not_exists(self):
        """Create the sheet with headers if it doesn't exist"""
        try:
            if not self.client:
                print("📝 Mock: Sheet would be created")
                return
            
            spreadsheet = self.client.open_by_key(self.sheet_id)
            worksheet = spreadsheet.sheet1
            
            # Check if headers exist
            existing_headers = worksheet.row_values(1)
            if not existing_headers:
                headers = [
                    "Timestamp", "Appointment ID", "Patient Name", "Patient Email", 
                    "Patient Phone", "Doctor Name", "Doctor Specialization",
                    "Appointment Date", "Appointment Time", "Symptoms", 
                    "Status", "Clinic Address", "Doctor Contact"
                ]
                worksheet.append_row(headers)
                print("✅ Google Sheets headers created")
                
        except Exception as e:
            print(f"❌ Error creating sheet: {e}")

# Global instance
google_sheets_manager = GoogleSheetsManager()