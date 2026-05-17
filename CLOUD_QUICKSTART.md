# 🚀 Quick Start: Deploy Manimations to Cloud (FREE)

Get your video generation app running in the cloud in under 10 minutes!

## ⚡ Fastest Path: Railway.app (Recommended)

### 1️⃣ Prerequisites (2 minutes)
- GitHub account
- OpenAI API key OR Gemini API key (free tier available)

### 2️⃣ Deploy (1 click!)
1. Fork this repository to your GitHub
2. Go to [railway.app](https://railway.app)
3. Click "Start a New Project"
4. Select "Deploy from GitHub repo"
5. Choose your forked repository

### 3️⃣ Configure (2 minutes)
Add environment variables in Railway dashboard:
```
OPENAI_API_KEY=sk-your-key-here
MANIM_QUALITY=low
JOB_TIMEOUT=600
```

### 4️⃣ Access Your App
Railway will give you a URL like: `https://manimations-production.up.railway.app`

**Done! 🎉** Your app is live and generating videos in the cloud!

---

## 🎯 What You Get

✅ **Faster Video Generation** - Cloud servers render videos faster than local
✅ **Always Online** - No need to keep your computer running
✅ **Free Hosting** - 500 hours/month on Railway's free tier
✅ **Auto Scaling** - Handles multiple requests automatically
✅ **Cloud Storage** - Optional S3/Cloudinary integration for persistence

---

## 📱 Using Your Cloud App

### Via Web Interface
Visit your Railway URL and use the form to generate videos!

### Via API
```bash
curl -X POST https://your-app.railway.app/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Explain the Pythagorean theorem with animations",
    "orchestrate": true,
    "voice_first": true
  }'
```

Response:
```json
{"job_id": "abc123def456"}
```

Check status:
```bash
curl https://your-app.railway.app/api/jobs/abc123def456
```

---

## 💰 Cost Breakdown (All FREE)

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| **Railway** | 500 hours | $0 |
| **OpenAI** | $5 credit | $0 (then usage-based) |
| **Gemini** | Free tier | $0 |
| **Cloudinary** | 25GB | $0 |
| **Total** | | **$0** 💚 |

---

## 🔧 Optional: Add Cloud Storage

For persistent video storage (survives restarts):

### Option 1: Cloudinary (Easiest)
1. Sign up at [cloudinary.com](https://cloudinary.com) (free)
2. Get credentials from dashboard
3. Add to Railway:
```
STORAGE_BACKEND=cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Option 2: AWS S3
1. Create AWS account (free tier: 5GB for 12 months)
2. Create S3 bucket
3. Add to Railway:
```
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket
```

---

## 🔥 Performance Tips

### For Faster Videos:
- Use `MANIM_QUALITY=low` (5-10x faster)
- Keep scenes under 10
- Limit element count under 50

### For Better Quality:
- Use `MANIM_QUALITY=medium` or `high`
- Add more detail to prompts
- Use `voice_first: true` for better audio sync

---

## 🐛 Troubleshooting

### Videos Not Generating?
1. Check Railway logs for errors
2. Verify OPENAI_API_KEY or GEMINI_API_KEY is set
3. Ensure you have API credits

### App Sleeping?
- Free tier sleeps after 15min inactivity on Render
- Railway keeps apps running with free tier
- First request after sleep takes ~30s

### Timeouts?
- Increase `JOB_TIMEOUT` (default 600s = 10 min)
- Use lower quality for complex scenes
- Simplify prompts

---

## 📊 Monitor Your App

### Check Health
```bash
curl https://your-app.railway.app/health
```

Should return:
```json
{"status": "ok", "service": "manimations-api"}
```

### View Logs
Railway Dashboard → Your Project → Logs

---

## 🚀 Next Steps

1. **Customize prompts** - Edit [Prompt.txt](Prompt.txt)
2. **Add custom scenes** - Modify generation logic
3. **Integrate with your app** - Use the REST API
4. **Share videos** - Enable cloud storage URLs
5. **Scale up** - Upgrade to paid tier for more resources

---

## 📚 Full Documentation

- [DEPLOY.md](DEPLOY.md) - Detailed deployment guide
- [README.md](README.md) - Project overview
- [GETTING_STARTED.md](GETTING_STARTED.md) - Local development setup

---

## 🎉 Success!

Your Manimations app is now running in the cloud!

**Test it:**
```bash
curl https://your-app.railway.app/health
```

**Generate a video:**
```bash
curl -X POST https://your-app.railway.app/api/run \
  -H "Content-Type: application/json" \
  -d '{"problem": "Explain Newton'\''s laws", "orchestrate": true}'
```

Need help? Check the logs in Railway dashboard or see [DEPLOY.md](DEPLOY.md) for troubleshooting.

**Happy animating! 🎬**
