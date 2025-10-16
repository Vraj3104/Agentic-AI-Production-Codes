# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime
# import requests

# from utils.config import Config

# class NotificationAgent:
#     def __init__(self):
#         self.smtp_server = Config.SMTP_SERVER
#         self.smtp_port = Config.SMTP_PORT
#         self.email_user = Config.EMAIL_USER
#         self.email_password = Config.EMAIL_PASSWORD
    
#     def send_appointment_confirmation(self, patient_email: str, appointment_details: dict):
#         """Send appointment confirmation email"""
#         try:
#             message = MIMEMultipart('alternative')
#             message["From"] = self.email_user
#             message["To"] = patient_email
#             message["Subject"] = "✅ Appointment Confirmation - MediSathi"
            
#             # Create HTML email content
#             html = f"""
#             <!DOCTYPE html>
#             <html>
#             <head>
#                 <style>
#                     body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                     .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                     .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
#                     .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
#                     .details {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
#                     .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
#                 </style>
#             </head>
#             <body>
#                 <div class="container">
#                     <div class="header">
#                         <h1>🏥 MediSathi</h1>
#                         <h2>Appointment Confirmed!</h2>
#                     </div>
#                     <div class="content">
#                         <p>Dear <strong>{appointment_details['patient_name']}</strong>,</p>
#                         <p>Your appointment has been successfully booked. Here are your appointment details:</p>
                        
#                         <div class="details">
#                             <h3>📋 Appointment Details</h3>
#                             <p><strong>Appointment ID:</strong> #{appointment_details['appointment_id']}</p>
#                             <p><strong>Doctor:</strong> Dr. {appointment_details['doctor_name']}</p>
#                             <p><strong>Specialization:</strong> {appointment_details['doctor_specialization']}</p>
#                             <p><strong>Date:</strong> {appointment_details['date']}</p>
#                             <p><strong>Time:</strong> {appointment_details['time']}</p>
#                             <p><strong>Clinic Address:</strong> {appointment_details['clinic_address']}</p>
#                             <p><strong>Contact:</strong> {appointment_details['doctor_phone']}</p>
#                         </div>
                        
#                         <h3>📝 Important Instructions:</h3>
#                         <ul>
#                             <li>Please arrive <strong>15 minutes before</strong> your scheduled appointment time</li>
#                             <li>Bring your ID proof and any previous medical reports</li>
#                             <li>Carry your health insurance details if applicable</li>
#                             <li>In case of cancellation, please inform at least 24 hours in advance</li>
#                         </ul>
                        
#                         <p>If you have any questions or need to reschedule, please contact the clinic directly.</p>
                        
#                         <p>Best regards,<br><strong>The MediSathi Team</strong></p>
#                     </div>
#                     <div class="footer">
#                         <p>This is an automated message. Please do not reply to this email.</p>
#                         <p>MediSathi - Your Trusted Healthcare Partner</p>
#                     </div>
#                 </div>
#             </body>
#             </html>
#             """
            
#             # Create plain text version as fallback
#             text = f"""
#             APPOINTMENT CONFIRMATION - MediSathi
            
#             Dear {appointment_details['patient_name']},
            
#             Your appointment has been successfully booked!
            
#             APPOINTMENT DETAILS:
#             - Appointment ID: #{appointment_details['appointment_id']}
#             - Doctor: Dr. {appointment_details['doctor_name']}
#             - Specialization: {appointment_details['doctor_specialization']}
#             - Date: {appointment_details['date']}
#             - Time: {appointment_details['time']}
#             - Clinic Address: {appointment_details['clinic_address']}
#             - Contact: {appointment_details['doctor_phone']}
            
#             IMPORTANT INSTRUCTIONS:
#             - Please arrive 15 minutes before your appointment
#             - Bring your ID and any medical reports
#             - Cancel at least 24 hours in advance if needed
            
#             Best regards,
#             MediSathi Team
#             """
            
#             # Attach both HTML and plain text versions
#             part1 = MIMEText(text, "plain")
#             part2 = MIMEText(html, "html")
            
#             message.attach(part1)
#             message.attach(part2)
            
#             # Send email
#             with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
#                 server.starttls()
#                 server.login(self.email_user, self.email_password)
#                 server.send_message(message)
            
#             print(f"✅ Confirmation email sent to {patient_email}")
#             return {"status": "success", "message": "Confirmation email sent successfully"}
            
#         except Exception as e:
#             print(f"❌ Error sending email: {e}")
#             return {"status": "error", "message": str(e)}
    
#     def send_telegram_notification(self, chat_id: str, message: str):
#         """Send notification via Telegram bot"""
#         try:
#             url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
#             payload = {
#                 "chat_id": chat_id,
#                 "text": message,
#                 "parse_mode": "HTML"
#             }
            
#             response = requests.post(url, json=payload)
#             return response.json()
#         except Exception as e:
#             return {"status": "error", "message": str(e)}
    
#     def send_booking_confirmation_telegram(self, chat_id: str, appointment_details: dict):
#         """Send booking confirmation via Telegram"""
#         message = f"""
#         ✅ <b>Appointment Confirmed!</b>

#         🏥 <b>MediSathi Booking Confirmation</b>

#         👤 <b>Patient:</b> {appointment_details['patient_name']}
#         🆔 <b>Appointment ID:</b> #{appointment_details['appointment_id']}
        
#         👨‍⚕️ <b>Doctor:</b> Dr. {appointment_details['doctor_name']}
#         🎯 <b>Specialization:</b> {appointment_details['doctor_specialization']}
        
#         📅 <b>Date:</b> {appointment_details['date']}
#         🕒 <b>Time:</b> {appointment_details['time']}
        
#         📍 <b>Clinic:</b> {appointment_details['clinic_address']}
#         📞 <b>Contact:</b> {appointment_details['doctor_phone']}

#         💡 <i>Please arrive 15 minutes early and bring your ID</i>
        
#         📧 <i>A confirmation email has been sent to your registered email address.</i>
        
#         Thank you for choosing MediSathi! 🏥
#         """
        
#         return self.send_telegram_notification(chat_id, message)

# notification_agent = NotificationAgent()/








import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

from utils.config import Config

class NotificationAgent:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_user = Config.EMAIL_USER
        self.email_password = Config.EMAIL_PASSWORD
    
    def send_appointment_confirmation(self, patient_email: str, appointment_details: dict):
        """Send appointment confirmation email"""
        try:
            message = MIMEMultipart('alternative')
            message["From"] = self.email_user
            message["To"] = patient_email
            message["Subject"] = "✅ Appointment Confirmation - MediSathi"
            
            # Create HTML email content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .details {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏥 MediSathi</h1>
                        <h2>Appointment Confirmed!</h2>
                    </div>
                    <div class="content">
                        <p>Dear <strong>{appointment_details['patient_name']}</strong>,</p>
                        <p>Your appointment has been successfully booked. Here are your appointment details:</p>
                        
                        <div class="details">
                            <h3>📋 Appointment Details</h3>
                            <p><strong>Appointment ID:</strong> #{appointment_details['appointment_id']}</p>
                            <p><strong>Doctor:</strong> Dr. {appointment_details['doctor_name']}</p>
                            <p><strong>Specialization:</strong> {appointment_details['doctor_specialization']}</p>
                            <p><strong>Date:</strong> {appointment_details['appointment_date']}</p>
                            <p><strong>Time:</strong> {appointment_details['appointment_time']}</p>
                            <p><strong>Clinic Address:</strong> {appointment_details['clinic_address']}</p>
                            <p><strong>Contact:</strong> {appointment_details['doctor_phone']}</p>
                        </div>
                        
                        <h3>📝 Important Instructions:</h3>
                        <ul>
                            <li>Please arrive <strong>15 minutes before</strong> your scheduled appointment time</li>
                            <li>Bring your ID proof and any previous medical reports</li>
                            <li>Carry your health insurance details if applicable</li>
                            <li>In case of cancellation, please inform at least 24 hours in advance</li>
                        </ul>
                        
                        <p>If you have any questions or need to reschedule, please contact the clinic directly.</p>
                        
                        <p>Best regards,<br><strong>The MediSathi Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                        <p>MediSathi - Your Trusted Healthcare Partner</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version as fallback
            text = f"""
            APPOINTMENT CONFIRMATION - MediSathi
            
            Dear {appointment_details['patient_name']},
            
            Your appointment has been successfully booked!
            
            APPOINTMENT DETAILS:
            - Appointment ID: #{appointment_details['appointment_id']}
            - Doctor: Dr. {appointment_details['doctor_name']}
            - Specialization: {appointment_details['doctor_specialization']}
            - Date: {appointment_details['appointment_date']}
            - Time: {appointment_details['appointment_time']}
            - Clinic Address: {appointment_details['clinic_address']}
            - Contact: {appointment_details['doctor_phone']}
            
            IMPORTANT INSTRUCTIONS:
            - Please arrive 15 minutes before your appointment
            - Bring your ID and any medical reports
            - Cancel at least 24 hours in advance if needed
            
            Best regards,
            MediSathi Team
            """
            
            # Attach both HTML and plain text versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(message)
            
            print(f"✅ Confirmation email sent to {patient_email}")
            return {"status": "success", "message": "Confirmation email sent successfully"}
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_telegram_notification(self, chat_id: str, message: str):
        """Send notification via Telegram bot"""
        try:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_booking_confirmation_telegram(self, chat_id: str, appointment_details: dict):
        """Send booking confirmation via Telegram"""
        message = f"""
        ✅ <b>Appointment Confirmed!</b>

        🏥 <b>MediSathi Booking Confirmation</b>

        👤 <b>Patient:</b> {appointment_details['patient_name']}
        🆔 <b>Appointment ID:</b> #{appointment_details['appointment_id']}
        
        👨‍⚕️ <b>Doctor:</b> Dr. {appointment_details['doctor_name']}
        🎯 <b>Specialization:</b> {appointment_details['doctor_specialization']}
        
        📅 <b>Date:</b> {appointment_details['appointment_date']}
        🕒 <b>Time:</b> {appointment_details['appointment_time']}
        
        📍 <b>Clinic:</b> {appointment_details['clinic_address']}
        📞 <b>Contact:</b> {appointment_details['doctor_phone']}

        💡 <i>Please arrive 15 minutes early and bring your ID</i>
        
        📧 <i>A confirmation email has been sent to your registered email address.</i>
        
        Thank you for choosing MediSathi! 🏥
        """
        
        return self.send_telegram_notification(chat_id, message)

notification_agent = NotificationAgent()