# 🎬 PHIVERSITY - QUICKSTART GUIDE

Welcome to **Phiversity** - Your AI-powered educational video generator!

---

## 🚀 THREE WAYS TO START

### 1️⃣ EASIEST - Interactive Launcher (Recommended)
**Double-click:** `LAUNCH_PHIVERSITY.bat`

This opens a menu with all options:
- Launch Web App
- Launch Desktop Mode
- Setup & Install
- Configure API Keys
- Test System
- And more...

---

### 2️⃣ QUICK - Desktop App
**Double-click:** `LAUNCH_DESKTOP.bat`

Opens a GUI desktop application with:
- Start/Stop server buttons
- Real-time logs
- Browser integration
- Clean interface

---

### 3️⃣ SIMPLE - Web App Direct
**Double-click:** `run_app.bat` or `run_app.vbs`

Instantly starts the web application:
- Server starts automatically
- Browser opens to http://127.0.0.1:8000
- Ready to create videos!

---

## ⚡ FIRST TIME SETUP (5 minutes)

### Step 1: Install Python
Download and install Python 3.9+: https://www.python.org/downloads/

✅ Check "Add Python to PATH" during installation

### Step 2: Run Setup
1. Double-click `LAUNCH_PHIVERSITY.bat`
2. Choose **Option 3** - Setup & Install
3. Wait 5-10 minutes for dependencies to install

### Step 3: Add API Keys
1. Choose **Option 4** - Configure API Keys
2. Get at least ONE API key (see below)
3. Add to `.env` file that opens
4. Save and close

### Step 4: Test
1. Choose **Option 5** - Test System Status
2. Verify everything works

### Step 5: Create Your First Video!
1. Choose **Option 1** - Launch Web App
2. Enter a question like: "Explain the Pythagorean theorem"
3. Click "Generate Video"
4. Wait 2-5 minutes
5. Enjoy your video!

---

## 🔑 GET API KEYS (Choose ONE)

### Option A: OpenAI (Recommended)
- **Best for:** Everything
- **Cost:** ~$0.01-0.05 per video
- **Get key:** https://platform.openai.com/api-keys
- **Add to .env:** `OPENAI_API_KEY=sk-xxxxx`

### Option B: DeepSeek (Budget-Friendly)
- **Best for:** Math & Science
- **Cost:** Very affordable
- **Get key:** https://platform.deepseek.com
- **Add to .env:** `DEEPSEEK_API_KEY=xxxxx`

### Option C: Google Gemini (Free Tier)
- **Best for:** Testing
- **Cost:** Free tier available
- **Get key:** https://makersuite.google.com/app/apikey
- **Add to .env:** `GEMINI_API_KEY=xxxxx`

### Optional: ElevenLabs (Premium Voice)
- **Best for:** Professional voice quality
- **Cost:** Free tier available
- **Get key:** https://elevenlabs.io
- **Add to .env:** `ELEVENLABS_API_KEY=xxxxx`

---

## 📝 EXAMPLE QUESTIONS TO TRY

### Mathematics
```
Explain the Pythagorean theorem and its proof
Show how to find the derivative of x squared
Demonstrate solving quadratic equations by completing the square
```

### Physics
```
Explain angular momentum conservation in collisions
Describe how constructive and destructive interference works
Show Newton's second law with examples
```

### Chemistry
```
Explain the difference between ionic and covalent bonds
Show how to balance the combustion reaction of methane
Describe hydrogen bonding in water molecules
```

### Computer Science
```
Explain how the quicksort algorithm works with visualization
Show how binary search is more efficient than linear search
Demonstrate how a stack data structure operates
```

---

## 🎯 USING THE WEB APP

1. **Open:** http://127.0.0.1:8000 (opens automatically)

2. **Enter Question:** Type your question in the text box

3. **Configure Options:**
   - ✅ Voice-First Mode (Recommended)
   - ☐ Element-Level Audio (Advanced)
   - ✅ AI Orchestration (Always keep on)

4. **Generate:** Click "Generate Video" button

5. **Wait:** Watch progress bar (2-5 minutes typical)

6. **Download:** Click "Download Video" when ready

7. **Share:** Your video is ready to share!

---

## 🔧 TROUBLESHOOTING

### "Virtual environment not found"
→ Run `LAUNCH_PHIVERSITY.bat` → Option 3 (Setup)

### "API key invalid"
→ Check your `.env` file, verify key is correct

### "Server won't start"
→ Make sure port 8000 is not in use
→ Close other instances of Phiversity

### "Video generation failed"
→ Check API key has credits
→ Try simpler question first
→ Run Option 5 (Test System)

### "Browser doesn't open"
→ Manually go to: http://127.0.0.1:8000

---

## 📚 MORE HELP

- **Full Guide:** See `USER_GUIDE.md`
- **Technical Docs:** See `README.md`
- **Getting Started:** See `START_HERE.md`
- **FAQs:** See `USER_GUIDE.md` FAQ section

---

## 🎉 YOU'RE READY!

**Three simple steps:**
1. ✅ Setup complete
2. ✅ API key added
3. ✅ Create amazing videos!

**Start creating now:**
- Double-click `LAUNCH_PHIVERSITY.bat`
- Choose Option 1
- Enter your question
- Generate!

---

## 💡 TIPS FOR BEST RESULTS

✅ **DO:**
- Ask specific, clear questions
- Use complete sentences
- One concept per video
- Request "step-by-step" explanations

❌ **DON'T:**
- Be too vague
- Ask multiple unrelated questions
- Expect videos longer than 10 minutes
- Use unclear abbreviations

---

## 🌟 FEATURES AT A GLANCE

- 🤖 **Multi-LLM Support** - GPT-4, DeepSeek, Gemini
- 🎨 **Professional Animations** - Manim-based (3Blue1Brown quality)
- 🎙️ **Natural Voice** - Multiple voice engines
- ⚡ **Fast Generation** - 2-5 minutes typical
- 📊 **Multi-Subject** - Math, Physics, Chemistry, CS, and more
- 🎯 **Smart AI** - Context-aware content generation
- 💾 **MP4 Output** - Compatible everywhere

---

## 📞 NEED HELP?

1. Read `USER_GUIDE.md` for detailed documentation
2. Check logs in `media/videos/web_jobs/[job-id]/log.txt`
3. Run system test: `LAUNCH_PHIVERSITY.bat` → Option 5
4. Create GitHub issue for bugs

---

### **Happy creating! 🎬✨**

**Transform questions into amazing educational videos in minutes!**

---

*Phiversity v2.0 - February 2026*
