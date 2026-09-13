import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from total import ask_rag
app = FastAPI(
    title="Local Ollama RAG API",
    description="API hỏi đáp tài liệu cục bộ sử dụng Qdrant và Ollama (Gemma 3)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str = Field(..., example="Tài liệu này nói về điều gì?")

@app.post("/api/ask", summary="Đặt câu hỏi cho RAG Chatbot")
def api_ask_question(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống!")
    try:
        result = ask_rag(req.question)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý: {str(e)}")

@app.get("/", summary="Health Check")
def root():
    return {"status": "online", "docs_url": "/docs"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)