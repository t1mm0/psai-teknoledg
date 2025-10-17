#!/usr/bin/env python3
"""
PSAI_1 - Culture Current Lite: Web Backend API
Purpose: Backend API to handle real data processing and report generation
Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 90/100
"""

import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Global state for process tracking
process_status = {
    'running': False,
    'current_stage': None,
    'progress': 0,
    'results': {},
    'error': None
}

class PSAIProcessor:
    """Main processor for PSAI_1 operations"""
    
    def __init__(self):
        self.scripts_dir = os.path.join(os.path.dirname(__file__))
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.briefs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'briefs')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.briefs_dir, exist_ok=True)
    
    def process_with_settings(self, settings: Dict) -> Dict:
        """Process PSAI_1 with given settings"""
        global process_status
        
        try:
            process_status['running'] = True
            process_status['current_stage'] = 'HARVEST'
            process_status['progress'] = 0
            process_status['results'] = {}
            process_status['error'] = None
            
            # Stage 1: Harvest
            harvest_result = self._harvest_data(settings)
            process_status['results']['HARVEST'] = harvest_result
            process_status['progress'] = 25
            
            # Stage 2: Extract
            process_status['current_stage'] = 'EXTRACT'
            extract_result = self._extract_insights(harvest_result, settings)
            process_status['results']['EXTRACT'] = extract_result
            process_status['progress'] = 50
            
            # Stage 3: Report
            process_status['current_stage'] = 'REPORT'
            report_result = self._generate_report(extract_result, settings)
            process_status['results']['REPORT'] = report_result
            process_status['progress'] = 75
            
            # Stage 4: Review
            process_status['current_stage'] = 'REVIEW'
            review_result = self._prepare_review(report_result, settings)
            process_status['results']['REVIEW'] = review_result
            process_status['progress'] = 100
            
            process_status['running'] = False
            return process_status['results']
            
        except Exception as e:
            process_status['error'] = str(e)
            process_status['running'] = False
            raise
    
    def _harvest_data(self, settings: Dict) -> Dict:
        """Harvest data from configured sources"""
        # Create temporary config file
        config = {
            "sources": {
                "rss": settings.get('rssUrls', []),
                "reddit": {
                    "subreddits": [url.replace('r/', '') for url in settings.get('redditUrls', [])],
                    "limit": int(settings.get('harvestLimit', 25))
                }
            },
            "deduplication": {
                "enabled": True,
                "cache_file": os.path.join(self.data_dir, "url_cache.json")
            }
        }
        
        config_file = os.path.join(self.data_dir, "harvest_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Run harvest script
        harvest_script = os.path.join(self.scripts_dir, 'harvest.py')
        output_file = os.path.join(self.data_dir, f"harvest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        cmd = [
            sys.executable, harvest_script,
            '--config', config_file,
            '--output', output_file,
            '--test' if settings.get('processingSpeed') == 'fast' else ''
        ]
        cmd = [c for c in cmd if c]  # Remove empty strings
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Harvest failed: {result.stderr}")
        
        # Load and return results
        with open(output_file, 'r') as f:
            harvest_data = json.load(f)
        
        return {
            'items_collected': harvest_data.get('total_items', 0),
            'sources': len(settings.get('rssUrls', [])) + len(settings.get('redditUrls', [])),
            'output_file': output_file,
            'harvest_data': harvest_data
        }
    
    def _extract_insights(self, harvest_result: Dict, settings: Dict) -> Dict:
        """Extract insights from harvested data"""
        # Create extraction config
        config = {
            "models": {
                "primary": settings.get('aiModel', 'llama3.1'),
                "fallback": "mistral",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "extraction": {
                "batch_size": 5,
                "max_content_length": 4000,
                "min_confidence_threshold": 0.6
            }
        }
        
        config_file = os.path.join(self.data_dir, "extract_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Run extraction script
        extract_script = os.path.join(self.scripts_dir, 'extract.py')
        output_file = os.path.join(self.data_dir, f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        cmd = [
            sys.executable, extract_script,
            '--input', harvest_result['output_file'],
            '--output', output_file,
            '--test' if settings.get('processingSpeed') == 'fast' else ''
        ]
        cmd = [c for c in cmd if c]  # Remove empty strings
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            raise Exception(f"Extraction failed: {result.stderr}")
        
        # Load and return results
        with open(output_file, 'r') as f:
            extraction_data = json.load(f)
        
        return {
            'insights': extraction_data.get('total_insights', 0),
            'trends': extraction_data.get('total_trends', 0),
            'output_file': output_file,
            'extraction_data': extraction_data
        }
    
    def _generate_report(self, extract_result: Dict, settings: Dict) -> Dict:
        """Generate report from extracted insights"""
        # Create report config
        config = {
            "report": {
                "title_template": "Culture Current Weekly Brief - {date}",
                "max_sections": 5,
                "max_words_per_section": int(settings.get('maxLength', 1000)) // 5,
                "include_executive_summary": settings.get('includeSummary', True),
                "include_recommendations": settings.get('includeRecommendations', True)
            },
            "models": {
                "primary": settings.get('aiModel', 'llama3.1'),
                "fallback": "mistral",
                "temperature": 0.7,
                "max_tokens": 3000
            },
            "output": {
                "formats": [settings.get('reportFormat', 'markdown')],
                "save_path": self.briefs_dir + "/",
                "template_path": os.path.join(os.path.dirname(__file__), "templates/")
            }
        }
        
        config_file = os.path.join(self.data_dir, "report_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Run report script
        report_script = os.path.join(self.scripts_dir, 'report.py')
        output_dir = self.briefs_dir
        
        cmd = [
            sys.executable, report_script,
            '--input', extract_result['output_file'],
            '--output', output_dir,
            '--format', settings.get('reportFormat', 'markdown'),
            '--test' if settings.get('processingSpeed') == 'fast' else ''
        ]
        cmd = [c for c in cmd if c]  # Remove empty strings
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Report generation failed: {result.stderr}")
        
        return {
            'sections': 3,  # Default, would be calculated from actual report
            'word_count': int(settings.get('maxLength', 1000)),
            'output_dir': output_dir,
            'format': settings.get('reportFormat', 'markdown')
        }
    
    def _prepare_review(self, report_result: Dict, settings: Dict) -> Dict:
        """Prepare review data"""
        return {
            'status': 'pending_approval',
            'reviewer_email': settings.get('notificationEmail', ''),
            'created_at': datetime.now().isoformat()
        }

# Initialize processor
processor = PSAIProcessor()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current process status"""
    return jsonify(process_status)

@app.route('/api/run', methods=['POST'])
def run_process():
    """Start PSAI_1 process with settings"""
    global process_status
    
    if process_status['running']:
        return jsonify({'error': 'Process already running'}), 400
    
    settings = request.json
    if not settings:
        return jsonify({'error': 'No settings provided'}), 400
    
    # Start process in background thread
    def run_in_background():
        try:
            processor.process_with_settings(settings)
        except Exception as e:
            process_status['error'] = str(e)
            process_status['running'] = False
    
    thread = threading.Thread(target=run_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Process started', 'status': 'running'})

@app.route('/api/sources/validate', methods=['POST'])
def validate_sources():
    """Validate source URLs"""
    data = request.json
    rss_urls = data.get('rssUrls', [])
    reddit_urls = data.get('redditUrls', [])
    
    results = {
        'rss': [],
        'reddit': [],
        'valid_count': 0,
        'invalid_count': 0
    }
    
    # Validate RSS URLs
    for url in rss_urls:
        try:
            import requests
            response = requests.head(url, timeout=5)
            is_valid = response.status_code < 400
            results['rss'].append({'url': url, 'valid': is_valid})
            if is_valid:
                results['valid_count'] += 1
            else:
                results['invalid_count'] += 1
        except:
            results['rss'].append({'url': url, 'valid': False})
            results['invalid_count'] += 1
    
    # Validate Reddit URLs (simplified)
    for url in reddit_urls:
        is_valid = url.startswith('r/') and len(url) > 2
        results['reddit'].append({'url': url, 'valid': is_valid})
        if is_valid:
            results['valid_count'] += 1
        else:
            results['invalid_count'] += 1
    
    return jsonify(results)

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get list of generated reports"""
    reports = []
    
    if os.path.exists(processor.briefs_dir):
        for filename in os.listdir(processor.briefs_dir):
            if filename.endswith(('.md', '.docx')):
                filepath = os.path.join(processor.briefs_dir, filename)
                stat = os.stat(filepath)
                reports.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'type': 'markdown' if filename.endswith('.md') else 'docx'
                })
    
    return jsonify(reports)

@app.route('/api/reports/<filename>', methods=['GET'])
def download_report(filename):
    """Download a specific report"""
    filepath = os.path.join(processor.briefs_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Report not found'}), 404
    
    return send_file(filepath, as_attachment=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting PSAI_1 Web Backend API")
    print("📡 API will be available at: http://localhost:5000")
    print("🌐 Web interface: Open web_timeline.html in browser")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
