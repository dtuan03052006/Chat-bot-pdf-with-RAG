from urllib import response

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import  Distance,VectorParams,PointStruct
import ollama
from processing_data import process_pdf


data= process_pdf("/home/abc/Code/Code AI/RAG/data/31-2024-qh15_1.pdf")
for dt in data:
    print(dt,end="\n")

# #chunk
# splitter= RecursiveCharacterTextSplitter(
#     chunk_size=100,
#     chunk_overlap=20,
# )
# chunks=splitter.split_text(text)

# #tokenizer, embedding
# device="cuda" if torch.cuda.is_available() else "cpu"
# model =SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# model=model.to(device)

# def embed_text(text):
#     vt=model.encode(text,normalize_embeddings=True)
#     return vt

# vector_ebd=[]
# for chunk in chunks:
#     vector_ebd.append(embed_text(chunk))

# #vector db
# client = QdrantClient(":memory:")
# client.create_collection(
#     collection_name="documents",
#     vectors_config=VectorParams(
#         size=384,
#         distance=Distance.COSINE
#     )
# )

# points=[]
# for i,(chunk,vteb) in enumerate(zip(chunks,vector_ebd)):
#     point=PointStruct(
#                 id=i,
#                 vector=vteb.tolist(),
#                 payload={
#                     "text": chunk,
#                     "chunk_id" : i
#                 }
#             )
#     points.append(point)

# client.upsert(
#     collection_name="documents",
#     points=points
# )


# #promt
# def build_prompt(question, context):
#     prompt = f"""
# Bạn là một trợ lý AI trả lời câu hỏi
# dựa trên tài liệu được cung cấp.

# QUY TẮC:

# 1. Chỉ sử dụng thông tin trong Context.
# 2. Không tự bịa thông tin.
# 3. Nếu Context không có câu trả lời,
#    hãy nói rằng không tìm thấy thông tin
#    trong tài liệu.

# Context:
# {context}

# Question:
# {question}

# Answer:
# """

#     return prompt

# #LLM
# def ask_rag(question: str) -> dict:
#     # 1. Embed câu hỏi
#     query_vector = embed_text(question)
#     # 2. Tìm kiếm đoạn tương đồng nhất trong Qdrant
#     results = client.query_points(
#         collection_name="documents",
#         query=query_vector,
#         limit=3
#     )
#     context_parts = [r.payload["text"] for r in results.points]
#     context = "\n\n".join(context_parts)
#     # 3. Dựng prompt
#     prompt = build_prompt(question, context)
#     # 4. Gọi Ollama sinh câu trả lời (lưu ý: bỏ dấu cách thừa ở tên model)
#     response = ollama.chat(
#         model="gemma3:4b",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return {
#         "question": question,
#         "answer": response["message"]["content"],
#         "context": context_parts
#     }