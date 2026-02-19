#!/bin/bash

# Quick setup script for local development

set -e

echo "🚀 Setting up EU AI Act Compliance Analyzer..."

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

echo "✅ All prerequisites found"

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Azure OpenAI credentials before continuing."
    exit 1
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/uploads data/outputs data/chroma_db

# Check for EU AI Act PDF
if [ ! -f data/EU_AI_ACT.pdf ]; then
    echo "⚠️  EU_AI_ACT.pdf not found in data/ directory."
    echo "Please download the EU AI Act PDF and place it in data/EU_AI_ACT.pdf"
    echo "You can find it at: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206"
    exit 1
fi

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install --silent
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  Option 1: Docker Compose (recommended)"
echo "    docker-compose up --build"
echo ""
echo "  Option 2: Manual start"
echo "    1. Backend: cd backend && source venv/bin/activate && python main.py"
echo "    2. Frontend: cd frontend && npm run dev"
echo ""
echo "Don't forget to index the EU AI Act after starting:"
echo "  curl -X POST http://localhost:8000/api/index-eu-act"
