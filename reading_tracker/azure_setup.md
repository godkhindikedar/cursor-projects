# 🚀 Azure Deployment Guide for Reading & Study Tracker

## Prerequisites

1. **Azure Subscription** with access to:
   - Azure App Service
   - Azure SQL Database (or MySQL if preferred)
   - Azure Active Directory (for domain verification)

2. **Google Cloud Console Account** for OAuth setup

## Step 1: Google OAuth Setup

### 1.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the **Google Identity API**

### 1.2 Configure OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** user type
3. Fill in required information:
   - App name: "Reading & Study Tracker"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users if needed

### 1.3 Create OAuth 2.0 Credentials
1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth 2.0 Client IDs**
3. Application type: **Web application**
4. Name: "Reading Tracker Web Client"
5. **Authorized JavaScript origins:**
   ```
   https://your-app-name.azurewebsites.net
   http://localhost:5000
   ```
6. **Authorized redirect URIs:**
   ```
   https://your-app-name.azurewebsites.net
   https://your-app-name.azurewebsites.net/auth/google
   ```
7. Save the **Client ID** (you'll need this later)

## Step 2: Azure Resource Setup

### 2.1 Create Azure App Service
```bash
# Using Azure CLI
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name reading-tracker-app \
  --runtime "PYTHON:3.9" \
  --deployment-container-image-name python:3.9-slim
```

### 2.2 Create Azure SQL Database (Recommended)
```bash
# Create SQL Server
az sql server create \
  --name reading-tracker-sql \
  --resource-group myResourceGroup \
  --location "East US" \
  --admin-user sqladmin \
  --admin-password "YourSecurePassword123!"

# Create Database
az sql db create \
  --resource-group myResourceGroup \
  --server reading-tracker-sql \
  --name reading_tracker \
  --service-objective Basic
```

**Alternative: Azure Database for MySQL**
```bash
az mysql server create \
  --resource-group myResourceGroup \
  --name reading-tracker-mysql \
  --location "East US" \
  --admin-user mysqladmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name B_Gen5_1
```

## Step 3: Azure App Configuration

### 3.1 Set Application Settings
In Azure Portal or using CLI:

```bash
# Essential Settings
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name reading-tracker-app \
  --settings \
    SECRET_KEY="your-super-secure-random-secret-key-here" \
    GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com" \
    FLASK_ENV="production" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

### 3.2 Set Connection String
**For Azure SQL:**
1. Go to Azure Portal > App Service > Configuration
2. Add Connection String:
   - Name: `DefaultConnection`
   - Value: `Server=tcp:reading-tracker-sql.database.windows.net,1433;Database=reading_tracker;User ID=sqladmin;Password=YourSecurePassword123!;Encrypt=true;Connection Timeout=30;`
   - Type: `SQLAzure`

**For MySQL:**
1. Connection String Name: `DefaultConnection`
2. Value: `mysql+pymysql://mysqladmin:YourSecurePassword123!@reading-tracker-mysql.mysql.database.azure.com:3306/reading_tracker`
3. Type: `MySQL`

## Step 4: Deployment

### 4.1 Deploy from GitHub (Recommended)
1. Fork/clone the repository to your GitHub account
2. In Azure Portal:
   - Go to App Service > Deployment Center
   - Select **GitHub** as source
   - Authorize and select your repository
   - Select branch (main/master)
   - Save

### 4.2 Deploy using Git
```bash
# Set up Git deployment
az webapp deployment source config-local-git \
  --name reading-tracker-app \
  --resource-group myResourceGroup

# Get deployment URL
az webapp deployment list-publishing-credentials \
  --name reading-tracker-app \
  --resource-group myResourceGroup \
  --query publishingUserName \
  --output tsv

# Add Azure as remote and deploy
git remote add azure https://<deployment-username>@reading-tracker-app.scm.azurewebsites.net/reading-tracker-app.git
git push azure main
```

### 4.3 Deploy using ZIP
```bash
# Create deployment package
zip -r app.zip . -x "*.git*" "*__pycache__*" "*.env" "*venv*"

# Deploy
az webapp deployment source config-zip \
  --resource-group myResourceGroup \
  --name reading-tracker-app \
  --src app.zip
```

## Step 5: Domain and SSL Setup

### 5.1 Custom Domain (Optional)
1. In Azure Portal > App Service > Custom domains
2. Add your custom domain
3. Verify domain ownership

### 5.2 SSL Certificate
- Azure provides free SSL certificates for `.azurewebsites.net` domains
- For custom domains, you can use Azure's managed certificates

## Step 6: Final Configuration

### 6.1 Update Google OAuth
Once deployed, update your Google OAuth configuration:
1. Go back to Google Cloud Console
2. Update **Authorized JavaScript origins** and **Redirect URIs**
3. Replace localhost URLs with your Azure domain

### 6.2 Test the Deployment
1. Visit `https://your-app-name.azurewebsites.net`
2. Test Google login functionality
3. Test all features (book tracking, study sessions)

## Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-super-secure-random-key` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `123456.apps.googleusercontent.com` |
| `FLASK_ENV` | Environment | `production` |
| `SQLCONNSTR_DefaultConnection` | Database connection | Set via Azure Portal |

## Troubleshooting

### Common Issues

1. **Google Login Not Working**
   - Verify Client ID is correct
   - Check authorized domains in Google Console
   - Ensure HTTPS is enabled

2. **Database Connection Errors**
   - Verify connection string format
   - Check firewall rules for Azure SQL
   - Ensure database exists

3. **Application Not Starting**
   - Check Application Logs in Azure Portal
   - Verify all required packages are in requirements.txt
   - Check startup.py for initialization errors

### Useful Azure CLI Commands

```bash
# View logs
az webapp log tail --name reading-tracker-app --resource-group myResourceGroup

# Restart app
az webapp restart --name reading-tracker-app --resource-group myResourceGroup

# Check configuration
az webapp config appsettings list --name reading-tracker-app --resource-group myResourceGroup
```

## Security Best Practices

1. **Environment Variables**: Never commit sensitive data to version control
2. **HTTPS Only**: Ensure redirect HTTP to HTTPS is enabled
3. **Regular Updates**: Keep all packages updated
4. **Database Security**: Use strong passwords and enable firewall rules
5. **Monitoring**: Set up Application Insights for monitoring

## Cost Optimization

1. Use **Basic** or **Standard** App Service plans for production
2. Use **Basic** tier for Azure SQL Database for small applications
3. Enable **Auto-scaling** based on usage
4. Monitor costs using Azure Cost Management

Happy Deployment! 🎉
