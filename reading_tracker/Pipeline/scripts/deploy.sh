#!/bin/bash

# Deploy Reading Tracker to Google Cloud Run
# This script builds and deploys the application using Cloud Build

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_REGION="us-central1"
SERVICE_NAME="reading-tracker"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project set. Run 'gcloud config set project YOUR_PROJECT_ID'${NC}"
    exit 1
fi

# Get region
REGION=${DEPLOY_REGION:-$DEFAULT_REGION}

echo -e "${BLUE}🚀 Deploying Reading Tracker to Cloud Run${NC}"
echo -e "${BLUE}📍 Project: ${PROJECT_ID}${NC}"
echo -e "${BLUE}📍 Region: ${REGION}${NC}"

# Check if we're in the right directory
if [ ! -f "../../app.py" ]; then
    echo -e "${RED}Error: Please run this script from the Pipeline/scripts directory${NC}"
    exit 1
fi

# Verify required files exist
required_files=("../../app.py" "../../requirements.txt" "../Dockerfile" "../cloudbuild.yaml")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}Error: Required file not found: $file${NC}"
        exit 1
    fi
done

# Check if secrets are set up
echo -e "${YELLOW}🔐 Checking if secrets are configured...${NC}"
secrets=("reading-tracker-secret-key" "reading-tracker-google-client-id")
missing_secrets=()

for secret in "${secrets[@]}"; do
    if ! gcloud secrets describe "$secret" --project="$PROJECT_ID" >/dev/null 2>&1; then
        missing_secrets+=("$secret")
    fi
done

if [ ${#missing_secrets[@]} -ne 0 ]; then
    echo -e "${RED}Error: Missing required secrets:${NC}"
    for secret in "${missing_secrets[@]}"; do
        echo "  - $secret"
    done
    echo -e "${YELLOW}Run: cd ../secrets && ./setup-secrets.sh${NC}"
    exit 1
fi

# Change to project root for build
cd ../..

# Build and deploy using Cloud Build
echo -e "${BLUE}🏗️ Starting Cloud Build deployment...${NC}"

# Add region substitution
gcloud builds submit \
    --config=Pipeline/cloudbuild.yaml \
    --substitutions=_DEPLOY_REGION="$REGION" \
    --project="$PROJECT_ID" \
    .

# Wait for deployment to be ready
echo -e "${YELLOW}⏳ Waiting for deployment to be ready...${NC}"
sleep 30

# Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)")

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}Error: Could not retrieve service URL${NC}"
    exit 1
fi

# Test the deployment
echo -e "${BLUE}🧪 Testing deployment...${NC}"
if curl -s --fail "$SERVICE_URL/health" >/dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed, but service might still be starting...${NC}"
fi

# Set up IAM for public access (optional)
echo -e "${YELLOW}🌐 Making service publicly accessible...${NC}"
gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --region="$REGION" \
    --project="$PROJECT_ID"

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo "  - Service: $SERVICE_NAME"
echo "  - Region: $REGION"
echo "  - URL: $SERVICE_URL"
echo "  - Image: gcr.io/$PROJECT_ID/reading-tracker:latest"

echo -e "${YELLOW}🔗 Useful commands:${NC}"
echo "  View logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo "  Get service info: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "  Update service: gcloud run services update $SERVICE_NAME --region=$REGION"

echo -e "${YELLOW}🌐 Access your application:${NC}"
echo "  $SERVICE_URL"

# Show recent logs
echo -e "${BLUE}📋 Recent logs:${NC}"
gcloud run services logs read "$SERVICE_NAME" \
    --region="$REGION" \
    --limit=10 \
    --format="table(timestamp.datetime(),severity,textPayload)" || true

echo -e "${GREEN}🎉 Happy reading tracking!${NC}"
