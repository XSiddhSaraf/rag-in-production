# EU AI Act Compliance Analyzer

A production-grade RAG (Retrieval-Augmented Generation) application that analyzes technical documents for compliance with the EU AI Act. Built with FastAPI, Next.js, and Azure OpenAI.

## Features

- **Document Analysis**: Upload PDF or Word documents for automated compliance analysis
- **EU AI Act Integration**: Vector database indexed with the complete EU AI Act
- **Risk Classification**: Automatic identification of high and low-risk AI components
- **Evaluation Framework**: RAG metrics (faithfulness, relevance, precision, recall) and LLM-as-judge validation
- **Interactive Dashboard**: Real-time results visualization with risk breakdowns
- **Excel Reports**: Downloadable compliance reports with detailed risk assessments

## Architecture

```
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── config.py           # Configuration management
│   ├── models.py           # Pydantic models
│   ├── vector_store.py     # ChromaDB integration
│   ├── rag_pipeline.py     # RAG implementation
│   ├── llm_client.py       # Azure OpenAI client
│   ├── evaluation.py       # Metrics & LLM-as-judge
│   ├── document_processor.py  # PDF/Word processing
│   └── excel_generator.py # Report generation
├── frontend/               # Next.js frontend
│   ├── app/               # Pages and routes
│   ├── components/        # React components
│   └── lib/               # API client
└── infrastructure/        # Azure deployment configs
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for containerized deployment)
- Azure OpenAI API access with:
  - GPT-4 deployment
  - text-embedding-ada-002 deployment

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-in-production
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```env
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### 3. Add EU AI Act PDF

Place the `EU_AI_ACT.pdf` file in the `data/` directory:

```bash
mkdir -p data
# Copy EU_AI_ACT.pdf to data/
```

### 4. Run with Docker Compose

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 5. Index the EU AI Act

Before first use, index the EU AI Act document:

```bash
curl -X POST http://localhost:8000/api/index-eu-act
```

## Local Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads data/outputs data/chroma_db

# Run the server
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. **Upload Document**: Navigate to the homepage and upload a technical document (PDF or Word)
2. **Processing**: The system will:
   - Extract text from the document
   - Retrieve relevant EU AI Act context
   - Analyze for AI components and risks
   - Generate evaluation metrics
3. **View Results**: Redirected to an interactive dashboard showing:
   - Project summary and AI detection
   - High and low risk classifications
   - RAG evaluation metrics
   - LLM-as-judge scores
4. **Download Report**: Export results as a formatted Excel file

## API Endpoints

### Core Endpoints

- `POST /api/upload` - Upload document for analysis
- `GET /api/analyze/{job_id}` - Get analysis results
- `GET /api/download/{job_id}` - Download Excel report
- `GET /api/health` - Health check

### Admin Endpoints

- `POST /api/index-eu-act` - Index EU AI Act document
- `GET /api/vector-stats` - Get vector database statistics

## Evaluation Metrics

### RAG Metrics

- **Faithfulness**: Are risk identifications grounded in EU AI Act context?
- **Answer Relevance**: Does the analysis address the input document?
- **Context Precision**: Is retrieved context relevant to the analysis?
- **Context Recall**: Was sufficient context retrieved?

### LLM-as-a-Judge

- **Accuracy**: Correctness of AI component and risk identification
- **Completeness**: Coverage of all relevant aspects
- **Consistency**: Alignment with EU AI Act classifications

## Azure Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed Azure deployment instructions.

### Quick Azure Deploy

1. Create Azure resources (App Service, Storage, OpenAI)
2. Configure environment variables in Azure Portal
3. Deploy using Azure CLI or GitHub Actions
4. Index EU AI Act via API endpoint

## Technology Stack

### Backend
- FastAPI - Modern Python web framework
- ChromaDB - Vector database for embeddings
- Azure OpenAI - LLM and embeddings
- LangChain - RAG framework
- RAGAS - RAG evaluation library
- Openpyxl - Excel generation

### Frontend
- Next.js 14 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Recharts - Data visualization
- Lucide React - Icons

## Project Structure

```
backend/
├── main.py              # FastAPI app & endpoints
├── config.py            # Environment config
├── models.py            # Pydantic schemas
├── vector_store.py      # Vector DB logic
├── rag_pipeline.py      # RAG orchestration
├── llm_client.py        # Azure OpenAI wrapper
├── evaluation.py        # Metrics calculation
├── document_processor.py # Document parsing
├── excel_generator.py   # Report generation
└── tests/               # Unit & integration tests

frontend/
├── app/
│   ├── page.tsx        # Landing page
│   ├── layout.tsx      # Root layout
│   ├── globals.css     # Global styles
│   └── dashboard/
│       └── [jobId]/
│           └── page.tsx # Results dashboard
├── components/
│   ├── FileUpload.tsx  # Upload component
│   ├── RiskCard.tsx    # Risk display
│   └── MetricsPanel.tsx # Metrics visualization
└── lib/
    └── api.ts          # API client
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create a GitHub issue
- Check the [documentation](docs/)
- Review API documentation at `/docs` endpoint

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- UI built with [Next.js](https://nextjs.org/)
- Icons from [Lucide](https://lucide.dev/)
