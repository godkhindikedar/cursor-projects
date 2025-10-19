# 🚀 Google Cloud Platform Deployment Guide

## Complete Step-by-Step Deployment

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed (for local testing)
4. **Google OAuth App** configured

### Step 1: Project Setup

```bash
# Set your project ID
export PROJECT_ID="reading-tracker-475504"
gcloud config set project $PROJECT_ID

# Navigate to the scripts directory
cd Pipeline/scripts

# Make scripts executable (Linux/Mac)
chmod +x *.sh
chmod +x ../secrets/*.sh

# Run GCP setup
./setup-gcp.sh
```

### Step 2: Configure Secrets

```bash
# Navigate to secrets directory
cd ../secrets

# Set up your secrets (you'll be prompted for values)
./setup-secrets.sh
```

**Required secrets:**
- `SECRET_KEY`: Flask session encryption key
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `ADMIN_EMAILS`: Comma-separated admin email addresses

### Step 3: Local Testing (Optional but Recommended)

```bash
# Navigate back to scripts
cd ../scripts

# Test locally with Docker
./local-test.sh

# Visit http://localhost:8080 to test
```

### Step 4: Deploy to Cloud Run

```bash
# Deploy the application
./deploy.sh
```

The deployment will:
- Build your Docker image
- Push to Google Container Registry  
- Deploy to Cloud Run
- Configure secrets and environment
- Make the service publicly accessible

### Step 5: Configure OAuth Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Find your OAuth 2.0 Client ID
3. Add your Cloud Run URL to **Authorized redirect URIs**:
   - `https://your-service-url.run.app`
   - `https://your-service-url.run.app/auth/google`

## 🔐 Security Best Practices

### Secret Management

✅ **DO:**
- Use Google Secret Manager for all sensitive data
- Rotate secrets regularly
- Use least-privilege IAM roles
- Monitor secret access logs

❌ **DON'T:**
- Store secrets in code or environment files
- Use weak secret keys
- Share production secrets

### Network Security

- Cloud Run automatically provides HTTPS
- All traffic is encrypted in transit
- Consider VPC connector for internal services

## 💰 Cost Optimization

### Expected Costs (Monthly)

**Family Use (1-4 users):**
- Cloud Run: $0-5 (likely free tier)
- Secrets: $0.06 per 10k operations  
- Storage: $0-1
- **Total: ~$0-6/month**

**Small Group (10-20 users):**
- Cloud Run: $5-15
- Database storage: $1-3
- **Total: ~$6-18/month**

### Free Tier Benefits

- **Cloud Run**: 2M requests/month free
- **Secret Manager**: First 6 operations/month free
- **Container Registry**: 0.5GB storage free

## 🔍 Monitoring & Troubleshooting

### View Logs

```bash
# Recent logs
gcloud run services logs read reading-tracker --region=us-central1

# Follow logs in real-time
gcloud run services logs tail reading-tracker --region=us-central1
```

### Common Issues

**1. OAuth Error "redirect_uri_mismatch"**
- Add your Cloud Run URL to Google OAuth settings
- Include both base URL and `/auth/google` endpoint

**2. Secret Not Found**
- Verify secrets exist: `gcloud secrets list`
- Check IAM permissions for service account

**3. Container Won't Start**
- Check logs for errors
- Verify PORT environment variable
- Test locally first with `./local-test.sh`

**4. Database Connection Error**
- SQLite should work out of the box
- Check file permissions in container

### Health Checks

Your app includes a health endpoint at `/health`:

```bash
curl https://your-app-url.run.app/health
```

## 🔄 Updates and Maintenance

### Deploy Updates

```bash
# Simple redeploy
cd Pipeline/scripts
./deploy.sh
```

### Update Secrets

```bash
# Update a secret
echo "new-secret-value" | gcloud secrets versions add secret-name --data-file=-
```

### Scale Configuration

```bash
# Update Cloud Run settings
gcloud run services update reading-tracker \
  --region=us-central1 \
  --max-instances=20 \
  --memory=1Gi
```

## 🎯 Production Checklist

- [ ] Google OAuth configured with correct redirect URIs
- [ ] Secrets configured in Secret Manager
- [ ] Admin emails added to `ADMIN_EMAILS` secret
- [ ] Health check endpoint responding
- [ ] HTTPS working correctly
- [ ] User registration and approval flow tested
- [ ] Study timer functionality verified
- [ ] Book tracking features working

## 🆘 Support

If you encounter issues:

1. Check the deployment logs
2. Verify all secrets are configured
3. Test locally first
4. Check Google OAuth configuration
5. Review the troubleshooting section above

## 🎉 Success!

Your Reading Tracker is now deployed on Google Cloud Platform!

- **Secure**: OAuth authentication + Secret Manager
- **Scalable**: Auto-scaling Cloud Run
- **Cost-effective**: Pay only for what you use
- **Reliable**: Google's infrastructure

Visit your application and start tracking those reading adventures! 📚✨
