# 🚀 Deploy to Railway - Step by Step Guide

## ✨ Method 1: Web Deploy (EASIEST - No CLI needed!)

### Step 1: Prepare GitHub Repository
1. Create a new repository on GitHub (if you haven't already)
2. Push your code:
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click **"Login"** (use GitHub)
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway will auto-detect the Dockerfile and start building!

### Step 3: Add Environment Variables
After deployment starts, click on your service → **Variables** tab:

**Required:**
```
OPENAI_API_KEY=sk-your-key-here
```
OR
```
GEMINI_API_KEY=your-gemini-key-here
```

**Recommended:**
```
MANIM_QUALITY=low
JOB_TIMEOUT=600
PORT=8000
```

**Optional (for cloud storage):**
```
STORAGE_BACKEND=cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Step 4: Get Your URL
1. Go to **Settings** tab
2. Click **"Generate Domain"**
3. Your app will be at: `https://your-app.up.railway.app`

### Step 5: Test It!
Visit your URL - you should see the web interface!

---

## 🖥️ Method 2: CLI Deploy (Advanced)

### Step 1: Install Railway CLI

**Option A - Using npm (if you have Node.js):**
```powershell
npm install -g @railway/cli
```

**Option B - Using PowerShell:**
```powershell
iwr https://railway.app/install.ps1 | iex
```

**Option C - Manual Download:**
1. Download from: https://github.com/railwayapp/cli/releases
2. Add to PATH

### Step 2: Login and Deploy
```powershell
# Login to Railway
railway login

# Initialize project
railway init

# Link to existing project (if web deployed) OR create new
railway link

# Deploy
railway up

# Set environment variables
railway variables set OPENAI_API_KEY=your-key-here
railway variables set MANIM_QUALITY=low
railway variables set JOB_TIMEOUT=600

# Generate domain
railway domain
```

---

## 📋 Checklist Before Deploying

- [ ] Code is working locally
- [ ] `railway.json` exists (✅ Created!)
- [ ] `.railwayignore` exists (✅ Created!)
- [ ] `Dockerfile` is configured (✅ Already there!)
- [ ] `requirements.txt` is up to date
- [ ] Have API keys ready (OpenAI or Gemini)
- [ ] Optional: Cloud storage credentials

---

## 🎯 What Happens During Deployment

1. **Build Phase** (~5-10 minutes):
   - Railway builds Docker image
   - Installs Python, LaTeX, FFmpeg
   - Installs Python dependencies
   - Creates necessary directories

2. **Deploy Phase** (~1 minute):
   - Starts your server
   - Runs health checks
   - Assigns public URL

3. **Ready!** 🎉
   - App is live and generating videos
   - Auto-restarts on crashes
   - Auto-scales with traffic

---

## 📊 Monitor Your Deployment

### Via Railway Dashboard:
- **Deployments** - Build logs and history
- **Metrics** - CPU, Memory, Network usage
- **Logs** - Real-time application logs
- **Settings** - Domain, environment, scaling

### Via CLI:
```powershell
railway logs           # View logs
railway status         # Check status
railway open           # Open in browser
railway variables      # List variables
```

---

## 🐛 Troubleshooting

### Build Fails:
- Check build logs in Railway dashboard
- Ensure all dependencies in `requirements.txt`
- Verify Dockerfile syntax

### App Crashes on Startup:
- Check environment variables are set
- Review logs for errors
- Ensure PORT is 8000 or uses $PORT env var

### API Not Working:
- Verify API keys are correct
- Check CORS settings if accessing from frontend
- Test with health endpoint: `/health`

### Videos Not Generating:
- Check Manim is installed (should be in Docker)
- Verify LaTeX packages installed
- Check disk space (Railway free tier: 1GB)

---

## 💡 Tips for Free Tier

Railway Free Tier includes:
- **$5 credit per month**
- **1GB disk space**
- **8GB RAM**
- **Auto-sleep after inactivity**

### Optimize Usage:
1. Use `MANIM_QUALITY=low` (faster + less CPU)
2. Keep videos under 2 minutes
3. Add `MANIM_TIMEOUT=600` to prevent long renders
4. Use cloud storage for videos (saves disk space)
5. Clear old jobs periodically

---

## 🔗 Quick Links

- [Railway Dashboard](https://railway.app/dashboard)
- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [CLI Documentation](https://docs.railway.app/develop/cli)

---

## ✅ Next Steps After Deployment

1. Test video generation with simple problem
2. Set up cloud storage (optional)
3. Configure custom domain (optional)
4. Monitor usage and logs
5. Share your app URL!

---

## 🆘 Need Help?

If you encounter issues:
1. Check Railway logs: Dashboard → Your Service → Logs
2. Verify environment variables are set
3. Review [CLOUD_QUICKSTART.md](CLOUD_QUICKSTART.md)
4. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (if exists)

Happy deploying! 🚀
