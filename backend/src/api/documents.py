import uuid
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.pdf_loader import load_pdf, chunk_text
from src.services.vector_store import VectorStore
from src.models.documents import DocumentUploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])
store = VectorStore()

# Get upload directory from environment or use default
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/data/uploads")

@router.post("", response_model=DocumentUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save original file persistently
    persistent_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    
    # Read and save the uploaded file
    file_content = await file.read()
    with open(persistent_path, "wb") as f:
        f.write(file_content)
    
    # Process the PDF for embedding
    pages = load_pdf(persistent_path)

    chunks = []
    metas = []
    for page_num, page_text in enumerate(pages):
        for chunk in chunk_text(page_text):
            chunks.append(chunk)
            metas.append({
                "document_id": doc_id, 
                "page": page_num, 
                "text": chunk,
                "filename": file.filename,
                "file_path": persistent_path
            })
    
    store.add_texts(chunks, metas)
    return DocumentUploadResponse(id=doc_id, chunks=len(chunks))

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    # Find and delete the original file
    files_to_delete = []
    for meta in store.metadata:
        if meta.get("document_id") == doc_id and meta.get("file_path"):
            files_to_delete.append(meta["file_path"])
    
    # Delete the physical files
    for file_path in set(files_to_delete):  # Use set to avoid duplicates
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            print(f"Warning: Could not delete file {file_path}: {e}")
    
    # Very naive delete: rebuild store without vectors matching doc_id
    new_texts, new_meta = [], []
    for meta in store.metadata:
        if meta.get("document_id") != doc_id:
            new_texts.append(meta["text"])
            new_meta.append(meta)
    # Recreate store
    store.index.reset()
    store.metadata = []
    store.save()
    store.add_texts(new_texts, new_meta)
    return {"status": "deleted"}

@router.get("")
async def list_documents():
    """Get a list of all uploaded documents with metadata"""
    documents = {}
    
    # Group metadata by document_id
    for meta in store.metadata:
        doc_id = meta.get("document_id")
        if doc_id and doc_id not in documents:
            documents[doc_id] = {
                "document_id": doc_id,
                "filename": meta.get("filename", "unknown.pdf"),
                "file_path": meta.get("file_path"),
                "chunks": 0,
                "pages": set()
            }
        
        if doc_id:
            documents[doc_id]["chunks"] += 1
            if "page" in meta:
                documents[doc_id]["pages"].add(meta["page"])
    
    # Convert pages set to sorted list and count
    result = []
    for doc_info in documents.values():
        doc_info["pages"] = len(doc_info["pages"]) if doc_info["pages"] else 0
        result.append(doc_info)
    
    return {"documents": result}

@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get detailed information about a specific document"""
    chunks = []
    document_info = None
    
    for meta in store.metadata:
        if meta.get("document_id") == doc_id:
            if not document_info:
                document_info = {
                    "document_id": doc_id,
                    "filename": meta.get("filename", "unknown.pdf"),
                    "file_path": meta.get("file_path")
                }
            
            chunks.append({
                "page": meta.get("page", 0),
                "text": meta.get("text", ""),
                "chunk_id": len(chunks)
            })
    
    if not document_info:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document": document_info,
        "chunks": chunks,
        "total_chunks": len(chunks)
    }

