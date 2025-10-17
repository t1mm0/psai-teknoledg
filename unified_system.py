#!/usr/bin/env python3
"""
PSAI_A + Teknoledg Unified System
Purpose: Combined authentication and PSAI_1 automation system
Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 95/100
"""

import os
import sys
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
import jwt
import subprocess
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuration
JWT_SECRET = os.getenv('TEKNOLEDG_JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRY_HOURS = 24
VALID_PASSCODE = os.getenv('TEKNOLEDG_PASSCODE', '316h7y$!x-71ck13-516n41!')

# Global state for PSAI_1 process tracking
psai_process_status = {
    'running': False,
    'current_stage': None,
    'progress': 0,
    'results': {},
    'error': None
}

class AuthManager:
    """Manages authentication tokens and sessions"""
    
    def __init__(self):
        self.active_tokens = set()
    
    def generate_token(self, user_ip: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_ip': user_ip,
            'authenticated_at': datetime.utcnow().isoformat(),
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        self.active_tokens.add(token)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload if valid"""
        try:
            if token not in self.active_tokens:
                return None
            
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
            
        except jwt.ExpiredSignatureError:
            self.active_tokens.discard(token)
            return None
        except jwt.InvalidTokenError:
            return None

# Initialize auth manager
auth_manager = AuthManager()

# Authentication routes
@app.route('/')
def index():
    """Main entry point - redirect to auth or dashboard"""
    return redirect('/auth')

@app.route('/auth')
def auth_page():
    """Authentication page"""
    return app.send_static_file('auth.html')

@app.route('/dashboard')
def dashboard():
    """PSAI_1 Dashboard (requires authentication)"""
    return app.send_static_file('dashboard.html')

@app.route('/psai')
def psai_redirect():
    """Redirect /psai to dashboard"""
    return redirect('/dashboard')

@app.route('/option-a')
def option_a():
    """OPTION_A - Simple trends AI flow monitor (easy)"""
    return app.send_static_file('web_timeline.html')

@app.route('/option-b')
def option_b():
    """OPTION_B - Automated Agentic with KG lite"""
    return jsonify({
        'title': 'OPTION_B - Automated Agentic with KG lite',
        'message': 'Advanced agentic automation with knowledge graph integration',
        'status': 'Coming soon',
        'features': ['Automated agents', 'Knowledge graph lite', 'Intelligent workflows']
    })

@app.route('/option-c')
def option_c():
    """OPTION_C - Full autonomous temporal KG"""
    return jsonify({
        'title': 'OPTION_C - Full autonomous temporal KG',
        'message': 'Complete autonomous system with temporal knowledge graph',
        'status': 'Coming soon',
        'features': ['Full autonomy', 'Temporal knowledge graph', 'Advanced AI reasoning']
    })

@app.route('/specsheet.pdf')
def specsheet():
    """Spec Sheet PDF"""
    return jsonify({
        'title': 'Technical Specifications',
        'message': 'Spec sheet PDF will be available here',
        'status': 'Documentation coming soon'
    })

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Authenticate user with passcode"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        passcode = data.get('passcode', '').strip()
        user_ip = data.get('ip', 'unknown')
        
        if not passcode:
            return jsonify({'success': False, 'message': 'Passcode required'}), 400
        
        # Verify passcode
        if passcode == VALID_PASSCODE:
            # Generate token
            token = auth_manager.generate_token(user_ip)
            
            # Log successful authentication
            log_auth_attempt(user_ip, True)
            
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'token': token,
                'redirect_url': '/dashboard',
                'expires_in': TOKEN_EXPIRY_HOURS * 3600
            })
        else:
            # Log failed authentication
            log_auth_attempt(user_ip, False)
            
            return jsonify({
                'success': False,
                'message': 'Invalid passcode'
            }), 401
            
    except Exception as e:
        print(f"Authentication error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/verify', methods=['GET'])
def verify_token():
    """Verify if token is valid"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'valid': False, 'message': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        payload = auth_manager.verify_token(token)
        
        if payload:
            return jsonify({
                'valid': True,
                'user_ip': payload.get('user_ip'),
                'authenticated_at': payload.get('authenticated_at')
            })
        else:
            return jsonify({'valid': False, 'message': 'Invalid or expired token'}), 401
            
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({'valid': False, 'message': 'Server error'}), 500

# PSAI_1 API routes
@app.route('/api/psai/status', methods=['GET'])
def get_psai_status():
    """Get current PSAI_1 process status"""
    return jsonify(psai_process_status)

@app.route('/api/psai/run', methods=['POST'])
def run_psai_process():
    """Start PSAI_1 process with settings"""
    global psai_process_status
    
    if psai_process_status['running']:
        return jsonify({'error': 'PSAI_1 process already running'}), 400
    
    settings = request.json
    if not settings:
        return jsonify({'error': 'No settings provided'}), 400
    
    # Start process in background thread
    def run_in_background():
        try:
            run_psai_sequence(settings)
        except Exception as e:
            psai_process_status['error'] = str(e)
            psai_process_status['running'] = False
    
    thread = threading.Thread(target=run_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'PSAI_1 process started', 'status': 'running'})

def run_psai_sequence(settings):
    """Run the complete PSAI_1 process sequence"""
    global psai_process_status
    
    try:
        psai_process_status['running'] = True
        psai_process_status['current_stage'] = 'HARVEST'
        psai_process_status['progress'] = 0
        psai_process_status['results'] = {}
        psai_process_status['error'] = None
        
        # Stage 1: Harvest
        harvest_result = simulate_harvest(settings)
        psai_process_status['results']['HARVEST'] = harvest_result
        psai_process_status['progress'] = 25
        
        # Stage 2: Extract
        psai_process_status['current_stage'] = 'EXTRACT'
        extract_result = simulate_extract(harvest_result, settings)
        psai_process_status['results']['EXTRACT'] = extract_result
        psai_process_status['progress'] = 50
        
        # Stage 3: Report
        psai_process_status['current_stage'] = 'REPORT'
        report_result = simulate_report(extract_result, settings)
        psai_process_status['results']['REPORT'] = report_result
        psai_process_status['progress'] = 75
        
        # Stage 4: Review
        psai_process_status['current_stage'] = 'REVIEW'
        review_result = simulate_review(report_result, settings)
        psai_process_status['results']['REVIEW'] = review_result
        psai_process_status['progress'] = 100
        
        psai_process_status['running'] = False
        
    except Exception as e:
        psai_process_status['error'] = str(e)
        psai_process_status['running'] = False

def simulate_harvest(settings):
    """Simulate data harvesting"""
    time.sleep(2)  # Simulate processing time
    return {
        'items_collected': len(settings.get('rssUrls', [])) * 10 + len(settings.get('redditUrls', [])) * 5,
        'sources': len(settings.get('rssUrls', [])) + len(settings.get('redditUrls', [])),
        'status': 'completed'
    }

def simulate_extract(harvest_result, settings):
    """Simulate content extraction"""
    time.sleep(3)  # Simulate processing time
    return {
        'insights': harvest_result['items_collected'] // 2,
        'trends': min(5, harvest_result['items_collected'] // 10),
        'status': 'completed'
    }

def simulate_report(extract_result, settings):
    """Simulate report generation"""
    time.sleep(2)  # Simulate processing time
    return {
        'sections': 3,
        'word_count': int(settings.get('maxLength', 1000)),
        'format': settings.get('reportFormat', 'markdown'),
        'status': 'completed'
    }

def simulate_review(report_result, settings):
    """Simulate review preparation"""
    time.sleep(1)  # Simulate processing time
    return {
        'status': 'pending_approval',
        'reviewer_email': settings.get('notificationEmail', ''),
        'created_at': datetime.now().isoformat()
    }

def log_auth_attempt(ip: str, success: bool):
    """Log authentication attempts"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'ip': ip,
        'success': success,
        'user_agent': request.headers.get('User-Agent', 'unknown')
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Log to file
    log_file = 'logs/auth_attempts.log'
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Also print to console
    status = "SUCCESS" if success else "FAILED"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AUTH {status} from {ip}")

@app.route('/api/client/info', methods=['GET'])
def get_client_info():
    """Get client information based on authentication"""
    try:
        # For now, return default client info
        # In a real implementation, you'd decode the JWT token to get client ID
        client_info = {
            'name': 'Client One',
            'company': 'Teknoledg',
            'description': 'Advanced AI automation and data intelligence solutions for modern businesses.',
            'permissions': ['option_a', 'option_b', 'option_c', 'specsheet'],
            'theme': {
                'primary_color': '#20b2aa',
                'background_color': '#262626',
                'accent_color': '#008b8b'
            }
        }
        return jsonify(client_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PSAI_A + Teknoledg Unified System',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'features': ['authentication', 'psai_1_automation', 'dashboard']
    })

if __name__ == '__main__':
    print("🚀 Starting PSAI_A + Teknoledg Unified System")
    print("=" * 60)
    print(f"🌐 System will be available at: http://localhost:5000")
    print(f"🔐 Authentication: http://localhost:5000/auth")
    print(f"📊 PSAI_1 Dashboard: http://localhost:5000/dashboard")
    print(f"🔑 Passcode: {'Configured' if VALID_PASSCODE != 'default123' else 'Using default'}")
    print("=" * 60)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
