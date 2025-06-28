#!/bin/bash

# Backend Setup Script for Sherpa Technical Task
# This script sets up the required directories and environment file

set -e  # Exit on any error

echo "🚀 Setting up Sherpa RAG Backend..."

# Create required data directories
echo "📁 Creating data directories..."
mkdir -p data/uploads
mkdir -p data/documents  
mkdir -p data/vector_store
mkdir -p data/logs
mkdir -p data/database

echo "✅ Data directories created successfully!"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Azure OpenAI Configuration (REQUIRED)
# Get these from your Azure OpenAI resource
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Optional Configuration
OPENAI_MODEL_TEMPERATURE=0.7
CHUNK_SIZE=800
CHUNK_OVERLAP=200

# Database Configuration (automatically set for Docker)
DATABASE_URL=sqlite:///./data/database/chat_history.db

# Data Paths (automatically set for Docker)
UPLOAD_DIR=/app/data/uploads
DOCUMENTS_DIR=/app/data/documents
VECTOR_STORE_DIR=/app/data/vector_store
LOGS_DIR=/app/data/logs
DATABASE_DIR=/app/data/database
EOF
    echo "✅ .env file created! Please edit it with your Azure OpenAI credentials."
    echo "📝 Edit .env file to add your Azure OpenAI endpoint and API key"
else
    echo "ℹ️  .env file already exists, skipping creation"
fi

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "⚡ UV detected!"
    
    # Offer to update requirements.txt
    echo ""
    read -p "🔄 Update requirements.txt from uv.lock? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Exporting dependencies to requirements.txt..."
        uv export --format requirements-txt --output-file requirements.txt
        echo "✅ requirements.txt updated successfully!"
    fi

    echo "🔄 Running uv sync..."
    uv sync
    echo "✅ uv sync complete!"
else
    echo "🐍 UV not found. You can install it with: pip install uv"
    echo "   Or use regular pip: pip install -r requirements.txt"
fi

# Check if Docker is installed
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected! You can use Docker Compose for development"
    echo "   Run: docker-compose up --build"
else
    echo "⚠️  Docker not found. Install Docker to use containerized development"
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Edit .env file with your Azure OpenAI credentials"
echo "2. Choose your development method:"
echo "   • UV (recommended): uv sync && uv run uvicorn src.main:app --reload --port 8080"
echo "   • Docker: docker-compose up --build"
echo "   • Python: pip install -r requirements.txt && python -m uvicorn src.main:app --reload --port 8080"
echo ""
echo "📖 Visit http://localhost:8080/docs for API documentation"
echo "💡 See README.md for detailed usage examples" 