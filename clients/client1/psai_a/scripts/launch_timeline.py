#!/usr/bin/env python3
"""
PSAI_1 - Culture Current Lite: Timeline Launcher
Purpose: Launch the visual timeline component (desktop or web version)
Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 85/100
"""

import os
import sys
import webbrowser
import subprocess
import argparse
from pathlib import Path

def launch_web_timeline():
    """Launch the web-based timeline"""
    script_dir = Path(__file__).parent
    html_file = script_dir / "web_timeline.html"
    
    if html_file.exists():
        # Get absolute path
        html_path = html_file.absolute()
        file_url = f"file://{html_path}"
        
        print(f"🌐 Opening web timeline: {file_url}")
        webbrowser.open(file_url)
        return True
    else:
        print(f"❌ Web timeline file not found: {html_file}")
        return False

def launch_desktop_timeline():
    """Launch the desktop timeline application"""
    script_dir = Path(__file__).parent
    timeline_script = script_dir / "visual_timeline.py"
    
    if timeline_script.exists():
        print("🖥️  Launching desktop timeline...")
        try:
            subprocess.run([sys.executable, str(timeline_script)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to launch desktop timeline: {e}")
            return False
    else:
        print(f"❌ Desktop timeline script not found: {timeline_script}")
        return False

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='PSAI_1 Timeline Launcher')
    parser.add_argument('--web', action='store_true', help='Launch web version')
    parser.add_argument('--desktop', action='store_true', help='Launch desktop version')
    parser.add_argument('--auto', action='store_true', help='Auto-detect best option')
    
    args = parser.parse_args()
    
    print("🚀 PSAI_1 Visual Timeline Launcher")
    print("=" * 40)
    
    if args.web:
        success = launch_web_timeline()
    elif args.desktop:
        success = launch_desktop_timeline()
    elif args.auto:
        # Try web first, fallback to desktop
        print("🔍 Auto-detecting best option...")
        success = launch_web_timeline()
        if not success:
            print("🔄 Falling back to desktop version...")
            success = launch_desktop_timeline()
    else:
        # Interactive mode
        print("Choose timeline version:")
        print("1. Web version (opens in browser)")
        print("2. Desktop version (requires tkinter)")
        print("3. Auto-detect")
        
        try:
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                success = launch_web_timeline()
            elif choice == "2":
                success = launch_desktop_timeline()
            elif choice == "3":
                success = launch_web_timeline()
                if not success:
                    success = launch_desktop_timeline()
            else:
                print("❌ Invalid choice")
                return 1
                
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
            return 0
    
    if success:
        print("✅ Timeline launched successfully!")
        return 0
    else:
        print("❌ Failed to launch timeline")
        return 1

if __name__ == "__main__":
    sys.exit(main())
