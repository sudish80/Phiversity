# 🎬 PHIVERSITY USER GUIDE
## Your Complete Guide to AI-Powered Educational Videos

---

## 📖 Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Using the Application](#using-the-application)
5. [Features](#features)
6. [Troubleshooting](#troubleshooting)
7. [Tips & Best Practices](#tips--best-practices)
8. [FAQ](#faq)

---

## 🚀 Quick Start

### The Fastest Way to Get Started:

1. **Double-click** `LAUNCH_PHIVERSITY.bat`
2. **Select Option 1** - Launch Web Application
3. **Enter your question** in the browser
4. **Click Generate** and wait for your video!

That's it! Your browser will open automatically at `http://127.0.0.1:8000`

---

## 💿 Installation

### Prerequisites

- **Windows 10/11** (64-bit)
- **Python 3.9 or higher** ([Download](https://www.python.org/downloads/))
- **4GB RAM minimum** (8GB recommended)
- **2GB free disk space**
- **Internet connection** (for API calls)

### First-Time Setup

1. **Extract Phiversity** to a folder (e.g., `C:\Phiversity`)

2. **Run Setup:**
   - Double-click `LAUNCH_PHIVERSITY.bat`
   - Choose **Option 3** - Setup and Install Dependencies
   - Wait for installation to complete (5-10 minutes)

3. **Configure API Keys:**
   - Choose **Option 4** - Configure API Keys
   - Add at least one LLM API key (see [Configuration](#configuration))

4. **Test Your Setup:**
   - Choose **Option 5** - Test System Status
   - Verify all systems are working

---

## 🔑 Configuration

### Required API Keys

You need **at least ONE** of these API keys:

#### OpenAI (Recommended)
- **Get Key:** [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Cost:** ~$0.01-0.05 per video
- **Best For:** General questions, all subjects

#### DeepSeek
- **Get Key:** [https://platform.deepseek.com](https://platform.deepseek.com)
- **Cost:** Very affordable
- **Best For:** Math and science

#### Google Gemini
- **Get Key:** [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **Cost:** Free tier available
- **Best For:** Quick testing

### Optional API Keys

#### ElevenLabs (Premium Voice)
- **Get Key:** [https://elevenlabs.io/](https://elevenlabs.io/)
- **Cost:** Free tier available
- **Best For:** Professional-quality voice

### Adding Keys to Phiversity

**Method 1: Using the Launcher**
1. Run `LAUNCH_PHIVERSITY.bat`
2. Choose **Option 4** - Configure API Keys
3. Notepad will open with your `.env` file
4. Replace `your_xxx_key_here` with your actual keys
5. Save and close

**Method 2: Manual Edit**
1. Open `.env` file in project folder
2. Add your keys:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
DEEPSEEK_API_KEY=xxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxx
```
3. Save the file

---

## 🎯 Using the Application

### Web Interface (Recommended)

1. **Start the Application:**
   - Double-click `LAUNCH_PHIVERSITY.bat`
   - Choose **Option 1** - Launch Web Application
   - Browser opens automatically

2. **Enter Your Question:**
   ```
   Good Examples:
   ✓ "Explain angular momentum conservation in collisions"
   ✓ "How does photosynthesis work at the molecular level?"
   ✓ "Prove the Pythagorean theorem step by step"
   ✓ "Explain how quicksort algorithm works"
   ```

3. **Configure Options:**
   - **Voice-First Mode** ✓ (Recommended - better sync)
   - **Element-Level Audio** ☐ (Advanced - slower)
   - **AI Orchestration** ✓ (Always keep checked)

4. **Generate Video:**
   - Click **"Generate Video"** button
   - Watch progress bar (typically 2-5 minutes)
   - Video appears automatically when done

5. **Download & Share:**
   - Click **"Download Video"** to save locally
   - Share directly from browser
   - Videos saved in `media/videos/web_jobs/`

### Desktop Mode

For a more app-like experience:

1. Run `LAUNCH_PHIVERSITY.bat`
2. Choose **Option 2** - Launch Desktop Mode
3. Works fullscreen like a native app

### Command Line (Advanced)

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Generate from question
python -m scripts.pipeline --question "Your question here" --out-dir media/videos/output

# Generate from existing plan
python -m scripts.pipeline --json media/texts/plan.json --out-dir media/videos/output
```

---

## ✨ Features

### 🎨 Animation Engine
- **Manim-based** - Same library used by 3Blue1Brown
- **Automatic layout** - Smart element positioning
- **Collision detection** - No overlapping elements
- **Professional quality** - Publication-ready output

### 🤖 AI Intelligence
- **Multi-LLM support** - GPT-4, DeepSeek, Gemini
- **Smart orchestration** - Optimal content structure
- **Context-aware** - Understands complex topics
- **JSON-based plans** - Reproducible results

### 🎙️ Voice Synthesis
- **Multiple engines:**
  - Google TTS (free, good quality)
  - ElevenLabs (premium, best quality)
  - System TTS (offline fallback)
- **Perfect sync** - Frame-accurate audio alignment
- **Natural pacing** - Human-like delivery

### 📊 Supported Subjects
- ✓ Mathematics (algebra, calculus, geometry)
- ✓ Physics (mechanics, waves, thermodynamics)
- ✓ Chemistry (reactions, bonding, stoichiometry)
- ✓ Biology (cells, DNA, ecology)
- ✓ Computer Science (algorithms, data structures)
- ✓ Economics (supply/demand, markets)
- ✓ And more!

---

## 🔧 Troubleshooting

### Common Issues

#### "Virtual environment not found"
**Solution:** Run Option 3 (Setup) in the launcher first

#### "API key invalid" or "LLM service error"
**Solutions:**
1. Check your API key in `.env` file
2. Verify key has credits/quota
3. Try a different LLM provider
4. Run Option 5 (Test Status) to diagnose

#### Video generation fails
**Solutions:**
1. Check logs in `media/videos/web_jobs/[job_id]/log.txt`
2. Verify API keys are working
3. Try simpler question first
4. Check internet connection
5. Ensure sufficient disk space

#### Browser doesn't open automatically
**Solution:** Manually open `http://127.0.0.1:8000` in your browser

#### "Port 8000 already in use"
**Solutions:**
1. Close other instances of Phiversity
2. Change port in launcher (advanced)
3. Restart computer

#### Video quality is poor
**Solutions:**
1. Edit `.env` file
2. Set `MANIM_QUALITY=production`
3. Use ElevenLabs for voice (set `ELEVENLABS_API_KEY`)

### Getting Help

1. **Check logs:** `media/videos/web_jobs/[job_id]/log.txt`
2. **Read documentation:** `README.md`, `START_HERE.md`
3. **Test system:** Run Option 5 in launcher
4. **Contact support:** [Create an issue on GitHub]

---

## 💡 Tips & Best Practices

### Writing Good Questions

**✅ DO:**
- Be specific and clear
- Include context when needed
- Use complete sentences
- Ask one concept at a time

**❌ DON'T:**
- Be too vague ("explain physics")
- Ask multiple unrelated questions
- Use unclear abbreviations
- Expect very long responses (>10 min videos)

### Example Questions

**Math:**
- "Prove the Pythagorean theorem using geometric rearrangement"
- "Explain how to find the derivative of x²"
- "Show how to solve quadratic equations by completing the square"

**Physics:**
- "Explain angular momentum conservation with collision examples"
- "Describe how waves interfere constructively and destructively"
- "Show the relationship between force, mass, and acceleration"

**Chemistry:**
- "Explain the difference between ionic and covalent bonds"
- "Show how to balance the combustion reaction of methane"
- "Describe the molecular structure of water and hydrogen bonding"

**Computer Science:**
- "Explain how the quicksort algorithm works with visualization"
- "Show how binary search is more efficient than linear search"
- "Demonstrate how a stack data structure works"

### Optimization Tips

1. **Voice-First Mode:** Always keep enabled for best audio sync
2. **Element Audio:** Disable unless you need it (saves time)
3. **Quality Settings:** Use "medium" for testing, "production" for final
4. **API Choice:** OpenAI for best results, DeepSeek for cost savings
5. **Caching:** Repeated questions are faster (plan reuse)

### Quality Improvements

1. **Better Questions = Better Videos**
   - More detailed questions → more detailed explanations
   - Request "step-by-step" or "with examples"

2. **Voice Quality**
   - Use ElevenLabs for professional voice
   - Keep Voice-First mode enabled

3. **Video Quality**
   - Set `MANIM_QUALITY=production` in `.env`
   - Allows longer processing time

---

## ❓ FAQ

### General Questions

**Q: How long does video generation take?**
A: Typically 2-5 minutes for medium-length videos. Longer questions or high quality settings take more time.

**Q: How much does it cost?**
A: Depends on your LLM provider. Typically $0.01-0.05 per video with OpenAI. DeepSeek is cheaper. Free tier available with Gemini.

**Q: Can I use Phiversity offline?**
A: No, internet connection required for LLM APIs. However, you can generate videos and watch them offline later.

**Q: What video format is generated?**
A: MP4 format (H.264), compatible with all platforms.

**Q: Can I edit the generated videos?**
A: Yes! Generated videos can be edited in any video editor (Adobe Premiere, DaVinci Resolve, etc.)

### Technical Questions

**Q: Which LLM should I use?**
A: 
- **OpenAI GPT-4:** Best quality, most reliable
- **DeepSeek:** Great for STEM, very affordable
- **Gemini:** Good all-around, free tier available

**Q: Can I customize animations?**
A: Yes, advanced users can edit the generated JSON plans before rendering.

**Q: Where are videos saved?**
A: `media/videos/web_jobs/[job_id]/final.mp4`

**Q: Can I generate videos programmatically?**
A: Yes! Use the REST API at `http://127.0.0.1:8000/api/run`

**Q: Does it support languages other than English?**
A: Currently optimized for English, but supports other languages if your LLM does.

### Troubleshooting Questions

**Q: Why is my video silent?**
A: Check voice engine settings in `.env`. Ensure `VOICE_ENGINE=gtts` or ElevenLabs key is set.

**Q: Video has overlapping text. How to fix?**
A: The overlap resolution system should handle this. If not, try regenerating or simplify the question.

**Q: Can I cancel a running job?**
A: Yes, press Ctrl+C in the terminal or close the browser and restart.

---

## 🎓 Advanced Usage

### Custom Prompts

You can provide custom system prompts:

1. Edit `Prompt.txt` in project root
2. This guides the LLM's response style
3. Restart application to use new prompt

### API Integration

**POST /api/run**
```json
{
  "problem": "Your question here",
  "voice_first": true,
  "element_audio": false,
  "orchestrate": true
}
```

**GET /api/jobs/{job_id}**
Returns job status and result URLs

### Batch Processing

```powershell
# Process multiple questions
$questions = @(
    "Question 1",
    "Question 2",
    "Question 3"
)

foreach ($q in $questions) {
    python -m scripts.pipeline --question $q --out-dir "media/videos/batch/$q"
}
```

---

## 📝 Appendix

### File Structure
```
Phiversity/
├── LAUNCH_PHIVERSITY.bat    # Main launcher
├── .env                      # Your configuration
├── api/                      # Backend API
├── scripts/                  # Core scripts
├── web/                      # Frontend UI
├── media/                    # Generated content
│   ├── videos/              # Output videos
│   └── texts/               # JSON plans
└── config/                   # System config
```

### Keyboard Shortcuts (Web UI)
- **Ctrl+Enter:** Submit form
- **F5:** Refresh page
- **Esc:** Close modals
- **Space:** Play/pause video

### System Requirements Details
- **CPU:** Multi-core recommended (video encoding)
- **GPU:** Optional (can speed up rendering)
- **RAM:** 4GB minimum, 8GB+ for complex videos
- **Storage:** SSD recommended for faster rendering
- **OS:** Windows 10/11, macOS, or Linux

---

## 🚀 Next Steps

1. **Explore Examples:** Try the example questions in the Examples tab
2. **Experiment:** Test different question styles
3. **Optimize:** Adjust settings for your needs
4. **Create:** Make educational content for your audience!
5. **Share:** Show off your amazing videos!

---

## 📞 Support & Community

- **Documentation:** See `README.md` and other MD files
- **Issues:** Create GitHub issue for bugs
- **Updates:** Check for new releases regularly
- **Contribute:** Pull requests welcome!

---

### 🎉 Enjoy creating amazing educational videos with Phiversity!

**Version:** 2.0  
**Last Updated:** February 2026  
**License:** See LICENSE file  

---
