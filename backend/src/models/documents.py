from pydantic import BaseModel

class DocumentMetadata(BaseModel):
    id: str
    pages: int

class DocumentUploadResponse(BaseModel):
    id: str
    chunks: int
