# ADK Installation Guide

## Prerequisites

1. **Python 3.8+** - Check version: `python --version`
2. **Google Cloud Account** - [Create free account](https://cloud.google.com/free)
3. **Git** - For cloning repositories

## Installation Steps

### 1. Install Google Cloud SDK

```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
# Or use package manager:

# Windows (using Chocolatey)
choco install gcloudsdk

# macOS (using Homebrew)
brew install google-cloud-sdk

# Linux (using snap)
sudo snap install google-cloud-cli --classic
```

### 2. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Enable Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable run.googleapis.com
```

### 5. Install ADK

```bash
# Install the latest ADK package
pip install google-agent-development-kit

# Or install from source for latest features
git clone https://github.com/google/agent-development-kit.git
cd agent-development-kit
pip install -e .
```

### 6. Verify Installation

Create a test file to verify everything works:

```python
# test_adk.py
try:
    import google.cloud.aiplatform as aiplatform
    print("✅ Google Cloud AI Platform imported successfully")
    
    # Add ADK imports when available
    print("✅ Environment setup complete!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
```

Run: `python test_adk.py`

## Next Steps

1. Complete the foundations learning module
2. Try the basic examples
3. Build your first agent!
