from sentence_transformers import SentenceTransformer
import torch
import numpy as np

device="cuda" if torch.cuda.is_available() else "cpu"
model =SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
model=model.to(device)

documents = [
    "Python là một ngôn ngữ lập trình.",
    "Con mèo đang ngủ trên ghế.",
    "PyTorch được sử dụng trong Deep Learning.",
    "Hà Nội là thủ đô của Việt Nam."
]
question = "Python được dùng trong AI."

doc_embd=model.encode(documents,normalize_embeddings=True)
ques_embd=model.encode([question],normalize_embeddings=True)

similarities=np.dot(doc_embd,ques_embd.T).flatten()
similarities=np.sort(similarities)[::-1][:2]
print(similarities)