#!/bin/bash

# Initial GCP project setup for Reading Tracker deployment
# This script sets up all necessary GCP services and configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_REGION="us-central1"
DEFAULT_SERVICE_ACCOUNT="reading-tracker-sa"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project set. Run 'gcloud config set project YOUR_PROJECT_ID'${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Setting up GCP project: ${PROJECT_ID}${NC}"

# Get region (allow override)
REGION=${DEPLOY_REGION:-$DEFAULT_REGION}
echo -e "${BLUE}📍 Using region: ${REGION}${NC}"

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com \
    cloudresourcemanager.googleapis.com \
    --project="$PROJECT_ID"

# Wait for APIs to be fully enabled
echo -e "${YELLOW}⏳ Waiting for APIs to be fully enabled...${NC}"
sleep 30

# Create service account for Cloud Run
SERVICE_ACCOUNT_EMAIL="${DEFAULT_SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo -e "${YELLOW}📝 Service account already exists: ${SERVICE_ACCOUNT_EMAIL}${NC}"
else
    echo -e "${GREEN}✨ Creating service account: ${SERVICE_ACCOUNT_EMAIL}${NC}"
    gcloud iam service-accounts create "$DEFAULT_SERVICE_ACCOUNT" \
        --display-name="Reading Tracker Cloud Run Service Account" \
        --description="Service account for Reading Tracker application on Cloud Run" \
        --project="$PROJECT_ID"
fi

# Grant necessary IAM roles to service account
echo -e "${BLUE}🔐 Granting IAM roles to service account...${NC}"

roles=(
    "roles/secretmanager.secretAccessor"
    "roles/cloudsql.client"
    "roles/storage.objectViewer"
)

for role in "${roles[@]}"; do
    echo -e "${YELLOW}  - Granting ${role}${NC}"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="$role" \
        --quiet
done

# Grant Cloud Build service account necessary permissions
CLOUD_BUILD_SA="${PROJECT_ID}@cloudbuild.gserviceaccount.com"
echo -e "${BLUE}🏗️ Granting Cloud Build permissions...${NC}"

build_roles=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/secretmanager.secretAccessor"
)

for role in "${build_roles[@]}"; do
    echo -e "${YELLOW}  - Granting ${role} to Cloud Build${NC}"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${CLOUD_BUILD_SA}" \
        --role="$role" \
        --quiet
done

# Create Cloud Build trigger (optional - for GitHub integration)
echo -e "${BLUE}📋 Cloud Build setup complete${NC}"
echo -e "${YELLOW}💡 To create a build trigger from GitHub:${NC}"
echo "  1. Go to Cloud Build > Triggers in the console"
echo "  2. Connect your GitHub repository"
echo "  3. Create trigger using cloudbuild.yaml"

# Set default region for Cloud Run
echo -e "${BLUE}🌍 Setting default region for Cloud Run...${NC}"
gcloud config set run/region "$REGION"

# Create a sample .gcloudignore file if it doesn't exist
if [ ! -f "../../.gcloudignore" ]; then
    echo -e "${GREEN}📝 Creating .gcloudignore file...${NC}"
    cat > "../../.gcloudignore" << EOF
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
.coverage
.pytest_cache/
.mypy_cache/
venv/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Local development
.env
.env.local
instance/
*.log

# Documentation
*.md
docs/

# Pipeline files (these are for local setup only)
Pipeline/secrets/*.env
Pipeline/config/*.env
Pipeline/scripts/*.log
EOF
fi

echo -e "${GREEN}✅ GCP project setup completed successfully!${NC}"
echo -e "${BLUE}📋 Summary:${NC}"
echo "  - Project ID: $PROJECT_ID"
echo "  - Region: $REGION"
echo "  - Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "  - APIs enabled: Cloud Build, Cloud Run, Container Registry, Secret Manager"

echo -e "${YELLOW}🚀 Next steps:${NC}"
echo "  1. Set up secrets: cd Pipeline/secrets && ./setup-secrets.sh"
echo "  2. Deploy application: cd Pipeline/scripts && ./deploy.sh"
echo "  3. Test locally first: cd Pipeline/scripts && ./local-test.sh"

echo -e "${YELLOW}🔗 Useful links:${NC}"
echo "  - Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
echo "  - Cloud Build: https://console.cloud.google.com/cloud-build?project=$PROJECT_ID"
echo "  - Secret Manager: https://console.cloud.google.com/security/secret-manager?project=$PROJECT_ID"
