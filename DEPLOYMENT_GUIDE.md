# 🚀 ScheduleAI Deployment Guide

## Quick Deployment (Vercel + Railway)

### 1. Frontend Deployment (Vercel)

**Option A: Vercel CLI**
```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy to Vercel
vercel --prod

# Follow prompts to connect your GitHub account
```

**Option B: Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Connect your GitHub repository
4. Select the `frontend` directory
5. Configure environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: Your Railway URL
6. Click "Deploy"

### 2. Backend Deployment (Railway)

**Option A: Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to agent directory
cd agents/schedule_ai_agent

# Initialize Railway project
railway init

# Deploy
railway up
```

**Option B: Railway Dashboard**
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Configure service:
   - **Service Type**: Web Service
   - **Start Command**: `python production_server.py`
   - **Port**: 8000
6. Add environment variables from `.env.production.example`
7. Click "Deploy"

### 3. Environment Variables Setup

**Vercel Environment Variables:**
- `NEXT_PUBLIC_API_URL`: `https://your-app-name.railway.app`
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: Your Google OAuth Client ID

**Railway Environment Variables:**
- `LLM_API_KEY`: Your OpenAI API Key
- `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth Client Secret
- `CORS_ORIGINS`: `https://your-vercel-app.vercel.app`

### 4. DNS Configuration (Optional Custom Domain)

**Vercel:**
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

**Railway:**
1. Go to Project Settings → Networking
2. Add your custom domain
3. Configure DNS records as instructed

### 5. SSL Certificates
- Both Vercel and Railway provide automatic SSL certificates
- Custom domains also get free SSL certificates

## Alternative Deployment Options

### Docker Deployment

**Build Docker image:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "production_server.py"]
```

**Deploy to any cloud:**
```bash
docker build -t schedule-ai .
docker run -p 8000:8000 -e LLM_API_KEY=your_key schedule-ai
```

### AWS Deployment

**Frontend (S3 + CloudFront):**
1. Build: `npm run build`
2. Deploy to S3 bucket
3. Configure CloudFront distribution

**Backend (EC2 + Elastic Beanstalk):**
1. Deploy using Elastic Beanstalk
2. Configure Auto Scaling
3. Set up Load Balancer

### DigitalOcean Deployment

**Frontend (Netlify):**
- Same as Vercel process
- Free tier available

**Backend (DigitalOcean Droplet):**
```bash
# On Droplet
sudo apt update
sudo apt install python3-pip nginx
pip3 install -r requirements.txt
# Configure nginx reverse proxy
```

## Testing Your Deployment

1. **Health Checks:**
   - Frontend: `https://your-domain.vercel.app`
   - Backend Health: `https://your-domain.railway.app/health`

2. **API Test:**
   ```bash
   curl -X POST https://your-domain.railway.app/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!"}'
   ```

3. **Monitor Logs:**
   - Vercel: Dashboard → Functions tab
   - Railway: Dashboard → Logs tab

## Cost Estimate

**Vercel (Frontend):**
- Free tier: 100GB bandwidth/month
- Pro tier: $20/month for higher limits

**Railway (Backend):**
- $5/month starting price
- Auto-scaling based on usage

**Total Estimated Cost:** $5-25/month depending on traffic

## Security Considerations

1. **API Keys:** Never commit API keys to Git
2. **CORS:** Configure proper CORS origins
3. **HTTPS:** Both platforms provide automatic SSL
4. **Environment Variables:** Use platform's secure storage
5. **Rate Limiting:** Implement on API endpoints

## Scaling Considerations

1. **Frontend:** Vercel handles scaling automatically
2. **Backend:** Railway auto-scales based on load
3. **Database:** Consider managed PostgreSQL for high traffic
4. **CDN:** Both platforms use global CDNs

## Troubleshooting

**Common Issues:**
1. **CORS errors:** Check CORS origins configuration
2. **API connection:** Verify environment variables
3. **Build failures:** Check logs in platform dashboard
4. **Slow performance:** Consider upgrading database tier

**Support:**
- Vercel: [support.vercel.com](https://support.vercel.com)
- Railway: [docs.railway.app](https://docs.railway.app)
- Community: Discord servers for both platforms