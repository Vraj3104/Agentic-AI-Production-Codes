# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     # Telegram
#     TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
#     # Google APIs
#     GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
#     GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
    
#     # AI/LLM
#     GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
#     # Database
#     DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/medisathi.db')
    
#     # Email
#     SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
#     SMTP_PORT = os.getenv('SMTP_PORT', '587')
#     EMAIL_USER = os.getenv('EMAIL_USER')
#     EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# # Create config instance
# config = Config()













import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Google APIs
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
    
    # AI/LLM
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/medisathi.db')
    
    # Email
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = os.getenv('SMTP_PORT', '587')
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # File paths - NEW: Doctor Finder Configuration
    DOCTOR_JSON_PATH = os.getenv('DOCTOR_JSON_PATH', 'data/doctor_new.json')
    
    # System Settings - NEW
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '50'))
    ENABLE_AI_SYMPTOM_ANALYSIS = os.getenv('ENABLE_AI_SYMPTOM_ANALYSIS', 'true').lower() == 'true'
    
    # Notification Settings - NEW
    SEND_EMAIL_NOTIFICATIONS = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'true').lower() == 'true'
    SEND_TELEGRAM_NOTIFICATIONS = os.getenv('SEND_TELEGRAM_NOTIFICATIONS', 'true').lower() == 'true'

# Create config instance
config = Config()

# Configuration validation and warnings
def validate_config():
    """Validate configuration and show warnings for missing required settings"""
    warnings = []
    
    # Required configurations
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == 'your-gemini-api-key-here':
        warnings.append("⚠️  GEMINI_API_KEY not set - AI symptom analysis will use fallback keyword matching")
    
    if not config.TELEGRAM_BOT_TOKEN:
        warnings.append("⚠️  TELEGRAM_BOT_TOKEN not set - Telegram bot functionality disabled")
    
    if not config.EMAIL_USER or not config.EMAIL_PASSWORD:
        warnings.append("⚠️  Email credentials not set - Email notifications disabled")
    
    # Check if doctor JSON file exists
    if not os.path.exists(config.DOCTOR_JSON_PATH):
        warnings.append(f"⚠️  Doctor JSON file not found at {config.DOCTOR_JSON_PATH} - Doctor finding will use database only")
    
    # Database file check
    db_path = config.DATABASE_URL.replace('sqlite:///', '')
    if db_path.startswith('./'):
        db_path = db_path[2:]
    if not os.path.exists(db_path) and 'sqlite' in config.DATABASE_URL:
        warnings.append("ℹ️  Database file will be created automatically on first run")
    
    return warnings

# Display configuration status
def display_config_status():
    """Display current configuration status"""
    print("🔧 MediSathi Configuration Status")
    print("=" * 40)
    
    # Basic info
    print(f"📊 Database: {config.DATABASE_URL}")
    print(f"📁 Doctor Data: {config.DOCTOR_JSON_PATH}")
    print(f"🔍 Max Results: {config.MAX_SEARCH_RESULTS}")
    
    # Feature status
    features = []
    if config.GEMINI_API_KEY and config.GEMINI_API_KEY != 'your-gemini-api-key-here':
        features.append("AI Symptom Analysis ✅")
    else:
        features.append("AI Symptom Analysis ❌ (using keywords)")
    
    if config.TELEGRAM_BOT_TOKEN:
        features.append("Telegram Bot ✅")
    else:
        features.append("Telegram Bot ❌")
    
    if config.EMAIL_USER and config.EMAIL_PASSWORD:
        features.append("Email Notifications ✅")
    else:
        features.append("Email Notifications ❌")
    
    if os.path.exists(config.DOCTOR_JSON_PATH):
        features.append("JSON Doctor Data ✅")
    else:
        features.append("JSON Doctor Data ❌")
    
    print("🚀 Features: " + " | ".join(features))
    print("=" * 40)

# Environment variable documentation
ENV_TEMPLATE = """
# MediSathi Environment Configuration Template
# Copy this to .env file and update with your values

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Google APIs (Optional)
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_CALENDAR_ID=your_google_calendar_id_here

# Gemini AI (Required for AI symptom analysis)
GEMINI_API_KEY=your_gemini_api_key_here

# Database (SQLite by default)
DATABASE_URL=sqlite:///./data/medisathi.db

# Email Settings (Optional - for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Doctor Finder Settings
DOCTOR_JSON_PATH=data/doctor_new.json
MAX_SEARCH_RESULTS=50
ENABLE_AI_SYMPTOM_ANALYSIS=true

# Notification Settings
SEND_EMAIL_NOTIFICATIONS=true
SEND_TELEGRAM_NOTIFICATIONS=true
"""

def generate_env_template():
    """Generate .env template file if it doesn't exist"""
    env_file = '.env'
    if not os.path.exists(env_file):
        try:
            with open(env_file, 'w') as f:
                f.write(ENV_TEMPLATE)
            print(f"📁 Created {env_file} template file")
            print("💡 Please update it with your actual configuration values")
        except Exception as e:
            print(f"❌ Could not create {env_file}: {e}")

# Initialize configuration checks when module is imported
config_warnings = validate_config()

if __name__ == "__main__":
    # When run directly, show configuration status
    display_config_status()
    
    if config_warnings:
        print("\n⚠️  Configuration Warnings:")
        for warning in config_warnings:
            print(f"   {warning}")
    
    # Offer to create .env template if missing
    if not os.path.exists('.env'):
        response = input("\n📁 No .env file found. Create template? (y/n): ")
        if response.lower() == 'y':
            generate_env_template()