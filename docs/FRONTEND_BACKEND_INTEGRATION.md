# Phiversity Frontend-Backend Integration Guide

## ✅ Fixed Issues

### 1. **CORS Configuration Issue** 
- **Problem**: CORS was only allowing `localhost:3000`, but the app runs on `localhost:8001`
- **Solution**: Updated CORS configuration to allow `localhost:8001`, `localhost:3000`, and `127.0.0.1:8001`
- **File**: `scripts/server/app.py` (lines 43-50)
- **Status**: ✓ FIXED

### 2. **Missing Share Button Handler**
- **Problem**: Share button existed in HTML but had no event listener
- **Solution**: Added `shareVideo()` method with Web Share API fallback
- **File**: `web/index.html`
- **Status**: ✓ FIXED

### 3. **Relative URL Handling**
- **Problem**: Video URLs from API might be relative, links wouldn't work correctly
- **Solution**: Added `makeAbsoluteUrl()` helper to convert relative → absolute URLs
- **File**: `web/index.html`
- **Status**: ✓ FIXED

### 4. **Poor Error Handling**
- **Problem**: Job submission errors weren't informative, polling gave up too quickly
- **Solution**:
  - Added request timeouts (10s for submit, 5s for poll)
  - Better error parsing from JSON responses
  - 10-retry maximum with incremental warnings
  - Specific error messages for different failure modes
- **File**: `web/index.html`
- **Status**: ✓ FIXED

### 5. **Download Filename Missing**
- **Problem**: Downloaded videos had no meaningful filename
- **Solution**: Added `download` attribute with dynamic filename: `phiversity-{jobId}.mp4`
- **File**: `web/index.html`
- **Status**: ✓ FIXED

---

## 🚀 Quick Start

### Option 1: Batch Script (Windows)
```bash
# Double-click START_SERVER.bat
# Or run from command prompt:
START_SERVER.bat
```

### Option 2: PowerShell Script (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\START_SERVER.ps1
```

### Option 3: Manual (Any OS)
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install if needed
pip install -r requirements.txt

# Start server
uvicorn scripts.server.app:app --host 0.0.0.0 --port 8001 --reload
```

---

## 📝 Environment Setup

Create a `.env` file in the project root for optional configuration:

```env
# API Configuration
CORS_ORIGINS=http://localhost:8001,http://localhost:3000,https://yourdomain.com

# LLM Keys (required for actual video generation)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Cloud Storage (optional)
CLOUD_STORAGE_PROVIDER=local  # or: s3, cloudinary, firebase
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Job Configuration
JOB_TIMEOUT=1200  # seconds (default 20 minutes)
```

---

## 🎯 How It Works

### Frontend → Backend Flow

```
User Input (index.html)
        ↓
   Form Validation
        ↓
  POST /api/run
        ↓
Backend Creates Job
        ↓
   Return job_id
        ↓
Frontend Polls GET /api/jobs/{job_id}
        ↓
   Show Progress
        ↓
    Status: done?
        ↓
  Display Video
```

### Video Generation Pipeline

```
1. Orchestration (if enabled)
   - Problem → AI Plan (JSON)
   
2. Rendering
   - Plan → Manim Script → Video (silent)
   
3. Audio Generation
   - Problem → Voice Synthesis (TTS)
   
4. Audio-Video Sync
   - Match timing + prepend intro
   
5. Post-Processing
   - Add logo watermark
   - Export as final.mp4
   
6. Return
   - video_url: /media/videos/web_jobs/{jobId}/final.mp4
```

---

## 🔍 API Endpoints

### 1. **Health Check**
```
GET /health
Response: { "status": "ok", "service": "manimations-api" }
```

### 2. **Submit Job**
```
POST /api/run
Headers: Content-Type: application/json

Request Body:
{
  "problem": "Explain quantum entanglement",
  "orchestrate": true,
  "voice_first": true,
  "element_audio": false,
  "custom_prompt": null  (optional)
}

Response:
{
  "job_id": "abc123def456"
}
```

### 3. **Check Job Status**
```
GET /api/jobs/{job_id}

Response:
{
  "job_id": "abc123def456",
  "status": "running",  // queued | running | done | error
  "progress": 45,       // 0-100
  "video_url": "/media/videos/web_jobs/abc123def456/final.mp4",
  "plan_url": "/media/texts/solution_plan_abc123def456.json",
  "log_url": "/media/videos/web_jobs/abc123def456/log.txt",
  "log": "... last 10000 characters of log ...",
  "plan_path": "/full/path/to/solution_plan_abc123def456.json"
}
```

---

## ⚠️ Troubleshooting

### Issue: "Backend may be offline"
- **Check**: Server running on port 8001?
- **Fix**: Run `START_SERVER.bat` or manual uvicorn command
- **Verify**: Open http://localhost:8001/health in browser

### Issue: "Connection lost" during generation
- **Check**: Network connectivity
- **Reason**: Jobs may take a long time (15-30 min for complex videos)
- **Note**: The system retries up to 10 times; if still failing after 20 seconds of failures, try refreshing the page

### Issue: "CORS error" in browser console
- **Problem**: CORS_ORIGINS not configured correctly
- **Fix**: Check `.env` file or restart server
- **Default**: Should work for localhost:8001

### Issue: "Failed to parse API response"
- **Reason**: Backend might be returning non-JSON
- **Check**: Browser DevTools → Network tab → Response
- **Fix**: Ensure FastAPI server is running (check console output)

### Issue: Video doesn't play
- **Check**: Is `video_url` pointing to valid file?
- **Check**: Are media files in `/media/videos/` directory?
- **Fix**: Check that `/media` route is mounted correctly

### Issue: "Problem text too long"
- **Limit**: Maximum 5000 characters
- **Reason**: API constraint to prevent abuse
- **Fix**: Reduce problem description length

---

## 📊 File Structure

```
project/
├── web/
│   ├── index.html          ← Main UI (now with backend integration)
│   ├── login.html          ← Authentication UI
│   ├── styles.css          ← Shared styles (external)
│   └── app.js              ← Shared JS (if exists)
│
├── scripts/
│   ├── server/
│   │   └── app.py          ← FastAPI backend
│   ├── orchestrator/        ← LLM orchestration
│   ├── pipeline.py         ← Video generation pipeline
│   └── ...
│
├── media/
│   ├── videos/             ← Output videos
│   │   └── web_jobs/       ← Job-specific folders
│   └── texts/              ← JSON plans and logs
│
├── START_SERVER.bat        ← Windows batch startup
├── START_SERVER.ps1        ← PowerShell startup
├── requirements.txt        ← Python dependencies
└── .env                    ← Configuration (optional)
```

---

## 🎬 Testing the Integration

### 1. Start the server
```bash
START_SERVER.bat  # or manual uvicorn
```

### 2. Open in browser
```
http://localhost:8001
```

### 3. Try simple test
- Enter: "Explain the Pythagorean theorem"
- Click: Send
- Watch: Progress bar updates
- Wait: Video generation (may take 5-30 minutes depending on complexity)
- See: Video appears when done

### 4. Experiment with options
- [x] Use AI Orchestration (recommended)
- [x] Voice-First Timing (recommended)
- [ ] Element Audio Sync (advanced)

---

## 🔧 Advanced Configuration

### Custom Prompt Template
```python
# In .env or as environment variable
CUSTOM_PROMPT="You are an expert educator. Create an animation that..."
```

### Job Timeout
```python
# Default: 1200 seconds (20 minutes)
# Set to 3600 for complex videos (1 hour timeout)
JOB_TIMEOUT=3600
```

### Cloud Storage
```python
# Keep videos in S3 or Cloudinary
CLOUD_STORAGE_PROVIDER=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

---

## 📞 Support

If you encounter issues:
1. Check the console logs in browser (F12 → Console)
2. Check server logs (terminal running uvicorn)
3. Verify `.env` and requirements are correct
4. Try a simple test problem first
5. Ensure LLM keys are configured if using orchestration

---

## ✨ Features

✅ Real-time progress updates
✅ Error reporting with copy-to-clipboard
✅ Download videos with proper filenames
✅ View generation plans and logs
✅ Share videos (native or via link copying)
✅ Responsive design (mobile-friendly)
✅ Professional dark-themed UI
✅ Input validation
✅ 10-retry fault tolerance
✅ Persistent job tracking (works after server restart)

---

Generated: February 6, 2026
