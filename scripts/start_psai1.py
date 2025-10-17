#!/usr/bin/env python3
"""
PSAI_1 - Culture Current Lite: Startup Script
Purpose: Start both backend API and web interface for full PSAI_1 system
Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 90/100
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def start_backend():
    """Start the Flask backend API"""
    script_dir = Path(__file__).parent
    backend_script = script_dir / "web_backend.py"
    
    print("🚀 Starting PSAI_1 Backend API...")
    
    try:
        # Start Flask backend
        subprocess.run([
            sys.executable, str(backend_script)
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend failed to start: {e}")

def start_frontend():
    """Start the web frontend"""
    script_dir = Path(__file__).parent
    html_file = script_dir / "web_timeline.html"
    
    if html_file.exists():
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Get absolute path
        html_path = html_file.absolute()
        file_url = f"file://{html_path}"
        
        print("🌐 Opening PSAI_1 Web Interface...")
        webbrowser.open(file_url)
    else:
        print(f"❌ Web interface not found: {html_file}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'requests',
        'beautifulsoup4',
        'feedparser',
        'praw',
        'google-api-python-client',
        'pandas',
        'markdown',
        'python-docx',
        'ollama',
        'loguru'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("🎯 PSAI_1 - Culture Current Lite")
    print("   Full-Featured Automation System")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return 1
    
    print("✅ All dependencies found")
    
    # Start backend in separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend
    start_frontend()
    
    print("\n🎉 PSAI_1 System Started!")
    print("📡 Backend API: http://localhost:5000")
    print("🌐 Web Interface: Opened in browser")
    print("\n💡 Features:")
    print("   • Editable source URLs with validation")
    print("   • Real-time process execution")
    print("   • Actual report generation")
    print("   • Settings persistence")
    print("   • Review and approval workflow")
    print("\n⌨️  Press Ctrl+C to stop the system")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 PSAI_1 system stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())
