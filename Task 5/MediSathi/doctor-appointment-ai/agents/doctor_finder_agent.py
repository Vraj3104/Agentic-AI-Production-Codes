# import google.generativeai as genai
# import requests
# from bs4 import BeautifulSoup
# import json
# import time
# from datetime import datetime
# import sys
# import os

# # Add parent directory to path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)

# from utils.config import Config
# from backend.database import SessionLocal, Doctor

# # Configure Gemini AI
# try:
#     genai.configure(api_key=Config.GEMINI_API_KEY)
# except:
#     print("⚠️  Gemini API key not configured")

# class DoctorFinderAgent:
#     def __init__(self):
#         self.model = genai.GenerativeModel('gemini-pro') if Config.GEMINI_API_KEY else None
    
#     def find_doctors_by_specialization(self, symptoms: str, city: str, state: str, max_results: int = 10):
#         """Find doctors based on symptoms and location using multiple sources"""
#         try:
#             # Step 1: Determine specialization from symptoms using AI
#             specialization = self._get_specialization_from_symptoms(symptoms)
            
#             # Step 2: Search in database first
#             database_doctors = self._search_doctors_in_database(specialization, city, state, max_results)
            
#             # Step 3: If not enough results, try web scraping
#             if len(database_doctors) < max_results:
#                 scraped_doctors = self._web_scrape_doctors(specialization, city, state, max_results - len(database_doctors))
#                 all_doctors = database_doctors + scraped_doctors
#             else:
#                 all_doctors = database_doctors
            
#             return {
#                 "suggested_specialization": specialization,
#                 "location": f"{city}, {state}",
#                 "doctors_found": len(all_doctors),
#                 "doctors": all_doctors[:max_results],
#                 "search_method": "database + web" if len(database_doctors) < max_results else "database"
#             }
            
#         except Exception as e:
#             print(f"❌ Error finding doctors: {e}")
#             return {
#                 "suggested_specialization": "General Physician",
#                 "location": f"{city}, {state}",
#                 "doctors_found": 0,
#                 "doctors": [],
#                 "error": str(e)
#             }
    
#     def _get_specialization_from_symptoms(self, symptoms: str):
#         """Use AI to determine medical specialization from symptoms"""
#         try:
#             if self.model:
#                 prompt = f"""
#                 Based on the following symptoms: "{symptoms}"
#                 Suggest the most appropriate medical specialization from this list:
#                 Cardiologist, Dermatologist, Orthopedic, Neurologist, Gastroenterologist, 
#                 Psychiatrist, Pediatrician, Gynecologist, Ophthalmologist, Dentist, 
#                 ENT Specialist, General Physician, Endocrinologist, Urologist, Pulmonologist
                
#                 Return only the specialization name. If unsure, return "General Physician".
#                 """
#                 response = self.model.generate_content(prompt)
#                 return response.text.strip()
#             else:
#                 # Fallback: simple keyword matching
#                 symptoms_lower = symptoms.lower()
#                 if any(word in symptoms_lower for word in ['heart', 'chest', 'blood pressure', 'cardio']):
#                     return "Cardiologist"
#                 elif any(word in symptoms_lower for word in ['skin', 'rash', 'acne', 'dermat']):
#                     return "Dermatologist"
#                 elif any(word in symptoms_lower for word in ['bone', 'joint', 'fracture', 'ortho']):
#                     return "Orthopedic"
#                 elif any(word in symptoms_lower for word in ['brain', 'nerve', 'headache', 'neuro']):
#                     return "Neurologist"
#                 elif any(word in symptoms_lower for word in ['child', 'pediatric', 'kids']):
#                     return "Pediatrician"
#                 else:
#                     return "General Physician"
                    
#         except Exception as e:
#             print(f"❌ Error determining specialization: {e}")
#             return "General Physician"
    
#     def _search_doctors_in_database(self, specialization: str, city: str, state: str, max_results: int):
#         """Search for doctors in the local database"""
#         session = SessionLocal()
#         try:
#             doctors = session.query(Doctor).filter(
#                 Doctor.specialization.ilike(f"%{specialization}%"),
#                 Doctor.city.ilike(f"%{city}%"),
#                 Doctor.state.ilike(f"%{state}%"),
#                 Doctor.is_active == True
#             ).limit(max_results).all()
            
#             result = []
#             for doctor in doctors:
#                 result.append({
#                     "name": doctor.name,
#                     "specialization": doctor.specialization,
#                     "address": doctor.address,
#                     "city": doctor.city,
#                     "state": doctor.state,
#                     "phone": doctor.phone,
#                     "email": doctor.email,
#                     "availability": self._parse_availability(doctor.availability),
#                     "source": "database",
#                     "rating": "4.5",  # Mock rating
#                     "experience": "10+ years"  # Mock experience
#                 })
            
#             return result
            
#         except Exception as e:
#             print(f"❌ Error searching database: {e}")
#             return []
#         finally:
#             session.close()
    
#     def _web_scrape_doctors(self, specialization: str, city: str, state: str, max_results: int):
#         """Web scrape doctor information from various sources"""
#         try:
#             doctors = []
            
#             # Method 1: Use JustDial API (simulated)
#             justdial_doctors = self._scrape_justdial(specialization, city, max_results)
#             doctors.extend(justdial_doctors)
            
#             # Method 2: Use Practo-like data (simulated)
#             practo_doctors = self._scrape_practo_like(specialization, city, max_results)
#             doctors.extend(practo_doctors)
            
#             # Method 3: Use government healthcare APIs (simulated)
#             govt_doctors = self._get_govt_healthcare_data(specialization, city, state, max_results)
#             doctors.extend(govt_doctors)
            
#             return doctors[:max_results]
            
#         except Exception as e:
#             print(f"❌ Web scraping error: {e}")
#             return []
    
#     def _scrape_justdial(self, specialization: str, city: str, max_results: int):
#         """Simulate JustDial scraping"""
#         try:
#             # Mock data - in real implementation, you would use requests + BeautifulSoup
#             mock_doctors = [
#                 {
#                     "name": f"Dr. {specialization} Expert",
#                     "specialization": specialization,
#                     "address": f"123 Health Street, {city}",
#                     "city": city,
#                     "state": "State",
#                     "phone": "+91-XXXX-XXXX",
#                     "email": f"contact@{specialization.lower().replace(' ', '')}.com",
#                     "availability": "Mon-Sat: 9AM-6PM",
#                     "source": "justdial",
#                     "rating": "4.3",
#                     "experience": "8 years"
#                 },
#                 {
#                     "name": f"Dr. Health Care Specialist",
#                     "specialization": specialization,
#                     "address": f"456 Medical Avenue, {city}",
#                     "city": city,
#                     "state": "State",
#                     "phone": "+91-YYYY-YYYY",
#                     "email": "info@healthcare.com",
#                     "availability": "Mon-Fri: 10AM-7PM",
#                     "source": "justdial",
#                     "rating": "4.7",
#                     "experience": "12 years"
#                 }
#             ]
#             return mock_doctors[:max_results]
#         except Exception as e:
#             print(f"❌ JustDial scraping error: {e}")
#             return []
    
#     def _scrape_practo_like(self, specialization: str, city: str, max_results: int):
#         """Simulate Practo-like platform scraping"""
#         try:
#             # Mock data
#             mock_doctors = [
#                 {
#                     "name": f"Dr. City {specialization}",
#                     "specialization": specialization,
#                     "address": f"789 Clinic Road, {city}",
#                     "city": city,
#                     "state": "State",
#                     "phone": "+91-ZZZZ-ZZZZ",
#                     "email": f"appointment@{specialization.lower()}.com",
#                     "availability": "Tue-Sat: 9AM-5PM",
#                     "source": "practo_like",
#                     "rating": "4.8",
#                     "experience": "15 years"
#                 }
#             ]
#             return mock_doctors[:max_results]
#         except Exception as e:
#             print(f"❌ Practo-like scraping error: {e}")
#             return []
    
#     def _get_govt_healthcare_data(self, specialization: str, city: str, state: str, max_results: int):
#         """Get government healthcare data (simulated)"""
#         try:
#             # Mock government hospital data
#             mock_doctors = [
#                 {
#                     "name": f"Dr. Government {specialization}",
#                     "specialization": specialization,
#                     "address": f"Government Hospital, {city}",
#                     "city": city,
#                     "state": state,
#                     "phone": "+91-GOVT-HOSP",
#                     "email": f"gh.{city}@gov.in",
#                     "availability": "Mon-Fri: 8AM-4PM",
#                     "source": "government",
#                     "rating": "4.2",
#                     "experience": "20+ years"
#                 }
#             ]
#             return mock_doctors[:max_results]
#         except Exception as e:
#             print(f"❌ Government data error: {e}")
#             return []
    
#     def _parse_availability(self, availability_str: str):
#         """Parse availability from string format"""
#         try:
#             if availability_str:
#                 availability = json.loads(availability_str)
#                 days = list(availability.keys())
#                 if days:
#                     return f"{days[0].title()}-{days[-1].title()}"
#             return "Contact for availability"
#         except:
#             return "Contact for availability"
    
#     def find_doctors_nearby(self, latitude: float, longitude: float, specialization: str = None, radius_km: int = 10):
#         """Find doctors near a location (would use GPS APIs in real implementation)"""
#         try:
#             # This would integrate with Google Places API or similar
#             # For now, return mock data
#             return {
#                 "location": f"Near coordinates ({latitude}, {longitude})",
#                 "radius": f"{radius_km} km",
#                 "doctors": [
#                     {
#                         "name": f"Dr. Nearby {specialization or 'Physician'}",
#                         "specialization": specialization or "General Physician",
#                         "address": "Near your location",
#                         "distance": "2.5 km",
#                         "phone": "+91-NEAR-BY",
#                         "rating": "4.5",
#                         "source": "location_based"
#                     }
#                 ]
#             }
#         except Exception as e:
#             return {"error": str(e)}

# # Global instance
# doctor_finder_agent = DoctorFinderAgent()














import google.generativeai as genai
import json
import sys
import os
from typing import List, Dict, Optional

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.config import Config
from agents.json_data_loader import json_data_loader  # Import the JSON data loader

# Configure Gemini AI
try:
    genai.configure(api_key=Config.GEMINI_API_KEY)
except:
    print("⚠️  Gemini API key not configured")

class DoctorFinderAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro') if Config.GEMINI_API_KEY else None
        self.data_loader = json_data_loader
    
    def find_doctors_by_symptoms(self, symptoms: str, city: str = None, max_results: int = 10) -> Dict:
        """
        Find doctors based on symptoms description
        Args:
            symptoms: Patient's symptoms description
            city: Optional city filter
            max_results: Maximum number of results to return
        Returns:
            Dictionary containing suggested specialization and matched doctors
        """
        try:
            # Step 1: Determine specialization from symptoms using AI
            specialization = self._get_specialization_from_symptoms(symptoms)
            
            # Step 2: Find doctors matching the specialization
            matched_doctors = self.data_loader.search_doctors_by_specialization(specialization)
            
            # Step 3: Apply city filter if provided
            if city:
                city_doctors = self.data_loader.search_doctors_by_city(city)
                # Intersection of specialization and city matches
                matched_doctors = [doc for doc in matched_doctors if doc in city_doctors]
            
            # Step 4: If no doctors found with AI specialization, try symptom-based matching
            if not matched_doctors:
                matched_doctors = self.data_loader.search_doctors_by_symptoms(symptoms)
            
            # Step 5: Limit results
            final_doctors = matched_doctors[:max_results]
            
            return {
                "success": True,
                "suggested_specialization": specialization,
                "symptoms": symptoms,
                "city_filter": city,
                "doctors_found": len(final_doctors),
                "doctors": final_doctors,
                "search_method": "AI + JSON data"
            }
            
        except Exception as e:
            print(f"❌ Error finding doctors: {e}")
            return {
                "success": False,
                "suggested_specialization": "General Physician",
                "symptoms": symptoms,
                "city_filter": city,
                "doctors_found": 0,
                "doctors": [],
                "error": str(e)
            }
    
    def find_doctors_by_specialization(self, specialization: str, city: str = None, max_results: int = 10) -> Dict:
        """
        Find doctors by specific specialization
        Args:
            specialization: Medical specialization
            city: Optional city filter
            max_results: Maximum number of results to return
        """
        try:
            matched_doctors = self.data_loader.search_doctors_by_specialization(specialization)
            
            if city:
                city_doctors = self.data_loader.search_doctors_by_city(city)
                matched_doctors = [doc for doc in matched_doctors if doc in city_doctors]
            
            final_doctors = matched_doctors[:max_results]
            
            return {
                "success": True,
                "specialization": specialization,
                "city_filter": city,
                "doctors_found": len(final_doctors),
                "doctors": final_doctors
            }
            
        except Exception as e:
            print(f"❌ Error finding doctors by specialization: {e}")
            return {
                "success": False,
                "specialization": specialization,
                "city_filter": city,
                "doctors_found": 0,
                "doctors": [],
                "error": str(e)
            }
    
    def _get_specialization_from_symptoms(self, symptoms: str) -> str:
        """Use AI to determine medical specialization from symptoms"""
        try:
            if self.model:
                prompt = f"""
                Based on the following symptoms: "{symptoms}"
                Suggest the most appropriate medical specialization.
                
                Common specializations:
                - Cardiologist (heart, chest pain, blood pressure)
                - Dermatologist (skin, rash, acne)
                - Orthopedic (bone, joint, fracture)
                - Neurologist (brain, headache, nerve)
                - Pediatrician (child, kids, baby)
                - Gynecologist (pregnancy, women health)
                - Ophthalmologist (eye, vision)
                - Dentist (teeth, dental)
                - ENT Specialist (ear, nose, throat)
                - Nephrologist (kidney, renal)
                - Gastroenterologist (stomach, digestive)
                - Psychiatrist (mental health)
                - General Physician (general health issues)
                
                Return only the specialization name. If unsure, return "General Physician".
                """
                response = self.model.generate_content(prompt)
                return response.text.strip()
            else:
                # Fallback: keyword matching
                return self._get_specialization_from_keywords(symptoms)
                    
        except Exception as e:
            print(f"❌ Error determining specialization: {e}")
            return "General Physician"
    
    def _get_specialization_from_keywords(self, symptoms: str) -> str:
        """Fallback method to determine specialization using keyword matching"""
        symptoms_lower = symptoms.lower()
        
        keyword_mapping = {
            'cardiologist': ['heart', 'chest', 'blood pressure', 'cardio', 'hypertension', 'cholesterol'],
            'dermatologist': ['skin', 'rash', 'acne', 'dermat', 'allergy', 'itching', 'eczema'],
            'orthopedic': ['bone', 'joint', 'fracture', 'ortho', 'pain', 'arthritis', 'back pain'],
            'neurologist': ['brain', 'nerve', 'headache', 'neuro', 'migraine', 'seizure', 'stroke'],
            'pediatrician': ['child', 'pediatric', 'kids', 'baby', 'children', 'infant'],
            'gynecologist': ['pregnancy', 'women', 'gynec', 'menstrual', 'pregnant', 'ovary'],
            'ophthalmologist': ['eye', 'vision', 'ophthal', 'cataract', 'glaucoma', 'retina'],
            'dentist': ['teeth', 'dental', 'tooth', 'gum', 'oral', 'cavity'],
            'ent specialist': ['ear', 'nose', 'throat', 'ent', 'sinus', 'tonsil', 'hearing'],
            'nephrologist': ['kidney', 'renal', 'nephro', 'dialysis', 'urine'],
            'gastroenterologist': ['stomach', 'gastro', 'digestive', 'liver', 'abdomen', 'ulcer'],
            'psychiatrist': ['mental', 'psych', 'depression', 'anxiety', 'stress', 'therapy']
        }
        
        for specialization, keywords in keyword_mapping.items():
            for keyword in keywords:
                if keyword in symptoms_lower:
                    return specialization.capitalize()
        
        return "General Physician"
    
    def get_available_specializations(self) -> List[str]:
        """Get list of all available specializations from the data"""
        return self.data_loader.get_unique_specializations()
    
    def get_available_cities(self) -> List[str]:
        """Get list of all available cities from the data"""
        return self.data_loader.get_unique_cities()
    
    def get_doctor_statistics(self) -> Dict:
        """Get statistics about the available doctors data"""
        all_doctors = self.data_loader.get_all_doctors()
        specializations = self.get_available_specializations()
        cities = self.get_available_cities()
        
        return {
            "total_doctors": len(all_doctors),
            "total_specializations": len(specializations),
            "total_cities": len(cities),
            "specializations": specializations,
            "cities": cities
        }

# Global instance
doctor_finder_agent = DoctorFinderAgent()