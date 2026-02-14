#!/usr/bin/env python3
"""
Phiversity Integration Verification Script
Checks if frontend-backend integration is properly configured
"""

import sys
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

class Checker:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def check(self, name, condition, error_msg=""):
        print(f"  {'✓' if condition else '✗'} {name}", end="")
        if error_msg and not condition:
            print(f" - {error_msg}")
        else:
            print()
        
        if condition:
            self.passed += 1
        else:
            self.failed += 1
            
    def warn(self, name, msg=""):
        print(f"  ⚠ {name}", end="")
        if msg:
            print(f" - {msg}")
        else:
            print()
        self.warnings += 1
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"Results: {self.passed}/{total} checks passed")
        if self.warnings:
            print(f"Warnings: {self.warnings}")
        if self.failed > 0:
            print(f"❌ {self.failed} issues need fixing")
        else:
            print("✅ All systems operational!")
        print(f"{'='*50}\n")
        return self.failed == 0

def main():
    print("\n" + "="*50)
    print("Phiversity Integration Check")
    print("="*50 + "\n")
    
    checker = Checker()
    
    # 1. Files Check
    print("1. Checking project files...")
    project_root = Path(__file__).parent
    
    files_to_check = {
        'web/index.html': 'Main UI',
        'web/login.html': 'Login UI',
        'scripts/server/app.py': 'FastAPI Backend',
        'requirements.txt': 'Dependencies',
    }
    
    for file_path, desc in files_to_check.items():
        full_path = project_root / file_path
        checker.check(f"{desc} ({file_path})", full_path.exists(), f"File not found at {file_path}")
    
    # 2. Python Check
    print("\n2. Checking Python environment...")
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        checker.check("Python installed", True, version)
    except Exception as e:
        checker.check("Python installed", False, str(e))
    
    # 3. Dependencies Check
    print("\n3. Checking dependencies...")
    required_packages = ['fastapi', 'uvicorn', 'pydantic', 'dotenv']
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'show', package],
                         capture_output=True, timeout=5, check=True)
            checker.check(f"Installed: {package}", True)
        except Exception:
            checker.warn(f"Missing: {package}", "Run: pip install -r requirements.txt")
    
    # 4. Backend Health Check
    print("\n4. Checking backend connectivity...")
    try:
        req = Request('http://localhost:8001/health', method='GET')
        with urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            checker.check("Backend running on :8001", True, f"Status: {data.get('status')}")
    except HTTPError as e:
        checker.warn("Backend server", f"HTTP {e.code} (server may need restart)")
    except URLError as e:
        checker.check("Backend running on :8001", False, "Server not responding")
    except Exception as e:
        checker.check("Backend running on :8001", False, str(e))
    
    # 5. Static Files Check
    print("\n5. Checking static files serving...")
    try:
        req = Request('http://localhost:8001/', method='GET')
        with urlopen(req, timeout=3) as response:
            content = response.read().decode()
            has_phiversity = 'Phiversity' in content
            has_svg = '.svg' in content or 'logo' in content.lower()
            checker.check("HTML loads from /", True)
            checker.check("Page contains header", has_phiversity, "Phiversity title not found")
    except URLError:
        checker.check("Can access /", False, "Backend not running")
    except Exception as e:
        checker.check("Can access /", False, str(e))
    
    # 6. API Configuration Check
    print("\n6. Checking API configuration...")
    
    app_py = project_root / 'scripts/server/app.py'
    if app_py.exists():
        content = app_py.read_text()
        checker.check("CORS configured", 
                     'CORSMiddleware' in content and 'localhost:8001' in content,
                     "CORS may not allow localhost:8001")
        checker.check("API routes defined", 
                     '/api/run' in content and '/api/jobs/' in content,
                     "Missing API endpoints")
    
    # 7. Frontend Integration Check
    print("\n7. Checking frontend integration...")
    
    index_html = project_root / 'web/index.html'
    if index_html.exists():
        content = index_html.read_text()
        checker.check("API endpoints configured", 
                     'API_ENDPOINTS' in content,
                     "No API configuration found")
        checker.check("Job polling implemented", 
                     'pollJobStatus' in content,
                     "Missing polling logic")
        checker.check("Error handling", 
                     'showError' in content,
                     "No error display")
        checker.check("Video display", 
                     'video-section' in content and 'result-video' in content,
                     "Missing video player")
    
    # 8. Environment Check
    print("\n8. Checking environment setup...")
    
    env_file = project_root / '.env'
    if env_file.exists():
        content = env_file.read_text()
        checker.check(".env file present", True)
        checker.check("CORS_ORIGINS configured", 'CORS_ORIGINS' in content)
        checker.check("API keys configured", 
                     'API_KEY' in content.upper(),
                     "No API keys in .env (needed for generation)")
    else:
        checker.warn(".env file", "Optional but recommended for configuration")
    
    # 9. Startup Scripts Check
    print("\n9. Checking startup scripts...")
    
    bat_file = project_root / 'START_SERVER.bat'
    ps_file = project_root / 'START_SERVER.ps1'
    
    checker.check("Windows batch script", bat_file.exists())
    checker.check("PowerShell script", ps_file.exists())
    
    # Summary
    print()
    success = checker.summary()
    
    if success:
        print("🎬 Ready to use! Start the server with:")
        print("   START_SERVER.bat  (Windows)")
        print("   ./START_SERVER.ps1  (PowerShell)")
        print("   uvicorn scripts.server.app:app --host 0.0.0.0 --port 8001 --reload")
        print("\nThen open: http://localhost:8001")
    else:
        print("❌ Please fix the issues above before running")
        sys.exit(1)

if __name__ == '__main__':
    main()
