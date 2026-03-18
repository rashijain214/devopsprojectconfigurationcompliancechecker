#!/usr/bin/env python3
"""
Flask Web App for Configuration Compliance Checker
Serves real-time compliance data to the dashboard
"""

from flask import Flask, render_template, jsonify
import subprocess
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/compliance')
def get_compliance_data():
    """API endpoint to get real compliance data"""
    try:
        # Run compliance checker on test files with absolute paths
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(base_path)))
        test_files = [
            os.path.join(project_root, 'test_violations', 'Dockerfile'),
            os.path.join(project_root, 'test_violations', 'docker-compose.yml'), 
            os.path.join(project_root, 'test_violations', 'deployment.yaml')
        ]
        
        result = subprocess.run([
            'python', 'compliance_checker.py', '--json'
        ] + test_files, 
        capture_output=True, text=True, cwd=base_path)
        
        print(f"DEBUG: Base path: {base_path}")
        print(f"DEBUG: Command result: {result.returncode}")
        print(f"DEBUG: stdout: {result.stdout[:200]}...")
        print(f"DEBUG: stderr: {result.stderr}")
        
        # Try to parse JSON output regardless of return code
        # The compliance checker returns exit code 1 when critical violations are found
        try:
            compliance_data = json.loads(result.stdout)
            # Convert to dashboard format
            violations = []
            for file_data in compliance_data.get('files', []):
                for violation in file_data.get('violations', []):
                    violations.append({
                        'severity': violation['severity'],
                        'message': f"[{violation['rule_id']}] {violation['message']}"
                    })
            
            dashboard_data = {
                'summary': {
                    'critical_issues': compliance_data.get('summary', {}).get('critical', 0),
                    'total_violations': compliance_data.get('summary', {}).get('total_violations', 0),
                    'status': 'NON-COMPLIANT' if compliance_data.get('summary', {}).get('critical', 0) > 0 else 'COMPLIANT'
                },
                'violations': violations,
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(dashboard_data)
        except json.JSONDecodeError:
            # If JSON parsing fails, parse as plain text
            compliance_data = parse_compliance_output(result.stdout)
            return jsonify(compliance_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

def parse_compliance_output(output):
    """Parse compliance checker output when JSON fails"""
    lines = output.split('\n')
    violations = []
    critical_count = 0
    
    for line in lines:
        if '[CRITICAL]' in line:
            critical_count += 1
            violations.append({
                'severity': 'CRITICAL',
                'message': line.strip()
            })
        elif '[HIGH]' in line:
            violations.append({
                'severity': 'HIGH', 
                'message': line.strip()
            })
        elif '[MEDIUM]' in line:
            violations.append({
                'severity': 'MEDIUM',
                'message': line.strip()
            })
    
    return {
        'summary': {
            'critical_issues': critical_count,
            'total_violations': len(violations),
            'status': 'NON-COMPLIANT' if critical_count > 0 else 'COMPLIANT'
        },
        'violations': violations,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)