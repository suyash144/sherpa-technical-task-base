from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import chat, documents, health
from src.models.database import create_tables

def create_app() -> FastAPI:
    app = FastAPI(title="RAG Chat Backend", version="0.1.0")
    
    # Initialize database tables
    @app.on_event("startup")
    async def startup_event():
        create_tables()
    
    @app.get("/")
    def read_root():
        return {"message": "Welcome to the Charter Backend API"}

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat.router)
    app.include_router(documents.router)
    app.include_router(health.router)
    return app

app = create_app()
