#!/bin/bash

# Local testing script for Reading Tracker container
# Test the containerized application locally before deploying to GCP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="reading-tracker-test"
IMAGE_NAME="reading-tracker:local"
PORT="8080"
LOCAL_PORT="8080"

echo -e "${BLUE}🐳 Local Docker testing for Reading Tracker${NC}"

# Check if we're in the right directory
if [ ! -f "../../app.py" ]; then
    echo -e "${RED}Error: Please run this script from the Pipeline/scripts directory${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Clean up any existing container
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}🧹 Removing existing container...${NC}"
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
fi

# Remove existing image if requested
if [ "$1" == "--rebuild" ]; then
    echo -e "${YELLOW}🔄 Rebuilding image...${NC}"
    docker rmi "$IMAGE_NAME" >/dev/null 2>&1 || true
fi

# Build the Docker image
echo -e "${BLUE}🏗️ Building Docker image...${NC}"
cd ../..
docker build -f Pipeline/Dockerfile -t "$IMAGE_NAME" .

# Set up environment variables for local testing
echo -e "${BLUE}⚙️ Setting up local environment...${NC}"

# Create temporary env file for local testing
ENV_FILE="Pipeline/config/local-test.env"
mkdir -p Pipeline/config

cat > "$ENV_FILE" << EOF
# Local testing environment variables
FLASK_ENV=development
DEBUG=True
SECRET_KEY=local-testing-secret-key-not-for-production
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
DATABASE_URL=sqlite:///data/reading_tracker.db
PORT=8080
EOF

echo -e "${YELLOW}📝 Created local environment file: $ENV_FILE${NC}"
echo -e "${YELLOW}💡 Edit this file to add your actual Google Client ID for OAuth testing${NC}"

# Run the container
echo -e "${BLUE}🚀 Starting container on port ${LOCAL_PORT}...${NC}"
docker run -d \
    --name "$CONTAINER_NAME" \
    --env-file "$ENV_FILE" \
    -p "${LOCAL_PORT}:${PORT}" \
    "$IMAGE_NAME"

# Wait for container to start
echo -e "${YELLOW}⏳ Waiting for container to start...${NC}"
sleep 5

# Check container status
if docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -q "$CONTAINER_NAME.*Up"; then
    echo -e "${GREEN}✅ Container is running!${NC}"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    echo -e "${YELLOW}📋 Container logs:${NC}"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Test health endpoint
echo -e "${BLUE}🧪 Testing health endpoint...${NC}"
sleep 3

if curl -s --fail "http://localhost:${LOCAL_PORT}/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed, checking if app is responding...${NC}"
    if curl -s "http://localhost:${LOCAL_PORT}/" >/dev/null 2>&1; then
        echo -e "${YELLOW}✅ App is responding (health endpoint might not be implemented)${NC}"
    else
        echo -e "${RED}❌ App is not responding${NC}"
        echo -e "${YELLOW}📋 Container logs:${NC}"
        docker logs "$CONTAINER_NAME"
        echo -e "${YELLOW}💡 The container will continue running for further inspection${NC}"
    fi
fi

echo -e "${GREEN}🎉 Local testing setup complete!${NC}"
echo -e "${BLUE}📋 Container Information:${NC}"
echo "  - Container Name: $CONTAINER_NAME"
echo "  - Image: $IMAGE_NAME"
echo "  - Port: http://localhost:${LOCAL_PORT}"
echo "  - Environment: $ENV_FILE"

echo -e "${YELLOW}🔗 Test URLs:${NC}"
echo "  - Application: http://localhost:${LOCAL_PORT}"
echo "  - Health Check: http://localhost:${LOCAL_PORT}/health"

echo -e "${YELLOW}🛠️ Useful commands:${NC}"
echo "  - View logs: docker logs $CONTAINER_NAME"
echo "  - Follow logs: docker logs -f $CONTAINER_NAME"
echo "  - Stop container: docker stop $CONTAINER_NAME"
echo "  - Remove container: docker rm $CONTAINER_NAME"
echo "  - Shell into container: docker exec -it $CONTAINER_NAME /bin/bash"

echo -e "${YELLOW}🧹 To clean up when done:${NC}"
echo "  docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"

# Show recent logs
echo -e "${BLUE}📋 Recent container logs:${NC}"
docker logs --tail 10 "$CONTAINER_NAME" || true

echo -e "${BLUE}🏃 Container is running in the background${NC}"
echo -e "${GREEN}Visit http://localhost:${LOCAL_PORT} to test your application!${NC}"
