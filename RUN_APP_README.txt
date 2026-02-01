# How to Run Phiversity

## Quick Start

### Option 1: Batch File (Easiest - Windows)
Simply double-click the **`run_app.bat`** file in the project root directory. The server will start automatically and open at `http://127.0.0.1:8000`

### Option 2: PowerShell Script (Windows)
1. Right-click **`run_app.ps1`** and select "Run with PowerShell"
   - Or open PowerShell and run: `.\run_app.ps1`

### Option 3: Manual Command Line
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1
# or
.venv312\Scripts\Activate.ps1

# Run the server
python -m uvicorn scripts.server.app:app --host 127.0.0.1 --port 8000 --reload
```

## What Happens

When you run the app:
1. ✅ Virtual environment is activated
2. ✅ Dependencies are checked and installed
3. ✅ Uvicorn server starts on port 8000
4. ✅ Browser will open to `http://127.0.0.1:8000`
5. ✅ Hot reload is enabled (changes update automatically)

## Stopping the Server

Press **Ctrl+C** in the terminal/PowerShell window

## Troubleshooting

- **Virtual environment not found**: Run `python -m venv .venv` first
- **Port 8000 already in use**: Change port in the script or close other apps using it
- **Permission denied (PowerShell)**: Run as Administrator or use the .bat file

Enjoy using Phiversity! 🎬
