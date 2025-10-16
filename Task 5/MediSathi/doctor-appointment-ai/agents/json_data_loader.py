import json
import os
from typing import List, Dict, Optional
import logging

class JSONDataLoader:
    def __init__(self, json_file_path: str = "data/doctor_new.json"):
        self.json_file_path = json_file_path
        self.doctors_data = []
        self.logger = logging.getLogger(__name__)
        self.load_doctors_data()
    
    def load_doctors_data(self) -> bool:
        """Load doctors data from JSON file"""
        try:
            if not os.path.exists(self.json_file_path):
                self.logger.error(f"JSON file not found: {self.json_file_path}")
                return False
            
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single doctor object and array of doctors
            if isinstance(data, dict):
                self.doctors_data = [data]
            elif isinstance(data, list):
                self.doctors_data = data
            else:
                self.logger.error("Invalid JSON format")
                return False
            
            self.logger.info(f"Loaded {len(self.doctors_data)} doctors from JSON file")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading JSON data: {e}")
            return False
    
    def get_all_doctors(self) -> List[Dict]:
        """Get all doctors from the JSON file"""
        return self.doctors_data
    
    def search_doctors_by_specialization(self, specialization: str) -> List[Dict]:
        """Search doctors by specialization"""
        try:
            specialization_lower = specialization.lower()
            matched_doctors = []
            
            for doctor in self.doctors_data:
                doctor_speciality = doctor.get("Speciality", "").lower()
                doctor_name = doctor.get("Name", "").lower()
                
                # Check if specialization matches in speciality or name
                if (specialization_lower in doctor_speciality or 
                    specialization_lower in doctor_name):
                    matched_doctors.append(doctor)
            
            return matched_doctors
            
        except Exception as e:
            self.logger.error(f"Error searching doctors by specialization: {e}")
            return []
    
    def search_doctors_by_city(self, city: str) -> List[Dict]:
        """Search doctors by city"""
        try:
            city_lower = city.lower()
            matched_doctors = []
            
            for doctor in self.doctors_data:
                doctor_city = doctor.get("City", "").lower()
                if city_lower in doctor_city:
                    matched_doctors.append(doctor)
            
            return matched_doctors
            
        except Exception as e:
            self.logger.error(f"Error searching doctors by city: {e}")
            return []
    
    def search_doctors_by_symptoms(self, symptoms: str, specialization_map: Dict[str, List[str]] = None) -> List[Dict]:
        """Search doctors based on symptoms using keyword matching"""
        try:
            symptoms_lower = symptoms.lower()
            
            # Default specialization mapping based on symptoms
            if specialization_map is None:
                specialization_map = {
                    'cardiology': ['heart', 'chest', 'blood pressure', 'cardio', 'hypertension'],
                    'dermatology': ['skin', 'rash', 'acne', 'dermat', 'allergy', 'itching'],
                    'orthopedics': ['bone', 'joint', 'fracture', 'ortho', 'pain', 'arthritis'],
                    'neurology': ['brain', 'nerve', 'headache', 'neuro', 'migraine', 'seizure'],
                    'pediatrics': ['child', 'pediatric', 'kids', 'baby', 'children'],
                    'gynecology': ['pregnancy', 'women', 'gynec', 'menstrual', 'pregnant'],
                    'ophthalmology': ['eye', 'vision', 'ophthal', 'cataract', 'glaucoma'],
                    'dentistry': ['teeth', 'dental', 'tooth', 'gum', 'oral'],
                    'ent': ['ear', 'nose', 'throat', 'ent', 'sinus', 'tonsil'],
                    'nephrology': ['kidney', 'renal', 'nephro', 'dialysis'],
                    'gastroenterology': ['stomach', 'gastro', 'digestive', 'liver', 'abdomen'],
                    'psychiatry': ['mental', 'psych', 'depression', 'anxiety', 'stress']
                }
            
            # Find matching specializations based on symptoms
            matched_specializations = []
            for spec, keywords in specialization_map.items():
                for keyword in keywords:
                    if keyword in symptoms_lower:
                        matched_specializations.append(spec)
                        break
            
            # If no specific match, default to general physician
            if not matched_specializations:
                matched_specializations = ['general physician', 'physician']
            
            # Find doctors matching these specializations
            matched_doctors = []
            for doctor in self.doctors_data:
                doctor_speciality = doctor.get("Speciality", "").lower()
                for spec in matched_specializations:
                    if spec in doctor_speciality:
                        matched_doctors.append(doctor)
                        break
            
            return matched_doctors
            
        except Exception as e:
            self.logger.error(f"Error searching doctors by symptoms: {e}")
            return []
    
    def get_doctors_by_fee_range(self, min_fee: int = 0, max_fee: int = 10000) -> List[Dict]:
        """Get doctors by consultation fee range"""
        try:
            matched_doctors = []
            
            for doctor in self.doctors_data:
                fee_text = doctor.get("Consult Fee", "₹0")
                # Extract numeric value from fee text
                fee_value = self._extract_fee_value(fee_text)
                
                if min_fee <= fee_value <= max_fee:
                    matched_doctors.append(doctor)
            
            return matched_doctors
            
        except Exception as e:
            self.logger.error(f"Error filtering doctors by fee: {e}")
            return []
    
    def _extract_fee_value(self, fee_text: str) -> int:
        """Extract numeric fee value from fee text"""
        try:
            # Remove currency symbols and extract numbers
            import re
            numbers = re.findall(r'\d+', fee_text.replace('₹', '').replace(',', ''))
            if numbers:
                return int(numbers[0])
            return 0
        except:
            return 0
    
    def get_unique_specializations(self) -> List[str]:
        """Get list of unique specializations available"""
        specializations = set()
        for doctor in self.doctors_data:
            spec = doctor.get("Speciality", "")
            if spec:
                specializations.add(spec)
        return sorted(list(specializations))
    
    def get_unique_cities(self) -> List[str]:
        """Get list of unique cities available"""
        cities = set()
        for doctor in self.doctors_data:
            city = doctor.get("City", "")
            if city:
                cities.add(city)
        return sorted(list(cities))

# Global instance
json_data_loader = JSONDataLoader()