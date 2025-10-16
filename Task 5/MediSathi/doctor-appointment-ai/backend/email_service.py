import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from src.utils.config import Config

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_user = Config.EMAIL_USER
        self.email_password = Config.EMAIL_PASSWORD
    
    def send_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP"""
        try:
            message = MimeMultipart()
            message["From"] = self.email_user
            message["To"] = to_email
            message["Subject"] = subject
            
            message.attach(MimeText(body, "plain"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(message)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

email_service = EmailService()