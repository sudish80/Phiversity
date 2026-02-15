# 🚀 Run Phiversity Locally - Quick Guide

## Prerequisites
- Python 3.10+ installed
- API keys for Groq/OpenRouter/Gemini in `.env` file

## Quick Start

### Option 1: Windows Batch File (Easiest)
```powershell
cd c:\Users\SUDISH_DEUJA\Desktop\Phiversity-main
run_local.bat
```

### Option 2: PowerShell
```powershell
cd c:\Users\SUDISH_DEUJA\Desktop\Phiversity-main
.\run_local.ps1
```

### Option 3: Manual Command
```powershell
cd c:\Users\SUDISH_DEUJA\Desktop\Phiversity-main
python -m uvicorn scripts.server.app:app --host 0.0.0.0 --port 8000 --reload
```

## Access the Application

Once the server is running, open these URLs in your browser:

### 🌐 **Main Web Application**
- **URL**: http://localhost:8000
- **Features**:
  - Input physics problems
  - Generate animations
  - Watch videos
  - Download outputs

### 📚 **Interactive API Documentation**
- **URL**: http://localhost:8000/docs
- **Features**:
  - Swagger UI with all endpoints
  - Try-it-out functionality
  - Request/response examples

## API Endpoints

### Generate Animation
```json
POST /run
{
  "problem": "Explain conservation of momentum",
  "voice_first": true,
  "orchestrate": true,
  "element_audio": false
}
```

### Test LLM Connection
```json
POST /test-llm
{
  "question": "What is physics?",
  "provider": "groq"
}
```

## Configuration

### Environment Variables (.env)
```bash
# LLM Configuration
LLM_MODEL=groq
GROQ_API_KEY=your_key_here

# Alternative providers
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Video Settings
VIDEO_QUALITY=low_quality  # low_quality, medium_quality, high_quality
GENERATE_AUDIO=true
GENERATE_VIDEO=true
```

## Output Locations

Generated files are stored in:
- **Videos**: `media/videos/`
- **Audio**: `media/videos/`
- **Images**: `media/images/`
- **Solutions**: `media/texts/`

## Troubleshooting

### Port 8000 Already in Use
```powershell
# Use a different port
python -m uvicorn scripts.server.app:app --host 0.0.0.0 --port 8001
```

### Module Not Found Errors
```powershell
# Install all dependencies
pip install -r requirements.txt
```

### Manim Errors
Ensure you have system dependencies installed:
- FFmpeg
- LaTeX
- espeak-ng (for audio)

### LLM API Key Issues
1. Check your `.env` file has the correct key
2. Test with API provider dashboard
3. Run the `/test-llm` endpoint to debug

## Keyboard Shortcuts

- **Ctrl+C**: Stop the server
- **F5** (in browser): Reload the UI
- **Ctrl+Shift+Delete**: Clear browser cache if UI doesn't update

## Support

- 📖 [GitHub Repository](https://github.com/sudish80/Phiversity)
- 📚 [Manim Documentation](https://docs.manim.community/)
- 🤖 [Groq API Docs](https://console.groq.com/docs)
- 🌐 [FastAPI Documentation](https://fastapi.tiangolo.com/)
