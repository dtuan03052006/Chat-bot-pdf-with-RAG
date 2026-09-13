from qdrant_client import QdrantClient
from qdrant_client.models import  Distance,VectorParams,PointStruct


client = QdrantClient(":memory:")
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=2,
        distance=Distance.COSINE
    )
)
client.upsert(
    collection_name="documents",
    points=[
        PointStruct(
            id=1,
            vector=[0.9, 0.1],
            payload={
                "text": "Python là ngôn ngữ lập trình.",
                "page": 1
            }
        ),

        PointStruct(
            id=2,
            vector=[0.1, 0.9],
            payload={
                "text": "Con mèo đang ngủ.",
                "page": 2
            }
        ),

        PointStruct(
            id=3,
            vector=[0.8, 0.2],
            payload={
                "text": "PyTorch được dùng trong Deep Learning.",
                "page": 5
            }
        ),
        PointStruct(
            id=4,
            vector=[0.8, 0.2],
            payload={
                "text": "FastAPI là web framework của Python.",
                "page": 12,
                "source": "fastapi.pdf"
            }
        )
    ]
)
query_vector = [0.85, 0.15]
result = client.query_points(
    collection_name="documents",
    query=query_vector,
    limit=2
)

print(result.points)