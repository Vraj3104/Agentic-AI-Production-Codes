import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta
import sys
import os
import json

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from utils.config import Config
    from backend.database import SessionLocal, Doctor, Appointment
    from agents.notification_agent import notification_agent
except ImportError as e:
    print(f"Import error: {e}")

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class MediSathiBot:
    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        if not self.token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup message handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("book", self.book_appointment))
        self.application.add_handler(CommandHandler("find", self.find_doctors))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when command /start is issued."""
        user = update.effective_user
        welcome_text = f"""
        🏥 Welcome to MediSathi, {user.first_name}!

        I'm your AI-powered medical appointment assistant.

        Available Commands:
        /book - Book a new appointment with date & time selection
        /find - Find doctors by specialization
        /help - Show help information

        Get started by booking an appointment with our step-by-step process!
        """
        
        keyboard = [
            [InlineKeyboardButton("📅 Book Appointment", callback_data="book_appointment")],
            [InlineKeyboardButton("🔍 Find Doctors", callback_data="find_doctors")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def book_appointment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the appointment booking process."""
        instruction_text = """
        📅 Let's book your appointment!

        Please provide your information in this format:

        👤 Name: Your Full Name
        📧 Email: your.email@example.com
        📞 Phone: Your phone number
        💊 Symptoms: Describe your health concerns

        Example:
        Name: John Doe
        Email: john@example.com
        Phone: +91 1234567890
        Symptoms: Fever and cough for 3 days

        I'll help you find available doctors and time slots.
        """
        
        await update.message.reply_text(instruction_text)
        context.user_data['booking_step'] = 'patient_info'
    
    async def process_patient_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Process patient information and show available doctors."""
        try:
            # Parse patient information (simplified parsing)
            lines = message.split('\n')
            patient_data = {}
            
            for line in lines:
                if 'name:' in line.lower():
                    patient_data['name'] = line.split(':', 1)[1].strip()
                elif 'email:' in line.lower():
                    patient_data['email'] = line.split(':', 1)[1].strip()
                elif 'phone:' in line.lower():
                    patient_data['phone'] = line.split(':', 1)[1].strip()
                elif 'symptoms:' in line.lower():
                    patient_data['symptoms'] = line.split(':', 1)[1].strip()
            
            # Validate required fields
            if not all([patient_data.get('name'), patient_data.get('email'), patient_data.get('symptoms')]):
                await update.message.reply_text(
                    "❌ Please provide Name, Email, and Symptoms clearly.\n"
                    "Use the format shown in the instructions."
                )
                return
            
            context.user_data['patient_data'] = patient_data
            
            # Get available doctors
            session = SessionLocal()
            doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
            session.close()
            
            if not doctors:
                await update.message.reply_text("❌ No doctors available at the moment. Please try again later.")
                return
            
            # Show available doctors with inline keyboard
            keyboard = []
            for doctor in doctors[:5]:  # Show max 5 doctors
                keyboard.append([
                    InlineKeyboardButton(
                        f"Dr. {doctor.name} - {doctor.specialization}",
                        callback_data=f"select_doctor_{doctor.id}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data="cancel_booking")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"👤 Patient: {patient_data['name']}\n"
                f"📧 Email: {patient_data['email']}\n"
                f"💊 Symptoms: {patient_data['symptoms']}\n\n"
                "Please select a doctor:",
                reply_markup=reply_markup
            )
            
            context.user_data['booking_step'] = 'select_doctor'
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing your information: {str(e)}")
    
    async def show_date_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, doctor_id: int):
        """Show date selection for the selected doctor."""
        query = update.callback_query
        await query.answer()
        
        session = SessionLocal()
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        session.close()
        
        if not doctor:
            await query.edit_message_text("❌ Doctor not found.")
            return
        
        context.user_data['selected_doctor'] = {
            'id': doctor.id,
            'name': doctor.name,
            'specialization': doctor.specialization
        }
        
        # Create date selection keyboard (next 7 days)
        keyboard = []
        today = datetime.now().date()
        
        for i in range(7):
            date = today + timedelta(days=i)
            day_name = date.strftime("%A")
            date_str = date.strftime("%Y-%m-%d")
            
            # Check if doctor is available on this day
            availability = eval(doctor.availability) if doctor.availability else {}
            day_availability = availability.get(date.strftime("%A").lower(), [])
            
            if day_availability:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📅 {day_name} - {date.strftime('%d %b')}",
                        callback_data=f"select_date_{date_str}"
                    )
                ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Doctors", callback_data="back_to_doctors")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"👨‍⚕️ Selected: Dr. {doctor.name}\n"
            f"🎯 Specialization: {doctor.specialization}\n\n"
            "Please select an available date:",
            reply_markup=reply_markup
        )
        
        context.user_data['booking_step'] = 'select_date'
    
    async def show_time_slots(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selected_date: str):
        """Show available time slots for the selected date."""
        query = update.callback_query
        await query.answer()
        
        doctor_id = context.user_data['selected_doctor']['id']
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        
        session = SessionLocal()
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        # Get availability for the selected day
        availability = eval(doctor.availability) if doctor.availability else {}
        day_name = selected_date_obj.strftime("%A").lower()
        available_slots = availability.get(day_name, [])
        
        # Get booked appointments
        start_of_day = datetime.combine(selected_date_obj, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)
        
        booked_appointments = session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_of_day,
            Appointment.appointment_date < end_of_day,
            Appointment.status == "scheduled"
        ).all()
        
        session.close()
        
        # Filter out booked slots
        booked_slots = []
        for appointment in booked_appointments:
            appointment_time = appointment.appointment_date.strftime("%H:%M")
            for slot in available_slots:
                if slot.startswith(appointment_time):
                    booked_slots.append(slot)
        
        available_slots = [slot for slot in available_slots if slot not in booked_slots]
        
        if not available_slots:
            await query.edit_message_text(
                f"❌ No available time slots on {selected_date_obj.strftime('%A, %d %b')}.\n"
                "Please select a different date."
            )
            return
        
        # Create time slot keyboard
        keyboard = []
        for slot in available_slots:
            start_time, end_time = slot.split('-')
            keyboard.append([
                InlineKeyboardButton(
                    f"🕒 {start_time} - {end_time}",
                    callback_data=f"select_time_{slot}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Dates", callback_data="back_to_dates")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"👨‍⚕️ Doctor: Dr. {context.user_data['selected_doctor']['name']}\n"
            f"📅 Date: {selected_date_obj.strftime('%A, %d %b %Y')}\n\n"
            "Please select a time slot:",
            reply_markup=reply_markup
        )
        
        context.user_data['selected_date'] = selected_date
        context.user_data['booking_step'] = 'select_time'
    
    async def confirm_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selected_slot: str):
        """Confirm and book the appointment."""
        query = update.callback_query
        await query.answer()
        
        patient_data = context.user_data['patient_data']
        doctor_data = context.user_data['selected_doctor']
        selected_date = context.user_data['selected_date']
        
        # Book the appointment
        session = SessionLocal()
        try:
            # Parse the selected slot to get start time
            start_time_str = selected_slot.split('-')[0]
            appointment_datetime = datetime.strptime(
                f"{selected_date} {start_time_str}", "%Y-%m-%d %H:%M"
            )
            
            # Create appointment
            appointment = Appointment(
                patient_id=1,  # In real scenario, create patient record
                doctor_id=doctor_data['id'],
                appointment_date=appointment_datetime,
                description=patient_data.get('symptoms', ''),
                status="scheduled"
            )
            
            session.add(appointment)
            session.commit()
            
            # Get complete doctor details
            doctor = session.query(Doctor).filter(Doctor.id == doctor_data['id']).first()
            
            # Prepare appointment details
            appointment_details = {
                'patient_name': patient_data['name'],
                'patient_email': patient_data['email'],
                'doctor_name': doctor.name,
                'doctor_specialization': doctor.specialization,
                'date': selected_date,
                'time': selected_slot,
                'appointment_id': appointment.id,
                'clinic_address': doctor.address,
                'doctor_phone': doctor.phone
            }
            
            # Send confirmation email
            email_result = notification_agent.send_appointment_confirmation(
                patient_data['email'],
                appointment_details
            )
            
            # Send Telegram confirmation
            confirmation_text = f"""
            ✅ <b>Appointment Confirmed!</b>

            🏥 <b>MediSathi Booking Confirmation</b>

            👤 <b>Patient:</b> {patient_data['name']}
            🆔 <b>Appointment ID:</b> #{appointment.id}
            
            👨‍⚕️ <b>Doctor:</b> Dr. {doctor.name}
            🎯 <b>Specialization:</b> {doctor.specialization}
            
            📅 <b>Date:</b> {selected_date}
            🕒 <b>Time:</b> {selected_slot}
            
            📍 <b>Clinic:</b> {doctor.address}
            📞 <b>Contact:</b> {doctor.phone}

            💡 <i>Please arrive 15 minutes early and bring your ID</i>
            
            📧 <i>A confirmation email has been sent to: {patient_data['email']}</i>
            
            Thank you for choosing MediSathi! 🏥
            """
            
            await query.edit_message_text(
                confirmation_text,
                parse_mode='HTML'
            )
            
            # Clear booking data
            for key in ['patient_data', 'selected_doctor', 'selected_date', 'booking_step']:
                if key in context.user_data:
                    del context.user_data[key]
                    
        except Exception as e:
            session.rollback()
            await query.edit_message_text(f"❌ Booking failed: {str(e)}")
        finally:
            session.close()
    
    async def find_doctors(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Find doctors based on symptoms and location."""
        instruction_text = """
        🔍 Let me help you find the right doctor!

        Please provide:
        - Your symptoms or preferred specialization
        - Your city and state

        Example:
        Symptoms: Skin allergy and rashes
        City: Mumbai
        State: Maharashtra

        I'll show you the best doctors in your area.
        """
        
        await update.message.reply_text(instruction_text)
        context.user_data['awaiting_find'] = True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages."""
        user_message = update.message.text
        user_data = context.user_data
        
        if user_data.get('booking_step') == 'patient_info':
            await self.process_patient_info(update, context, user_message)
        
        elif user_data.get('awaiting_find'):
            await update.message.reply_text(
                "🔍 Searching for doctors... We'll send you the available options shortly."
            )
            user_data['awaiting_find'] = False
        
        else:
            await update.message.reply_text(
                "💡 I understand you have a query. Please use:\n"
                "/book - to schedule an appointment with date & time selection\n"
                "/find - to search for doctors\n"
                "/help - for assistance\n\n"
                "For urgent medical issues, please contact emergency services immediately."
            )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        data = query.data
        
        if data == "book_appointment":
            await self.book_appointment(update, context)
        elif data == "find_doctors":
            await self.find_doctors(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "cancel_booking":
            # Clear booking data
            for key in ['patient_data', 'selected_doctor', 'selected_date', 'booking_step']:
                if key in context.user_data:
                    del context.user_data[key]
            await query.edit_message_text("❌ Booking cancelled.")
        elif data == "back_to_doctors":
            await self.book_appointment(update, context)
        elif data == "back_to_dates":
            await self.show_date_selection(update, context, context.user_data['selected_doctor']['id'])
        elif data.startswith("select_doctor_"):
            doctor_id = int(data.split("_")[2])
            await self.show_date_selection(update, context, doctor_id)
        elif data.startswith("select_date_"):
            selected_date = data.split("_")[2]
            await self.show_time_slots(update, context, selected_date)
        elif data.startswith("select_time_"):
            selected_slot = data.split("_")[2]
            await self.confirm_booking(update, context, selected_slot)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message."""
        help_text = """
        🆘 MediSathi Bot Help

        Available Commands:
        /start - Start the bot and see welcome message
        /book - Book a doctor appointment with date & time selection
        /find - Find doctors by symptoms and location
        /help - Show this help message

        Booking Process:
        1. Use /book command
        2. Provide your information (name, email, phone, symptoms)
        3. Select from available doctors
        4. Choose appointment date
        5. Select time slot
        6. Get instant confirmation with email

        For urgent medical assistance, please contact:
        • Emergency Services: 108
        • Medical Helpline: 104

        Stay healthy! 🏥
        """
        
        await update.message.reply_text(help_text)
    
    def run(self):
        """Run the bot."""
        print("🤖 Telegram Bot is starting...")
        print("✅ Bot is ready! Search for it on Telegram")
        self.application.run_polling()

if __name__ == '__main__':
    try:
        bot = MediSathiBot()
        bot.run()
    except Exception as e:
        print(f"❌ Failed to start Telegram bot: {e}")
        input("Press Enter to exit...")