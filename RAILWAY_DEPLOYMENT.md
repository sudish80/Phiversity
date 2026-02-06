# Railway Deployment Guide for Manimations

This guide walks you through deploying Manimations to Railway.app with the latest changes.

## Prerequisites

1. **Railway CLI** installed:
   ```powershell
   npm install -g @railway/cli
   ```

2. **Railway Account** - Sign up at [railway.app](https://railway.app)

3. **Environment Variables Prepared**:
   - `OPENAI_API_KEY` (or `GEMINI_API_KEY`)
   - `AWS_ACCESS_KEY_ID` (optional, for cloud storage)
   - `AWS_SECRET_ACCESS_KEY` (optional)
   - `AWS_S3_BUCKET` (optional)

## Step-by-Step Deployment

### 1. Login to Railway

```powershell
railway login
```

This opens a browser window. Authenticate with your Railway account and return to the terminal.

### 2. Initialize New Project (First Time Only)

```powershell
cd c:\Users\SUDISH_DEUJA\manimations
railway init
```

When prompted:
- **Project name**: `manimations` or `manimations-prod`
- **Environment**: `production`
- **Service name**: `manimations-api`

### 3. View Project Info

```powershell
railway status
```

This shows your Railway project ID and connected services.

### 4. Set Environment Variables

```powershell
# Core API Keys
railway variables set OPENAI_API_KEY=sk-...
# OR
railway variables set GEMINI_API_KEY=your-gemini-key

# Optional: Cloud Storage (S3)
railway variables set AWS_ACCESS_KEY_ID=your_aws_key
railway variables set AWS_SECRET_ACCESS_KEY=your_aws_secret
railway variables set AWS_S3_BUCKET=your-bucket-name
railway variables set AWS_REGION=us-east-1
railway variables set STORAGE_BACKEND=s3

# Quality Settings
railway variables set MANIM_QUALITY=low
railway variables set JOB_TIMEOUT=600
```

### 5. Deploy

```powershell
railway up
```

This builds and deploys the Docker image. First deployment takes 3-5 minutes.

### 6. Monitor Deployment

```powershell
railway logs
```

Watch the logs stream to see build progress and runtime messages.

### 7. Get Your URL

```powershell
railway domain
```

Your app is now live at the displayed URL!

## Accessing Your Deployed App

- **Web UI**: `https://your-project.railway.app`
- **API Root**: `https://your-project.railway.app/api`
- **Health Check**: `https://your-project.railway.app/health`

## Useful Commands

```powershell
# View current variables
railway variables

# View logs (last 100 lines)
railway logs --tail 100

# View real-time logs
railway logs -f

# Redeploy after pushing code
railway up

# View project info
railway status

# Delete project
railway down
```

## Troubleshooting

### Deployment Fails with "Out of Memory"
- Set `MANIM_QUALITY=low` for lower quality animations
- Increase `JOB_TIMEOUT` if jobs are being killed prematurely

### API Keys Not Working
```powershell
# Verify variables are set
railway variables

# Update a variable
railway variables set OPENAI_API_KEY=new_key

# After updating, redeploy
railway up
```

### Build Fails
```powershell
# Clear Docker cache and rebuild
railway up --force

# Check build logs
railway logs --tail 500
```

### Accessing Logs

Latest changes include:
- **Progress tracking**: Jobs now report 5%, 10%, 30%, 40%, 90%, 100% completion
- **Fixed null bytes**: Removed corrupted bytes from orchestrator modules
- **Progress UI**: Real-time progress bar in web interface

Monitor progress in logs with this string: `[server]`

## Performance Tips

1. **Set quality to low**: `MANIM_QUALITY=low`
2. **Reduce timeout**: `JOB_TIMEOUT=900` (15 minutes instead of 20)
3. **Enable cloud storage**: S3 or Cloudinary to avoid file bloat
4. **Monitor memory**: Use `railway logs` to check for memory errors

## Undeploying

To remove the project from Railway:

```powershell
railway down
```

This tears down all services but keeps your Railway project configured locally.

## Additional Resources

- [Railway Docs](https://docs.railway.app)
- [Railway CLI Reference](https://docs.railway.app/reference/cli-api)
- Manimations README: `README.md`
