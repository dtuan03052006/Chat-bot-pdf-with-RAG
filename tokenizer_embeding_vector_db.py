import collections
import uuid
import torch
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


device = "cuda" if torch.cuda.is_available() else "cpu"
embed_model = SentenceTransformer("BAAI/bge-m3", device=device)

client = QdrantClient(path="qdrant_storage")
collection_name= "pdf_knowledge_base"

def init_collection():
    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )


def index_chunks(chunks):
    init_collection()
    texts=[c["text"] for c in chunks]
    vector_emb=embed_model.encode(texts,normalize_embeddings=True)
    points=[]
    for chunnk_id,(c,vt) in enumerate( zip(chunks,vector_emb)):
        points.append(
            PointStruct(
                id=chunnk_id+1,
                vector=vt.tolist(),
                payload={
                    "text": c["text"],
                    "source": c["source"],
                    "page": c["page"],
                }
            )
        )
    client.upsert(collection_name,points=points)

def retrieve_top_k(query,top_k):
    query_vt=embed_model.encode(query,normalize_embeddings=True)
    result=client.query_points(
        collection_name=collection_name,
        query=query_vt,
        limit=top_k
    )
    return [res.payload for res in result.points]
