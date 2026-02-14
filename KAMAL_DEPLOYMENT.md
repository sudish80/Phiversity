# Kamal Deployment Guide for Manimations

## Prerequisites

1. **Kamal installed locally**:
   ```powershell
   gem install kamal
   ```

2. **Server with Docker**: A VPS/cloud server (DigitalOcean, AWS EC2, Hetzner, etc.) with:
   - Docker installed
   - SSH access
   - Port 80/443 open

3. **Docker Hub account** (or GitHub Container Registry)

## Setup Steps

### 1. Install Kamal

```powershell
# Install Ruby first (if not installed)
# Download from: https://rubyinstaller.org/

# Install Kamal
gem install kamal
```

### 2. Configure Your Server

Edit `config/deploy.yml`:

```yaml
servers:
  web:
    - YOUR_SERVER_IP  # Replace with actual IP like 147.182.123.45
```

Update registry credentials:
```yaml
registry:
  username: YOUR_DOCKER_USERNAME
  password:
    - KAMAL_REGISTRY_PASSWORD  # Set via: kamal envify
```

Update Traefik email:
```yaml
traefik:
  args:
    certificatesResolvers.letsencrypt.acme.email: "your-email@example.com"
```

### 3. Set Environment Variables

Create `.env` file (Kamal will upload secrets automatically):

```bash
# Required API Keys
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=your-deepseek-key

# Docker Registry
KAMAL_REGISTRY_PASSWORD=your-docker-hub-password

# Optional: Cloud Storage
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

### 4. Setup SSH Access

```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "kamal-deploy"

# Copy public key to server
type ~/.ssh/id_ed25519.pub | ssh user@YOUR_SERVER_IP "cat >> ~/.ssh/authorized_keys"
```

### 5. Initialize Kamal on Server

```powershell
# Bootstrap the server (installs Docker, sets up directories)
kamal setup
```

This command:
- Installs Docker on the server
- Creates necessary directories
- Sets up Traefik (reverse proxy)
- Configures SSL certificates (Let's Encrypt)

### 6. Deploy!

```powershell
# First deployment
kamal deploy

# Watch logs
kamal app logs --follow

# Check status
kamal app details
```

## Common Commands

```powershell
# Deploy latest changes
kamal deploy

# Rollback to previous version
kamal rollback

# View logs
kamal app logs --follow
kamal app logs --since 1h

# SSH into container
kamal app exec --interactive bash

# Restart app
kamal app restart

# Stop app
kamal app stop

# Check running containers
kamal app details

# View environment variables
kamal app exec env

# Run database migrations (if applicable)
kamal app exec --interactive "python manage.py migrate"

# Access Rails console (for Ruby apps)
kamal console

# Get server stats
kamal app stats
```

## Environment Management

```powershell
# Update environment variables
# 1. Edit .env file
# 2. Redeploy
kamal env push
kamal app restart

# Or just redeploy
kamal deploy
```

## Zero-Downtime Deployments

Kamal uses rolling deployments by default:
1. Pulls new Docker image
2. Starts new container
3. Runs health checks
4. Switches traffic to new container
5. Stops old container

## Troubleshooting

### Check deployment status
```powershell
kamal app details
```

### View full logs
```powershell
kamal app logs --since 24h
```

### SSH into container
```powershell
kamal app exec --interactive bash
ls -la
ps aux
env
```

### Check Traefik logs
```powershell
kamal traefik logs
```

### Restart everything
```powershell
kamal app stop
kamal deploy
```

### Manual Docker commands on server
```powershell
ssh user@YOUR_SERVER_IP
docker ps
docker logs CONTAINER_ID
docker exec -it CONTAINER_ID bash
```

## Server Requirements

**Minimum**:
- 1 CPU core
- 2GB RAM
- 20GB disk
- Ubuntu 20.04+ or Debian 11+

**Recommended** (for video rendering):
- 2+ CPU cores
- 4GB+ RAM
- 50GB disk (for media files)
- SSD storage

## Cost Comparison

| Provider | Specs | Cost/month |
|----------|-------|-----------|
| DigitalOcean Droplet | 2 CPU, 4GB RAM | $24/mo |
| Hetzner Cloud | 2 CPU, 4GB RAM | €9.29/mo (~$10) |
| AWS Lightsail | 2 CPU, 4GB RAM | $40/mo |
| Linode | 2 CPU, 4GB RAM | $24/mo |
| Railway | Free tier | $0 (500h/mo) |

## Advantages of Kamal

✅ Deploy to **any server** (no vendor lock-in)  
✅ Zero-downtime deployments  
✅ Automatic SSL certificates (Let's Encrypt)  
✅ Built-in reverse proxy (Traefik)  
✅ Simple rollbacks  
✅ No platform fees - just server costs  

## Next Steps

1. Choose a VPS provider
2. Create a server
3. Update `config/deploy.yml` with server IP
4. Run `kamal setup`
5. Run `kamal deploy`

Your app will be live at `http://YOUR_SERVER_IP:8000` (or with domain + SSL if configured)!

## Custom Domain & SSL

To use a custom domain:

1. Point your domain's DNS A record to server IP:
   ```
   @ → YOUR_SERVER_IP
   www → YOUR_SERVER_IP
   ```

2. Update `config/deploy.yml`:
   ```yaml
   traefik:
     args:
       entryPoints.websecure.http.tls.domains:
         - main: yourdomain.com
           sans:
             - www.yourdomain.com
   ```

3. Redeploy:
   ```powershell
   kamal deploy
   ```

Traefik will automatically get SSL certificates from Let's Encrypt!
