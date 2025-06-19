from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration pulled from environment variables or a .env file."""
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_openai_deployment: str            # Chat completion deployment name
    azure_openai_embedding_deployment: str  # Embeddings deployment name
    openai_model_temperature: float = 0.7

    vector_store_path: str = "/app/data/vector_store"
    faiss_index_file: str = "faiss.index"
    metadata_file: str = "metadata.json"

    chunk_size: int = 800      # characters
    chunk_overlap: int = 200   # characters overlap between chunks

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
