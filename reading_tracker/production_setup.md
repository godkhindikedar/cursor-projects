# 🔧 Production Setup Instructions

## Quick Start for Google Authentication

### Step 1: Create Your Environment File
```bash
# Copy the example file
cp .env.example .env

# Edit with your values
notepad .env  # Windows
nano .env     # Linux/Mac
```

### Step 2: Google OAuth Setup (5 minutes)

1. **Go to Google Cloud Console**: https://console.cloud.google.com
2. **Create/Select Project**: Create a new project or select existing
3. **Enable API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Identity" and enable it
4. **Configure OAuth**:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" → Fill basic info → Save
5. **Create Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - **Authorized JavaScript origins**: Add your domains:
     ```
     http://localhost:5000
     https://your-domain.com
     https://your-app.azurewebsites.net
     ```
   - **Authorized redirect URIs**: Same as above
   - Copy the **Client ID** to your `.env` file

### Step 3: Database Setup

**Option A: MySQL (Local Development)**
```bash
# Install MySQL and create database
mysql -u root -p
CREATE DATABASE reading_tracker;
```

**Option B: Azure SQL (Production)**
- Will be automatically configured during Azure deployment
- See `azure_setup.md` for details

### Step 4: Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Step 5: Test Google Login
1. Visit http://localhost:5000
2. Click "Sign in with Google"
3. Authorize the app
4. You should be logged in and see the dashboard!

## Environment Variables Explained

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Flask session encryption key |
| `GOOGLE_CLIENT_ID` | ✅ | From Google Cloud Console |
| `DATABASE_URL` | ✅ | Database connection string |
| `FLASK_ENV` | ⚠️ | `development` or `production` |

## Security Checklist

- [ ] **Secret Key**: Generated randomly, never shared
- [ ] **Google Client ID**: Correct domains authorized
- [ ] **Database**: Strong password, firewall configured  
- [ ] **HTTPS**: Enabled in production (Azure does this automatically)
- [ ] **Environment File**: Never committed to version control

## Troubleshooting

### "Invalid Client ID" Error
- Check `GOOGLE_CLIENT_ID` in `.env` file
- Verify authorized domains in Google Console
- Ensure no extra spaces or quotes

### Database Connection Error
- Verify `DATABASE_URL` format
- Check MySQL/database is running
- Confirm database name exists

### "Redirect URI Mismatch" Error
- Add your domain to Google Console authorized URIs
- Include both `http://localhost:5000` and production domain

## Ready to Deploy to Azure?

See the complete guide in `azure_setup.md` for step-by-step Azure deployment instructions.

Happy coding! 🚀
