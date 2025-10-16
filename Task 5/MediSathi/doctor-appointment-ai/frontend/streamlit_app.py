# import streamlit as st
# import sys
# import os
# from datetime import datetime, timedelta
# import json

# # Add current directory to path for imports
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)

# try:
#     from backend.database import SessionLocal, Doctor, Appointment, init_db
#     from agents.notification_agent import notification_agent
#     from agents.doctor_finder_agent import doctor_finder_agent
#     from backend.google_sheets import google_sheets_manager
#     st.success("✅ All modules imported successfully!")
# except ImportError as e:
#     st.error(f"❌ Import error: {e}")
#     st.stop()

# # Initialize database and Google Sheets
# try:
#     init_db()
#     google_sheets_manager.create_sheet_if_not_exists()
# except Exception as e:
#     st.error(f"❌ Initialization failed: {e}")

# try:
#     from backend.database import SessionLocal, Doctor, Appointment, init_db
#     from agents.notification_agent import notification_agent
#     st.success("✅ All modules imported successfully!")
# except ImportError as e:
#     st.error(f"❌ Import error: {e}")
#     st.info("Trying alternative import approach...")
    
#     # Alternative import approach
#     try:
#         import importlib.util
#         spec = importlib.util.spec_from_file_location("database", os.path.join(parent_dir, "backend", "database.py"))
#         database_module = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(database_module)
        
#         spec2 = importlib.util.spec_from_file_location("notification_agent", os.path.join(parent_dir, "agents", "notification_agent.py"))
#         notification_module = importlib.util.module_from_spec(spec2)
#         spec2.loader.exec_module(notification_module)
        
#         SessionLocal = database_module.SessionLocal
#         Doctor = database_module.Doctor
#         Appointment = database_module.Appointment
#         init_db = database_module.init_db
#         notification_agent = notification_module.notification_agent
        
#         st.success("✅ Modules imported using alternative approach!")
#     except Exception as alt_e:
#         st.error(f"❌ Alternative import also failed: {alt_e}")
#         st.stop()

# # Add current directory to path for imports
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)

# try:
#     from backend.database import SessionLocal, Doctor, Appointment, init_db
#     from agents.notification_agent import notification_agent
#     st.success("✅ All modules imported successfully!")
# except ImportError as e:
#     st.error(f"❌ Import error: {e}")
#     st.stop()

# # Initialize database
# try:
#     init_db()
# except Exception as e:
#     st.error(f"❌ Database initialization failed: {e}")

# st.set_page_config(
#     page_title="MediSathi - AI Doctor Appointment",
#     page_icon="🏥",
#     layout="wide"
# )

# def generate_time_slots():
#     """Generate time slots in 30-minute intervals"""
#     slots = []
#     start_time = datetime.strptime("09:00", "%H:%M")
#     end_time = datetime.strptime("18:00", "%H:%M")
    
#     current_time = start_time
#     while current_time < end_time:
#         slot_end = current_time + timedelta(minutes=30)
#         slots.append(f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}")
#         current_time = slot_end
    
#     return slots

# def get_available_slots(doctor_id, selected_date):
#     """Get available time slots for a doctor on a specific date"""
#     session = SessionLocal()
#     try:
#         # Get doctor's availability
#         doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
#         if not doctor or not doctor.availability:
#             return []
        
#         # Parse availability
#         availability = eval(doctor.availability) if doctor.availability else {}
#         day_name = selected_date.strftime("%A").lower()
        
#         if day_name not in availability:
#             return []
        
#         # Get all possible slots for the day
#         all_slots = availability[day_name]
        
#         # Get booked appointments for that day
#         start_of_day = datetime.combine(selected_date, datetime.min.time())
#         end_of_day = start_of_day + timedelta(days=1)
        
#         booked_appointments = session.query(Appointment).filter(
#             Appointment.doctor_id == doctor_id,
#             Appointment.appointment_date >= start_of_day,
#             Appointment.appointment_date < end_of_day,
#             Appointment.status == "scheduled"
#         ).all()
        
#         # Extract booked time slots
#         booked_slots = []
#         for appointment in booked_appointments:
#             appointment_time = appointment.appointment_date.strftime("%H:%M")
#             # Find which slot this appointment falls into
#             for slot in all_slots:
#                 start_time = slot.split("-")[0]
#                 if start_time == appointment_time:
#                     booked_slots.append(slot)
#                     break
        
#         # Return available slots
#         available_slots = [slot for slot in all_slots if slot not in booked_slots]
#         return available_slots
        
#     except Exception as e:
#         st.error(f"Error getting available slots: {e}")
#         return []
#     finally:
#         session.close()

# def book_appointment(patient_data, doctor_id, selected_date, selected_slot):
#     """Book an appointment and send confirmation"""
#     session = SessionLocal()
#     try:
#         # Parse the selected slot to get start time
#         start_time_str = selected_slot.split("-")[0]
#         appointment_datetime = datetime.combine(selected_date, 
#                                               datetime.strptime(start_time_str, "%H:%M").time())
        
#         # Create appointment
#         appointment = Appointment(
#             patient_id=1,  # In real scenario, create patient record
#             doctor_id=doctor_id,
#             appointment_date=appointment_datetime,
#             description=patient_data.get('symptoms', ''),
#             status="scheduled"
#         )
        
#         session.add(appointment)
#         session.commit()
        
#         # Get doctor details
#         doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        
#         # Prepare appointment details
#         appointment_details = {
#             'appointment_id': appointment.id,
#             'patient_name': patient_data['name'],
#             'patient_email': patient_data['email'],
#             'patient_phone': patient_data.get('phone', 'N/A'),
#             'doctor_name': doctor.name,
#             'doctor_specialization': doctor.specialization,
#             'appointment_date': selected_date.strftime("%Y-%m-%d"),
#             'appointment_time': selected_slot,
#             'symptoms': patient_data.get('symptoms', ''),
#             'clinic_address': doctor.address,
#             'doctor_phone': doctor.phone,
#             'status': 'scheduled'
#         }
        
#         # Send confirmation email
#         email_result = notification_agent.send_appointment_confirmation(
#             patient_data['email'],
#             appointment_details
#         )
        
#         # Add to Google Sheets
#         sheets_result = google_sheets_manager.add_appointment_record(appointment_details)
        
#         return {
#             'success': True,
#             'appointment_id': appointment.id,
#             'email_result': email_result,
#             'sheets_result': sheets_result,
#             'appointment_details': appointment_details
#         }
        
#     except Exception as e:
#         session.rollback()
#         return {'success': False, 'error': str(e)}
#     finally:
#         session.close()

# def main():
#     st.title("🏥 MediSathi - AI Doctor Appointment System")
#     st.markdown("### Your Intelligent Healthcare Assistant")
    
#     # Initialize session state
#     if 'booking_data' not in st.session_state:
#         st.session_state.booking_data = {}
#     if 'selected_doctor' not in st.session_state:
#         st.session_state.selected_doctor = None
#     if 'show_doctors' not in st.session_state:
#         st.session_state.show_doctors = False
#     if 'show_date_selection' not in st.session_state:
#         st.session_state.show_date_selection = False
#     if 'show_time_selection' not in st.session_state:
#         st.session_state.show_time_selection = False
#     if 'booking_confirmed' not in st.session_state:
#         st.session_state.booking_confirmed = False
    
#     tab1, tab2, tab3 = st.tabs(["Book Appointment", "Find Doctors", "My Appointments"])
    
#     with tab1:
#         st.header("Book Doctor Appointment")
        
#         # Step 1: Patient Information
#         if not st.session_state.show_doctors and not st.session_state.show_date_selection:
#             with st.form("patient_info_form"):
#                 st.subheader("Step 1: Patient Information")
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     name = st.text_input("Full Name *", placeholder="Enter your full name")
#                     email = st.text_input("Email *", placeholder="your.email@example.com")
                
#                 with col2:
#                     phone = st.text_input("Phone Number *", placeholder="+91 XXXXX XXXXX")
#                     age = st.number_input("Age *", min_value=1, max_value=120, value=30)
                
#                 symptoms = st.text_area("Describe your symptoms *", 
#                                       placeholder="Example: Fever, cough, and headache for 3 days...",
#                                       height=100)
                
#                 submitted = st.form_submit_button("Find Available Doctors")
                
#                 if submitted:
#                     if not all([name, email, phone, symptoms]):
#                         st.error("Please fill in all required fields (*)")
#                     else:
#                         st.session_state.booking_data = {
#                             'name': name,
#                             'email': email,
#                             'phone': phone,
#                             'age': age,
#                             'symptoms': symptoms
#                         }
#                         st.session_state.show_doctors = True
#                         st.rerun()
        
#         # Step 2: Doctor Selection
#         elif st.session_state.show_doctors and not st.session_state.show_date_selection:
#             st.subheader("Step 2: Select Doctor")
#             st.info(f"Patient: {st.session_state.booking_data['name']}")
            
#             # Get available doctors from database
#             session = SessionLocal()
#             doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
#             session.close()
            
#             if doctors:
#                 for doctor in doctors:
#                     with st.expander(f"👨‍⚕️ Dr. {doctor.name} - {doctor.specialization}", expanded=False):
#                         col1, col2 = st.columns([3, 1])
                        
#                         with col1:
#                             st.write(f"**📍 Location:** {doctor.city}, {doctor.state}")
#                             st.write(f"**🏢 Address:** {doctor.address}")
#                             st.write(f"**📞 Contact:** {doctor.phone}")
#                             st.write(f"**📧 Email:** {doctor.email}")
                            
#                             # Show availability
#                             try:
#                                 availability = eval(doctor.availability) if doctor.availability else {}
#                                 if availability:
#                                     st.write("**🕒 Available Days:**")
#                                     for day, slots in availability.items():
#                                         st.write(f"   - {day.title()}: {', '.join(slots)}")
#                             except:
#                                 st.write("**🕒 Availability:** Contact for timings")
                        
#                         with col2:
#                             if st.button("Select Doctor", key=f"select_{doctor.id}", use_container_width=True):
#                                 st.session_state.selected_doctor = doctor
#                                 st.session_state.show_date_selection = True
#                                 st.rerun()
                
#                 if st.button("← Back to Patient Info"):
#                     st.session_state.show_doctors = False
#                     st.rerun()
#             else:
#                 st.warning("No doctors available at the moment.")
#                 if st.button("← Back to Patient Info"):
#                     st.session_state.show_doctors = False
#                     st.rerun()
        
#         # Step 3: Date Selection
#         elif st.session_state.show_date_selection and not st.session_state.show_time_selection:
#             st.subheader("Step 3: Select Date")
#             st.info(f"Doctor: Dr. {st.session_state.selected_doctor.name}")
            
#             # Date selection
#             min_date = datetime.now().date()
#             max_date = min_date + timedelta(days=30)
#             selected_date = st.date_input(
#                 "Select Appointment Date",
#                 min_value=min_date,
#                 max_value=max_date,
#                 value=min_date
#             )
            
#             if selected_date:
#                 # Check if selected date is available
#                 available_slots = get_available_slots(
#                     st.session_state.selected_doctor.id, 
#                     selected_date
#                 )
                
#                 if available_slots:
#                     st.success(f"Available on {selected_date.strftime('%A, %B %d, %Y')}")
#                     if st.button("Proceed to Time Selection →"):
#                         st.session_state.selected_date = selected_date
#                         st.session_state.available_slots = available_slots
#                         st.session_state.show_time_selection = True
#                         st.rerun()
#                 else:
#                     st.warning(f"No available slots on {selected_date.strftime('%A, %B %d, %Y')}")
#                     st.info("Please select a different date")
            
#             if st.button("← Back to Doctor Selection"):
#                 st.session_state.show_date_selection = False
#                 st.rerun()
        
#         # Step 4: Time Selection
#         elif st.session_state.show_time_selection and not st.session_state.booking_confirmed:
#             st.subheader("Step 4: Select Time Slot")
#             st.info(f"Doctor: Dr. {st.session_state.selected_doctor.name}")
#             st.info(f"Date: {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
            
#             if st.session_state.available_slots:
#                 selected_slot = st.radio(
#                     "Available Time Slots:",
#                     st.session_state.available_slots,
#                     format_func=lambda x: f"{x.split('-')[0]} - {x.split('-')[1]}"
#                 )
                
#                 col1, col2, col3 = st.columns([1, 1, 1])
                
#                 with col2:
#                     if st.button("Confirm Booking", type="primary", use_container_width=True):
#                         # Book the appointment
#                         result = book_appointment(
#                             st.session_state.booking_data,
#                             st.session_state.selected_doctor.id,
#                             st.session_state.selected_date,
#                             selected_slot
#                         )
                        
#                         if result['success']:
#                             st.session_state.booking_result = result
#                             st.session_state.booking_confirmed = True
#                             st.rerun()
#                         else:
#                             st.error(f"Booking failed: {result['error']}")
                
#                 with col1:
#                     if st.button("← Back to Date Selection"):
#                         st.session_state.show_time_selection = False
#                         st.rerun()
                
#                 with col3:
#                     if st.button("🔄 Change Doctor"):
#                         st.session_state.show_doctors = False
#                         st.session_state.show_date_selection = False
#                         st.session_state.show_time_selection = False
#                         st.rerun()
#             else:
#                 st.error("No time slots available for selected date")
#                 if st.button("← Back to Date Selection"):
#                     st.session_state.show_time_selection = False
#                     st.rerun()
        
#         # Step 5: Booking Confirmation
#         elif st.session_state.booking_confirmed:
#             st.subheader("🎉 Appointment Confirmed!")
#             st.balloons()
            
#             result = st.session_state.booking_result
#             details = result['appointment_details']
            
#             # Display confirmation details
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.success("**Appointment Details:**")
#                 st.write(f"**Appointment ID:** #{details['appointment_id']}")
#                 st.write(f"**Patient:** {details['patient_name']}")
#                 st.write(f"**Doctor:** Dr. {details['doctor_name']}")
#                 st.write(f"**Specialization:** {details['doctor_specialization']}")
#                 st.write(f"**Date:** {details['date']}")
#                 st.write(f"**Time:** {details['time']}")
#                 st.write(f"**Clinic:** {details['clinic_address']}")
#                 st.write(f"**Contact:** {details['doctor_phone']}")
            
#             with col2:
#                 st.success("**Confirmation Email Sent**")
#                 st.write(f"✅ Confirmation email sent to: {details['patient_email']}")
#                 st.write("📧 Please check your inbox (and spam folder)")
#                 st.write("📱 You will also receive a reminder before your appointment")
                
#                 st.info("""
#                 **Important Notes:**
#                 - Please arrive 15 minutes before your appointment
#                 - Bring your ID and any medical reports
#                 - Cancel at least 24 hours in advance if needed
#                 """)
            
#             if st.button("Book Another Appointment"):
#                 # Reset all session states
#                 for key in list(st.session_state.keys()):
#                     if key != 'rerun':
#                         del st.session_state[key]
#                 st.rerun()
    
#     with tab2:
#         st.header("Find Doctors")
        
#         # Search form
#         with st.form("search_doctors_form"):
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 specialization = st.selectbox(
#                     "Specialization",
#                     ["All Specializations", "Cardiologist", "Dermatologist", "Orthopedic", 
#                      "Neurologist", "General Physician", "Pediatrician", "Gynecologist"]
#                 )
#                 city = st.text_input("City *", placeholder="Enter your city")
            
#             with col2:
#                 state = st.text_input("State *", placeholder="Enter your state")
#                 search_btn = st.form_submit_button("🔍 Search Doctors")
            
#             if search_btn:
#                 if not city or not state:
#                     st.error("Please enter both city and state")
#                 else:
#                     session = SessionLocal()
                    
#                     if specialization == "All Specializations":
#                         doctors = session.query(Doctor).filter(
#                             Doctor.city.ilike(f"%{city}%"),
#                             Doctor.state.ilike(f"%{state}%"),
#                             Doctor.is_active == True
#                         ).all()
#                     else:
#                         doctors = session.query(Doctor).filter(
#                             Doctor.specialization == specialization,
#                             Doctor.city.ilike(f"%{city}%"),
#                             Doctor.state.ilike(f"%{state}%"),
#                             Doctor.is_active == True
#                         ).all()
                    
#                     session.close()
                    
#                     if doctors:
#                         st.success(f"Found {len(doctors)} doctors in {city}, {state}")
                        
#                         for i, doctor in enumerate(doctors):
#                             st.markdown("---")
#                             col1, col2 = st.columns([3, 1])
                            
#                             with col1:
#                                 st.subheader(f"Dr. {doctor.name}")
#                                 st.write(f"**Specialization:** {doctor.specialization}")
#                                 st.write(f"**📍 Address:** {doctor.address}")
#                                 st.write(f"**📞 Phone:** {doctor.phone}")
#                                 st.write(f"**📧 Email:** {doctor.email}")
                                
#                                 # Show availability
#                                 try:
#                                     availability = eval(doctor.availability) if doctor.availability else {}
#                                     if availability:
#                                         st.write("**🕒 Available Days:**")
#                                         available_days = [day.title() for day in availability.keys()]
#                                         st.write(f"{', '.join(available_days)}")
#                                 except:
#                                     st.write("**🕒 Availability:** Contact clinic for timings")
                            
#                             with col2:
#                                 if st.button("Book Now", key=f"find_book_{i}", use_container_width=True):
#                                     st.session_state.booking_data = {'name': '', 'email': '', 'phone': '', 'symptoms': ''}
#                                     st.session_state.selected_doctor = doctor
#                                     st.session_state.show_doctors = True
#                                     st.session_state.show_date_selection = True
#                                     st.switch_page("streamlit_app.py")
                    
#                     else:
#                         st.warning(f"No {specialization.lower()} found in {city}, {state}")
    
#     with tab3:
#         st.header("My Appointments")
#         st.info("Appointment management features coming soon!")
        
#         # Placeholder for appointment history
#         with st.expander("View Sample Appointment", expanded=True):
#             st.write("""
#             **Future Features:**
#             - View upcoming appointments
#             - Cancel or reschedule
#             - Appointment history
#             - Download reports
#             """)

# if __name__ == "__main__":
#     main()













# import streamlit as st
# import sys
# import os
# from datetime import datetime, timedelta
# import json

# # Add current directory to path for imports
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)

# try:
#     from backend.database import SessionLocal, Doctor, Appointment, init_db
#     from agents.notification_agent import notification_agent
#     from agents.doctor_finder_agent import doctor_finder_agent
#     from backend.google_sheets import google_sheets_manager
#     st.success("✅ All modules imported successfully!")
# except ImportError as e:
#     st.error(f"❌ Import error: {e}")
#     st.stop()

# # Initialize database and Google Sheets
# try:
#     init_db()
#     google_sheets_manager.create_sheet_if_not_exists()
# except Exception as e:
#     st.error(f"❌ Initialization failed: {e}")

# st.set_page_config(
#     page_title="MediSathi - AI Doctor Appointment",
#     page_icon="🏥",
#     layout="wide"
# )

# def generate_time_slots():
#     """Generate time slots in 30-minute intervals"""
#     slots = []
#     start_time = datetime.strptime("09:00", "%H:%M")
#     end_time = datetime.strptime("18:00", "%H:%M")
    
#     current_time = start_time
#     while current_time < end_time:
#         slot_end = current_time + timedelta(minutes=30)
#         slots.append(f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}")
#         current_time = slot_end
    
#     return slots

# def get_available_slots(doctor_id, selected_date):
#     """Get available time slots for a doctor on a specific date"""
#     session = SessionLocal()
#     try:
#         # Get doctor's availability
#         doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
#         if not doctor or not doctor.availability:
#             return []
        
#         # Parse availability
#         availability = json.loads(doctor.availability) if doctor.availability else {}
#         day_name = selected_date.strftime("%A").lower()
        
#         if day_name not in availability:
#             return []
        
#         # Get all possible slots for the day
#         all_slots = availability[day_name]
        
#         # Get booked appointments for that day
#         start_of_day = datetime.combine(selected_date, datetime.min.time())
#         end_of_day = start_of_day + timedelta(days=1)
        
#         booked_appointments = session.query(Appointment).filter(
#             Appointment.doctor_id == doctor_id,
#             Appointment.appointment_date >= start_of_day,
#             Appointment.appointment_date < end_of_day,
#             Appointment.status == "scheduled"
#         ).all()
        
#         # Extract booked time slots
#         booked_slots = []
#         for appointment in booked_appointments:
#             appointment_time = appointment.appointment_date.strftime("%H:%M")
#             # Find which slot this appointment falls into
#             for slot in all_slots:
#                 start_time = slot.split("-")[0]
#                 if start_time == appointment_time:
#                     booked_slots.append(slot)
#                     break
        
#         # Return available slots
#         available_slots = [slot for slot in all_slots if slot not in booked_slots]
#         return available_slots
        
#     except Exception as e:
#         st.error(f"Error getting available slots: {e}")
#         return []
#     finally:
#         session.close()

# # def book_appointment(patient_data, doctor_id, selected_date, selected_slot):
# #     """Book an appointment and send confirmation"""
# #     session = SessionLocal()
# #     try:
# #         # Parse the selected slot to get start time
# #         start_time_str = selected_slot.split("-")[0]
# #         appointment_datetime = datetime.combine(selected_date, 
# #                                               datetime.strptime(start_time_str, "%H:%M").time())
        
# #         # Create appointment
# #         appointment = Appointment(
# #             patient_id=1,  # In real scenario, create patient record
# #             doctor_id=doctor_id,
# #             appointment_date=appointment_datetime,
# #             description=patient_data.get('symptoms', ''),
# #             status="scheduled"
# #         )
        
# #         session.add(appointment)
# #         session.commit()
        
# #         # Get doctor details
# #         doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        
# #         # Prepare appointment details
# #         appointment_details = {
# #             'appointment_id': appointment.id,
# #             'patient_name': patient_data['name'],
# #             'patient_email': patient_data['email'],
# #             'patient_phone': patient_data.get('phone', 'N/A'),
# #             'doctor_name': doctor.name,
# #             'doctor_specialization': doctor.specialization,
# #             'appointment_date': selected_date.strftime("%Y-%m-%d"),
# #             'appointment_time': selected_slot,
# #             'symptoms': patient_data.get('symptoms', ''),
# #             'clinic_address': doctor.address,
# #             'doctor_phone': doctor.phone,
# #             'status': 'scheduled'
# #         }
        
# #         # Send confirmation email
# #         email_result = notification_agent.send_appointment_confirmation(
# #             patient_data['email'],
# #             appointment_details
# #         )
        
# #         # Add to Google Sheets
# #         sheets_result = google_sheets_manager.add_appointment_record(appointment_details)
        
# #         return {
# #             'success': True,
# #             'appointment_id': appointment.id,
# #             'email_result': email_result,
# #             'sheets_result': sheets_result,
# #             'appointment_details': appointment_details
# #         }
        
# #     except Exception as e:
# #         session.rollback()
# #         return {'success': False, 'error': str(e)}
# #     finally:
# #         session.close()  

# def book_appointment(patient_data, doctor_id, selected_date, selected_slot):
#     """Book an appointment and send confirmation"""
#     session = SessionLocal()
#     try:
#         # Parse the selected slot to get start time
#         start_time_str = selected_slot.split("-")[0]
#         appointment_datetime = datetime.combine(selected_date, 
#                                               datetime.strptime(start_time_str, "%H:%M").time())
        
#         # Create appointment
#         appointment = Appointment(
#             patient_id=1,  # In real scenario, create patient record
#             doctor_id=doctor_id,
#             appointment_date=appointment_datetime,
#             description=patient_data.get('symptoms', ''),
#             status="scheduled"
#         )
        
#         session.add(appointment)
#         session.commit()
        
#         # Get doctor details
#         doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        
#         # Prepare appointment details
#         appointment_details = {
#             'appointment_id': appointment.id,
#             'patient_name': patient_data['name'],
#             'patient_email': patient_data['email'],
#             'patient_phone': patient_data.get('phone', 'N/A'),
#             'doctor_name': doctor.name,
#             'doctor_specialization': doctor.specialization,
#             'appointment_date': selected_date.strftime("%Y-%m-%d"),
#             'appointment_time': selected_slot,
#             'symptoms': patient_data.get('symptoms', ''),
#             'clinic_address': doctor.address,
#             'doctor_phone': doctor.phone,
#             'status': 'scheduled'
#         }
        
#         # Debug: Print appointment details before sending email
#         print("📧 Debug - Appointment details being sent to email:")
#         for key, value in appointment_details.items():
#             print(f"   {key}: {value}")
        
#         # Send confirmation email
#         email_result = notification_agent.send_appointment_confirmation(
#             patient_data['email'],
#             appointment_details
#         )
        
#         # Add to Google Sheets
#         sheets_result = google_sheets_manager.add_appointment_record(appointment_details)
        
#         return {
#             'success': True,
#             'appointment_id': appointment.id,
#             'email_result': email_result,
#             'sheets_result': sheets_result,
#             'appointment_details': appointment_details
#         }
        
#     except Exception as e:
#         session.rollback()
#         print(f"❌ Error in book_appointment: {e}")
#         return {'success': False, 'error': str(e)}
#     finally:
#         session.close()

# def display_doctors(doctors, source_type="database"):
#     """Display doctors from database"""
#     for i, doctor in enumerate(doctors):
#         with st.expander(f"👨‍⚕️ Dr. {doctor.name} - {doctor.specialization}", expanded=False):
#             col1, col2 = st.columns([3, 1])
            
#             with col1:
#                 st.write(f"**📍 Location:** {doctor.city}, {doctor.state}")
#                 st.write(f"**🏢 Address:** {doctor.address}")
#                 st.write(f"**📞 Contact:** {doctor.phone}")
#                 st.write(f"**📧 Email:** {doctor.email}")
                
#                 # Show availability
#                 try:
#                     availability = json.loads(doctor.availability) if doctor.availability else {}
#                     if availability:
#                         st.write("**🕒 Available Days:**")
#                         for day, slots in availability.items():
#                             st.write(f"   - {day.title()}: {', '.join(slots[:2])}..." if len(slots) > 2 else f"   - {day.title()}: {', '.join(slots)}")
#                 except:
#                     st.write("**🕒 Availability:** Contact for timings")
            
#             with col2:
#                 if st.button("Select Doctor", key=f"select_{source_type}_{doctor.id}", use_container_width=True):
#                     st.session_state.selected_doctor = doctor
#                     st.session_state.show_doctors = False
#                     st.session_state.show_date_selection = True
#                     st.rerun()

# def display_enhanced_doctors(doctors):
#     """Display doctors with enhanced information from web search"""
#     for i, doctor in enumerate(doctors):
#         with st.expander(f"👨‍⚕️ Dr. {doctor['name']} - {doctor['specialization']}", expanded=False):
#             col1, col2 = st.columns([3, 1])
            
#             with col1:
#                 st.write(f"**📍 Address:** {doctor.get('address', 'N/A')}")
#                 st.write(f"**🏙️ Location:** {doctor.get('city', 'N/A')}, {doctor.get('state', 'N/A')}")
#                 st.write(f"**📞 Phone:** {doctor.get('phone', 'N/A')}")
#                 st.write(f"**📧 Email:** {doctor.get('email', 'N/A')}")
                
#                 # Additional info
#                 if doctor.get('rating'):
#                     st.write(f"**⭐ Rating:** {doctor.get('rating')}/5.0")
#                 if doctor.get('experience'):
#                     st.write(f"**📅 Experience:** {doctor.get('experience')}")
#                 if doctor.get('availability'):
#                     st.write(f"**🕒 Availability:** {doctor.get('availability')}")
                
#                 st.write(f"**🔍 Source:** {doctor.get('source', 'N/A')}")
            
#             with col2:
#                 if st.button("Book Appointment", key=f"enhanced_book_{i}", use_container_width=True):
#                     st.session_state.booking_data = {
#                         'name': '', 'email': '', 'phone': '', 'symptoms': ''
#                     }
#                     # For database doctors, we can pre-fill some info
#                     if doctor.get('source') == 'database':
#                         st.info("Switch to 'Book Appointment' tab to schedule")
#                     else:
#                         st.info("Doctor found through external source. Please contact directly or search in local database.")

# def main():
#     st.title("🏥 MediSathi - AI Doctor Appointment System")
#     st.markdown("### Your Intelligent Healthcare Assistant")
    
#     # Initialize session state
#     if 'booking_data' not in st.session_state:
#         st.session_state.booking_data = {}
#     if 'selected_doctor' not in st.session_state:
#         st.session_state.selected_doctor = None
#     if 'show_doctors' not in st.session_state:
#         st.session_state.show_doctors = False
#     if 'show_date_selection' not in st.session_state:
#         st.session_state.show_date_selection = False
#     if 'show_time_selection' not in st.session_state:
#         st.session_state.show_time_selection = False
#     if 'booking_confirmed' not in st.session_state:
#         st.session_state.booking_confirmed = False
    
#     tab1, tab2, tab3 = st.tabs(["Book Appointment", "Find Doctors", "My Appointments"])
    
#     with tab1:
#         st.header("Book Doctor Appointment")
        
#         # Step 1: Patient Information
#         if not st.session_state.show_doctors and not st.session_state.show_date_selection:
#             with st.form("patient_info_form"):
#                 st.subheader("Step 1: Patient Information")
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     name = st.text_input("Full Name *", placeholder="Enter your full name")
#                     email = st.text_input("Email *", placeholder="your.email@example.com")
                
#                 with col2:
#                     phone = st.text_input("Phone Number *", placeholder="+91 XXXXX XXXXX")
#                     age = st.number_input("Age *", min_value=1, max_value=120, value=30)
                
#                 symptoms = st.text_area("Describe your symptoms *", 
#                                       placeholder="Example: Fever, cough, and headache for 3 days...",
#                                       height=100)
                
#                 submitted = st.form_submit_button("Find Available Doctors")
                
#                 if submitted:
#                     if not all([name, email, phone, symptoms]):
#                         st.error("Please fill in all required fields (*)")
#                     else:
#                         st.session_state.booking_data = {
#                             'name': name,
#                             'email': email,
#                             'phone': phone,
#                             'age': age,
#                             'symptoms': symptoms
#                         }
#                         st.session_state.show_doctors = True
#                         st.rerun()
        
#         # Step 2: Doctor Selection
#         elif st.session_state.show_doctors and not st.session_state.show_date_selection:
#             st.subheader("Step 2: Select Doctor")
#             st.info(f"Patient: {st.session_state.booking_data['name']}")
            
#             # Get available doctors from database
#             session = SessionLocal()
#             doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
#             session.close()
            
#             if doctors:
#                 display_doctors(doctors, "booking_flow")
                
#                 if st.button("← Back to Patient Info"):
#                     st.session_state.show_doctors = False
#                     st.rerun()
#             else:
#                 st.warning("No doctors available at the moment.")
#                 if st.button("← Back to Patient Info"):
#                     st.session_state.show_doctors = False
#                     st.rerun()
        
#         # Step 3: Date Selection
#         elif st.session_state.show_date_selection and not st.session_state.show_time_selection:
#             st.subheader("Step 3: Select Date")
#             st.info(f"Doctor: Dr. {st.session_state.selected_doctor.name}")
            
#             # Date selection
#             min_date = datetime.now().date()
#             max_date = min_date + timedelta(days=30)
#             selected_date = st.date_input(
#                 "Select Appointment Date",
#                 min_value=min_date,
#                 max_value=max_date,
#                 value=min_date
#             )
            
#             if selected_date:
#                 # Check if selected date is available
#                 available_slots = get_available_slots(
#                     st.session_state.selected_doctor.id, 
#                     selected_date
#                 )
                
#                 if available_slots:
#                     st.success(f"Available on {selected_date.strftime('%A, %B %d, %Y')}")
#                     if st.button("Proceed to Time Selection →"):
#                         st.session_state.selected_date = selected_date
#                         st.session_state.available_slots = available_slots
#                         st.session_state.show_time_selection = True
#                         st.rerun()
#                 else:
#                     st.warning(f"No available slots on {selected_date.strftime('%A, %B %d, %Y')}")
#                     st.info("Please select a different date")
            
#             if st.button("← Back to Doctor Selection"):
#                 st.session_state.show_date_selection = False
#                 st.rerun()
        
#         # Step 4: Time Selection
#         elif st.session_state.show_time_selection and not st.session_state.booking_confirmed:
#             st.subheader("Step 4: Select Time Slot")
#             st.info(f"Doctor: Dr. {st.session_state.selected_doctor.name}")
#             st.info(f"Date: {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
            
#             if st.session_state.available_slots:
#                 selected_slot = st.radio(
#                     "Available Time Slots:",
#                     st.session_state.available_slots,
#                     format_func=lambda x: f"{x.split('-')[0]} - {x.split('-')[1]}"
#                 )
                
#                 col1, col2, col3 = st.columns([1, 1, 1])
                
#                 with col2:
#                     if st.button("Confirm Booking", type="primary", use_container_width=True):
#                         # Book the appointment
#                         result = book_appointment(
#                             st.session_state.booking_data,
#                             st.session_state.selected_doctor.id,
#                             st.session_state.selected_date,
#                             selected_slot
#                         )
                        
#                         if result['success']:
#                             st.session_state.booking_result = result
#                             st.session_state.booking_confirmed = True
#                             st.rerun()
#                         else:
#                             st.error(f"Booking failed: {result['error']}")
                
#                 with col1:
#                     if st.button("← Back to Date Selection"):
#                         st.session_state.show_time_selection = False
#                         st.rerun()
                
#                 with col3:
#                     if st.button("🔄 Change Doctor"):
#                         st.session_state.show_doctors = False
#                         st.session_state.show_date_selection = False
#                         st.session_state.show_time_selection = False
#                         st.rerun()
#             else:
#                 st.error("No time slots available for selected date")
#                 if st.button("← Back to Date Selection"):
#                     st.session_state.show_time_selection = False
#                     st.rerun()
        
#         # Step 5: Booking Confirmation
#         # elif st.session_state.booking_confirmed:
#         #     st.subheader("🎉 Appointment Confirmed!")
#         #     st.balloons()
            
#         #     result = st.session_state.booking_result
#         #     details = result['appointment_details']
            
#         #     # Display confirmation details
#         #     col1, col2 = st.columns(2)
            
#         #     with col1:
#         #         st.success("**Appointment Details:**")
#         #         st.write(f"**Appointment ID:** #{details['appointment_id']}")
#         #         st.write(f"**Patient:** {details['patient_name']}")
#         #         st.write(f"**Doctor:** Dr. {details['doctor_name']}")
#         #         st.write(f"**Specialization:** {details['doctor_specialization']}")
#         #         st.write(f"**Date:** {details['date']}")
#         #         st.write(f"**Time:** {details['time']}")
#         #         st.write(f"**Clinic:** {details['clinic_address']}")
#         #         st.write(f"**Contact:** {details['doctor_phone']}")
            
#         #     with col2:
#         #         st.success("**Confirmation Status**")
#         #         st.write(f"✅ Email sent to: {details['patient_email']}")
                
#         #         if result.get('sheets_result', {}).get('status') == 'success':
#         #             st.write("✅ Record added to Google Sheets")
#         #         else:
#         #             st.write("⚠️ Google Sheets update pending")
                
#         #         st.info("""
#         #         **Important Notes:**
#         #         - Please arrive 15 minutes before your appointment
#         #         - Bring your ID and any medical reports
#         #         - Cancel at least 24 hours in advance if needed
#         #         """)
            
#         #     if st.button("Book Another Appointment"):
#         #         # Reset all session states
#         #         for key in list(st.session_state.keys()):
#         #             if key not in ['_runners', '_handles']:
#         #                 del st.session_state[key]
#         #         st.rerun()
#         # Step 5: Booking Confirmation
#         elif st.session_state.booking_confirmed:
#             st.subheader("🎉 Appointment Confirmed!")
#             st.balloons()
            
#             result = st.session_state.booking_result
#             details = result['appointment_details']
            
#             # Display confirmation details
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.success("**Appointment Details:**")
#                 st.write(f"**Appointment ID:** #{details['appointment_id']}")
#                 st.write(f"**Patient:** {details['patient_name']}")
#                 st.write(f"**Doctor:** Dr. {details['doctor_name']}")
#                 st.write(f"**Specialization:** {details['doctor_specialization']}")
#                 st.write(f"**Date:** {details['appointment_date']}")  # Fixed: changed 'date' to 'appointment_date'
#                 st.write(f"**Time:** {details['appointment_time']}")  # Fixed: changed 'time' to 'appointment_time'
#                 st.write(f"**Clinic:** {details['clinic_address']}")
#                 st.write(f"**Contact:** {details['doctor_phone']}")
            
#             with col2:
#                 st.success("**Confirmation Status**")
#                 st.write(f"✅ Email sent to: {details['patient_email']}")
                
#                 if result.get('sheets_result', {}).get('status') == 'success':
#                     st.write("✅ Record added to Google Sheets")
#                 else:
#                     st.write("⚠️ Google Sheets update pending")
                
#                 st.info("""
#                 **Important Notes:**
#                 - Please arrive 15 minutes before your appointment
#                 - Bring your ID and any medical reports
#                 - Cancel at least 24 hours in advance if needed
#                 """)
            
#             if st.button("Book Another Appointment"):
#                 # Reset all session states
#                 for key in list(st.session_state.keys()):
#                     if key not in ['_runners', '_handles']:
#                         del st.session_state[key]
#                 st.rerun()

#     with tab2:
#         st.header("🔍 Find Doctors")
        
#         # Enhanced search options
#         with st.form("search_doctors_form"):
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 search_type = st.radio(
#                     "Search by:",
#                     ["Symptoms", "Specialization"]
#                 )
                
#                 if search_type == "Symptoms":
#                     symptoms = st.text_area("Describe your symptoms *", 
#                                           placeholder="Example: Fever, cough, headache...",
#                                           height=80)
#                     specialization = None
#                 else:
#                     symptoms = ""
#                     specialization = st.selectbox(
#                         "Specialization *",
#                         ["Cardiologist", "Dermatologist", "Orthopedic", "Neurologist", 
#                          "General Physician", "Pediatrician", "Gynecologist", "Dentist",
#                          "Psychiatrist", "Ophthalmologist", "All Specializations"]
#                     )
            
#             with col2:
#                 city = st.text_input("City *", placeholder="Enter your city")
#                 state = st.text_input("State *", placeholder="Enter your state")
                
#                 search_method = st.selectbox(
#                     "Search Method",
#                     ["Local Database", "Extended Search (Database + Web)"]
#                 )
            
#             col3, col4 = st.columns(2)
#             with col3:
#                 max_results = st.slider("Maximum Results", 5, 20, 10)
#             with col4:
#                 search_btn = st.form_submit_button("🔍 Search Doctors", use_container_width=True)
            
#             if search_btn:
#                 if not city or not state:
#                     st.error("Please enter both city and state")
#                 elif search_type == "Symptoms" and not symptoms:
#                     st.error("Please describe your symptoms")
#                 else:
#                     with st.spinner("Searching for doctors..."):
#                         if search_method == "Local Database":
#                             # Search only in database
#                             session = SessionLocal()
#                             if specialization == "All Specializations" or not specialization:
#                                 doctors = session.query(Doctor).filter(
#                                     Doctor.city.ilike(f"%{city}%"),
#                                     Doctor.state.ilike(f"%{state}%"),
#                                     Doctor.is_active == True
#                                 ).limit(max_results).all()
#                             else:
#                                 doctors = session.query(Doctor).filter(
#                                     Doctor.specialization == specialization,
#                                     Doctor.city.ilike(f"%{city}%"),
#                                     Doctor.state.ilike(f"%{state}%"),
#                                     Doctor.is_active == True
#                                 ).limit(max_results).all()
#                             session.close()
                            
#                             if doctors:
#                                 st.success(f"Found {len(doctors)} doctors in local database")
#                                 display_doctors(doctors, "search_results")
#                             else:
#                                 st.warning("No doctors found in local database. Try extended search.")
                        
#                         else:  # Extended Search
#                             if search_type == "Symptoms":
#                                 result = doctor_finder_agent.find_doctors_by_specialization(
#                                     symptoms, city, state, max_results
#                                 )
#                             else:
#                                 result = doctor_finder_agent.find_doctors_by_specialization(
#                                     specialization, city, state, max_results
#                                 )
                            
#                             if result['doctors']:
#                                 st.success(f"Found {result['doctors_found']} doctors in {result['location']}")
#                                 st.info(f"Suggested Specialization: {result['suggested_specialization']}")
#                                 st.info(f"Search Method: {result.get('search_method', 'extended')}")
                                
#                                 display_enhanced_doctors(result['doctors'])
#                             else:
#                                 st.warning("No doctors found. Please try different search criteria.")
    
#     with tab3:
#         st.header("My Appointments")
#         st.info("Appointment management features coming soon!")
        
#         # Placeholder for appointment history
#         with st.expander("View Sample Appointment", expanded=True):
#             st.write("""
#             **Future Features:**
#             - View upcoming appointments
#             - Cancel or reschedule
#             - Appointment history
#             - Download reports
#             """)

# if __name__ == "__main__":
#     main()
















import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import json

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from backend.database import SessionLocal, Doctor, Appointment, init_db
    from agents.notification_agent import notification_agent
    from agents.doctor_finder_agent import doctor_finder_agent
    from backend.google_sheets import google_sheets_manager
    st.success("✅ All modules imported successfully!")
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

# Initialize database and Google Sheets
try:
    init_db()
    google_sheets_manager.create_sheet_if_not_exists()
except Exception as e:
    st.error(f"❌ Initialization failed: {e}")

st.set_page_config(
    page_title="MediSathi - AI Doctor Appointment",
    page_icon="🏥",
    layout="wide"
)

def generate_time_slots():
    """Generate time slots in 30-minute intervals"""
    slots = []
    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("18:00", "%H:%M")
    
    current_time = start_time
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=30)
        slots.append(f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}")
        current_time = slot_end
    
    return slots

def get_available_slots(doctor_id, selected_date):
    """Get available time slots for a doctor on a specific date"""
    session = SessionLocal()
    try:
        # Get doctor's availability
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor or not doctor.availability:
            return []
        
        # Parse availability
        availability = json.loads(doctor.availability) if doctor.availability else {}
        day_name = selected_date.strftime("%A").lower()
        
        if day_name not in availability:
            return []
        
        # Get all possible slots for the day
        all_slots = availability[day_name]
        
        # Get booked appointments for that day
        start_of_day = datetime.combine(selected_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)
        
        booked_appointments = session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_of_day,
            Appointment.appointment_date < end_of_day,
            Appointment.status == "scheduled"
        ).all()
        
        # Extract booked time slots
        booked_slots = []
        for appointment in booked_appointments:
            appointment_time = appointment.appointment_date.strftime("%H:%M")
            # Find which slot this appointment falls into
            for slot in all_slots:
                start_time = slot.split("-")[0]
                if start_time == appointment_time:
                    booked_slots.append(slot)
                    break
        
        # Return available slots
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        return available_slots
        
    except Exception as e:
        st.error(f"Error getting available slots: {e}")
        return []
    finally:
        session.close()

def book_appointment(patient_data, doctor_id, selected_date, selected_slot):
    """Book an appointment and send confirmation"""
    session = SessionLocal()
    try:
        # Parse the selected slot to get start time
        start_time_str = selected_slot.split("-")[0]
        appointment_datetime = datetime.combine(selected_date, 
                                              datetime.strptime(start_time_str, "%H:%M").time())
        
        # Create appointment
        appointment = Appointment(
            patient_id=1,  # In real scenario, create patient record
            doctor_id=doctor_id,
            appointment_date=appointment_datetime,
            description=patient_data.get('symptoms', ''),
            status="scheduled"
        )
        
        session.add(appointment)
        session.commit()
        
        # Get doctor details
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        # Prepare appointment details
        appointment_details = {
            'appointment_id': appointment.id,
            'patient_name': patient_data['name'],
            'patient_email': patient_data['email'],
            'patient_phone': patient_data.get('phone', 'N/A'),
            'doctor_name': doctor.name,
            'doctor_specialization': doctor.specialization,
            'appointment_date': selected_date.strftime("%Y-%m-%d"),
            'appointment_time': selected_slot,
            'symptoms': patient_data.get('symptoms', ''),
            'clinic_address': doctor.address,
            'doctor_phone': doctor.phone,
            'status': 'scheduled'
        }
        
        # Debug: Print appointment details before sending email
        print("📧 Debug - Appointment details being sent to email:")
        for key, value in appointment_details.items():
            print(f"   {key}: {value}")
        
        # Send confirmation email
        email_result = notification_agent.send_appointment_confirmation(
            patient_data['email'],
            appointment_details
        )
        
        # Add to Google Sheets
        sheets_result = google_sheets_manager.add_appointment_record(appointment_details)
        
        return {
            'success': True,
            'appointment_id': appointment.id,
            'email_result': email_result,
            'sheets_result': sheets_result,
            'appointment_details': appointment_details
        }
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error in book_appointment: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        session.close()

def display_doctors(doctors, source_type="database"):
    """Display doctors from database"""
    for i, doctor in enumerate(doctors):
        with st.expander(f"👨‍⚕️ Dr. {doctor.name} - {doctor.specialization}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**📍 Location:** {doctor.city}, {doctor.state}")
                st.write(f"**🏢 Address:** {doctor.address}")
                st.write(f"**📞 Contact:** {doctor.phone}")
                st.write(f"**📧 Email:** {doctor.email}")
                
                # Show availability
                try:
                    availability = json.loads(doctor.availability) if doctor.availability else {}
                    if availability:
                        st.write("**🕒 Available Days:**")
                        for day, slots in availability.items():
                            st.write(f"   - {day.title()}: {', '.join(slots[:2])}..." if len(slots) > 2 else f"   - {day.title()}: {', '.join(slots)}")
                except:
                    st.write("**🕒 Availability:** Contact for timings")
            
            with col2:
                if st.button("Select Doctor", key=f"select_{source_type}_{doctor.id}", use_container_width=True):
                    st.session_state.selected_doctor = doctor
                    st.session_state.show_doctors = False
                    st.session_state.show_date_selection = True
                    st.rerun()

def display_doctor_card(doctor, index):
    """Display individual doctor information in a card format"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"👨‍⚕️ {doctor.get('Name', 'N/A')}")
            
            # Doctor details in a nice layout
            details_col1, details_col2 = st.columns(2)
            
            with details_col1:
                if doctor.get('Degree'):
                    st.write(f"**🎓 Degree:** {doctor['Degree']}")
                if doctor.get('Speciality'):
                    st.write(f"**🎯 Specialization:** {doctor['Speciality']}")
                if doctor.get('Years of Experience'):
                    st.write(f"**📅 Experience:** {doctor['Years of Experience']} years")
                
            with details_col2:
                if doctor.get('Consult Fee'):
                    st.write(f"**💰 Consultation Fee:** {doctor['Consult Fee']}")
                if doctor.get('Location'):
                    st.write(f"**📍 Location:** {doctor['Location']}")
                if doctor.get('City'):
                    st.write(f"**🏙️ City:** {doctor['City']}")
            
            # Additional information if available
            if doctor.get('Clinic'):
                st.write(f"**🏢 Clinic:** {doctor['Clinic']}")
            if doctor.get('Rating'):
                st.write(f"**⭐ Rating:** {doctor['Rating']}/5.0")
            if doctor.get('Availability'):
                st.write(f"**🕒 Availability:** {doctor['Availability']}")
        
        with col2:
            st.write("")  # Spacer
            if st.button("View Details", key=f"view_{index}", use_container_width=True):
                # Show detailed view in expander
                with st.expander("Detailed Information", expanded=True):
                    st.json(doctor)
        
        st.markdown("---")

def main():
    st.title("🏥 MediSathi - AI Doctor Appointment System")
    st.markdown("### Your Intelligent Healthcare Assistant")
    
    # Initialize session state for booking
    if 'booking_data' not in st.session_state:
        st.session_state.booking_data = {}
    if 'selected_doctor' not in st.session_state:
        st.session_state.selected_doctor = None
    if 'show_doctors' not in st.session_state:
        st.session_state.show_doctors = False
    if 'show_date_selection' not in st.session_state:
        st.session_state.show_date_selection = False
    if 'show_time_selection' not in st.session_state:
        st.session_state.show_time_selection = False
    if 'booking_confirmed' not in st.session_state:
        st.session_state.booking_confirmed = False
    
    # Initialize session state for doctor finding
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_type' not in st.session_state:
        st.session_state.search_type = "symptoms"
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["Book Appointment", "Find Doctors", "Browse Doctors", "My Appointments"])
    
    # Tab 1: Book Appointment (Original Functionality)
    with tab1:
        st.header("Book Doctor Appointment")
        
        # Step 1: Patient Information
        if not st.session_state.show_doctors and not st.session_state.show_date_selection:
            with st.form("patient_info_form"):
                st.subheader("Step 1: Patient Information")
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name *", placeholder="Enter your full name")
                    email = st.text_input("Email *", placeholder="your.email@example.com")
                
                with col2:
                    phone = st.text_input("Phone Number *", placeholder="+91 XXXXX XXXXX")
                    age = st.number_input("Age *", min_value=1, max_value=120, value=30)
                
                symptoms = st.text_area("Describe your symptoms *", 
                                      placeholder="Example: Fever, cough, and headache for 3 days...",
                                      height=100)
                
                submitted = st.form_submit_button("Find Available Doctors")
                
                if submitted:
                    if not all([name, email, phone, symptoms]):
                        st.error("Please fill in all required fields (*)")
                    else:
                        st.session_state.booking_data = {
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'age': age,
                            'symptoms': symptoms
                        }
                        st.session_state.show_doctors = True
                        st.rerun()
        
        # Step 2: Doctor Selection
        elif st.session_state.show_doctors and not st.session_state.show_date_selection:
            st.subheader("Step 2: Select Doctor")
            st.info(f"Patient: {st.session_state.booking_data['name']}")
            
            # Get available doctors from database
            session = SessionLocal()
            doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
            session.close()
            
            if doctors:
                display_doctors(doctors, "booking_flow")
                
                if st.button("← Back to Patient Info"):
                    st.session_state.show_doctors = False
                    st.rerun()
            else:
                st.warning("No doctors available at the moment.")
                if st.button("← Back to Patient Info"):
                    st.session_state.show_doctors = False
                    st.rerun()
        
        # Step 3: Date Selection
        elif st.session_state.show_date_selection and not st.session_state.show_time_selection:
            st.subheader("Step 3: Select Date")
            st.info(f"Doctor: Dr. {st.session_state.selected_doctor.name}")
            
            # Date selection
            min_date = datetime.now().date()
            max_date = min_date + timedelta(days=30)
            selected_date = st.date_input(
                "Select Appointment Date",
                min_value=min_date,
                max_value=max_date,
                value=min_date
            )
            
            if selected_date:
                # Check if selected date is available
                available_slots = get_available_slots(
                    st.session_state.selected_doctor.id, 
                    selected_date
                )
                
                if available_slots:
                    st.success(f"Available on {selected_date.strftime('%A, %B %d, %Y')}")
                    if st.button("Proceed to Time Selection →"):
                        st.session_state.selected_date = selected_date
                        st.session_state.available_slots = available_slots
                        st.session_state.show_time_selection = True
                        st.rerun()
                else:
                    st.warning(f"No available slots on {selected_date.strftime('%A, %B %d, %Y')}")
                    st.info("Please select a different date")
            
            if st.button("← Back to Doctor Selection"):
                st.session_state.show_date_selection = False
                st.rerun()
        
        # Step 4: Time Selection
        elif st.session_state.show_time_selection and not st.session_state.booking_confirmed:
            st.subheader("Step 4: Select Time Slot")
            st.info(f"Doctor: Dr. {st.session_state.selected_doctor.name}")
            st.info(f"Date: {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
            
            if st.session_state.available_slots:
                selected_slot = st.radio(
                    "Available Time Slots:",
                    st.session_state.available_slots,
                    format_func=lambda x: f"{x.split('-')[0]} - {x.split('-')[1]}"
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col2:
                    if st.button("Confirm Booking", type="primary", use_container_width=True):
                        # Book the appointment
                        result = book_appointment(
                            st.session_state.booking_data,
                            st.session_state.selected_doctor.id,
                            st.session_state.selected_date,
                            selected_slot
                        )
                        
                        if result['success']:
                            st.session_state.booking_result = result
                            st.session_state.booking_confirmed = True
                            st.rerun()
                        else:
                            st.error(f"Booking failed: {result['error']}")
                
                with col1:
                    if st.button("← Back to Date Selection"):
                        st.session_state.show_time_selection = False
                        st.rerun()
                
                with col3:
                    if st.button("🔄 Change Doctor"):
                        st.session_state.show_doctors = False
                        st.session_state.show_date_selection = False
                        st.session_state.show_time_selection = False
                        st.rerun()
            else:
                st.error("No time slots available for selected date")
                if st.button("← Back to Date Selection"):
                    st.session_state.show_time_selection = False
                    st.rerun()
        
        # Step 5: Booking Confirmation
        elif st.session_state.booking_confirmed:
            st.subheader("🎉 Appointment Confirmed!")
            st.balloons()
            
            result = st.session_state.booking_result
            details = result['appointment_details']
            
            # Display confirmation details
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("**Appointment Details:**")
                st.write(f"**Appointment ID:** #{details['appointment_id']}")
                st.write(f"**Patient:** {details['patient_name']}")
                st.write(f"**Doctor:** Dr. {details['doctor_name']}")
                st.write(f"**Specialization:** {details['doctor_specialization']}")
                st.write(f"**Date:** {details['appointment_date']}")
                st.write(f"**Time:** {details['appointment_time']}")
                st.write(f"**Clinic:** {details['clinic_address']}")
                st.write(f"**Contact:** {details['doctor_phone']}")
            
            with col2:
                st.success("**Confirmation Status**")
                st.write(f"✅ Email sent to: {details['patient_email']}")
                
                if result.get('sheets_result', {}).get('status') == 'success':
                    st.write("✅ Record added to Google Sheets")
                else:
                    st.write("⚠️ Google Sheets update pending")
                
                st.info("""
                **Important Notes:**
                - Please arrive 15 minutes before your appointment
                - Bring your ID and any medical reports
                - Cancel at least 24 hours in advance if needed
                """)
            
            if st.button("Book Another Appointment"):
                # Reset all session states
                for key in list(st.session_state.keys()):
                    if key not in ['_runners', '_handles']:
                        del st.session_state[key]
                st.rerun()

    # Tab 2: Find Doctors by Symptoms (New Functionality)
    with tab2:
        st.header("🔍 Find Doctors by Symptoms")
        st.markdown("### Find the Right Doctor Based on Your Symptoms")
        
        # Sidebar for statistics and filters
        with st.sidebar:
            st.header("📊 Doctor Database")
            
            # Show statistics
            stats = doctor_finder_agent.get_doctor_statistics()
            st.metric("Total Doctors", stats["total_doctors"])
            st.metric("Specializations", stats["total_specializations"])
            st.metric("Cities", stats["total_cities"])
            
            st.markdown("---")
            st.header("🔍 Search Options")
            
            search_type = st.radio(
                "Search by:",
                ["Symptoms", "Specialization", "City"]
            )
            
            if search_type == "Specialization":
                specializations = stats["specializations"]
                selected_specialization = st.selectbox(
                    "Select Specialization",
                    ["All Specializations"] + specializations
                )
            
            elif search_type == "City":
                cities = stats["cities"]
                selected_city = st.selectbox(
                    "Select City",
                    ["All Cities"] + cities
                )
        
        # Main content area for symptom-based search
        st.header("Describe Your Symptoms")
        
        with st.form("symptoms_form"):
            symptoms = st.text_area(
                "What symptoms are you experiencing?",
                placeholder="Example: I have been having chest pain and shortness of breath for 3 days...",
                height=100
            )
            
            city_filter = st.text_input(
                "Preferred City (Optional)",
                placeholder="Enter your city for local results"
            )
            
            max_results = st.slider("Maximum Results", 5, 50, 10)
            
            submitted = st.form_submit_button("🔍 Find Suitable Doctors")
            
            if submitted:
                if not symptoms.strip():
                    st.error("Please describe your symptoms")
                else:
                    with st.spinner("Finding the best doctors for your symptoms..."):
                        result = doctor_finder_agent.find_doctors_by_symptoms(
                            symptoms, 
                            city_filter if city_filter else None,
                            max_results
                        )
                        
                        st.session_state.search_results = result
                        st.session_state.search_type = "symptoms"
        
        # Display search results
        if st.session_state.search_results and st.session_state.search_type == "symptoms":
            results = st.session_state.search_results
            
            if results["success"]:
                st.header("🎯 Search Results")
                
                if st.session_state.search_type == "symptoms":
                    st.success(f"**Suggested Specialization:** {results['suggested_specialization']}")
                    st.info(f"Based on your symptoms: '{results['symptoms']}'")
                
                st.success(f"Found {results['doctors_found']} doctors matching your criteria")
                
                if results['doctors_found'] > 0:
                    for i, doctor in enumerate(results['doctors']):
                        display_doctor_card(doctor, f"result_{i}")
                else:
                    st.warning("No doctors found matching your criteria. Try broadening your search.")
                    
                    # Show suggestions
                    st.info("💡 **Suggestions:**")
                    st.write("- Try different symptoms or keywords")
                    st.write("- Remove city filter")
                    st.write("- Check the 'Browse All Doctors' tab")
            else:
                st.error(f"Search failed: {results.get('error', 'Unknown error')}")

    # Tab 3: Browse All Doctors (New Functionality)
    with tab3:
        st.header("Browse All Doctors")
        
        # Show all doctors with filters
        all_doctors = doctor_finder_agent.data_loader.get_all_doctors()
        
        st.info(f"Showing all {len(all_doctors)} doctors from our database")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            specialization_filter = st.selectbox(
                "Filter by Specialization",
                ["All"] + doctor_finder_agent.get_available_specializations(),
                key="browse_spec"
            )
        
        with col2:
            city_filter = st.selectbox(
                "Filter by City",
                ["All"] + doctor_finder_agent.get_available_cities(),
                key="browse_city"
            )
        
        with col3:
            fee_filter = st.selectbox(
                "Sort by Fee",
                ["Default", "Low to High", "High to Low"]
            )
        
        # Apply filters
        filtered_doctors = all_doctors
        
        if specialization_filter != "All":
            filtered_doctors = [doc for doc in filtered_doctors 
                              if specialization_filter.lower() in doc.get('Speciality', '').lower()]
        
        if city_filter != "All":
            filtered_doctors = [doc for doc in filtered_doctors 
                              if city_filter.lower() in doc.get('City', '').lower()]
        
        # Sort by fee
        if fee_filter == "Low to High":
            filtered_doctors.sort(key=lambda x: doctor_finder_agent.data_loader._extract_fee_value(x.get('Consult Fee', '0')))
        elif fee_filter == "High to Low":
            filtered_doctors.sort(key=lambda x: doctor_finder_agent.data_loader._extract_fee_value(x.get('Consult Fee', '0')), reverse=True)
        
        st.success(f"Found {len(filtered_doctors)} doctors matching your criteria")
        
        # Display doctors
        for i, doctor in enumerate(filtered_doctors):
            display_doctor_card(doctor, i)

    # Tab 4: My Appointments (Original Functionality)
    with tab4:
        st.header("My Appointments")
        st.info("Appointment management features coming soon!")
        
        # Placeholder for appointment history
        with st.expander("View Sample Appointment", expanded=True):
            st.write("""
            **Future Features:**
            - View upcoming appointments
            - Cancel or reschedule
            - Appointment history
            - Download reports
            """)

if __name__ == "__main__":
    main()