# Azure Deployment Guide

This guide walks through deploying the EU AI Act Compliance Analyzer to Microsoft Azure.

## Prerequisites

- Azure account with active subscription
- Azure CLI installed and configured
- Docker installed (for containerized deployment)
- Azure OpenAI access approved

## Architecture Overview

The application will use the following Azure services:

- **Azure Container Apps** - Host backend and frontend containers
- **Azure OpenAI Service** - GPT-4 and embedding models
- **Azure Storage Account** - File uploads and outputs
- **Azure Key Vault** - Secrets management (optional)
- **Application Insights** - Monitoring and logging

## Deployment Steps

### 1. Create Azure Resource Group

```bash
az group create \
  --name rg-euaiact-analyzer \
  --location eastus
```

### 2. Create Azure OpenAI Service

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name openai-euaiact \
  --resource-group rg-euaiact-analyzer \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Deploy GPT-4 model
az cognitiveservices account deployment create \
  --name openai-euaiact \
  --resource-group rg-euaiact-analyzer \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --scale-settings-scale-type "Standard"

# Deploy embedding model
az cognitiveservices account deployment create \
  --name openai-euaiact \
  --resource-group rg-euaiact-analyzer \
  --deployment-name text-embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version "2" \
  --model-format OpenAI \
  --scale-settings-scale-type "Standard"

# Get API key and endpoint
az cognitiveservices account keys list \
  --name openai-euaiact \
  --resource-group rg-euaiact-analyzer

az cognitiveservices account show \
  --name openai-euaiact \
  --resource-group rg-euaiact-analyzer \
  --query properties.endpoint
```

### 3. Create Azure Storage Account

```bash
# Create storage account
az storage account create \
  --name steuaiact \
  --resource-group rg-euaiact-analyzer \
  --location eastus \
  --sku Standard_LRS

# Create blob containers
az storage container create \
  --name uploads \
  --account-name steuaiact

az storage container create \
  --name outputs \
  --account-name steuaiact

az storage container create \
  --name euaiact-pdf \
  --account-name steuaiact

# Upload EU AI Act PDF
az storage blob upload \
  --account-name steuaiact \
  --container-name euaiact-pdf \
  --name EU_AI_ACT.pdf \
  --file ./data/EU_AI_ACT.pdf
```

### 4. Create Container Registry

```bash
# Create Azure Container Registry
az acr create \
  --name acreuaiact \
  --resource-group rg-euaiact-analyzer \
  --sku Basic \
  --admin-enabled true

# Login to ACR
az acr login --name acreuaiact

# Build and push backend image
cd backend
docker build -t acreuaiact.azurecr.io/backend:latest .
docker push acreuaiact.azurecr.io/backend:latest

# Build and push frontend image
cd ../frontend
docker build -t acreuaiact.azurecr.io/frontend:latest .
docker push acreuaiact.azurecr.io/frontend:latest
```

### 5. Create Container Apps Environment

```bash
# Install Container Apps extension
az extension add --name containerapp --upgrade

# Create environment
az containerapp env create \
  --name env-euaiact \
  --resource-group rg-euaiact-analyzer \
  --location eastus
```

### 6. Deploy Backend Container App

```bash
# Get ACR credentials
ACR_PASSWORD=$(az acr credential show \
  --name acreuaiact \
  --query "passwords[0].value" \
  --output tsv)

# Get OpenAI credentials
OPENAI_KEY=$(az cognitiveservices account keys list \
  --name openai-euaiact \
  --resource-group rg-euaiact-analyzer \
  --query "key1" \
  --output tsv)

OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name openai-euaiact \
  --resource-group rg-euaiact-analyzer \
  --query properties.endpoint \
  --output tsv)

# Create backend container app
az containerapp create \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --environment env-euaiact \
  --image acreuaiact.azurecr.io/backend:latest \
  --registry-server acreuaiact.azurecr.io \
  --registry-username acreuaiact \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars \
    AZURE_OPENAI_API_KEY=$OPENAI_KEY \
    AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT \
    AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4 \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002 \
    VECTOR_DB_TYPE=chroma \
    LOG_LEVEL=INFO
```

### 7. Deploy Frontend Container App

```bash
# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Create frontend container app
az containerapp create \
  --name app-frontend \
  --resource-group rg-euaiact-analyzer \
  --environment env-euaiact \
  --image acreuaiact.azurecr.io/frontend:latest \
  --registry-server acreuaiact.azurecr.io \
  --registry-username acreuaiact \
  --registry-password $ACR_PASSWORD \
  --target-port 3000 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 2 \
  --env-vars \
    NEXT_PUBLIC_API_URL=https://$BACKEND_URL
```

### 8. Index EU AI Act

```bash
# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Index the document
curl -X POST https://$BACKEND_URL/api/index-eu-act
```

### 9. Access the Application

```bash
# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name app-frontend \
  --resource-group rg-euaiact-analyzer \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Application URL: https://$FRONTEND_URL"
```

## Configuration

### Environment Variables

Backend environment variables:
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME` - GPT-4 deployment name
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Embedding model deployment
- `VECTOR_DB_TYPE` - Vector database type (chroma)
- `LOG_LEVEL` - Logging level (INFO, DEBUG)

Frontend environment variables:
- `NEXT_PUBLIC_API_URL` - Backend API URL

### Scaling

Container Apps auto-scale based on HTTP traffic. Adjust scaling rules:

```bash
az containerapp update \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --min-replicas 1 \
  --max-replicas 5
```

### Monitoring

Enable Application Insights:

```bash
# Create Application Insights
az monitor app-insights component create \
  --app insights-euaiact \
  --resource-group rg-euaiact-analyzer \
  --location eastus

# Get instrumentation key
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app insights-euaiact \
  --resource-group rg-euaiact-analyzer \
  --query instrumentationKey \
  --output tsv)

# Update backend with Application Insights
az containerapp update \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --set-env-vars APPLICATIONINSIGHTS_CONNECTION_STRING=$INSIGHTS_KEY
```

## Cost Optimization

1. **Azure OpenAI**: Use pay-as-you-go pricing, monitor token usage
2. **Container Apps**: Use consumption-based pricing, adjust replica counts
3. **Storage**: Use cool tier for infrequently accessed data
4. **Reserved Instances**: Consider for predictable workloads

## Security Best Practices

1. **Use Azure Key Vault** for sensitive credentials
2. **Enable HTTPS** for all endpoints (default with Container Apps)
3. **Configure CORS** properly in backend
4. **Use Managed Identities** instead of service principals where possible
5. **Enable Azure AD authentication** for production deployments

## Troubleshooting

### Check Container Logs

```bash
az containerapp logs show \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --follow
```

### Restart Container App

```bash
az containerapp revision restart \
  --name app-backend \
  --resource-group rg-euaiact-analyzer
```

### Update Environment Variables

```bash
az containerapp update \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --set-env-vars NEW_VAR=value
```

## CI/CD with GitHub Actions

See `.github/workflows/azure-deploy.yml` for automated deployment pipeline.

## Clean Up

To delete all resources:

```bash
az group delete --name rg-euaiact-analyzer --yes --no-wait
```

## Support

For Azure-specific issues:
- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
