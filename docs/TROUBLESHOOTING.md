# Troubleshooting Guide

Common issues and solutions for the EU AI Act Compliance Analyzer.

## Installation Issues

### Python Dependencies Installation Fails

**Problem**: `pip install -r requirements.txt` fails

**Solutions**:
```bash
# Update pip
python -m pip install --upgrade pip

# Install build tools (macOS)
xcode-select --install

# Install build tools (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install build-essential python3-dev

# Try installing problematic packages individually
pip install chromadb
pip install pdfplumber
```

### Node Dependencies Installation Fails

**Problem**: `npm install` fails in frontend

**Solutions**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try with legacy peer deps
npm install --legacy-peer-deps
```

## Runtime Issues

### "EU AI Act not indexed" Error

**Problem**: API returns warning that EU AI Act is not indexed

**Solution**:
```bash
# 1. Ensure EU_AI_ACT.pdf exists
ls data/EU_AI_ACT.pdf

# 2. Index the document
curl -X POST http://localhost:8000/api/index-eu-act

# 3. Verify indexing
curl http://localhost:8000/api/vector-stats
```

### Azure OpenAI Authentication Errors

**Problem**: `AuthenticationError` or `InvalidAPIKey`

**Solutions**:

1. **Check environment variables**:
```bash
# Verify .env file
cat .env | grep AZURE_OPENAI

# Test with direct values
export AZURE_OPENAI_API_KEY="your-actual-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

2. **Verify Azure OpenAI setup**:
```bash
# Test API key with curl
curl https://your-resource.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-02-15-preview \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_API_KEY" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

3. **Check deployment names**:
- Ensure `AZURE_OPENAI_DEPLOYMENT_NAME` matches your actual GPT-4 deployment name
- Ensure `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` matches your embedding deployment name

### File Upload Fails

**Problem**: Upload returns 400 or 500 error

**Solutions**:

1. **Check file size**:
```bash
# Max 50MB by default
ls -lh your-document.pdf
```

2. **Check file format**:
```bash
# Must be PDF, DOC, or DOCX
file your-document.pdf
```

3. **Check backend logs**:
```bash
# Docker
docker-compose logs backend

# Manual
# Check terminal where backend is running
```

4. **Verify upload directory exists**:
```bash
mkdir -p data/uploads data/outputs
chmod 755 data/uploads data/outputs
```

### Document Processing Errors

**Problem**: Analysis fails with "Failed to extract text"

**Solutions**:

1. **Encrypted PDFs**:
```bash
# Remove encryption with qpdf
qpdf --decrypt input.pdf output.pdf
```

2. **Scanned PDFs** (images, not text):
```bash
# Use OCR tool first
# Or ensure PDF has selectable text
```

3. **Corrupted Documents**:
- Try opening in Adobe Reader/Word
- Re-save as new file
- Convert format (PDF → DOCX or vice versa)

### ChromaDB Errors

**Problem**: `chromadb.errors.*` exceptions

**Solutions**:

1. **Permission issues**:
```bash
chmod -R 755 data/chroma_db
```

2. **Corrupted database**:
```bash
# Backup and reset
mv data/chroma_db data/chroma_db.backup
mkdir data/chroma_db

# Re-index
curl -X POST http://localhost:8000/api/index-eu-act?force_reindex=true
```

3. **Version mismatch**:
```bash
pip install --upgrade chromadb
```

## Docker Issues

### Docker Compose Fails to Start

**Problem**: `docker-compose up` fails

**Solutions**:

1. **Port already in use**:
```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

2. **Missing .env file**:
```bash
cp .env.example .env
# Edit .env with your values
```

3. **Build cache issues**:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Container Keeps Restarting

**Problem**: Backend or frontend container restarts repeatedly

**Solutions**:

1. **Check logs**:
```bash
docker-compose logs backend
docker-compose logs frontend
```

2. **Missing environment variables**:
```bash
# Verify all required vars are set
docker-compose config
```

3. **Dependency issues**:
```bash
# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Frontend Issues

### "Failed to fetch" or CORS Errors

**Problem**: Frontend can't connect to backend

**Solutions**:

1. **Check API URL**:
```bash
# In frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. **Backend CORS settings**:
```python
# In backend/config.py
cors_origins: str = "http://localhost:3000,http://localhost:3001"
```

3. **Backend not running**:
```bash
# Verify backend is accessible
curl http://localhost:8000/api/health
```

### Page Not Found (404)

**Problem**: Dashboard page shows 404

**Solutions**:

1. **Build issue**:
```bash
cd frontend
rm -rf .next
npm run build
npm run dev
```

2. **Check file structure**:
```bash
# Should exist:
frontend/app/dashboard/[jobId]/page.tsx
```

### Styling Issues

**Problem**: Tailwind styles not applying

**Solutions**:

1. **Rebuild**:
```bash
cd frontend
npm run build
npm run dev
```

2. **Check tailwind.config.js**:
```javascript
content: [
  './app/**/*.{js,ts,jsx,tsx,mdx}',
  './components/**/*.{js,ts,jsx,tsx,mdx}',
],
```

## API Issues

### Slow Response Times

**Problem**: Analysis takes too long

**Solutions**:

1. **Reduce chunk retrieval**:
```python
# In backend/rag_pipeline.py
self.top_k = 3  # Reduce from 5 to 3
```

2. **Check Azure OpenAI quotas**:
- Verify you're not hitting rate limits
- Check token usage

3. **Optimize document chunking**:
```python
# In backend/document_processor.py
chunk_size = 800  # Reduce from 1000
```

### Out of Memory Errors

**Problem**: Backend crashes with OOM

**Solutions**:

1. **Increase Docker memory**:
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
```

2. **Process documents in batches**:
```python
# Split large documents
# Implement streaming processing
```

3. **Clear job cache periodically**:
```python
# Implement job cleanup
# Delete old results after 24h
```

## Azure Deployment Issues

### Container App Won't Start

**Problem**: Azure Container App deployment fails

**Solutions**:

1. **Check logs**:
```bash
az containerapp logs show \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --follow
```

2. **Verify environment variables**:
```bash
az containerapp show \
  --name app-backend \
  --resource-group rg-euaiact-analyzer \
  --query properties.configuration.secrets
```

3. **Check container registry**:
```bash
# Verify image exists
az acr repository show-tags \
  --name acreuaiact \
  --repository backend
```

### High Azure Costs

**Problem**: Unexpected Azure charges

**Solutions**:

1. **Monitor token usage**:
- Implement token counting
- Set up cost alerts in Azure Portal

2. **Optimize API calls**:
- Cache frequently used results
- Reduce context window size

3. **Use cheaper models for testing**:
```python
# Use GPT-3.5-turbo for development
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
```

## Performance Optimization

### Speed Up Indexing

```python
# Batch process embeddings
# Use async operations
# Implement caching
```

### Reduce Excel Generation Time

```python
# Stream write to Excel
# Simplify formatting
# Generate in background
```

## Getting Help

If you're still experiencing issues:

1. **Check logs**:
```bash
# Backend logs
cat backend/*.log

# Docker logs
docker-compose logs

# Azure logs
az containerapp logs show ...
```

2. **Enable debug mode**:
```bash
# In .env
LOG_LEVEL=DEBUG
```

3. **Test components individually**:
```bash
# Test vector store
python -c "from vector_store import vector_store; print(vector_store.get_collection_stats())"

# Test LLM client
python -c "from llm_client import llm_client; print(llm_client.get_embedding('test'))"
```

4. **Create a minimal reproduction**:
- Isolate the issue
- Test with sample data
- Document exact error messages

5. **Check GitHub Issues** (if applicable)

6. **Review documentation**:
- [README.md](../README.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [EVALUATION.md](EVALUATION.md)
- [API_EXAMPLES.md](API_EXAMPLES.md)
