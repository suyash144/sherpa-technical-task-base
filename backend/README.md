# RAG Chat Backend (FastAPI + Azure OpenAI + UV)

A modern, production-ready RAG (Retrieval-Augmented Generation) backend that combines FastAPI, Azure OpenAI, and persistent document storage. Built with UV for fast dependency management and Docker for containerization.

## ✨ Features

* **💬 Intelligent Chat** – Chat with Azure OpenAI GPT models with streaming support
* **📚 Document RAG** – Upload PDFs and chat with their content using vector similarity search
* **🔗 Source References** – Get structured references to source documents with every response
* **💾 Persistent Storage** – Uploaded files and vector indexes persist outside containers
* **⚡ Fast Development** – UV for lightning-fast dependency management
* **🐳 Docker Ready** – Optimized multi-stage Docker builds with volume mounting
* **📊 Vector Search** – FAISS-powered semantic search with embeddings
* **🔄 Streaming & Sync** – Both streaming and synchronous response formats

## 🚀 Quick Start

### Prerequisites
- [UV](https://github.com/astral-sh/uv) (recommended) or Python 3.12+
- Docker & Docker Compose
- Azure OpenAI account with deployments

### 1. Environment Setup

```bash
# Clone and navigate
git clone <your-repo> && cd backend

# Create environment file
cat <<EOF > .env
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
EOF
```

### 2. Development with UV (Recommended)

```bash
# Initialize UV project (if not done)
uv init --no-readme

# Install dependencies
uv sync

# Run development server
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 3. Development with Docker Compose

Build the image
```bash
# Start with docker-compose (includes file persistence)
docker-compose build --no-cache
```

```bash
# Or run in background
docker-compose up
```

## 📋 API Endpoints

### Chat Endpoints
- `POST /chat/message` - **Streaming chat** with source references
- `POST /chat/message-sync` - **Synchronous chat** with structured response
- `GET /chat/history` - Get conversation history

### Document Management
- `POST /documents` - **Upload PDF** files for RAG
- `GET /documents` - **List all** uploaded documents  
- `GET /documents/{doc_id}` - **Get document** details and chunks
- `DELETE /documents/{doc_id}` - **Delete document** and cleanup files

### Health & Docs
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive Swagger UI at `http://localhost:8080/docs`

## 💡 Usage Examples

### Upload a Document
```bash
curl -X POST "http://localhost:8080/documents" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf"
```

### Chat with Streaming
```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "What does the document say about AI?"}' \
  --no-buffer
```

### Chat with Structured Response
```bash
curl -X POST "http://localhost:8080/chat/message-sync" \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize the key points"}' | jq
```

## 🏗️ Project Structure

```
backend/
├── src/                          # Source code
│   ├── api/                      # FastAPI routers
│   │   ├── chat.py              # Chat endpoints (streaming & sync)
│   │   ├── documents.py         # Document upload/management
│   │   └── health.py            # Health checks
│   ├── models/                   # Pydantic schemas
│   │   ├── chat.py              # Chat models with source references
│   │   └── documents.py         # Document models
│   ├── services/                 # Business logic
│   │   ├── openai_client.py     # Azure OpenAI integration
│   │   ├── pdf_loader.py        # PDF processing
│   │   ├── rag.py               # RAG engine with source tracking
│   │   └── vector_store.py      # FAISS vector operations
│   ├── main.py                  # FastAPI application
│   └── settings.py              # Configuration management
├── data/                        # Persistent data (mounted volumes)
│   ├── uploads/                 # Original PDF files
│   ├── documents/               # Processed documents
│   ├── vector_store/            # FAISS indexes and metadata
│   └── logs/                    # Application logs
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Development setup with volumes
├── pyproject.toml              # UV project configuration
├── uv.lock                     # UV lock file
└── requirements.txt            # Fallback requirements
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Optional
OPENAI_MODEL_TEMPERATURE=0.7
CHUNK_SIZE=800
CHUNK_OVERLAP=200

# Data paths (automatically set in Docker)
UPLOAD_DIR=/app/data/uploads
DOCUMENTS_DIR=/app/data/documents
VECTOR_STORE_DIR=/app/data/vector_store
LOGS_DIR=/app/data/logs
```

## 📊 Source References

Responses include structured source metadata:

### Streaming Format
```
data: Based on the document...
data: [SOURCES]{"sources":[{"document_id":"abc123","filename":"report.pdf","page":2,"relevance_score":0.85}]}
data: [DONE]
```

### Synchronous Format
```json
{
  "response": "Based on the document...",
  "sources": [
    {
      "document_id": "abc123",
      "filename": "report.pdf",
      "page": 2,
      "relevance_score": 0.85
    }
  ]
}
```

## 💾 Data Persistence

- **Uploaded PDFs**: Stored in `./data/uploads/` with UUID prefixes
- **Vector Index**: FAISS index and metadata in `./data/vector_store/`
- **Docker Volumes**: Mounted for development and production
- **File Cleanup**: Automatic cleanup when documents are deleted

## 🐳 Docker Features

- **Multi-stage builds** for optimized production images
- **UV integration** for fast dependency installation  
- **Volume mounting** for persistent data
- **Non-root user** for security
- **Health checks** built-in
- **Development vs Production** stages

## 🛠️ Development

### With UV (Recommended)
```bash
# Install dependencies
uv sync

# Run with auto-reload
uv run uvicorn src.main:app --reload --port 8080

# Add new dependencies
uv add package-name

# Run tests (when added)
uv run pytest
```

### With Docker Compose
```bash
# Development with volume mounting
docker-compose up

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build
```
