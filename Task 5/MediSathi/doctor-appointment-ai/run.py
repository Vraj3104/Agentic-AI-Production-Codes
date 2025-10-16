# import os
# import sys
# import subprocess
# import time

# def setup_environment():
#     """Setup the project environment"""
#     print("🏥 Setting up MediSathi environment...")
    
#     # Initialize database
#     try:
#         from backend.database import init_db
#         init_db()
#         print("✅ Database initialized successfully")
#         return True
#     except Exception as e:
#         print(f"❌ Database initialization failed: {e}")
#         return False

# def main():
#     print("🚀 Starting MediSathi AI Doctor Appointment System...")
    
#     if not setup_environment():
#         return
    
#     print("\n🎯 Choose how to run the system:")
#     print("1. Run Streamlit frontend only")
#     print("2. Run Telegram bot only") 
#     print("3. Run both services (recommended for development)")
    
#     choice = input("\nEnter your choice (1-3): ").strip()
    
#     if choice == "1":
#         print("\n🚀 Starting Streamlit frontend...")
#         subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        
#     elif choice == "2":
#         print("\n🤖 Starting Telegram bot...")
#         subprocess.run([sys.executable, "telegram_bot/bot.py"])
        
#     elif choice == "3":
#         print("\n🚀 Starting both services...")
#         print("✅ Streamlit: http://localhost:8501")
#         print("✅ Telegram: Check your bot")
#         print("⏳ Starting services...")
        
#         # Start Streamlit
#         import threading
        
#         def start_streamlit():
#             subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        
#         def start_telegram():
#             subprocess.run([sys.executable, "telegram_bot/bot.py"])
        
#         streamlit_thread = threading.Thread(target=start_streamlit)
#         telegram_thread = threading.Thread(target=start_telegram)
        
#         streamlit_thread.start()
#         time.sleep(5)  # Wait for Streamlit to start
#         telegram_thread.start()
        
#     else:
#         print("❌ Invalid choice")

# if __name__ == "__main__":
#     main()    










import os
import sys
import subprocess
import time

def setup_environment():
    """Setup the project environment"""
    print("🏥 Setting up MediSathi environment...")
    
    # Initialize database
    try:
        from backend.database import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def load_doctor_data():
    """Load and display doctor data from JSON file"""
    try:
        from agents.doctor_finder_agent import doctor_finder_agent
        stats = doctor_finder_agent.get_doctor_statistics()
        print(f"✅ Loaded {stats['total_doctors']} doctors with {stats['total_specializations']} specializations")
        print(f"📍 Available in {stats['total_cities']} cities")
        return True
    except Exception as e:
        print(f"⚠️ Doctor data loading warning: {e}")
        print("📋 Continuing with database doctors only...")
        return False

def main():
    print("🚀 Starting MediSathi AI Doctor Appointment System...")
    print("=" * 50)
    
    # Setup database environment
    if not setup_environment():
        print("❌ System initialization failed. Please check the error above.")
        return
    
    # Load doctor data from JSON
    doctor_data_loaded = load_doctor_data()
    
    if doctor_data_loaded:
        print("\n📊 System Status: Full functionality available")
        print("   • Appointment booking with database doctors")
        print("   • Doctor finding from JSON data")
        print("   • AI-powered symptom analysis")
    else:
        print("\n📊 System Status: Basic functionality available") 
        print("   • Appointment booking with database doctors")
        print("   • Limited doctor finding capabilities")
    
    print("\n" + "=" * 50)
    print("\n🎯 Choose how to run the system:")
    print("1. Run Streamlit frontend only")
    print("2. Run Telegram bot only") 
    print("3. Run both services (recommended for development)")
    print("4. Run Doctor Finder only (JSON data)")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting Streamlit frontend...")
        print("📍 Access at: http://localhost:8501")
        print("📋 Features: Booking + Doctor Finding")
        print("⏳ Launching...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        
    elif choice == "2":
        print("\n🤖 Starting Telegram bot...")
        print("📱 Check your Telegram bot")
        print("⏳ Launching...")
        subprocess.run([sys.executable, "telegram_bot/bot.py"])
        
    elif choice == "3":
        print("\n🚀 Starting both services...")
        print("✅ Streamlit: http://localhost:8501")
        print("✅ Telegram: Check your bot")
        print("📋 Features: Full system with booking and doctor finding")
        print("⏳ Starting services...")
        
        # Start Streamlit
        import threading
        
        def start_streamlit():
            subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        
        def start_telegram():
            subprocess.run([sys.executable, "telegram_bot/bot.py"])
        
        streamlit_thread = threading.Thread(target=start_streamlit)
        telegram_thread = threading.Thread(target=start_telegram)
        
        streamlit_thread.start()
        time.sleep(5)  # Wait for Streamlit to start
        telegram_thread.start()
        
    elif choice == "4":
        print("\n🔍 Starting Doctor Finder only...")
        print("📊 Using JSON doctor data")
        print("📍 Access at: http://localhost:8501") 
        print("📋 Features: Doctor finding and browsing only")
        print("⏳ Launching...")
        
        # Check if doctor data is available
        if not doctor_data_loaded:
            print("\n❌ No doctor data found in JSON file!")
            print("💡 Please ensure 'data/doctor_new.json' exists with doctor data")
            response = input("Continue anyway? (y/n): ").strip().lower()
            if response != 'y':
                return
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        
    else:
        print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def display_welcome():
    """Display welcome message and system information"""
    print("🏥 MediSathi - AI Doctor Appointment System")
    print("=" * 50)
    print("📋 System Features:")
    print("   • AI-powered doctor appointment booking")
    print("   • Symptom-based doctor recommendations") 
    print("   • Multi-source doctor database (Database + JSON)")
    print("   • Email and Telegram notifications")
    print("   • Google Calendar integration")
    print("   • Real-time availability checking")
    print("=" * 50)

if __name__ == "__main__":
    display_welcome()
    main()