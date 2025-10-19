# 🚀 GCP Cloud Run Deployment Pipeline

This directory contains all the necessary files and scripts to deploy the Reading Tracker application to Google Cloud Platform using Cloud Run with SQLite.

## 📁 Structure

```
Pipeline/
├── README.md              # This file
├── Dockerfile             # Container configuration
├── cloudbuild.yaml        # Cloud Build CI/CD configuration
├── cloudrun.yaml          # Cloud Run service configuration
├── secrets/
│   ├── setup-secrets.sh   # Script to create secrets in Google Secret Manager
│   └── secrets.yaml       # Template for secret values
├── scripts/
│   ├── deploy.sh          # Main deployment script
│   ├── setup-gcp.sh       # Initial GCP project setup
│   └── local-test.sh      # Local container testing
└── config/
    ├── gcp-config.py      # GCP-specific configuration
    └── production.env     # Production environment template
```

## 🔐 Security Architecture

### Secret Management Strategy
- **Google Secret Manager**: Stores all sensitive configuration
- **Cloud Run Service Account**: Accesses secrets at runtime
- **Build-time vs Runtime**: Secrets injected at runtime, not build-time
- **Least Privilege**: Minimal permissions for each component

### Secrets Stored:
1. `SECRET_KEY` - Flask session encryption key
2. `GOOGLE_CLIENT_ID` - OAuth client ID
3. `ADMIN_EMAILS` - Comma-separated list of admin emails
4. `DATABASE_ENCRYPTION_KEY` - SQLite database encryption (optional)

## 🚀 Quick Deployment

1. **Setup GCP Project:**
   ```bash
   cd Pipeline/scripts
   ./setup-gcp.sh
   ```

2. **Configure Secrets:**
   ```bash
   cd Pipeline/secrets
   ./setup-secrets.sh
   ```

3. **Deploy Application:**
   ```bash
   cd Pipeline/scripts
   ./deploy.sh
   ```

## 📊 Cost Optimization

- **SQLite**: No database server costs ($0/month)
- **Cloud Run**: Pay-per-request (free tier: 2M requests/month)
- **Secret Manager**: $0.06 per 10k operations
- **Container Registry**: $0.10/GB/month

Expected monthly cost: **$0-5** for family use!

## 🔧 Local Development

Test the containerized app locally:
```bash
cd Pipeline/scripts
./local-test.sh
```

## 📈 Monitoring & Scaling

- **Cloud Run Metrics**: Request count, latency, errors
- **Auto-scaling**: 0-100 instances based on demand
- **Health Checks**: Built-in liveness and readiness probes
