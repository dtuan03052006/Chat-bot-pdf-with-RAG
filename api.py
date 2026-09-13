import os
import shutil
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from Promt_LLM import answer_ques
from chunk import chunking
from processing_data import process_pdf
from tokenizer_embeding_vector_db import index_chunks

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Vietnamese PDF RAG API",
    description="REST API cho hệ thống RAG Hỏi đáp tài liệu PDF tiếng Việt sử dụng Qdrant và Ollama",
    version="1.0.0",
)

# Cấu hình CORS để frontend (React, Vue, Web) hoặc Postman có thể gọi được
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., example="Nội dung chính của tài liệu là gì?", description="Câu hỏi của bạn")
    top_k: Optional[int] = Field(default=3, example=3, description="Số đoạn trích dẫn liên quan nhất cần lấy")


class IndexLocalRequest(BaseModel):
    file_path: str = Field(..., example="/home/abc/Code/Code AI/RAG/data/31-2024-qh15_1.pdf", description="Đường dẫn tuyệt đối hoặc tương đối tới file PDF")


@app.get("/", tags=["General"])
def root():
    """Kiểm tra trạng thái hoạt động của server."""
    return {
        "status": "online",
        "service": "Vietnamese PDF RAG API",
        "docs_url": "/docs",
    }


@app.post("/api/ask", tags=["RAG QA"], summary="Hỏi đáp dựa trên tài liệu đã index")
def api_ask(req: AskRequest):
    """Nhận câu hỏi -> Tìm kiếm Top-K đoạn liên quan từ Qdrant -> Gọi Ollama sinh câu trả lời."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống!")

    try:
        result = answer_ques(query=req.question, top_k=req.top_k)
        return {
            "status": "success",
            "question": req.question,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý câu hỏi: {str(e)}",
        )


@app.post("/api/upload", tags=["Data Ingestion"], summary="Upload file PDF mới và tự động nạp vào Qdrant")
async def api_upload_pdf(file: UploadFile = File(...)):
    """Tải lên file PDF -> Làm sạch văn bản & bảng biểu -> Tách đoạn -> Nhúng vector vào Qdrant."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận định dạng file .pdf!")

    try:
        os.makedirs("data", exist_ok=True)
        save_path = os.path.join("data", file.filename)

        # Lưu file tải lên vào thư mục data/
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Trích xuất & làm sạch sâu PDF
        pages_data = process_pdf(save_path)

        # 2. Tách đoạn (Chunking)
        chunks = chunking(pages_data, chunk_size=600, chunk_overlap=100)

        # 3. Nạp vào Qdrant
        index_chunks(chunks)

        return {
            "status": "success",
            "filename": file.filename,
            "total_pages": len(pages_data),
            "total_chunks": len(chunks),
            "message": f"Đã xử lý và nạp thành công {len(chunks)} đoạn vào cơ sở tri thức Qdrant!",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý file upload: {str(e)}",
        )


@app.post("/api/index-local", tags=["Data Ingestion"], summary="Index một file PDF đã có sẵn trên máy")
def api_index_local(req: IndexLocalRequest):
    """Nạp và index một file PDF đã có sẵn trên ổ đĩa."""
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy file tại đường dẫn: {req.file_path}")

    try:
        pages_data = process_pdf(req.file_path)
        chunks = chunking(pages_data, chunk_size=600, chunk_overlap=100)
        index_chunks(chunks)

        return {
            "status": "success",
            "file_path": req.file_path,
            "total_pages": len(pages_data),
            "total_chunks": len(chunks),
            "message": f"Đã nạp thành công {len(chunks)} đoạn vào Qdrant!",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi index file: {str(e)}",
        )



if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)