#!/bin/bash

# Make all shell scripts executable
# Run this script after cloning the repository

echo "🔧 Making shell scripts executable..."

# Find all .sh files in the Pipeline directory and make them executable
find ../.. -name "*.sh" -type f -exec chmod +x {} \;

# Specifically ensure these key scripts are executable
chmod +x setup-gcp.sh
chmod +x deploy.sh  
chmod +x local-test.sh
chmod +x ../secrets/setup-secrets.sh

echo "✅ All shell scripts are now executable!"
echo ""
echo "📋 Executable scripts:"
echo "  - setup-gcp.sh (GCP project setup)"
echo "  - deploy.sh (deployment)"
echo "  - local-test.sh (local testing)"
echo "  - ../secrets/setup-secrets.sh (secret management)"
echo ""
echo "🚀 You can now run the deployment scripts!"
