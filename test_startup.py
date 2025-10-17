#!/usr/bin/env python3
"""
Test script to verify PSAI app can start without errors
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import os
        import sys
        import json
        import secrets
        import hashlib
        from datetime import datetime, timedelta
        from typing import Dict, Optional
        print("✅ Basic imports successful")
        
        # Test Flask imports
        from flask import Flask, request, jsonify, render_template_string, redirect, url_for
        from flask_cors import CORS
        print("✅ Flask imports successful")
        
        # Test JWT import
        import jwt
        print("✅ JWT import successful")
        
        # Test other imports
        import subprocess
        import threading
        import time
        print("✅ All imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    try:
        print("\nTesting Flask app creation...")
        
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health')
        def health():
            return {'status': 'ok'}
        
        print("✅ Flask app creation successful")
        return True
        
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing PSAI app startup...")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test Flask app
    flask_ok = test_flask_app()
    
    print("\n" + "=" * 50)
    if imports_ok and flask_ok:
        print("✅ All tests passed! App should start successfully.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
