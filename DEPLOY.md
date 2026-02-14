# 🚀 Deploy Manimations to Cloud (Free!)

This guide walks you through deploying Manimations as a free cloud-based app on various platforms.

## ☁️ Supported Free Platforms

1. **Railway.app** - 500 hours/month free
2. **Render.com** - 750 hours/month free
3. **Fly.io** - Free tier available

---

## 🔧 Prerequisites

Before deploying, set up these environment variables (API keys):

### Required Variables
```bash
OPENAI_API_KEY=your_openai_key          # For GPT-based generation
# OR
GEMINI_API_KEY=your_gemini_key          # Alternative to OpenAI
```

### Optional Cloud Storage (Recommended)
```bash
# For AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your_bucket_name
AWS_REGION=us-east-1

# OR for Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
STORAGE_BACKEND=cloudinary              # Options: s3, cloudinary, local
```

---

## 🚂 Deploy to Railway.app

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
# OR
curl -fsSL https://railway.app/install.sh | sh
```

### Step 2: Login
```bash
railway login
```

### Step 3: Initialize and Deploy
```bash
railway init
railway up
```

### Step 4: Add Environment Variables
```bash
railway variables set OPENAI_API_KEY=your_key_here
railway variables set MANIM_QUALITY=low
railway variables set JOB_TIMEOUT=600
```

### Step 5: Get Your URL
```bash
railway domain
```

Your app will be available at `https://your-app.railway.app`

---

## 🎨 Deploy to Render.com

### Step 1: Create Account
Go to [render.com](https://render.com) and sign up

### Step 2: Connect Repository
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the `manimations` repo

### Step 3: Configure Service
- **Name**: manimations-api
- **Environment**: Docker
- **Region**: Choose closest to you
- **Plan**: Free

### Step 4: Add Environment Variables
In the Render dashboard:
1. Go to Environment tab
2. Add your API keys:
   - `OPENAI_API_KEY`
   - `MANIM_QUALITY=low`
   - `JOB_TIMEOUT=600`

### Step 5: Deploy
Click "Create Web Service" - Render will automatically deploy!

Your app will be at `https://your-app.onrender.com`

---

## 🪰 Deploy to Fly.io

### Step 1: Install Fly CLI
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login
```bash
fly auth login
```

### Step 3: Launch App
```bash
fly launch
```

Answer the prompts:
- App name: Choose a unique name
- Region: Select closest to you
- Postgres: No
- Redis: No (unless you want caching)

### Step 4: Set Environment Variables
```bash
fly secrets set OPENAI_API_KEY=your_key_here
fly secrets set MANIM_QUALITY=low
fly secrets set JOB_TIMEOUT=600
```

### Step 5: Deploy
```bash
fly deploy
```

Your app will be at `https://your-app.fly.dev`

---

## 📦 Local Docker Testing (Before Cloud Deploy)

Test locally first:

```bash
# Build the Docker image
docker build -t manimations .

# Run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e MANIM_QUALITY=low \
  manimations
```

Visit `http://localhost:8000` to test.

---

## 🗄️ Cloud Storage Setup (Optional but Recommended)

Cloud storage prevents video files from being lost when containers restart.

### Option 1: AWS S3 (Free Tier: 5GB for 12 months)

1. Create AWS account at [aws.amazon.com](https://aws.amazon.com)
2. Create S3 bucket:
   ```bash
   aws s3 mb s3://manimations-videos
   ```
3. Set bucket policy for public read access
4. Add environment variables to your cloud platform

### Option 2: Cloudinary (Free: 25GB storage, 25GB bandwidth/month)

1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Get your credentials from dashboard
3. Add environment variables:
   ```bash
   STORAGE_BACKEND=cloudinary
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_key
   CLOUDINARY_API_SECRET=your_secret
   ```

---

## ⚙️ Performance Optimization for Free Tiers

Free tiers have limitations. Optimize with:

```bash
# Environment variables for faster generation
MANIM_QUALITY=low              # Use low quality for speed
JOB_TIMEOUT=600                # 10-minute timeout
MAX_CONCURRENT_JOBS=1          # Process one job at a time
```

### Tips:
- **Low quality videos** render 5-10x faster
- **Limit scene count** to < 10 scenes per video
- **Use cloud storage** to persist videos across restarts
- **Set timeouts** to prevent long-running jobs

---

## 🔍 Monitoring Your Deployment

### Check Logs

**Railway:**
```bash
railway logs
```

**Render:**
View logs in dashboard

**Fly.io:**
```bash
fly logs
```

### Health Check
All platforms check `/health` endpoint automatically.

Test manually:
```bash
curl https://your-app.example.com/health
```

Should return: `{"status": "ok"}`

---

## 🌐 Update Web Frontend

After deployment, update your [web/index.html](web/index.html) API URL:

```javascript
// Change this line to your deployed URL
const API_URL = 'https://your-app.railway.app';
```

---

## 📊 Cost Estimates (Free Tiers)

| Platform | Free Tier | Limits |
|----------|-----------|--------|
| **Railway** | 500 hours/month | $5 credit monthly |
| **Render** | 750 hours/month | Sleeps after 15min inactivity |
| **Fly.io** | 3 shared-cpu VMs | 160GB bandwidth/month |
| **Cloudinary** | 25GB storage | 25GB bandwidth/month |
| **AWS S3** | 5GB for 12 months | Then ~$0.023/GB/month |

All platforms are **completely free** for light usage!

---

## 🐛 Troubleshooting

### Container Build Fails
- Check Docker build locally first
- Ensure all dependencies in requirements.txt
- Check platform-specific logs

### Videos Not Generating
- Verify OPENAI_API_KEY or GEMINI_API_KEY is set
- Check job timeout isn't too short
- Review logs for specific errors

### Slow Performance
- Set MANIM_QUALITY=low
- Reduce scene complexity
- Consider upgrading to paid tier for more resources

### Files Disappear After Restart
- Set up cloud storage (S3 or Cloudinary)
- Free tiers use ephemeral storage

---

## 🎉 Success!

Once deployed, your API will be accessible at:
- Railway: `https://your-app.railway.app`
- Render: `https://your-app.onrender.com`
- Fly.io: `https://your-app.fly.dev`

Test with:
```bash
curl -X POST https://your-app.example.com/run \
  -H "Content-Type: application/json" \
  -d '{"problem": "Explain the Pythagorean theorem", "orchestrate": true}'
```

---

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
