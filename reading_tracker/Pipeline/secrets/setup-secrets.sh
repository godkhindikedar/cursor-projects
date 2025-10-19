#!/bin/bash

# Setup Google Secret Manager secrets for Reading Tracker
# Run this script after setting up your GCP project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project set. Run 'gcloud config set project YOUR_PROJECT_ID'${NC}"
    exit 1
fi

echo -e "${BLUE}🔐 Setting up secrets for project: ${PROJECT_ID}${NC}"

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo -e "${YELLOW}📝 Updating existing secret: $secret_name${NC}"
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=-
    else
        echo -e "${GREEN}✨ Creating new secret: $secret_name${NC}"
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --replication-policy="automatic" \
            --data-file=- \
            --labels="app=reading-tracker"
    fi
}

# Generate a secure SECRET_KEY if not provided
if [ -z "$SECRET_KEY" ]; then
    echo -e "${YELLOW}🔑 Generating secure SECRET_KEY...${NC}"
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
fi

# Prompt for Google Client ID if not set
if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo -e "${YELLOW}📱 Enter your Google OAuth Client ID:${NC}"
    read -r GOOGLE_CLIENT_ID
    if [ -z "$GOOGLE_CLIENT_ID" ]; then
        echo -e "${RED}Error: Google Client ID is required${NC}"
        exit 1
    fi
fi

# Prompt for admin emails if not set
if [ -z "$ADMIN_EMAILS" ]; then
    echo -e "${YELLOW}👤 Enter admin email addresses (comma-separated):${NC}"
    read -r ADMIN_EMAILS
    if [ -z "$ADMIN_EMAILS" ]; then
        echo -e "${YELLOW}Warning: No admin emails set. You can add them later.${NC}"
        ADMIN_EMAILS=""
    fi
fi

# Create secrets
echo -e "${BLUE}🚀 Creating/updating secrets...${NC}"

create_or_update_secret "reading-tracker-secret-key" "$SECRET_KEY" "Flask secret key for session encryption"
create_or_update_secret "reading-tracker-google-client-id" "$GOOGLE_CLIENT_ID" "Google OAuth client ID"
create_or_update_secret "reading-tracker-admin-emails" "$ADMIN_EMAILS" "Comma-separated list of admin emails"

# Grant Cloud Run service account access to secrets
SERVICE_ACCOUNT="reading-tracker-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${BLUE}🔐 Granting secret access to service account: ${SERVICE_ACCOUNT}${NC}"

secrets=("reading-tracker-secret-key" "reading-tracker-google-client-id" "reading-tracker-admin-emails")

for secret in "${secrets[@]}"; do
    gcloud secrets add-iam-policy-binding "$secret" \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/secretmanager.secretAccessor" \
        --project="$PROJECT_ID"
done

echo -e "${GREEN}✅ Secrets setup completed successfully!${NC}"
echo -e "${BLUE}📋 Created secrets:${NC}"
echo "  - reading-tracker-secret-key"
echo "  - reading-tracker-google-client-id" 
echo "  - reading-tracker-admin-emails"

echo -e "${YELLOW}🔍 To view secrets:${NC}"
echo "  gcloud secrets list --filter='labels.app=reading-tracker'"

echo -e "${YELLOW}💡 To update a secret later:${NC}"
echo "  echo 'new-value' | gcloud secrets versions add SECRET_NAME --data-file=-"
