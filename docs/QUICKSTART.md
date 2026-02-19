# Quick Start Guide

Get up and running with the EU AI Act Compliance Analyzer in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed  
- [ ] Docker and Docker Compose installed (recommended)
- [ ] Azure OpenAI API access
- [ ] EU AI Act PDF document

## Option 1: Docker Compose (Fastest ⚡)

### Step 1: Setup Environment

```bash
# Clone or navigate to the project
cd rag-in-production

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Azure OpenAI

Edit `.env` and add your credentials:

```bash
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### Step 3: Add EU AI Act PDF

```bash
# Create data directory
mkdir -p data

# Place your EU_AI_ACT.pdf file in data/
# Download from: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206
```

### Step 4: Start Services

```bash
# Start everything with one command
docker-compose up --build

# Or in detached mode
docker-compose up -d --build
```

### Step 5: Index EU AI Act

```bash
# Wait for services to be ready (30-60 seconds)
# Then index the document
curl -X POST http://localhost:8000/api/index-eu-act
```

### Step 6: Access the Application

Open your browser to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Option 2: Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp ../.env.example ../.env
# Edit .env with your Azure credentials

# Create data directories
mkdir -p data/uploads data/outputs data/chroma_db

# Start server
python main.py
```

Backend will run on http://localhost:8000

### Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Frontend will run on http://localhost:3000

### Index EU AI Act

```bash
curl -X POST http://localhost:8000/api/index-eu-act
```

## Testing the Application

### Method 1: Use Sample Document

```bash
# Convert sample to PDF (requires pandoc)
cd examples
pandoc sample_technical_document.md -o sample_technical_document.pdf

# Upload via API
curl -X POST http://localhost:8000/api/upload \
  -F "file=@sample_technical_document.pdf"
```

### Method 2: Use the Web Interface

1. Go to http://localhost:3000
2. Drag and drop your PDF/Word document
3. Wait for analysis (30-60 seconds)
4. View results on the dashboard
5. Download Excel report

## Verifying Installation

### Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_db_status": "ready",
  "llm_status": "ready"
}
```

### Check Vector Database

```bash
curl http://localhost:8000/api/vector-stats
```

Expected response:
```json
{
  "collection_name": "eu_ai_act",
  "total_documents": 245,
  "indexed": true
}
```

### Check Frontend

Open http://localhost:3000 - you should see the landing page with upload interface.

## Common Issues

### "EU AI Act not indexed"

```bash
# Make sure EU_AI_ACT.pdf is in data/ directory
ls data/EU_AI_ACT.pdf

# Index it
curl -X POST http://localhost:8000/api/index-eu-act
```

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Azure OpenAI Authentication Error

- Verify API key is correct
- Check endpoint URL format
- Ensure deployment names match your Azure setup

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Next Steps

1. **Read the Documentation**
   - [README.md](../README.md) - Full project overview
   - [API_EXAMPLES.md](API_EXAMPLES.md) - API usage examples
   - [EVALUATION.md](EVALUATION.md) - Understanding metrics
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Azure deployment

2. **Test with Different Documents**
   - Try various PDF and Word documents
   - Compare evaluation scores
   - Test edge cases

3. **Deploy to Azure**
   - Follow the Azure deployment guide
   - Set up CI/CD pipeline
   - Configure monitoring

4. **Customize**
   - Adjust chunking parameters
   - Tune evaluation metrics
   - Modify prompts for your use case
   - Add custom risk categories

## Getting Help

- Check [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review API documentation at http://localhost:8000/docs
- Examine logs: `docker-compose logs backend`
- Enable debug mode: Set `LOG_LEVEL=DEBUG` in `.env`

## Stopping the Application

### Docker Compose

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Manual Setup

- Press `Ctrl+C` in both backend and frontend terminals
- Deactivate virtual environment: `deactivate`

## What You've Built

✅ Complete RAG application  
✅ Vector database with EU AI Act indexed  
✅ Azure OpenAI integration  
✅ Evaluation framework  
✅ Interactive dashboard  
✅ Excel report generation  
✅ Docker containerization  

**Ready for production deployment!** 🚀
