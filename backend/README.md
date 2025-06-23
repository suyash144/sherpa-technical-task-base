# RAG Chat Backend (FastAPI + Azure OpenAI + UV)

A modern, production-ready RAG (Retrieval-Augmented Generation) backend that combines FastAPI, Azure OpenAI, and persistent document storage. Built with UV for fast dependency management and Docker for containerization.

## ✨ Features

* **💬 Intelligent Chat** – Chat with Azure OpenAI GPT models with streaming support
* **📚 Document RAG** – Upload PDFs and chat with their content using vector similarity search
* **🔗 Source References** – Get structured references to source documents with every response
* **💾 Persistent Storage** – Uploaded files, vector indexes, and chat history persist outside containers
* **🗂️ Session Management** – Create, manage, and persist multiple chat sessions with SQLite/PostgreSQL
* **📝 Chat History** – Full conversation history with source tracking per session
* **⚡ Fast Development** – UV for lightning-fast dependency management
* **🐳 Docker Ready** – Optimized multi-stage Docker builds with volume mounting
* **📊 Vector Search** – FAISS-powered semantic search with embeddings
* **🔄 Streaming & Sync** – Both streaming and synchronous response formats
* **🗄️ Database Integration** – SQLAlchemy with Alembic migrations for robust data management

## 🚀 Quick Start

### Prerequisites
- [UV](https://github.com/astral-sh/uv) (recommended) or Python 3.12+
- Docker & Docker Compose (optional, for containerized development)
- Azure OpenAI account with deployments

### 1. Automated Setup (Recommended)

```bash
# Clone and navigate to backend
git clone <your-repo> && cd backend

# Run the setup script (creates directories and .env template)
./setup.sh

# Edit .env file with your Azure OpenAI credentials
nano .env  # or use your preferred editor
```

The setup script will:
- ✅ Create all required data directories (`data/uploads`, `data/documents`, etc.)
- ✅ Generate a `.env` template with all necessary variables
- ✅ Check for UV and Docker installations
- ✅ Provide next steps for your preferred development method

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Clone and navigate
git clone <your-repo> && cd backend

# Create required directories
mkdir -p data/{uploads,documents,vector_store,logs,database}

# Create environment file
cat <<EOF > .env
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
EOF
```

### 3. Choose Your Development Method

#### Option A: UV (Recommended - Fastest)
```bash
# Install dependencies
uv sync

# Run development server with auto-reload
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

# Add new dependencies (if needed)
uv add package_name && uv sync
```

#### Option B: Docker Compose (Containerized)
```bash
# Build and start with docker-compose (includes file persistence)
docker-compose up --build

# View logs
docker-compose logs -f

# Stop and clean up
docker-compose down
```

#### Option C: Standard Python (Fallback)
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Verify Setup

After starting the server with any method:

```bash
# Test health endpoint
curl http://localhost:8080/health

# Visit interactive docs
open http://localhost:8080/docs
```

## 🔧 Troubleshooting Setup

### Common Issues

**Missing data directories:**
```bash
# If you get permission or path errors, ensure directories exist:
mkdir -p data/{uploads,documents,vector_store,logs,database}
```

**Environment variables not loaded:**
```bash
# Verify .env file exists and has correct format
cat .env
# Ensure no spaces around = in environment variables
```

**Docker volume mount issues:**
```bash
# If Docker can't mount volumes, check directory permissions:
ls -la data/
# Ensure directories are readable/writable
chmod -R 755 data/
```

**Port 8080 already in use:**
```bash
# Check what's using port 8080
lsof -i :8080
# Kill process or change port in docker-compose.yml
```

**Azure OpenAI authentication errors:**
- Verify your `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY` in `.env`
- Ensure your Azure OpenAI deployment names match your actual deployments
- Check that your Azure OpenAI resource is active and has sufficient quota

### Getting Help

If you encounter issues:
1. Check the application logs: `docker-compose logs -f` (Docker) or console output (UV/Python)
2. Verify all environment variables are set correctly
3. Ensure all required directories exist with proper permissions
4. Test with a simple health check: `curl http://localhost:8080/health`

## 📋 API Endpoints

### Chat Endpoints
- `POST /chat/message` - **Streaming chat** with source references
- `POST /chat/message-sync` - **Synchronous chat** with structured response
- `POST /chat/sessions` - **Create new chat session**
- `GET /chat/sessions` - **List all chat sessions**
- `GET /chat/sessions/{session_id}/history` - **Get chat history** for specific session
- `DELETE /chat/sessions/{session_id}` - **Delete chat session**
- `GET /chat/history` - Get conversation history (legacy)
- `DELETE /chat/history` - Clear conversation history (legacy)

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

### Create a Chat Session
```bash
curl -X POST "http://localhost:8080/chat/sessions" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Research Session"}'
```

### List All Chat Sessions
```bash
curl -X GET "http://localhost:8080/chat/sessions" | jq
```

### Chat with Streaming (with session)
```bash
curl -X POST "http://localhost:8080/chat/message?session_id=your-session-id" \
  -H "Content-Type: application/json" \
  -d '{"message": "What does the document say about AI?"}' \
  --no-buffer
```

### Chat with Structured Response
```bash
curl -X POST "http://localhost:8080/chat/message-sync?session_id=your-session-id" \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize the key points"}' | jq
```

### Get Chat History for Session
```bash
curl -X GET "http://localhost:8080/chat/sessions/your-session-id/history" | jq
```

### Delete a Chat Session
```bash
curl -X DELETE "http://localhost:8080/chat/sessions/your-session-id"
```

## 🏗️ Project Structure

```
backend/
├── src/                          # Source code
│   ├── api/                      # FastAPI routers
│   │   ├── chat.py              # Chat endpoints (streaming & sync) with session management
│   │   ├── documents.py         # Document upload/management
│   │   └── health.py            # Health checks
│   ├── models/                   # Pydantic schemas & SQLAlchemy models
│   │   ├── chat.py              # Chat models with source references & session management
│   │   ├── database.py          # SQLAlchemy models (ChatSession, ChatMessage, MessageSource)
│   │   └── documents.py         # Document models
│   ├── services/                 # Business logic
│   │   ├── chat_service.py      # Session & message management with database persistence
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
│   ├── database/                # SQLite database files
│   └── logs/                    # Application logs
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Development setup with volumes
├── pyproject.toml              # UV project configuration
├── uv.lock                     # UV lock file
└── requirements.txt            # Fallback requirements (includes SQLAlchemy & Alembic)
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

# Database (automatically set in Docker)
DATABASE_URL=sqlite:///./data/database/chat_history.db

# Data paths (automatically set in Docker)
UPLOAD_DIR=/app/data/uploads
DOCUMENTS_DIR=/app/data/documents
VECTOR_STORE_DIR=/app/data/vector_store
LOGS_DIR=/app/data/logs
DATABASE_DIR=/app/data/database
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
- **Chat Database**: SQLite database in `./data/database/` with full conversation history
- **Session Management**: Persistent chat sessions with message history and source tracking
- **Docker Volumes**: Mounted for development and production
- **File Cleanup**: Automatic cleanup when documents are deleted
- **Database Schema**: 
  - `chat_sessions` - Session metadata with titles and timestamps
  - `chat_messages` - Individual messages with role, content, and timestamps  
  - `message_sources` - Source document references linked to messages

## 🗄️ Database Setup

The application uses SQLAlchemy with SQLite by default, with PostgreSQL support for production:

### Automatic Setup
- Database tables are created automatically on first run
- No manual migration needed for development
- SQLite file stored in `./data/database/chat_history.db`

### Production Database
For production, you can use PostgreSQL by setting:
```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Schema Overview
- **ChatSession**: Stores session metadata (ID, title, timestamps)
- **ChatMessage**: Individual messages with role, content, and creation time
- **MessageSource**: Links messages to their source documents with relevance scores

## 🐳 Docker Features

- **Multi-stage builds** for optimized production images
- **UV integration** for fast dependency installation  
- **Volume mounting** for persistent data
- **Non-root user** for security
- **Health checks** built-in
- **Development vs Production** stages